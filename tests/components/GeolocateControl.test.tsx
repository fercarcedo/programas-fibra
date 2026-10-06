import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, render, screen } from "@testing-library/react";
import { useControl } from "react-map-gl/maplibre";
import GeolocateControl, {
  PendingGeolocateControl,
} from "../../src/components/GeolocateControl";

vi.mock("react-map-gl/maplibre", () => ({ useControl: vi.fn() }));

const WAITING_CLASS = "maplibregl-ctrl-geolocate-waiting";

type Callbacks = {
  onSuccess: PositionCallback;
  onError: PositionErrorCallback;
};

// The control is exercised without a map: only the button and the answer from
// the device matter here, so it is given a button of its own and treated as
// already set up, and geolocation is answered by hand.
const setUp = (
  control = new PendingGeolocateControl(),
  maxBounds: { west: number; east: number; south: number; north: number } = {
    west: -19.1,
    east: 8,
    south: 26.8,
    north: 44.5,
  },
) => {
  const requests: Callbacks[] = [];
  const getCurrentPosition = vi.fn(
    (
      onSuccess: PositionCallback,
      onError: PositionErrorCallback,
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      _options?: PositionOptions,
    ) => {
      requests.push({ onSuccess, onError });
    },
  );
  Object.defineProperty(window.navigator, "geolocation", {
    configurable: true,
    value: { getCurrentPosition },
  });

  const button = document.createElement("button");
  control._geolocateButton = button;
  control._setup = true;
  // Stands in for the map: moving the camera is not what is under test.
  const fakeMap = {
    getMaxBounds: () => ({
      getWest: () => maxBounds.west,
      getEast: () => maxBounds.east,
      getSouth: () => maxBounds.south,
      getNorth: () => maxBounds.north,
    }),
    _getUIString: (key: string) => key,
  };
  (control as unknown as { _map: unknown })._map = fakeMap;
  control._updateCamera = vi.fn();

  return { control, button, requests, getCurrentPosition };
};

const position = {
  coords: { latitude: 40.4, longitude: -3.7, accuracy: 10 },
  timestamp: 0,
} as GeolocationPosition;

