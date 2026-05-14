import base64
import json
import sys
from unittest.mock import AsyncMock, MagicMock, patch

mock_workers = MagicMock()
mock_workers.fetch = AsyncMock()
sys.modules['workers'] = mock_workers

from infrastructure.clients.scrape_do_client import ScrapeDoClient

PAGE_URL = "https://avance.digital.gob.es/page.aspx"
XLSX_URL = "https://avance.digital.gob.es/file.xlsx"
VALID_HTML = "<html><body>Page content</body></html>"
SAFELINE_HTML = "<html><body>content /.safeline/ blocked</body></html>"
VALID_XLSX_BYTES = b"PK\x03\x04" + b"\x00" * 100
VALID_DATA_URL = (
    "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,"
    + base64.b64encode(VALID_XLSX_BYTES).decode()
)


def _make_response(body: str, status: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.ok = status < 400
    resp.status = status
    resp.text = AsyncMock(return_value=body)
    return resp


@patch("infrastructure.clients.scrape_do_client.fetch")
async def test_fetch_page_returns_html(mock_fetch):
    mock_fetch.return_value = _make_response(json.dumps({"content": VALID_HTML, "networkRequests": []}))

    client = ScrapeDoClient(token="mytoken")
    html = await client.fetch_page(PAGE_URL)

    assert html == VALID_HTML
    assert mock_fetch.call_count == 1
    called_url = mock_fetch.call_args[0][0]
    assert "token=mytoken" in called_url
    assert "render=true" in called_url
    assert "geoCode=es" in called_url
    assert "returnJSON=true" in called_url
    assert "playWithBrowser" not in called_url


@patch("infrastructure.clients.scrape_do_client.fetch")
async def test_fetch_page_raises_on_safeline(mock_fetch):
    mock_fetch.return_value = _make_response(json.dumps({"content": SAFELINE_HTML, "networkRequests": []}))

    client = ScrapeDoClient(token="tok")
    try:
        await client.fetch_page(PAGE_URL)
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "SafeLine" in str(exc)
        assert PAGE_URL in str(exc)


@patch("infrastructure.clients.scrape_do_client.fetch")
async def test_fetch_page_raises_on_non_ok_status(mock_fetch):
    mock_fetch.return_value = _make_response("server error", status=503)

    client = ScrapeDoClient(token="tok")
    try:
        await client.fetch_page(PAGE_URL)
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "503" in str(exc)
        assert "server error" in str(exc)


@patch("infrastructure.clients.scrape_do_client.fetch")
async def test_fetch_page_raises_on_non_json(mock_fetch):
    mock_fetch.return_value = _make_response("<html>not json</html>")

    client = ScrapeDoClient(token="tok")
    try:
        await client.fetch_page(PAGE_URL)
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "non-JSON" in str(exc)


@patch("infrastructure.clients.scrape_do_client.fetch")
async def test_fetch_page_with_xlsx_returns_html_and_bytes(mock_fetch):
    mock_fetch.return_value = _make_response(json.dumps({
        "content": VALID_HTML,
        "actionResults": [{"action": "Execute", "index": 0, "response": VALID_DATA_URL}],
        "networkRequests": [],
    }))

    client = ScrapeDoClient(token="tok")
    html, xlsx_bytes = await client.fetch_page_with_xlsx(PAGE_URL, XLSX_URL)

    assert html == VALID_HTML
    assert xlsx_bytes == VALID_XLSX_BYTES
    called_url = mock_fetch.call_args[0][0]
    assert "playWithBrowser=" in called_url


@patch("infrastructure.clients.scrape_do_client.fetch")
async def test_fetch_page_with_xlsx_includes_xlsx_url_in_execute_js(mock_fetch):
    mock_fetch.return_value = _make_response(json.dumps({
        "content": VALID_HTML,
        "actionResults": [{"action": "Execute", "index": 0, "response": VALID_DATA_URL}],
        "networkRequests": [],
    }))

    client = ScrapeDoClient(token="tok")
    await client.fetch_page_with_xlsx(PAGE_URL, XLSX_URL)

    from urllib.parse import unquote
    called_url = mock_fetch.call_args[0][0]
    decoded = unquote(called_url)
    assert XLSX_URL in decoded


@patch("infrastructure.clients.scrape_do_client.fetch")
async def test_fetch_page_with_xlsx_raises_on_err_response(mock_fetch):
    mock_fetch.return_value = _make_response(json.dumps({
        "content": VALID_HTML,
        "actionResults": [{"action": "Execute", "index": 0, "response": "ERR_HTTP_403"}],
        "networkRequests": [],
    }))

    client = ScrapeDoClient(token="tok")
    try:
        await client.fetch_page_with_xlsx(PAGE_URL, XLSX_URL)
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "ERR_HTTP_403" in str(exc)


@patch("infrastructure.clients.scrape_do_client.fetch")
async def test_fetch_page_with_xlsx_raises_when_no_action_results(mock_fetch):
    mock_fetch.return_value = _make_response(json.dumps({
        "content": VALID_HTML,
        "actionResults": [],
        "networkRequests": [],
    }))

    client = ScrapeDoClient(token="tok")
    try:
        await client.fetch_page_with_xlsx(PAGE_URL, XLSX_URL)
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "actionResults" in str(exc)


@patch("infrastructure.clients.scrape_do_client.fetch")
async def test_fetch_page_with_xlsx_raises_on_safeline(mock_fetch):
    mock_fetch.return_value = _make_response(json.dumps({
        "content": SAFELINE_HTML,
        "actionResults": [{"action": "Execute", "index": 0, "response": VALID_DATA_URL}],
        "networkRequests": [],
    }))

    client = ScrapeDoClient(token="tok")
    try:
        await client.fetch_page_with_xlsx(PAGE_URL, XLSX_URL)
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "SafeLine" in str(exc)
