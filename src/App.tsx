import { useCallback, useEffect, useState } from "react";
import "./App.css";
import Map, {
  GeolocateControl,
  NavigationControl,
  Popup,
  useControl,
} from "react-map-gl/maplibre";
import type { MapEvent } from "react-map-gl/maplibre";
import maplibregl, { type Map as MapLibreMap } from 'maplibre-gl';
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { layers, namedFlavor } from "@protomaps/basemaps";
import SearchControl from "./components/SearchControl";
import type { MapViewState, PickingInfo } from "@deck.gl/core";

import { MVTLayer } from '@deck.gl/geo-layers';
import { MapboxOverlay } from '@deck.gl/mapbox';
import type { MapboxOverlayProps } from '@deck.gl/mapbox';
import type { Feature, Geometry } from 'geojson';

const INITIAL_VIEW_STATE: MapViewState = {
  latitude: 40.413401,
  longitude: -3.692422,
  zoom: 6.5,
  maxZoom: 18,
};

interface PopupInfo {
  longitude: number;
  latitude: number;
  data: any;
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
      })
    } else {
      setPopupInfo(null);
    }
  }

  const mapLayers = [
    new MVTLayer({
      id: 'fiber-layer',
      sourceLayer: 'output',
      data: [
        'https://programas-fibra-tile-server.fercarcedo.workers.dev/output-9f4202d6a0/{z}/{x}/{y}.mvt'
      ],
      minZoom: 0,
      maxZoom: 15,
      filled: true,
      stroked: true,
      pickable: true,
      autoHighlight: true,
      getFillColor: feature => {
        const grantee: string = feature.properties.grantee;
        const fillAlpha = 128;
        switch (grantee) {
          case 'TELEFONICA DE ESPAÑA, S.A.': 
            return [1, 157, 244, fillAlpha];
          case 'ORANGE ESPAÑA COMUNICACIONES FIJAS S.L.U.': 
            return [255, 94, 14, fillAlpha];
          case 'AVATEL TELECOM S.A.': 
            return [160, 94, 181, fillAlpha];
          case 'ADAMO TELECOM IBERIA SA': 
            return [43, 195, 110, fillAlpha];
          case 'ASTEO RED NEUTRA SL': 
            return [36, 114, 183, fillAlpha];
          case 'VENTO REDE, S.L.': 
            return [59, 156, 63, fillAlpha];
        }
        return [255, 0, 0, fillAlpha];
      },
      getLineColor: [254, 0, 0, 255],
      lineWidthMinPixels: 0.5,
      onClick: handleLayerClick,
    }),
  ];

  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [popupInfo, setPopupInfo] = useState<PopupInfo | null>(null);

  return (
    <div className="app">
      <Map
          {...viewState}
          onMove={e => setViewState(e.viewState)}
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
            },
            layers: [
              ...layers("protomaps", namedFlavor("grayscale"), { lang: "es" }),
            ]
          }}
          attributionControl={false}
          renderWorldCopies={false}
          maxBounds={[-19.116211,26.824071,7.954102,44.527843]}
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

          {mapLoaded && <DeckGLOverlay layers={[mapLayers]} />}

          {popupInfo && (
            <Popup 
              longitude={popupInfo.longitude} 
              latitude={popupInfo.latitude} 
              onClose={() => setPopupInfo(null)}
              style={{ zIndex: 9999 }}
            >
              <div>
                <p>Test tooltip</p>
              </div>
            </Popup>
          )}
        </Map>
      </div>
  );
}

export default App;
