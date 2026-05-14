from abc import ABC, abstractmethod

class XlsxFetcher(ABC):
    @abstractmethod
    async def fetch(self, page_url: str, xlsx_url: str) -> tuple[bytes, str | None]:
        """Fetch the xlsx at xlsx_url rendered in the context of page_url. Returns (bytes, sha256_hex)."""

    @abstractmethod
    async def get_latest_digest(self, page_url: str, xlsx_url: str) -> str | None:
        """Return the current content digest for xlsx_url. None on failure."""
