import type { NominatimSearchResponse } from "./types";

async function search(query: string): Promise<NominatimSearchResponse> {
  const url = new URL("https://nominatim.openstreetmap.org/search");
  url.searchParams.set("q", query.toString());
  url.searchParams.set("format", "geojson");
  url.searchParams.set("polygon_geojson", "1");
  url.searchParams.set("addressdetails", "1");
  url.searchParams.set("countrycodes", "es");
  url.searchParams.set("accept-language", "es");

  const response = await fetch(url.toString());
  return await response.json();
}

export default search;
