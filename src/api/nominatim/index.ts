import type { NominatimSearchResponse } from "./types";

const EMPTY_RESPONSE = {
  "type": "FeatureCollection",
  "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
  "features": []
}

async function search(query: string): Promise<NominatimSearchResponse> {
  if (!query || !query.trim()) {
    return EMPTY_RESPONSE;
  }

  const url = new URL("https://nominatim.openstreetmap.org/search");
  url.searchParams.set("q", query.toString());
  url.searchParams.set("format", "geojson");
  url.searchParams.set("polygon_geojson", "1");
  url.searchParams.set("addressdetails", "1");
  url.searchParams.set("countrycodes", "es");
  url.searchParams.set("accept-language", "es");

  const response = await fetch(url.toString());

  if (!response.ok) {
    throw new Error(`Nominatim search not successful: ${response.status}`);
  }

  return await response.json();
}

export default search;
