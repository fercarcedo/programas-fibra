import MaplibreGeocoder, {
  type CarmenGeojsonFeature,
  type MaplibreGeocoderApi,
  type MaplibreGeocoderFeatureResults,
} from "@maplibre/maplibre-gl-geocoder";
import "@maplibre/maplibre-gl-geocoder/dist/maplibre-gl-geocoder.css";
import { useControl, type ControlPosition } from "react-map-gl/maplibre";
import maplibregl from "maplibre-gl";
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

function SearchControl(props: SearchControlProps) {
  useControl(
    () => {
      const geocoderApi: MaplibreGeocoderApi = {
        forwardGeocode: async (config) => {
          if (!config.query) {
            return featuresFromSearchResults([]);
          }

          try {
            const results = await search(config.query.toString());
            return featuresFromSearchResults(results);
          } catch (e) {
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

  return null;
}

export default SearchControl;
