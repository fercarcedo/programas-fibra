import { beforeAll, beforeEach, describe, expect, it, Mock, vi } from "vitest";
import { useControl } from "react-map-gl/maplibre";
import { render } from "@testing-library/react";
import SearchControl from "../../src/components/SearchControl";
import MaplibreGeocoder, {
  MaplibreGeocoderFeatureResults,
} from "@maplibre/maplibre-gl-geocoder";
import maplibregl from "maplibre-gl";
import search from "../../src/api/nominatim";
import { MOCK_NOMINATIM_RESPONSE_SUCCESS } from "../data/nominatim_responses";

vi.mock("react-map-gl/maplibre", () => ({
  useControl: vi.fn(),
}));

const mockGeocoderInstance = {
  on: vi.fn(),
  off: vi.fn(),
  onAdd: vi.fn(),
  onRemove: vi.fn(),
  getDefaultPosition: vi.fn(() => "top-left"),
};

vi.mock("@maplibre/maplibre-gl-geocoder", () => {
  return {
    default: vi.fn(() => mockGeocoderInstance),
  };
});

vi.mock("maplibre-gl", () => ({
  default: vi.fn(),
  Map: vi.fn(() => ({
    on: vi.fn(),
    off: vi.fn(),
    remove: vi.fn(),
    addControl: vi.fn(),
    removeControl: vi.fn(),
  })),
  NavigationControl: vi.fn(),
  Marker: vi.fn(() => ({
    setLngLat: vi.fn().mockReturnThis(),
    addTo: vi.fn().mockReturnThis(),
    remove: vi.fn(),
  })),
}));

vi.mock("../../src/api/nominatim");

describe("SearchControl", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("creates geocoder with correct parameters", () => {
    render(
      <SearchControl
        position="top-left"
        showResultsWhileTyping={true}
        collapsed={true}
        language="es"
        placeholder="Buscar"
      />,
    );

    const factory = (useControl as Mock).mock.calls[0][0];

    factory();

    expect(MaplibreGeocoder).toHaveBeenCalledWith(
      expect.objectContaining({
        forwardGeocode: expect.any(Function),
      }),
      expect.objectContaining({
        maplibregl,
        placeholder: "Buscar",
        showResultsWhileTyping: true,
        collapsed: true,
        language: "es",
      }),
    );
  });

  it("passes correct options to useControl", () => {
    render(
      <SearchControl
        position="top-left"
        showResultsWhileTyping={true}
        collapsed={true}
        language="es"
        placeholder="Buscar"
      />,
    );

    expect(useControl).toHaveBeenCalledWith(expect.any(Function), {
      position: "top-left",
    });
  });

  it("should invoke nominatim api when it calls forwardGeocode", async () => {
    vi.mocked(search).mockResolvedValue(MOCK_NOMINATIM_RESPONSE_SUCCESS);

    render(
      <SearchControl
        position="top-left"
        showResultsWhileTyping={true}
        collapsed={true}
        language="es"
        placeholder="Buscar"
      />,
    );

    const factory = (useControl as Mock).mock.calls[0][0];

    factory();

    const geocoder = (MaplibreGeocoder as Mock).mock.calls[0][0];

    const result: MaplibreGeocoderFeatureResults =
      await geocoder.forwardGeocode({ query: "Bucharest" });
    const mockFeature = MOCK_NOMINATIM_RESPONSE_SUCCESS.features[0];
    expect(result).toEqual({
      type: "FeatureCollection",
      features: [
        {
          id: "2846295644",
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: [
              mockFeature.bbox[0] +
                (mockFeature.bbox[2] - mockFeature.bbox[0]) / 2,
              mockFeature.bbox[1] +
                (mockFeature.bbox[3] - mockFeature.bbox[1]) / 2,
            ],
          },
          place_name:
            "17, Strada Pictor Alexandru Romano, Bukarest, Bucharest, Sector 2, Bucharest, 023964, Romania",
          text: "17, Strada Pictor Alexandru Romano, Bukarest, Bucharest, Sector 2, Bucharest, 023964, Romania",
          place_type: ["place"],
          properties: mockFeature.properties,
        },
      ],
    });
  });

  it("should return empty feature list if query is empty", async () => {
    render(
      <SearchControl
        position="top-left"
        showResultsWhileTyping={true}
        collapsed={true}
        language="es"
        placeholder="Buscar"
      />,
    );

    const factory = (useControl as Mock).mock.calls[0][0];

    factory();

    const geocoder = (MaplibreGeocoder as Mock).mock.calls[0][0];

    const result: MaplibreGeocoderFeatureResults =
      await geocoder.forwardGeocode({ query: "" });

    expect(result).toEqual({
      type: "FeatureCollection",
      features: [],
    });
  });

  it("should return empty feature list if nominatim search throws error", async () => {
    vi.mocked(search).mockRejectedValue(new Error("failed to fetch"));

    render(
      <SearchControl
        position="top-left"
        showResultsWhileTyping={true}
        collapsed={true}
        language="es"
        placeholder="Buscar"
      />,
    );

    const factory = (useControl as Mock).mock.calls[0][0];

    factory();

    const geocoder = (MaplibreGeocoder as Mock).mock.calls[0][0];

    const result: MaplibreGeocoderFeatureResults =
      await geocoder.forwardGeocode({ query: "Bucharest" });

    expect(result).toEqual({
      type: "FeatureCollection",
      features: [],
    });
  });
});
