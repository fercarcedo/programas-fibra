import { NominatimSearchResponse } from "../../src/api/nominatim/types";

export const MOCK_NOMINATIM_RESPONSE_SUCCESS: NominatimSearchResponse[] = [
  {
    type: "FeatureCollection",
    licence:
      "Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright",
    place_id: "35811445",
    osm_type: "node",
    osm_id: 2846295644,
    lat: "35.275",
    lon: "35.275",
    class: "place",
    place_rank: 30,
    importance: 0.62025,
    addresstype: "place",
    name: "Strada Pictor Alexandru Romano",
    display_name:
      "17, Strada Pictor Alexandru Romano, Bukarest, Bucharest, Sector 2, Bucharest, 023964, Romania",
    boundingbox: ["26.1156689", "44.4354754", "26.1157689", "44.4355754"],
  },
];
