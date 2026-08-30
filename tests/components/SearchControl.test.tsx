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

// Dismissing the search bar reaches the geocoder through the map container and
// through whatever useControl hands back, so the tests covering it supply both
// here. The rest leave them unset, which keeps that effect a no-op for them.
const mocks = vi.hoisted(() => ({
  mapContainer: null as HTMLElement | null,
  geocoder: null as { on: Mock; off: Mock; clear: Mock } | null,
}));

vi.mock("react-map-gl/maplibre", () => ({
  useControl: vi.fn(() => mocks.geocoder),
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

  describe("dismissing the search bar", () => {
    const COLLAPSED_CLASS = "maplibregl-ctrl-geocoder--collapsed";
    const EDITING_CLASS = "pf-search-editing";
    let geocoderEl: HTMLElement;
    let input: HTMLInputElement;
    let clearButton: HTMLElement;

    const clickBackButton = () =>
      geocoderEl.querySelector<HTMLElement>(".pf-geocoder-back")!.click();

    // the press is what tells the bar whether a result is being dropped or a
    // half-typed query, so a bare click() would not stand in for a real tap
    const pressClearButton = () => {
      clearButton.dispatchEvent(
        new MouseEvent("mousedown", { bubbles: true, cancelable: true }),
      );
      clearButton.click();
    };

    const emitResult = () => {
      const [, onResult] =
        mocks.geocoder!.on.mock.calls.find(([type]) => type === "result") ?? [];
      onResult();
    };

    const renderWithMap = () => {
      const mapContainer = document.createElement("div");
      mapContainer.innerHTML =
        '<div class="maplibregl-ctrl-geocoder">' +
        '<input class="maplibregl-ctrl-geocoder--input" />' +
        '<button class="maplibregl-ctrl-geocoder--button"></button>' +
        "</div>";
      document.body.appendChild(mapContainer);
      mocks.mapContainer = mapContainer;
      mocks.geocoder = { on: vi.fn(), off: vi.fn(), clear: vi.fn() };

      geocoderEl = mapContainer.querySelector(".maplibregl-ctrl-geocoder")!;
      input = mapContainer.querySelector(".maplibregl-ctrl-geocoder--input")!;
      clearButton = mapContainer.querySelector(
        ".maplibregl-ctrl-geocoder--button",
      )!;

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
      mocks.geocoder = null;
    });

    it("adds a back button to the geocoder", () => {
      renderWithMap();

      const backButton = geocoderEl.querySelector(".pf-geocoder-back");

      expect(backButton).not.toBeNull();
      expect(backButton?.getAttribute("aria-label")).toBe("Cerrar búsqueda");
    });

    it("collapses the search bar but keeps the query when going back", () => {
      renderWithMap();
      input.value = "Oviedo";

      clickBackButton();

      expect(geocoderEl.classList.contains(COLLAPSED_CLASS)).toBe(true);
      // going back is not clearing, that is what the geocoder's own X is for
      expect(input.value).toBe("Oviedo");
      expect(mocks.geocoder!.clear).not.toHaveBeenCalled();
    });

    it("keeps the click from reaching the geocoder container", () => {
      renderWithMap();
      // the geocoder reopens its suggestion list from a listener of its own
      const containerListener = vi.fn();
      geocoderEl.addEventListener("click", containerListener);

      clickBackButton();

      expect(containerListener).not.toHaveBeenCalled();
    });

    it("marks the bar as being edited only while the field has the focus", () => {
      renderWithMap();

      input.focus();
      expect(geocoderEl.classList.contains(EDITING_CLASS)).toBe(true);

      input.blur();
      expect(geocoderEl.classList.contains(EDITING_CLASS)).toBe(false);
    });

    it("holds on to the focus while the back button is pressed", () => {
      renderWithMap();
      const mousedown = new MouseEvent("mousedown", {
        bubbles: true,
        cancelable: true,
      });

      geocoderEl
        .querySelector<HTMLElement>(".pf-geocoder-back")!
        .dispatchEvent(mousedown);

      // losing the focus here would resize the bar and hide the arrow before
      // the press became a click
      expect(mousedown.defaultPrevented).toBe(true);
    });

    it("keeps the query on screen but drops the focus once a result is picked", () => {
      renderWithMap();
      input.value = "Oviedo, Asturias, España";
      input.focus();

      emitResult();

      // picking a result commits it: the query stays as a label of where the
      // map now is, so only the keyboard and the cursor go away
      expect(mocks.geocoder!.clear).not.toHaveBeenCalled();
      expect(input.value).toBe("Oviedo, Asturias, España");
      expect(document.activeElement).not.toBe(input);
      expect(geocoderEl.classList.contains(COLLAPSED_CLASS)).toBe(false);
      expect(geocoderEl.classList.contains(EDITING_CLASS)).toBe(false);
    });

    it("puts the bar away rather than reopening it when a result is dropped", () => {
      renderWithMap();
      // a committed result: on screen, but not being typed into
      input.value = "Oviedo, Asturias, España";

      pressClearButton();

      // the geocoder refocuses the field as it clears, which would otherwise
      // leave the bar open for a search that was never asked for
      expect(geocoderEl.classList.contains(COLLAPSED_CLASS)).toBe(true);
    });

    it("leaves the bar open when it is cleared mid-query", () => {
      renderWithMap();
      input.focus();
      input.value = "Ovi";

      pressClearButton();

      expect(geocoderEl.classList.contains(COLLAPSED_CLASS)).toBe(false);
    });

    it("leaves session history alone while the bar is opened and closed", () => {
      const entries = window.history.length;
      renderWithMap();

      geocoderEl.classList.remove(COLLAPSED_CLASS);
      clickBackButton();

      // holding an entry would let the back gesture close the bar, at the cost
      // of Chrome on Android sliding the whole page on the way out
      expect(window.history.length).toBe(entries);
      expect(window.history.state?.pfSearchOpen).toBeUndefined();
    });

    it("stops listening for results when unmounted", () => {
      const { unmount } = renderWithMap();

      unmount();

      expect(geocoderEl.querySelector(".pf-geocoder-back")).toBeNull();
      expect(mocks.geocoder!.off).toHaveBeenCalledWith(
        "result",
        expect.any(Function),
      );
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