describe("PendingGeolocateControl", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("shows it is busy while waiting for a position", () => {
    const { control, button } = setUp();

    control.trigger();

    expect(button.classList.contains(WAITING_CLASS)).toBe(true);
    expect(button.getAttribute("aria-disabled")).toBe("true");
    expect(button.getAttribute("aria-busy")).toBe("true");
  });

  it("ignores taps while a request is out", () => {
    const { control, getCurrentPosition } = setUp();

    expect(control.trigger()).toBe(true);
    expect(control.trigger()).toBe(false);

    expect(getCurrentPosition).toHaveBeenCalledTimes(1);
  });

  it("is handed back once the position arrives", () => {
    const { control, button, requests, getCurrentPosition } = setUp();

    control.trigger();
    requests[0].onSuccess(position);

    expect(control._updateCamera).toHaveBeenCalled();
    expect(button.classList.contains(WAITING_CLASS)).toBe(false);
    expect(button.hasAttribute("aria-disabled")).toBe(false);
    expect(button.hasAttribute("aria-busy")).toBe(false);

    control.trigger();
    expect(getCurrentPosition).toHaveBeenCalledTimes(2);
  });

  it("is handed back when the position cannot be found", () => {
    const { control, button, requests } = setUp();

    control.trigger();
    requests[0].onError({ code: 3 } as GeolocationPositionError);

    expect(button.classList.contains(WAITING_CLASS)).toBe(false);
    expect(button.hasAttribute("aria-disabled")).toBe(false);
    expect(button.disabled).toBe(false);
  });

  it("stays disabled once permission has been refused", () => {
    const { control, button, requests } = setUp();

    control.trigger();
    requests[0].onError({ code: 1 } as GeolocationPositionError);

    expect(button.classList.contains(WAITING_CLASS)).toBe(false);
    expect(button.disabled).toBe(true);
  });

  it("gives up if the device never answers", () => {
    const { control, button } = setUp();

    control.trigger();
    vi.advanceTimersByTime(30_000);

    expect(button.classList.contains(WAITING_CLASS)).toBe(false);
    expect(button.hasAttribute("aria-disabled")).toBe(false);
  });

  it("asks for a position with room for a slow first fix", () => {
    const { control, getCurrentPosition } = setUp();

    control.trigger();

    expect(getCurrentPosition.mock.calls[0][2]).toMatchObject({
      timeout: 15_000,
      maximumAge: 60_000,
    });
  });

  it("reports a refusal to share the location", () => {
    const onFailureChange = vi.fn();
    const { control, requests } = setUp(
      new PendingGeolocateControl(onFailureChange),
    );

    control.trigger();
    requests[0].onError({ code: 1 } as GeolocationPositionError);

    expect(onFailureChange).toHaveBeenLastCalledWith("denied");
  });

  it("reports a position that could not be found", () => {
    const onFailureChange = vi.fn();
    const { control, requests } = setUp(
      new PendingGeolocateControl(onFailureChange),
    );

    control.trigger();
    requests[0].onError({ code: 3 } as GeolocationPositionError);

    expect(onFailureChange).toHaveBeenLastCalledWith("unavailable");
  });

  it("reports a position outside the map", () => {
    const onFailureChange = vi.fn();
    const { control, requests } = setUp(
      new PendingGeolocateControl(onFailureChange),
      { west: 0, east: 1, south: 0, north: 1 },
    );

    control.trigger();
    requests[0].onSuccess(position);

    expect(control._updateCamera).not.toHaveBeenCalled();
    expect(onFailureChange).toHaveBeenLastCalledWith("outofbounds");
  });

  it("reports giving up on a device that never answers", () => {
    const onFailureChange = vi.fn();
    const { control } = setUp(new PendingGeolocateControl(onFailureChange));

    control.trigger();
    vi.advanceTimersByTime(30_000);

    expect(onFailureChange).toHaveBeenLastCalledWith("unavailable");
  });

  it("does not report a position that arrives after giving up", () => {
    const onFailureChange = vi.fn();
    const { control, requests } = setUp(
      new PendingGeolocateControl(onFailureChange),
    );

    control.trigger();
    vi.advanceTimersByTime(30_000);
    requests[0].onError({ code: 3 } as GeolocationPositionError);

    expect(
      onFailureChange.mock.calls.filter(([failure]) => failure !== null),
    ).toHaveLength(1);
  });

  it("clears the last failure with a new tap", () => {
    const onFailureChange = vi.fn();
    const { control, requests } = setUp(
      new PendingGeolocateControl(onFailureChange),
    );

    control.trigger();
    requests[0].onError({ code: 3 } as GeolocationPositionError);
    control.trigger();

    expect(onFailureChange).toHaveBeenLastCalledWith(null);
  });

  it("does not report a position on the map", () => {
    const onFailureChange = vi.fn();
    const { control, requests } = setUp(
      new PendingGeolocateControl(onFailureChange),
    );

    control.trigger();
    requests[0].onSuccess(position);

    expect(
      onFailureChange.mock.calls.filter(([failure]) => failure !== null),
    ).toHaveLength(0);
  });
});

describe("GeolocateControl", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  // Hands back the control GeolocateControl asked useControl to create, which
  // is how the failures it reports reach the component.
  const renderControl = () => {
    let control: PendingGeolocateControl | undefined;
    vi.mocked(useControl).mockImplementation(((
      create: () => PendingGeolocateControl,
    ) => {
      control ??= create();
      return control;
    }) as unknown as typeof useControl);
    render(<GeolocateControl position="top-left" />);
    return control!;
  };

  it("tells the user when the location could not be found", () => {
    const control = renderControl();
    const { requests } = setUp(control);

    act(() => {
      control.trigger();
      requests[0].onError({ code: 3 } as GeolocationPositionError);
    });

    expect(screen.getByRole("status").textContent).toBe(
      "No se ha podido obtener tu ubicación. Inténtalo de nuevo.",
    );
  });

  it("tells the user when they have refused to share the location", () => {
    const control = renderControl();
    const { requests } = setUp(control);

    act(() => {
      control.trigger();
      requests[0].onError({ code: 1 } as GeolocationPositionError);
    });

    expect(screen.getByRole("status").textContent).toContain(
      "No se ha permitido el acceso a tu ubicación",
    );
  });

  it("tells the user when they are outside the map", () => {
    const control = renderControl();
    const { requests } = setUp(control, {
      west: 0,
      east: 1,
      south: 0,
      north: 1,
    });

    act(() => {
      control.trigger();
      requests[0].onSuccess(position);
    });

    expect(screen.getByRole("status").textContent).toBe(
      "Tu ubicación está fuera de la zona que cubre el mapa.",
    );
  });

  it("shows nothing while the location is being found", () => {
    const control = renderControl();
    setUp(control);

    act(() => {
      control.trigger();
    });

    expect(screen.queryByRole("status")).toBeNull();
  });
});
