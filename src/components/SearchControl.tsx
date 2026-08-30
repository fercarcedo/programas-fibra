import MaplibreGeocoder, {
  type CarmenGeojsonFeature,
  type MaplibreGeocoderApi,
  type MaplibreGeocoderFeatureResults,
} from "@maplibre/maplibre-gl-geocoder";
import "@maplibre/maplibre-gl-geocoder/dist/maplibre-gl-geocoder.css";
import {
  useControl,
  useMap,
  type ControlPosition,
} from "react-map-gl/maplibre";
import maplibregl from "maplibre-gl";
import { useEffect } from "react";
import search from "../api/nominatim";
import type { NominatimSearchResponse } from "../api/nominatim/types";

export type SearchControlProps = {
  showResultsWhileTyping?: boolean;
  collapsed?: boolean;
  language?: string;
  placeholder?: string;
  position: ControlPosition;
};

const featuresFromSearchResults = (
  results: NominatimSearchResponse[],
): MaplibreGeocoderFeatureResults => {
  const features: CarmenGeojsonFeature[] =
    results.map((result: NominatimSearchResponse) => {
      return {
        id: result.osm_id.toString(),
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: [parseFloat(result.lon), parseFloat(result.lat)],
        },
        place_name: result.display_name,
        properties: {
          place_id: result.place_id,
          osm_type: result.osm_type,
          osm_id: result.osm_id,
          place_rank: result.place_rank,
          type: result.type,
          importance: result.importance,
          addresstype: result.addresstype,
          name: result.name,
          display_name: result.display_name,
        },
        text: result.display_name,
        place_type: ["place"],
      };
    }) ?? [];
  return { type: "FeatureCollection", features };
};

const BACK_ARROW_ICON =
  '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
  'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<path d="M19 12H5"/><path d="m12 19-7-7 7-7"/></svg>';

const EDITING_CLASS = "pf-search-editing";
const COLLAPSED_CLASS = "maplibregl-ctrl-geocoder--collapsed";
const SEARCH_HISTORY_STATE = "pfSearchOpen";
const NARROW_SCREEN = "(max-width: 640px)";

/**
 * Drives the three states the search bar moves through on narrow screens, which
 * CSS then styles: collapsed to its icon, being typed into, and showing a
 * result that has been picked.
 *
 * While a query is being typed the bar needs the whole row, and the back arrow
 * this adds on the left abandons it, keeping the text for the next time the bar
 * is opened. Picking a result instead commits it: the map has travelled there
 * and the query stays on as a label of where that is, so the bar only drops the
 * keyboard and the cursor. Emptying the field is left to the geocoder's own X,
 * which puts the bar away with the result it drops.
 *
 * While the bar is open it holds a history entry, so that a phone's back
 * gesture closes it rather than leaving the page.
 */
