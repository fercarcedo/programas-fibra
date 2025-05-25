import { beforeEach, describe, expect, it, vi } from "vitest";
import search from "../../../src/api/nominatim";
import { MOCK_NOMINATIM_RESPONSE_SUCCESS } from "../../data/nominatim_responses";

describe("Nominatim API", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  it("should search and return result", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_NOMINATIM_RESPONSE_SUCCESS),
    } as Response);

    const result = await search("Bucharest");
    expect(result).toEqual(MOCK_NOMINATIM_RESPONSE_SUCCESS);
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
