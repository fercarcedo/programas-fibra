from domain.renderers.page_renderer import PageRenderer
from infrastructure.clients.scrape_do_client import ScrapeDoClient


class ScrapeDoPageRenderer(PageRenderer):
    def __init__(self, client: ScrapeDoClient):
        self._client = client

    async def render(self, url: str) -> str:
        return await self._client.fetch_page(url)
