import type { NominatimSearchResponse } from "./types";

async function search(query: string): Promise<NominatimSearchResponse[]> {
  if (!query || !query.trim()) {
    return [];
  }

  const url = new URL("https://nominatim.openstreetmap.org/search");
  url.searchParams.set("q", query.toString());
  url.searchParams.set("format", "json");
  url.searchParams.set("countrycodes", "ES");

  const response = await fetch(url.toString());

  if (!response.ok) {
    throw new Error(`Nominatim search not successful: ${response.status}`);
  }

  return await response.json();
}

export default search;
