import base64
import json
from urllib.parse import urlencode, quote
from workers import fetch


def _build_execute_js(xlsx_url: str) -> str:
    url_literal = json.dumps(xlsx_url)
    return (
        f"(async () => {{"
        f" try {{"
        f" const r = await fetch({url_literal});"
        f" if (!r.ok) return 'ERR_HTTP_' + r.status;"
        f" const b = await r.blob();"
        f" return await new Promise((res) => {{"
        f" const rdr = new FileReader();"
        f" rdr.onloadend = () => res(rdr.result);"
        f" rdr.readAsDataURL(b);"
        f" }});"
        f" }} catch(e) {{"
        f" return 'ERR_FETCH_' + e.message;"
        f" }}"
        f" }})();"
    )


class ScrapeDoClient:
    _API = "https://api.scrape.do/"
    _SAFELINE_MARKER = "/.safeline/"

    def __init__(self, token: str):
        self._token = token

    async def fetch_page(self, url: str) -> str:
        response_json = await self._call(self._base_params(url), f"fetch_page({url!r})")
        html = response_json.get("content", "")
        self._check_safeline(html, url)
        return html

    async def fetch_page_with_xlsx(self, page_url: str, xlsx_url: str) -> tuple[str, bytes]:
        execute_js = _build_execute_js(xlsx_url)
        params = {
            **self._base_params(page_url),
            "playWithBrowser": json.dumps([{"Action": "Execute", "Execute": execute_js}]),
        }
        context = f"fetch_page_with_xlsx({page_url!r}, {xlsx_url!r})"
        response_json = await self._call(params, context)

        html = response_json.get("content", "")
        self._check_safeline(html, page_url)

        action_results = response_json.get("actionResults", [])
        if not action_results:
            raise RuntimeError(f"[scrape-do] {context}: no actionResults in response")
        result_value = action_results[0].get("response", "")
        if result_value.startswith("ERR_"):
            raise RuntimeError(f"[scrape-do] {context}: in-browser fetch failed: {result_value}")
        if not result_value.startswith("data:"):
            raise RuntimeError(f"[scrape-do] {context}: unexpected actionResult response: {result_value[:100]!r}")

        _, b64 = result_value.split(",", 1)
        return html, base64.b64decode(b64)

    def _base_params(self, url: str) -> dict:
        return {
            "token": self._token,
            "url": url,
            "render": "true",
            "geoCode": "es",
            "returnJSON": "true",
        }

    async def _call(self, params: dict, context: str) -> dict:
        api_url = self._API + "?" + urlencode(params, quote_via=quote)
        print(f"[scrape-do] GET {context}")
        response = await fetch(api_url)
        text = await response.text()
        if not response.ok:
            raise RuntimeError(f"[scrape-do] {context}: HTTP {response.status}: {text[:500]!r}")
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"[scrape-do] {context}: non-JSON response: {text[:500]!r}") from exc

    def _check_safeline(self, html: str, url: str) -> None:
        if self._SAFELINE_MARKER in html:
            raise RuntimeError(f"[scrape-do] SafeLine challenge detected for {url!r}")
