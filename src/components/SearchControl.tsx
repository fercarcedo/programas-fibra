import MaplibreGeocoder, {
  type CarmenGeojsonFeature,
  type MaplibreGeocoderApi,
  type MaplibreGeocoderFeatureResults,
} from "@maplibre/maplibre-gl-geocoder";
import "@maplibre/maplibre-gl-geocoder/dist/maplibre-gl-geocoder.css";
import { useControl, useMap, type ControlPosition } from "react-map-gl/maplibre";
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

/**
 * Takes care of dismissing the search bar. On narrow screens closing the bar
 * and clearing its contents are two separate actions: the back arrow this adds
 * on the left dismisses the bar and keeps the query, while the geocoder's own X
 * on the right only empties the field. CSS decides when the arrow is visible.
 *
 * Picking a result also dismisses the bar, since the map has already travelled
 * to the place being searched for and the query is spent.
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

    // Blurring alone does not close the bar: the geocoder only collapses itself
    // while the field is empty, and it puts the focus back on the input after a
    // result is picked. Collapse it here instead.
    const dismiss = () => {
      input.blur();
      geocoderEl.classList.add("maplibregl-ctrl-geocoder--collapsed");
    };

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
      dismiss();
    };

    // Picking a result leaves a query that has already been travelled to, so
    // the bar is emptied as well as closed.
    const onResult = () => {
      geocoder?.clear();
      dismiss();
    };

    backButton.addEventListener("click", onBackButtonClick);
    geocoderEl.prepend(backButton);
    geocoder?.on("result", onResult);

    return () => {
      backButton.removeEventListener("click", onBackButtonClick);
      backButton.remove();
      geocoder?.off("result", onResult);
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
