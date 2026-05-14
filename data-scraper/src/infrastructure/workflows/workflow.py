from workers import WorkflowEntrypoint
from contextlib import asynccontextmanager
from dataclasses import asdict
from application.use_cases.check_updated_programs_use_case import CheckUpdatedProgramsUseCase
from application.use_cases.process_programs_use_case import ProcessProgramsUseCase
from application.use_cases.rebuild_status_summary_use_case import RebuildStatusSummaryUseCase
from application.use_cases.update_aggregated_use_case import UpdateAggregatedUseCase
from domain.program_update_result import ProgramUpdateResult
from domain.check_updated_programs_result import SkippedProgram
from domain.notifications.email_notifier import EmailNotifier
from infrastructure.clients.scrape_do_client import ScrapeDoClient
from infrastructure.fetchers.scrape_do_xlsx_fetcher import ScrapeDoXlsxFetcher
from infrastructure.readers.xlsx_sheet_file_reader import XlsxSheetFileReader
from infrastructure.renderers.scrape_do_page_renderer import ScrapeDoPageRenderer
from infrastructure.repositories.kv_config_repository import KVConfigRepository
from infrastructure.repositories.kv_program_repository import KVProgramRepository
from infrastructure.notifications.cloudflare_email_notifier import CloudflareEmailNotifier
from pyodide.ffi import to_js
from js import Object

def _format_skip_summary(skipped: list[SkippedProgram]) -> str:
    lines = [f"- {s.program_name} ({s.url}): {s.reason}" for s in skipped]
    return "The following programs were skipped during scraping:\n\n" + "\n".join(lines)

def _build_skip_alert_subject(skipped_count: int, total_count: int) -> str:
    if skipped_count == total_count:
        return f"[data-scraper] all {total_count} programs skipped"
    return f"[data-scraper] {skipped_count} of {total_count} programs skipped"

@asynccontextmanager
async def _notify_on_failure(notifier: EmailNotifier, context: str):
    try:
        yield
    except Exception as exc:
        try:
            await notifier.send_alert(
                subject=f"[data-scraper] Failure: {context}",
                body=f"An error occurred:\n\n{exc!r}"
            )
        except Exception:
            print(f"[email-notifier][ERROR] Failed to send failure alert for {context}")
        raise

class DataScraperWorkflow(WorkflowEntrypoint):
    def __init__(self, ctx, env):
        config_repository = KVConfigRepository(env)
        program_repository = KVProgramRepository(env)
        sheet_reader = XlsxSheetFileReader()
        scrape_do_client = ScrapeDoClient(token=env.SCRAPEDO_TOKEN)
        page_renderer = ScrapeDoPageRenderer(scrape_do_client)
        xlsx_fetcher = ScrapeDoXlsxFetcher(scrape_do_client)
        self.check_updated_programs_use_case = CheckUpdatedProgramsUseCase(config_repository, program_repository, page_renderer, xlsx_fetcher)
        self.process_programs_use_case = ProcessProgramsUseCase(sheet_reader, program_repository, xlsx_fetcher)
        self.rebuild_status_summary_use_case = RebuildStatusSummaryUseCase(program_repository)
        self.update_aggregated_use_case = UpdateAggregatedUseCase(program_repository)
        self.email_notifier = CloudflareEmailNotifier(env)
        self.env = env

    async def run(self, event, step):
        @step.do('check-updated-programs')
        async def check_updated_programs_step():
            result = await self.check_updated_programs_use_case.execute()
            if result.skipped:
                total = len(result.skipped) + len(result.updated)
                await self.email_notifier.send_alert(
                    subject=_build_skip_alert_subject(len(result.skipped), total),
                    body=_format_skip_summary(result.skipped),
                )
            return [asdict(r) for r in result.updated]

        @step.do('rebuild-status-summary')
        async def rebuild_status_summary_step():
            await self.rebuild_status_summary_use_case.execute()

        @step.do('update-aggregated')
        async def update_aggregated_step():
            await self.update_aggregated_use_case.execute()

        async with _notify_on_failure(self.email_notifier, "data-scraper-workflow"):
            updated_programs_dict = await check_updated_programs_step()
            if len(updated_programs_dict) > 0:
                for i, program_dict in enumerate(updated_programs_dict):
                    @step.do(f'process-program-{program_dict["program_name"]}')
                    async def process_program():
                        program_data = await self.process_programs_use_case.execute(ProgramUpdateResult(**program_dict))
                        return to_js(program_data.to_dict(), dict_converter=Object.fromEntries)

                    await process_program()

                    if i < len(updated_programs_dict) - 1:
                        await step.sleep(f"delay-{updated_programs_dict[i + 1]["program_name"]}", "1 minute")

                await rebuild_status_summary_step()
                await update_aggregated_step()
