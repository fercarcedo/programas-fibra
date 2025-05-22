import MaplibreGeocoder, {
  type CarmenGeojsonFeature,
  type MaplibreGeocoderApi,
  type MaplibreGeocoderFeatureResults,
} from "@maplibre/maplibre-gl-geocoder";
import "@maplibre/maplibre-gl-geocoder/dist/maplibre-gl-geocoder.css";
import { useControl, type ControlPosition } from "react-map-gl/maplibre";
import maplibregl from "maplibre-gl";
import search from "../api/nominatim";
import type {
  NominatimFeature,
  NominatimSearchResponse,
} from "../api/nominatim/types";

export type SearchControlProps = {
  showResultsWhileTyping?: boolean;
  collapsed?: boolean;
  language?: string;
  placeholder?: string;
  position: ControlPosition;
};

const featuresFromGeojson = (
  geojson: NominatimSearchResponse | null,
): MaplibreGeocoderFeatureResults => {
  const features: CarmenGeojsonFeature[] =
    geojson?.features.map((feature: NominatimFeature) => {
      const center = [
        feature.bbox[0] + (feature.bbox[2] - feature.bbox[0]) / 2,
        feature.bbox[1] + (feature.bbox[3] - feature.bbox[1]) / 2,
      ];
      return {
        id: feature.properties.osm_id,
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: center,
        },
        place_name: feature.properties.display_name,
        properties: feature.properties,
        text: feature.properties.display_name,
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
            return featuresFromGeojson(null);
          }

          try {
            const geojson = await search(config.query.toString());
            return featuresFromGeojson(geojson);
          } catch (e) {
            console.log("Error while searching");
          }

          return featuresFromGeojson(null);
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
