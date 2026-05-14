import hashlib
import sys
from unittest.mock import AsyncMock, MagicMock

mock_workers = MagicMock()
sys.modules['workers'] = mock_workers

from infrastructure.fetchers.scrape_do_xlsx_fetcher import ScrapeDoXlsxFetcher

PAGE_URL = "https://avance.digital.gob.es/page.aspx"
XLSX_URL = "https://avance.digital.gob.es/file.xlsx"
VALID_XLSX_BYTES = b"PK\x03\x04" + b"\x00" * 100
EXPECTED_DIGEST = hashlib.sha256(VALID_XLSX_BYTES).hexdigest()


def _make_client(xlsx_bytes: bytes = VALID_XLSX_BYTES, raises: Exception = None) -> MagicMock:
    client = MagicMock()
    if raises:
        client.fetch_page_with_xlsx = AsyncMock(side_effect=raises)
    else:
        client.fetch_page_with_xlsx = AsyncMock(return_value=("<html/>", xlsx_bytes))
    return client


async def test_fetch_returns_bytes_and_digest():
    client = _make_client()
    fetcher = ScrapeDoXlsxFetcher(client=client)
    xlsx_bytes, digest = await fetcher.fetch(PAGE_URL, XLSX_URL)

    assert xlsx_bytes == VALID_XLSX_BYTES
    assert digest == EXPECTED_DIGEST
    client.fetch_page_with_xlsx.assert_called_once_with(PAGE_URL, XLSX_URL)


async def test_fetch_raises_on_invalid_xlsx_magic():
    client = _make_client(xlsx_bytes=b"<html>SafeLine blocked</html>")
    fetcher = ScrapeDoXlsxFetcher(client=client)

    try:
        await fetcher.fetch(PAGE_URL, XLSX_URL)
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "not a valid xlsx" in str(exc)


async def test_fetch_propagates_client_error():
    client = _make_client(raises=RuntimeError("[scrape-do] ERR_HTTP_403"))
    fetcher = ScrapeDoXlsxFetcher(client=client)

    try:
        await fetcher.fetch(PAGE_URL, XLSX_URL)
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "ERR_HTTP_403" in str(exc)


async def test_get_latest_digest_returns_digest():
    client = _make_client()
    fetcher = ScrapeDoXlsxFetcher(client=client)
    digest = await fetcher.get_latest_digest(PAGE_URL, XLSX_URL)

    assert digest == EXPECTED_DIGEST


async def test_get_latest_digest_returns_none_on_failure():
    client = _make_client(raises=RuntimeError("network error"))
    fetcher = ScrapeDoXlsxFetcher(client=client)
    digest = await fetcher.get_latest_digest(PAGE_URL, XLSX_URL)

    assert digest is None
