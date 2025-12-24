import { useCallback, useEffect, useState } from "react";
import "./App.css";
import Map, {
  GeolocateControl,
  NavigationControl,
  useControl,
} from "react-map-gl/maplibre";
import type { MapEvent } from "react-map-gl/maplibre";
import maplibregl, { type Map as MapLibreMap } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { layers, namedFlavor } from "@protomaps/basemaps";
import SearchControl from "./components/SearchControl";
import type { MapViewState, PickingInfo } from "@deck.gl/core";

import { H3HexagonLayer, MVTLayer } from "@deck.gl/geo-layers";
import { MapboxOverlay } from "@deck.gl/mapbox";
import type { MapboxOverlayProps } from "@deck.gl/mapbox";
import type { Feature, Geometry } from "geojson";
import type { AreaProperties } from "./api/areas/types";
import AreaPopup from "./components/AreaPopup";

const INITIAL_VIEW_STATE: MapViewState = {
  latitude: 40.413401,
  longitude: -3.692422,
  zoom: 6.5,
  maxZoom: 18,
};

interface PopupInfo {
  longitude: number;
  latitude: number;
  data: AreaProperties;
}

function DeckGLOverlay(props: MapboxOverlayProps) {
  const overlay = useControl<MapboxOverlay>(() => new MapboxOverlay(props));
  overlay.setProps(props);
  return null;
}

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

    setMapLoaded(true);
  }, []);

  const handleLayerClick = (info: PickingInfo<Feature<Geometry, any>>) => {
    if (info.object && info.coordinate) {
      setPopupInfo({
        longitude: info.coordinate[0],
        latitude: info.coordinate[1],
        data: info.object.properties,
      });
    } else {
      setPopupInfo(null);
    }
  };

  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [popupInfo, setPopupInfo] = useState<PopupInfo | null>(null);

  const mapLayers =
    viewState.zoom < 9
      ? [
          new H3HexagonLayer({
            id: "hexagon-layer",
            data: "/data/aggregated-ae9af1d73c.json",
            extruded: false,
            getHexagon: (d) => d.h3Index,
            getElevation: 0,
            getFillColor: (d) => [255, (1 - d.totalCount / 500) * 255, 0],
          }),
        ]
      : [
          new MVTLayer({
            id: "fiber-layer",
            sourceLayer: "output",
            data: ["/tiles/output-10dcd48293/{z}/{x}/{y}"],
            minZoom: 0,
            maxZoom: 15,
            filled: true,
            stroked: true,
            pickable: true,
            autoHighlight: true,
            getFillColor: (feature) => {
              const grantee: string = feature.properties.grantee;
              const fillAlpha = 128;
              switch (grantee) {
                case "TELEFONICA DE ESPAÑA, S.A.":
                  return [1, 157, 244, fillAlpha];
                case "ORANGE ESPAÑA COMUNICACIONES FIJAS S.L.U.":
                  return [255, 94, 14, fillAlpha];
                case "AVATEL TELECOM S.A.":
                  return [160, 94, 181, fillAlpha];
                case "ADAMO TELECOM IBERIA SA":
                  return [43, 195, 110, fillAlpha];
                case "ASTEO RED NEUTRA SL":
                  return [36, 114, 183, fillAlpha];
                case "VENTO REDE, S.L.":
                  return [59, 156, 63, fillAlpha];
              }
              return [255, 0, 0, fillAlpha];
            },
            getLineColor: [254, 0, 0, 255],
            lineWidthMinPixels: 0.5,
            onClick: handleLayerClick,
          }),
        ];

  return (
    <div className="app">
      <Map
        {...viewState}
        onMove={(e) => setViewState(e.viewState)}
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
                `${window.location.origin}/tiles/map-3a858e9500/{z}/{x}/{y}`,
              ],
              maxzoom: 15,
            },
          },
          layers: [
            ...layers("protomaps", namedFlavor("grayscale"), { lang: "es" }),
          ],
        }}
        attributionControl={false}
        renderWorldCopies={false}
        maxBounds={[-19.116211, 26.824071, 7.954102, 44.527843]}
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

        {mapLoaded && <DeckGLOverlay layers={[mapLayers]} interleaved={true} />}

        {popupInfo && (
          <AreaPopup
            latitude={popupInfo.latitude}
            longitude={popupInfo.longitude}
            data={popupInfo.data}
            onClose={() => setPopupInfo(null)}
          />
        )}
      </Map>
    </div>
  );
}

export default App;
