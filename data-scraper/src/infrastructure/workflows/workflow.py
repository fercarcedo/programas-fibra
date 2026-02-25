from workers import WorkflowEntrypoint
from dataclasses import asdict
from application.use_cases.check_updated_programs_use_case import CheckUpdatedProgramsUseCase
from application.use_cases.process_programs_use_case import ProcessProgramsUseCase
from application.use_cases.rebuild_status_summary_use_case import RebuildStatusSummaryUseCase
from domain.program_update_result import ProgramUpdateResult
from infrastructure.readers.xlsx_sheet_file_reader import XlsxSheetFileReader
from infrastructure.repositories.kv_config_repository import KVConfigRepository
from infrastructure.repositories.kv_program_repository import KVProgramRepository
from pyodide.ffi import to_js
from js import Object

class DataScraperWorkflow(WorkflowEntrypoint):
    def __init__(self, ctx, env):
        config_repository = KVConfigRepository(env)
        program_repository = KVProgramRepository(env)
        sheet_reader = XlsxSheetFileReader()
        self.check_updated_programs_use_case = CheckUpdatedProgramsUseCase(config_repository, program_repository)
        self.process_programs_use_case = ProcessProgramsUseCase(sheet_reader, program_repository)
        self.rebuild_status_summary_use_case = RebuildStatusSummaryUseCase(program_repository)
        self.env = env

    async def run(self, event, step):
        @step.do('check-updated-programs')
        async def check_updated_programs_step():
            program_update_results = await self.check_updated_programs_use_case.execute()
            return [asdict(program_update_result) for program_update_result in program_update_results]

        @step.do('rebuild-status-summary')
        async def rebuild_status_summary_step():
            await self.rebuild_status_summary_use_case.execute()

        updated_programs_dict = await check_updated_programs_step()
        for i, program_dict in enumerate(updated_programs_dict):
            @step.do(f'process-program-{program_dict["program_name"]}')
            async def process_program():
                program_data = await self.process_programs_use_case.execute(ProgramUpdateResult(**program_dict))
                return to_js(program_data.to_dict(), dict_converter=Object.fromEntries)

            await process_program()

            if i < len(updated_programs_dict) - 1:
                await step.sleep(f"delay-{updated_programs_dict[i + 1]["program_name"]}", "1 minute")

        await rebuild_status_summary_step()