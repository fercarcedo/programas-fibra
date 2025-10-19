from workers import fetch, Request
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import json
from util.date_parser import parse_last_updated
from dataclasses import dataclass

@dataclass
class ProgramUpdateResult:
    file_url: str
    program_name: str
    last_updated: int

class CheckUpdatedProgramsStep:
    def __init__(self, env):
        self.env = env

    async def run(self):
        url_map = await self.env.CONFIG.get("workflow:fiber-program-url-map")
        url_map_object = json.loads(url_map)

        result = [await self._process_url(program_name, url) for program_name, url in url_map_object.items()]
        return [r for r in result if await self._is_updated(r)]

    async def _process_url(self, program_name: str, url: str) -> ProgramUpdateResult:
        response = await fetch(url)
        page_html = await response.text()

        date_regex = re.compile(r"Fecha de actualización:\s*(?P<date>\d{2}/\d{2}/\d{4})")

        soup = BeautifulSoup(page_html, "html.parser")
        content_div = soup.find("div", class_="col-contenido")
        paragraphs = content_div.find_all("p", string=date_regex)

        excel_link_element = soup.find("a", class_="file xlsx")
        excel_link = excel_link_element.get("href")
        excel_absolute_link = urljoin(url, excel_link)

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

    async def _is_updated(self, result: ProgramUpdateResult) -> bool:
        saved_last_updated = await self.env.PROJECTS.get(f"programs:{result.program_name}:last-updated")
        if not saved_last_updated:
            saved_last_updated = 0
        return result.last_updated > saved_last_updated