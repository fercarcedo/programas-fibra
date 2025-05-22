import { type Geometry } from "geojson";

export interface NominatimSearchResponse {
  type: string;
  licence: string;
  features: NominatimFeature[];
}

export interface NominatimFeature {
  type: string;
  properties: NominatimFeatureProperties;
  bbox: number[];
  geometry: Geometry;
}

export interface NominatimFeatureProperties {
  place_id: string;
  osm_type: string;
  osm_id: string;
  display_name: string;
  place_rank: string;
  category: string;
  type: string;
  importance: number;
  addresstype?: string;
  name?: string;
}
