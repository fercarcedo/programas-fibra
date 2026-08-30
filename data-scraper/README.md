## Usage

This is a Python Workers project, so `dev`/`deploy` go through
[`pywrangler`](https://pypi.org/project/workers-py/) (`npm run dev` / `npm run deploy`)
rather than plain `wrangler`. `pywrangler` vendors this project's `pyproject.toml`
dependencies (via a Pyodide-targeted build) into `python_modules/` before proxying to
`wrangler` — that vendoring step is what plain `wrangler deploy` skips, and skipping it is
what produces a `ModuleNotFoundError` for a dependency like `bs4` at runtime.

You'll need `uv`, which you can install by following
https://docs.astral.sh/uv/getting-started/installation/. Then run:

```
uv sync
```

This installs `pywrangler` plus this project's dependencies into `.venv`, and also gives
you working autocomplete/type hints if you point your editor's Python plugin at `.venv`.

## Secrets

One secret must be configured via `wrangler secret put` before deploying:

- `SCRAPEDO_TOKEN` — API token for [scrape.do](https://scrape.do). Used to render program pages and fetch xlsx files via in-browser fetch. Run `wrangler secret put SCRAPEDO_TOKEN` and paste the token when prompted.
