import maplibregl from "maplibre-gl";
import { AnimatePresence, motion } from "motion/react";
import { useCallback, useEffect, useState } from "react";
import { useControl, type ControlPosition } from "react-map-gl/maplibre";

export type GeolocateControlProps = {
  position: ControlPosition;
};

const WAITING_CLASS = "maplibregl-ctrl-geolocate-waiting";

/**
 * Why a tap on the button did not take the map to the user: they refused to
 * share their location, they are somewhere the map does not cover, or the
 * device could not come up with a position in time.
 */
export type GeolocateFailure = "denied" | "outofbounds" | "unavailable";

const FAILURE_MESSAGES: Record<GeolocateFailure, string> = {
  denied:
    "No se ha permitido el acceso a tu ubicación. Puedes activarlo en los ajustes del navegador.",
  outofbounds: "Tu ubicación está fuera de la zona que cubre el mapa.",
  unavailable: "No se ha podido obtener tu ubicación. Inténtalo de nuevo.",
};

// Long enough to read the longest of the messages, short enough not to linger
// over the map once it has been read.
const MESSAGE_DURATION_MS = 5_000;

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
 * answer of any kind. Every answer other than a position on the map is passed
 * on to onFailureChange, so that it can be told to the user, and is cleared
 * through it again with the next tap, which makes it out of date.
 *
 * The button is only marked as disabled rather than actually disabled, since
 * MapLibre draws a disabled geolocate button crossed out, as it does when
 * location is not available at all. That is still left to MapLibre, which
 * disables the button for good once permission has been refused.
 */
export class PendingGeolocateControl extends maplibregl.GeolocateControl {
  _pending = false;
  _giveUpTimeoutId: ReturnType<typeof setTimeout> | undefined;

  _onFailureChange: (failure: GeolocateFailure | null) => void;

  constructor(
    onFailureChange: (failure: GeolocateFailure | null) => void = () => {},
  ) {
    super({ positionOptions: POSITION_OPTIONS, showUserLocation: false });
    this._onFailureChange = onFailureChange;
    // There is no location dot to move, and MapLibre would trip over its
    // absence when a position falls outside the map.
    this._updateMarker = () => {};
    this.on("geolocate", this._settle);
    this.on("outofmaxbounds", this._onOutOfMaxBounds);
    this.on("error", this._onPositionError);
  }

  trigger(): boolean {
    if (this._pending) return false;
    const started = super.trigger();
    if (started) {
      this._pending = true;
      this._onFailureChange(null);
      this._geolocateButton.classList.add(WAITING_CLASS);
      this._geolocateButton.setAttribute("aria-disabled", "true");
      this._geolocateButton.setAttribute("aria-busy", "true");
      this._giveUpTimeoutId = setTimeout(this._giveUp, GIVE_UP_AFTER_MS);
    }
    return started;
  }

  // MapLibre marks the button as being in error when a position falls outside
  // the map, but only knows how to do that while tracking: without it, it
  // throws instead, before ever announcing that the position was outside.
  _setErrorState(): void {
    if (this.options.trackUserLocation) super._setErrorState();
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

  _fail = (failure: GeolocateFailure) => {
    // An answer that turns up after the control has given up on it has
    // already been reported as a failure.
    if (!this._pending) return;
    this._settle();
    this._onFailureChange(failure);
  };

  _giveUp = () => this._fail("unavailable");

  _onOutOfMaxBounds = () => this._fail("outofbounds");

  // MapLibre passes on a copy of the browser's error, so the code is compared
  // against its value rather than the PERMISSION_DENIED constant.
  _onPositionError = (error: { code?: number }) =>
    this._fail(error.code === 1 ? "denied" : "unavailable");
}

const GeolocateMessage = ({
  failure,
  onDismiss,
}: {
  failure: GeolocateFailure;
  onDismiss: () => void;
}) => {
  useEffect(() => {
    const timeoutId = setTimeout(onDismiss, MESSAGE_DURATION_MS);
    return () => clearTimeout(timeoutId);
  }, [failure, onDismiss]);

  return (
    <motion.div
      role="status"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 8 }}
      transition={{ duration: 0.2 }}
      onClick={onDismiss}
      className="absolute bottom-16 left-1/2 -translate-x-1/2 z-[50] w-max max-w-[calc(100%-32px)]
                 px-4 py-2.5 rounded-xl bg-gray-800/90 text-white text-sm shadow-lg text-center cursor-pointer"
    >
      {FAILURE_MESSAGES[failure]}
    </motion.div>
  );
};

function GeolocateControl(props: GeolocateControlProps) {
  const [failure, setFailure] = useState<GeolocateFailure | null>(null);
  const dismiss = useCallback(() => setFailure(null), []);

  useControl(() => new PendingGeolocateControl(setFailure), {
    position: props.position,
  });

  return (
    <AnimatePresence>
      {failure && (
        <GeolocateMessage key={failure} failure={failure} onDismiss={dismiss} />
      )}
    </AnimatePresence>
  );
}

export default GeolocateControl;
