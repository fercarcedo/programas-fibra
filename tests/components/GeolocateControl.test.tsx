import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { PendingGeolocateControl } from "../../src/components/GeolocateControl";

const WAITING_CLASS = "maplibregl-ctrl-geolocate-waiting";

type Callbacks = {
  onSuccess: PositionCallback;
  onError: PositionErrorCallback;
};

// The control is exercised without a map: only the button and the answer from
// the device matter here, so it is given a button of its own and treated as
// already set up, and geolocation is answered by hand.
const setUp = () => {
  const requests: Callbacks[] = [];
  const getCurrentPosition = vi.fn(
    (onSuccess: PositionCallback, onError: PositionErrorCallback) => {
      requests.push({ onSuccess, onError });
    },
  );
  Object.defineProperty(window.navigator, "geolocation", {
    configurable: true,
    value: { getCurrentPosition },
  });

  const control = new PendingGeolocateControl();
  const button = document.createElement("button");
  control._geolocateButton = button;
  control._setup = true;
  // Stands in for the map: moving the camera is not what is under test.
  const fakeMap = {
    getMaxBounds: () => null,
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
});
