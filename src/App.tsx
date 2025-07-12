import { useEffect } from "react";
import "./App.css";
import Map, {
  GeolocateControl,
  NavigationControl,
} from "react-map-gl/maplibre";
import maplibregl from "maplibre-gl";
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

  return (
    <div className="app">
      <Map
        style={{ width: "100%", height: "100%" }}
        mapStyle={{
          version: 8,
          glyphs:
            "https://protomaps.github.io/basemaps-assets/fonts/{fontstack}/{range}.pbf",
          sprite:
            "https://protomaps.github.io/basemaps-assets/sprites/v4/light",
          sources: {
            protomaps: {
              type: "vector",
              tiles: [
                "https://programas-fibra-tile-server.fercarcedo.workers.dev/map/{z}/{x}/{y}.mvt",
              ],
              maxzoom: 15
            },
            fiber: {
              type: "vector",
              tiles: [
                "https://programas-fibra-tile-server.fercarcedo.workers.dev/output/{z}/{x}/{y}.mvt"
              ],
              maxzoom: 15
            }
          },
          layers: [
            ...layers("protomaps", namedFlavor("light"), { lang: "es" }),
            {
              id: "fiber-layer",
              type: "fill",
              source: "fiber",
              "source-layer": "output",
              paint: {
                  "fill-color": "#ff0000",
                  "fill-opacity": .5
              }
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
