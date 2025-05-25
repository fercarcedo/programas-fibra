import { NominatimFeature, NominatimSearchResponse } from "../../src/api/nominatim/types";
import { type Point } from "geojson";

// Mock response from osm website
export const MOCK_NOMINATIM_RESPONSE_SUCCESS: NominatimSearchResponse = {
  type: "FeatureCollection",
  licence:
    "Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright",
  features: [
    {
      type: "Feature",
      properties: {
        place_id: "35811445",
        osm_type: "node",
        osm_id: "2846295644",
        display_name:
          "17, Strada Pictor Alexandru Romano, Bukarest, Bucharest, Sector 2, Bucharest, 023964, Romania",
        place_rank: "30",
        category: "place",
        type: "house",
        importance: 0.62025,
      },
      bbox: [26.1156689, 44.4354754, 26.1157689, 44.4355754],
      geometry: {
        type: "Point",
        coordinates: [26.1157189, 44.4355254],
      } as Point,
    } as NominatimFeature,
  ],
};