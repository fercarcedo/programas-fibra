import { useCallback, useEffect } from "react";
import "./App.css";
import Map, {
  GeolocateControl,
  NavigationControl,
} from "react-map-gl/maplibre";
import type { MapEvent } from "react-map-gl/maplibre";
import maplibregl, { type Map as MapLibreMap } from 'maplibre-gl';
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { layers, namedFlavor } from "@protomaps/basemaps";
import SearchControl from "./components/SearchControl";

function App() {
  useEffect(() => {
    let protocol = new Protocol();
    maplibregl.addProtocol("pmtiles", protocol.tile);
    return () => {
      maplibregl.removeProtocol("pmtiles");
    };
  }, []);

  const handleMapLoad = useCallback((event: MapEvent) => {
    const map = event.target as MapLibreMap;

    map.touchZoomRotate.disableRotation();
    map.keyboard.disableRotation();
    map.dragRotate.disable();

    const currentPitch = map.getPitch();
    map.setMaxPitch(currentPitch);
    map.setMinPitch(currentPitch);
  }, []);

  return (
    <div className="app">
      <Map
        style={{ width: "100%", height: "100%" }}
        mapStyle={{
          version: 8,
          glyphs:
            "https://protomaps.github.io/basemaps-assets/fonts/{fontstack}/{range}.pbf",
          sprite:
            "https://protomaps.github.io/basemaps-assets/sprites/v4/grayscale",
          sources: {
            protomaps: {
              type: "vector",
              tiles: [
                "https://programas-fibra-tile-server.fercarcedo.workers.dev/map-3a858e9500/{z}/{x}/{y}.mvt",
              ],
              maxzoom: 15
            },
            fiber: {
              type: "vector",
              tiles: [
                "https://programas-fibra-tile-server.fercarcedo.workers.dev/output-9f4202d6a0/{z}/{x}/{y}.mvt"
              ],
              maxzoom: 15
            }
          },
          layers: [
            ...layers("protomaps", namedFlavor("grayscale"), { lang: "es" }),
            {
              id: "fiber-layer",
              type: "fill",
              source: "fiber",
              "source-layer": "output",
              paint: {
                  "fill-color": [
                    "match",
                    ["get", "grantee"],
                    "TELEFONICA DE ESPAÑA, S.A.", "#019DF4",
                    "ORANGE ESPAÑA COMUNICACIONES FIJAS S.L.U.", "#FF5E0E",
                    "AVATEL TELECOM S.A.", "#A05EB5",
                    "ADAMO TELECOM IBERIA SA", "#2BC36E",
                    "ASTEO RED NEUTRA SL", "#2472B7",
                    "VENTO REDE, S.L.", "#3B9C3F",
                    "#ff0000"
                  ],
                  "fill-opacity": .5
              }
            },
            {
              id: "outline-layer",
              type: "line",
              source: "fiber",
              "source-layer": "output",
              "paint": {
                "line-color": "#FE0000",
                "line-width": 0.5,
              },
              minzoom: 10
            }
          ]
        }}
        attributionControl={false}
        renderWorldCopies={false}
        initialViewState={{
          latitude: 40.413401,
          longitude: -3.692422,
          zoom: 6.5,
        }}
        maxBounds={[-19.116211,26.824071,7.954102,44.527843]}
        maxZoom={18}
        dragRotate={false}
        touchPitch={false}
        pitchWithRotate={false}
        onLoad={handleMapLoad}
      >
        <SearchControl
          position="top-left"
          showResultsWhileTyping={true}
          collapsed={true}
          language="es"
          placeholder="Buscar"
        />
        <NavigationControl position="top-left" showCompass={false} />
        <GeolocateControl position="top-left" showUserLocation={false} />
      </Map>
    </div>
  );
}

export default App;
