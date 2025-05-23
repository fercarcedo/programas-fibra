import { beforeEach, describe, expect, it, vi } from "vitest";
import search from "../../../src/api/nominatim";

// Mock response from osm website
const MOCK_RESPONSE_SUCCESS = {
  type: "FeatureCollection",
  licence:
    "Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright",
  features: [
    {
      type: "Feature",
      properties: {
        place_id: "35811445",
        osm_type: "node",
        osm_id: "2846295644",
        display_name:
          "17, Strada Pictor Alexandru Romano, Bukarest, Bucharest, Sector 2, Bucharest, 023964, Romania",
        place_rank: "30",
        category: "place",
        type: "house",
        importance: 0.62025,
      },
      bbox: [26.1156689, 44.4354754, 26.1157689, 44.4355754],
      geometry: {
        type: "Point",
        coordinates: [26.1157189, 44.4355254],
      },
    },
  ],
};

describe("Nominatim API", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  it("should search and return result", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_RESPONSE_SUCCESS),
    } as Response);

    const result = await search("Bucharest");
    expect(result).toEqual(MOCK_RESPONSE_SUCCESS);
  });

  it("should return empty response if query is empty", async () => {
    const result = await search("");
    expect(result).toEqual({
      type: "FeatureCollection",
      licence:
        "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
      features: [],
    });
  });

  it("should return empty response if query is blank", async () => {
    const result = await search("");
    expect(result).toEqual({
      type: "FeatureCollection",
      licence:
        "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
      features: [],
    });
  });

  it("should throw if api call status not ok", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
    } as Response);

    await expect(search("Bucharest")).rejects.toThrowError(
      "Nominatim search not successful: 500",
    );
  });

  it("should throw if api call throws", async () => {
    vi.mocked(fetch).mockRejectedValue(new TypeError("failed to fetch"));

    await expect(search("Bucharest")).rejects.toThrowError("failed to fetch");
  });
});
