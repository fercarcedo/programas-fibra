from workers import fetch, Request
from urllib.parse import urljoin
import re
import json
from application.parsers.date_parser import parse_last_updated
from dataclasses import dataclass
from domain.program_update_result import ProgramUpdateResult
from domain.check_updated_programs_result import CheckUpdatedProgramsResult, SkippedProgram
from domain.repositories.config_repository import ConfigRepository
from domain.repositories.program_repository import ProgramRepository

class CheckUpdatedProgramsUseCase:
    def __init__(self, config_repository: ConfigRepository, program_repository: ProgramRepository):
        self.config_repository = config_repository
        self.program_repository = program_repository

    async def execute(self) -> CheckUpdatedProgramsResult:
        self._skipped: list[SkippedProgram] = []
        url_map = await self.config_repository.get_fiber_program_to_url_map()

        results = [await self._process_url(program_name, url) for program_name, url in url_map.items()]
        updated = [r for r in results if r is not None and await self._is_updated(r)]
        return CheckUpdatedProgramsResult(updated=updated, skipped=self._skipped)

    def _log_skip(self, program_name: str, url: str, reason: str) -> None:
        print(f"[check-updated-programs][ERROR] program={program_name!r} url={url!r} reason={reason}")
        self._skipped.append(SkippedProgram(program_name=program_name, url=url, reason=reason))

    async def _process_url(self, program_name: str, url: str) -> ProgramUpdateResult | None:
        from bs4 import BeautifulSoup

        try:
            response = await fetch(url)

            if not getattr(response, "ok", True):
                self._log_skip(program_name, url, f"non-2xx status={response.status}")
                return None

            page_html = await response.text()

            soup = BeautifulSoup(page_html, "html.parser")

            excel_link_element = soup.find("a", class_="file xlsx")
            if excel_link_element is None:
                self._log_skip(program_name, url, "missing xlsx anchor")
                return None
            excel_absolute_link = urljoin(url, excel_link_element.get("href"))

            date_regex = re.compile(r"Fecha de actualización:\s*(?P<date>\d{2}/\d{2}/\d{4})")
            content_div = soup.find("div", class_="col-contenido")
            paragraphs = content_div.find_all("p", string=date_regex) if content_div else []

            if len(paragraphs) > 0:
                last_update_text = paragraphs[0].get_text(strip=True)
                match = date_regex.search(last_update_text)
                last_updated = match.group("date")
            else:
                excel_head_response = await fetch(Request(excel_absolute_link, method="HEAD"))
                last_updated = excel_head_response.headers['last-modified']

            return ProgramUpdateResult(
                file_url=excel_absolute_link,
                program_name=program_name,
                last_updated=parse_last_updated(last_updated)
            )
        except Exception as exc:
            self._log_skip(program_name, url, f"unhandled error: {exc!r}")
            return None

    async def _is_updated(self, result: ProgramUpdateResult) -> bool:
        saved_last_updated = await self.program_repository.get_last_update(result.program_name)
        if not saved_last_updated:
            saved_last_updated = 0
        return result.last_updated > saved_last_updated