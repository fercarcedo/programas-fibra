import { afterEach, beforeEach, describe, expect, it, Mock, vi } from "vitest";
import { useControl } from "react-map-gl/maplibre";
import { render } from "@testing-library/react";
import SearchControl from "../../src/components/SearchControl";
import MaplibreGeocoder, {
  MaplibreGeocoderFeatureResults,
} from "@maplibre/maplibre-gl-geocoder";
import maplibregl from "maplibre-gl";
import search from "../../src/api/nominatim";
import { MOCK_NOMINATIM_RESPONSE_SUCCESS } from "../data/nominatim_responses";

// The back button looks the geocoder up through the map container, so the tests
// that cover it hand a real one over here. The rest leave it unset, which keeps
// the component's effect a no-op for them.
const mocks = vi.hoisted(() => ({ mapContainer: null as HTMLElement | null }));

vi.mock("react-map-gl/maplibre", () => ({
  useControl: vi.fn(),
  useMap: vi.fn(() => ({
    current: mocks.mapContainer
      ? { getContainer: () => mocks.mapContainer }
      : undefined,
  })),
}));

const mockGeocoderInstance = {
  on: vi.fn(),
  off: vi.fn(),
  onAdd: vi.fn(),
  onRemove: vi.fn(),
  getDefaultPosition: vi.fn(() => "top-left"),
};

vi.mock("@maplibre/maplibre-gl-geocoder", () => {
  function MockMaplibreGeocoder() {
    return mockGeocoderInstance;
  }
  return {
    default: vi.fn(MockMaplibreGeocoder),
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
    const mockFeature = MOCK_NOMINATIM_RESPONSE_SUCCESS[0];
    expect(result).toEqual({
      type: "FeatureCollection",
      features: [
        {
          id: "2846295644",
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: [
              parseFloat(mockFeature.lon),
              parseFloat(mockFeature.lat),
            ],
          },
          place_name:
            "17, Strada Pictor Alexandru Romano, Bukarest, Bucharest, Sector 2, Bucharest, 023964, Romania",
          text: "17, Strada Pictor Alexandru Romano, Bukarest, Bucharest, Sector 2, Bucharest, 023964, Romania",
          place_type: ["place"],
          properties: {
            addresstype: mockFeature.addresstype,
            display_name: mockFeature.display_name,
            importance: mockFeature.importance,
            name: mockFeature.name,
            osm_id: mockFeature.osm_id,
            osm_type: mockFeature.osm_type,
            place_id: mockFeature.place_id,
            place_rank: mockFeature.place_rank,
            type: mockFeature.type,
          },
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

  describe("back button", () => {
    const COLLAPSED_CLASS = "maplibregl-ctrl-geocoder--collapsed";
    let geocoder: HTMLElement;
    let input: HTMLInputElement;

    const renderWithMap = () => {
      const mapContainer = document.createElement("div");
      mapContainer.innerHTML =
        '<div class="maplibregl-ctrl-geocoder">' +
        '<input class="maplibregl-ctrl-geocoder--input" />' +
        "</div>";
      document.body.appendChild(mapContainer);
      mocks.mapContainer = mapContainer;

      geocoder = mapContainer.querySelector(".maplibregl-ctrl-geocoder")!;
      input = mapContainer.querySelector(".maplibregl-ctrl-geocoder--input")!;

      return render(
        <SearchControl
          position="top-left"
          showResultsWhileTyping={true}
          collapsed={true}
          language="es"
          placeholder="Buscar"
        />,
      );
    };

    afterEach(() => {
      mocks.mapContainer?.remove();
      mocks.mapContainer = null;
    });

    it("adds a back button to the geocoder", () => {
      renderWithMap();

      const backButton = geocoder.querySelector(".pf-geocoder-back");

      expect(backButton).not.toBeNull();
      expect(backButton?.getAttribute("aria-label")).toBe("Cerrar búsqueda");
    });

    it("collapses the search bar but keeps the query when clicked", () => {
      renderWithMap();
      input.value = "Oviedo";

      geocoder.querySelector<HTMLElement>(".pf-geocoder-back")!.click();

      expect(geocoder.classList.contains(COLLAPSED_CLASS)).toBe(true);
      // dismissing the bar is not the same as clearing it, that is what the
      // geocoder's own X button is for
      expect(input.value).toBe("Oviedo");
    });

    it("keeps the click from reaching the geocoder container", () => {
      renderWithMap();
      // the geocoder reopens its suggestion list from a listener of its own
      const containerListener = vi.fn();
      geocoder.addEventListener("click", containerListener);

      geocoder.querySelector<HTMLElement>(".pf-geocoder-back")!.click();

      expect(containerListener).not.toHaveBeenCalled();
    });

    it("removes the back button when unmounted", () => {
      const { unmount } = renderWithMap();

      unmount();

      expect(geocoder.querySelector(".pf-geocoder-back")).toBeNull();
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
