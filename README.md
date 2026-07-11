# <img src="public/icon_192.png" width="32" align="center" alt="" /> Programas Fibra

[programasfibra.es](https://programasfibra.es) is a map that shows all Spanish public
fiber-optic broadband subsidy programs (PEBA and UNICO, 2013–2024) on top of each other,
so you can check which operator is deploying fiber in a given area and under which
program.

Data is published by the Ministry across dozens of scattered Excel and shapefile
releases, one per program per year. This project scrapes, normalizes and merges all of
them into a single set of vector tiles served by an interactive map.

Want the technical details? I gave a talk about how it's built at T3chFest:
[watch it on YouTube](https://youtu.be/YzOBWkEtX6M).

## Modules

This is a monorepo with three independent modules:

### [`/`](.) — Map site (frontend + backend)

The main app: a React + MapLibre/deck.gl map served together with its API, both deployed
as a single Cloudflare Worker via `@cloudflare/vite-plugin`. The worker exposes the
project/area data (backed by KV and R2-hosted PMTiles) and serves the built frontend as
static assets.

```bash
npm install
npm run dev      # local dev server (Vite + worker)
npm test         # vitest
npm run deploy   # build and wrangler deploy
```

### [`data-scraper`](./data-scraper) — Update workflow

A Python Cloudflare Workflow, triggered on a weekly cron, that checks the Ministry's
sources for new or updated program data, downloads it, and updates the KV/R2 data the
main site reads from. See [`data-scraper/README.md`](./data-scraper/README.md) for setup
details (including the `SCRAPEDO_TOKEN` secret).

### [`programas-fibra-data-processing`](./programas-fibra-data-processing) — Geo data generation

A local Python script (`main.py`) that turns the raw PEBA/UNICO releases (shapefiles and
Excel files with awarded-area info) into the GeoJSON/PMTiles and H3 hexagon aggregates
consumed by the site. This runs by hand whenever a new program vintage needs to be
processed for the first time; see
[`process_files.sh`](./programas-fibra-data-processing/process_files.sh) for the full
pipeline (`ogr2ogr` → `main.py` → `tippecanoe` → `tile-join`).

```bash
uv sync
uv run main.py unico -e <eligible-areas.geojson> -a <awarded-areas.xlsx> -o out.geojson -p "UNICO 2024"
```
