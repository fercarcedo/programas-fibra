from urllib.parse import urljoin
import re
import time
from bs4 import BeautifulSoup
from application.parsers.date_parser import parse_last_updated
from domain.program_update_result import ProgramUpdateResult
from domain.check_updated_programs_result import CheckUpdatedProgramsResult, SkippedProgram
from domain.repositories.config_repository import ConfigRepository
from domain.repositories.program_repository import ProgramRepository
from domain.renderers.page_renderer import PageRenderer
from domain.fetchers.xlsx_fetcher import XlsxFetcher

_DATE_REGEX = re.compile(r"Fecha de actualización:\s*(?P<date>\d{2}/\d{2}/\d{4})")

class CheckUpdatedProgramsUseCase:
    def __init__(
        self,
        config_repository: ConfigRepository,
        program_repository: ProgramRepository,
        page_renderer: PageRenderer,
        xlsx_fetcher: XlsxFetcher,
    ):
        self.config_repository = config_repository
        self.program_repository = program_repository
        self.page_renderer = page_renderer
        self.xlsx_fetcher = xlsx_fetcher

    async def execute(self) -> CheckUpdatedProgramsResult:
        self._skipped: list[SkippedProgram] = []
        url_map = await self.config_repository.get_fiber_program_to_url_map()
        updated = []
        for program_name, url in url_map.items():
            result = await self._process_url(program_name, url)
            if result is not None:
                updated.append(result)
        return CheckUpdatedProgramsResult(updated=updated, skipped=self._skipped)

    def _log_skip(self, program_name: str, url: str, reason: str) -> None:
        print(f"[check-updated-programs][ERROR] program={program_name!r} url={url!r} reason={reason}")
        self._skipped.append(SkippedProgram(program_name=program_name, url=url, reason=reason))

    async def _process_url(self, program_name: str, url: str) -> ProgramUpdateResult | None:
        try:
            html = await self.page_renderer.render(url)
            xlsx_url, last_update_date = self._parse_page(url, html)
            if xlsx_url is None:
                self._log_skip(program_name, url, "missing xlsx anchor")
                return None
            if last_update_date is not None:
                return await self._check_by_date(program_name, url, xlsx_url, last_update_date)
            return await self._check_by_digest(program_name, url, xlsx_url)
        except Exception as exc:
            self._log_skip(program_name, url, f"unhandled error: {exc!r}")
            return None

    def _parse_page(self, url: str, html: str) -> tuple[str | None, str | None]:
        soup = BeautifulSoup(html, "html.parser")
        excel_link = soup.find("a", class_="file xlsx")
        if excel_link is None:
            return None, None
        xlsx_url = urljoin(url, excel_link.get("href"))

        content_div = soup.find("div", class_="col-contenido")
        paragraphs = content_div.find_all("p", string=_DATE_REGEX) if content_div else []
        if not paragraphs:
            return xlsx_url, None
        match = _DATE_REGEX.search(paragraphs[0].get_text(strip=True))
        return xlsx_url, match.group("date")

    async def _check_by_date(self, program_name: str, page_url: str, xlsx_url: str, date_str: str) -> ProgramUpdateResult | None:
        last_updated_ts = parse_last_updated(date_str)
        saved_last_updated = await self.program_repository.get_last_update(program_name) or 0
        if last_updated_ts <= saved_last_updated:
            return None
        return ProgramUpdateResult(file_url=xlsx_url, page_url=page_url, program_name=program_name, last_updated=last_updated_ts)

    async def _check_by_digest(self, program_name: str, page_url: str, xlsx_url: str) -> ProgramUpdateResult | None:
        latest_digest = await self.xlsx_fetcher.get_latest_digest(page_url, xlsx_url)
        if latest_digest is None:
            self._log_skip(program_name, page_url, "could not fetch xlsx digest (and no Fecha de actualización)")
            return None
        stored_digest = await self.program_repository.get_last_xlsx_digest(program_name)
        if latest_digest == stored_digest:
            return None
        return ProgramUpdateResult(file_url=xlsx_url, page_url=page_url, program_name=program_name, last_updated=int(time.time()))
