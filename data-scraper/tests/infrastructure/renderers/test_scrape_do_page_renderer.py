import sys
from unittest.mock import AsyncMock, MagicMock

mock_workers = MagicMock()
sys.modules['workers'] = mock_workers

from infrastructure.renderers.scrape_do_page_renderer import ScrapeDoPageRenderer

PAGE_URL = "https://avance.digital.gob.es/page.aspx"
HTML_CONTENT = "<html><body>Valid content</body></html>"


def _make_client(html: str = HTML_CONTENT, raises: Exception = None) -> MagicMock:
    client = MagicMock()
    if raises:
        client.fetch_page = AsyncMock(side_effect=raises)
    else:
        client.fetch_page = AsyncMock(return_value=html)
    return client


async def test_render_returns_html():
    client = _make_client()
    renderer = ScrapeDoPageRenderer(client=client)
    html = await renderer.render(PAGE_URL)

    assert html == HTML_CONTENT
    client.fetch_page.assert_called_once_with(PAGE_URL)


async def test_render_propagates_safeline_error():
    client = _make_client(raises=RuntimeError("[scrape-do] SafeLine challenge detected for 'url'"))
    renderer = ScrapeDoPageRenderer(client=client)

    try:
        await renderer.render(PAGE_URL)
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "SafeLine" in str(exc)


async def test_render_propagates_http_error():
    client = _make_client(raises=RuntimeError("[scrape-do] fetch_page: HTTP 503"))
    renderer = ScrapeDoPageRenderer(client=client)

    try:
        await renderer.render(PAGE_URL)
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "503" in str(exc)
