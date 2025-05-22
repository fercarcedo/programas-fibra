import MaplibreGeocoder, {
  type CarmenGeojsonFeature,
  type MaplibreGeocoderApi,
  type MaplibreGeocoderFeatureResults,
} from "@maplibre/maplibre-gl-geocoder";
import "@maplibre/maplibre-gl-geocoder/dist/maplibre-gl-geocoder.css";
import { useControl, type ControlPosition } from "react-map-gl/maplibre";
import maplibregl from "maplibre-gl";

export type SearchControlProps = {
  showResultsWhileTyping?: boolean;
  collapsed?: boolean;
  language?: string;
  placeholder?: string;
  position: ControlPosition;
};

const featuresFromGeojson = (
  geojson: any | null,
): MaplibreGeocoderFeatureResults => {
  const features: CarmenGeojsonFeature[] =
    geojson?.features.map((feature: any) => {
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
            const url = new URL("https://nominatim.openstreetmap.org/search");
            url.searchParams.set("q", config.query.toString());
            url.searchParams.set("format", "geojson");
            url.searchParams.set("polygon_geojson", "1");
            url.searchParams.set("addressdetails", "1");
            url.searchParams.set("countrycodes", "es");
            url.searchParams.set("accept-language", "es");

            const response = await fetch(url.toString());
            const geojson = await response.json();

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
