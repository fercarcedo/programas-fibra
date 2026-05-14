## Usage

You can run the Worker defined by your new project by executing `wrangler dev` in this
directory. This will start up an HTTP server and will allow you to iterate on your
Worker without having to restart `wrangler`.

### Types and autocomplete

This project also includes a pyproject.toml and uv.lock file with some requirements which
set up autocomplete and type hints for this Python Workers project.

To get these installed you'll need `uv`, which you can install by following
https://docs.astral.sh/uv/getting-started/installation/.

Once `uv` is installed, you can run the following:

```
uv venv
uv sync
```

Then point your editor's Python plugin at the `.venv` directory. You should then have working
autocomplete and type information in your editor.

## Secrets

One secret must be configured via `wrangler secret put` before deploying:

- `SCRAPEDO_TOKEN` — API token for [scrape.do](https://scrape.do). Used to render program pages and fetch xlsx files via in-browser fetch. Run `wrangler secret put SCRAPEDO_TOKEN` and paste the token when prompted.