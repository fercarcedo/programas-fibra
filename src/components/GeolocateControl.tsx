import maplibregl from "maplibre-gl";
import { useControl, type ControlPosition } from "react-map-gl/maplibre";

export type GeolocateControlProps = {
  position: ControlPosition;
};

const WAITING_CLASS = "maplibregl-ctrl-geolocate-waiting";

// A phone with no recent fix can take well over MapLibre's default of six
// seconds to come up with one, and running out of time fails silently: the map
// just never moves, and it takes a second tap, by then on a warmed-up fix, to
// get there. A position from the last minute is as good as a fresh one for
// centring the map, and lets a repeat tap answer straight away.
const POSITION_OPTIONS: PositionOptions = {
  enableHighAccuracy: false,
  maximumAge: 60_000,
  timeout: 15_000,
};

// Some browsers never answer at all when their permission prompt is dismissed
// rather than refused, so the button cannot be left waiting on an answer
// indefinitely.
const GIVE_UP_AFTER_MS = 30_000;

/**
 * MapLibre's geolocate control, made to show that it is busy.
 *
 * Without tracking, the stock control gives no sign that a tap has been taken
 * while it waits on the device for a position: the button sits there as though
 * nothing had happened until the map suddenly sets off, and a second tap in the
 * meantime starts a second request. Here the button spins its icon and ignores
 * taps for as long as a request is out, and is handed back once there is an
 * answer of any kind.
 *
 * The button is only marked as disabled rather than actually disabled, since
 * MapLibre draws a disabled geolocate button crossed out, as it does when
 * location is not available at all. That is still left to MapLibre, which
 * disables the button for good once permission has been refused.
 */
export class PendingGeolocateControl extends maplibregl.GeolocateControl {
  _pending = false;
  _giveUpTimeoutId: ReturnType<typeof setTimeout> | undefined;

  constructor() {
    super({ positionOptions: POSITION_OPTIONS, showUserLocation: false });
    this.on("geolocate", this._settle);
    this.on("outofmaxbounds", this._settle);
    this.on("error", this._settle);
  }

  trigger(): boolean {
    if (this._pending) return false;
    const started = super.trigger();
    if (started) {
      this._pending = true;
      this._geolocateButton.classList.add(WAITING_CLASS);
      this._geolocateButton.setAttribute("aria-disabled", "true");
      this._geolocateButton.setAttribute("aria-busy", "true");
      this._giveUpTimeoutId = setTimeout(this._settle, GIVE_UP_AFTER_MS);
    }
    return started;
  }

  onRemove(): void {
    clearTimeout(this._giveUpTimeoutId);
    super.onRemove();
  }

  _settle = () => {
    clearTimeout(this._giveUpTimeoutId);
    this._giveUpTimeoutId = undefined;
    if (!this._pending) return;
    this._pending = false;
    this._geolocateButton.classList.remove(WAITING_CLASS);
    this._geolocateButton.removeAttribute("aria-disabled");
    this._geolocateButton.removeAttribute("aria-busy");
  };
}

function GeolocateControl(props: GeolocateControlProps) {
  useControl(() => new PendingGeolocateControl(), {
    position: props.position,
  });

  return null;
}

export default GeolocateControl;
