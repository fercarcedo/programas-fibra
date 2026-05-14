import hashlib
from domain.fetchers.xlsx_fetcher import XlsxFetcher
from infrastructure.clients.scrape_do_client import ScrapeDoClient


class ScrapeDoXlsxFetcher(XlsxFetcher):
    def __init__(self, client: ScrapeDoClient):
        self._client = client

    async def fetch(self, page_url: str, xlsx_url: str) -> tuple[bytes, str | None]:
        _, xlsx_bytes = await self._client.fetch_page_with_xlsx(page_url, xlsx_url)
        if xlsx_bytes[:4] != b"PK\x03\x04":
            raise RuntimeError(
                f"[scrape-do-xlsx-fetcher] {xlsx_url!r}: not a valid xlsx (magic={xlsx_bytes[:4].hex()!r})"
            )
        digest = hashlib.sha256(xlsx_bytes).hexdigest()
        return xlsx_bytes, digest

    async def get_latest_digest(self, page_url: str, xlsx_url: str) -> str | None:
        try:
            _, digest = await self.fetch(page_url, xlsx_url)
            return digest
        except Exception as exc:
            print(f"[scrape-do-xlsx-fetcher] get_latest_digest failed for {xlsx_url!r}: {exc!r}")
            return None