const useDismissableSearchBar = (geocoder: MaplibreGeocoder | undefined) => {
  const { current: map } = useMap();

  useEffect(() => {
    if (!map) return;

    const geocoderEl = map
      .getContainer()
      .querySelector<HTMLElement>(".maplibregl-ctrl-geocoder");
    const input = geocoderEl?.querySelector<HTMLInputElement>(
      ".maplibregl-ctrl-geocoder--input",
    );
    if (!geocoderEl || !input) return;

    const isOpen = () => !geocoderEl.classList.contains(COLLAPSED_CLASS);
    const isEditing = () => geocoderEl.classList.contains(EDITING_CLASS);
    // Blurring alone would not put the bar away: the geocoder only collapses
    // itself while the field is empty.
    const close = () => {
      input.blur();
      geocoderEl.classList.add(COLLAPSED_CLASS);
    };

    const onFocus = () => geocoderEl.classList.add(EDITING_CLASS);
    const onBlur = () => geocoderEl.classList.remove(EDITING_CLASS);

    const backButton = document.createElement("button");
    backButton.type = "button";
    backButton.className = "pf-geocoder-back";
    backButton.setAttribute("aria-label", "Cerrar búsqueda");
    backButton.innerHTML = BACK_ARROW_ICON;

    const onBackButtonClick = (event: MouseEvent) => {
      event.preventDefault();
      // The geocoder listens for clicks on its own container to reopen the
      // suggestion list. That listener sits on an ancestor, so the event has to
      // be stopped here at the target to keep the list from popping back up.
      event.stopPropagation();
      // Going back is not clearing, so the query is left in place for the next
      // time the bar is opened.
      close();
    };

    // The geocoder puts the focus back on the input as it announces a result,
    // which is what was leaving the keyboard up over the map the bar had just
    // travelled to. The query itself stays, now labelling that result.
    const onResult = () => input.blur();

    // Pressing either of the buttons inside the bar would otherwise take the
    // focus off the field, which ends the editing state, which resizes the bar
    // and hides the back arrow, all before the press has turned into a click:
    // the arrow moves out from under the finger that is tapping it. Holding on
    // to the focus keeps the bar still until the click has been dealt with.
    const keepFocus = (event: MouseEvent) => event.preventDefault();
    const clearButton = geocoderEl.querySelector<HTMLElement>(
      ".maplibregl-ctrl-geocoder--button",
    );

    // Whether the X is dropping a result that is on screen has to be noted
    // before the geocoder handles the click, because clearing refocuses the
    // field and so leaves the bar looking as though it were being typed into.
    let clearingResult = false;
    const onClearMouseDown = (event: MouseEvent) => {
      keepFocus(event);
      clearingResult = !isEditing();
    };

    // Dropping a result was never a request to search again, so the bar is put
    // away rather than reopened on the refocus the geocoder does while clearing.
    const onClearClick = () => {
      if (clearingResult) close();
      clearingResult = false;
    };

    // An open search bar is the sort of thing a phone's back gesture is expected
    // to close, so it takes a history entry of its own while it is open, and
    // gives it back on the way out however it was closed.
    const narrowScreen = window.matchMedia(NARROW_SCREEN);
    let pushedHistoryEntry = false;

    const syncHistoryEntry = () => {
      if (isOpen()) {
        if (pushedHistoryEntry || !narrowScreen.matches) return;
        window.history.pushState({ [SEARCH_HISTORY_STATE]: true }, "");
        pushedHistoryEntry = true;
        return;
      }
      if (!pushedHistoryEntry) return;
      pushedHistoryEntry = false;
      // Only the bar's own entry is ever dropped: anything else on top of it
      // means going back would take the page with it.
      if (window.history.state?.[SEARCH_HISTORY_STATE]) window.history.back();
    };

    const onPopState = () => {
      if (!pushedHistoryEntry) return;
      pushedHistoryEntry = false;
      close();
    };

    const openState = new MutationObserver(syncHistoryEntry);

    backButton.addEventListener("click", onBackButtonClick);
    backButton.addEventListener("mousedown", keepFocus);
    clearButton?.addEventListener("mousedown", onClearMouseDown);
    clearButton?.addEventListener("click", onClearClick);
    geocoderEl.prepend(backButton);
    input.addEventListener("focus", onFocus);
    input.addEventListener("blur", onBlur);
    geocoder?.on("result", onResult);
    openState.observe(geocoderEl, {
      attributes: true,
      attributeFilter: ["class"],
    });
    window.addEventListener("popstate", onPopState);

    return () => {
      backButton.removeEventListener("click", onBackButtonClick);
      backButton.removeEventListener("mousedown", keepFocus);
      clearButton?.removeEventListener("mousedown", onClearMouseDown);
      clearButton?.removeEventListener("click", onClearClick);
      backButton.remove();
      input.removeEventListener("focus", onFocus);
      input.removeEventListener("blur", onBlur);
      geocoder?.off("result", onResult);
      openState.disconnect();
      window.removeEventListener("popstate", onPopState);
    };
  }, [map, geocoder]);
};

function SearchControl(props: SearchControlProps) {
  const geocoder = useControl<MaplibreGeocoder>(
    () => {
      const geocoderApi: MaplibreGeocoderApi = {
        forwardGeocode: async (config) => {
          if (!config.query) {
            return featuresFromSearchResults([]);
          }

          try {
            const results = await search(config.query.toString());
            return featuresFromSearchResults(results);
          } catch {
            console.log("Error while searching");
            return featuresFromSearchResults([]);
          }
        },
      };
      return new MaplibreGeocoder(geocoderApi, {
        maplibregl,
        showResultsWhileTyping: props.showResultsWhileTyping,
        collapsed: props.collapsed,
        language: props.language,
        placeholder: props.placeholder,
      });
    },
    { position: props.position },
  );

  useDismissableSearchBar(geocoder);

  return null;
}

export default SearchControl;
