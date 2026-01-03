import { useCallback, useEffect, useState } from "react";
import "./App.css";
import Map, {
  GeolocateControl,
  NavigationControl,
  useControl,
} from "react-map-gl/maplibre";
import type { MapEvent } from "react-map-gl/maplibre";
import { type Map as MapLibreMap } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { layers, namedFlavor } from "@protomaps/basemaps";
import SearchControl from "./components/SearchControl";
import { type MapViewState, type PickingInfo } from "@deck.gl/core";

import { H3HexagonLayer, MVTLayer } from "@deck.gl/geo-layers";
import { MapboxOverlay } from "@deck.gl/mapbox";
import type { MapboxOverlayProps } from "@deck.gl/mapbox";
import type { Feature, Geometry } from "geojson";
import type { AreaProperties } from "./api/areas/types";
import AreaPopup from "./components/AreaPopup";
import centroid from "@turf/centroid";

const INITIAL_VIEW_STATE: MapViewState = {
  latitude: 40.413401,
  longitude: -3.692422,
  zoom: 6.5,
  maxZoom: 18,
};

interface PopupInfo {
  longitude: number;
  latitude: number;
  centroidLongitude: number;
  centroidLatitude: number;
  data: AreaProperties;
}

function DeckGLOverlay(props: MapboxOverlayProps) {
  const overlay = useControl<MapboxOverlay>(() => new MapboxOverlay(props));
  overlay.setProps(props);
  return null;
}

function App() {
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
      const polygonCentroid = centroid(info.object);
      const [lon, lat] = polygonCentroid.geometry.coordinates;

      setPopupInfo({
        longitude: info.coordinate[0],
        latitude: info.coordinate[1],
        centroidLongitude: lon,
        centroidLatitude: lat,
        data: info.object.properties,
      });
    } else {
      setPopupInfo(null);
    }
  };

  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [popupInfo, setPopupInfo] = useState<PopupInfo | null>(null);
  const [fontLoaded, setFontLoaded] = useState(false);

  useEffect(() => {
    document.fonts.load("24px 'Material Icons'").then(() => {
      setFontLoaded(true);
    });
  }, []);

  const MARKER_ICON_SIZE_METERS = 100;
  const MARKER_SIZE_MIN_PIXELS = 20;
  const MARKER_SIZE_MAX_PIXELS = 200;

  const mapLayers =
    viewState.zoom < 9
      ? [
          new H3HexagonLayer({
            id: "hexagon-layer",
            data: "/data/aggregated-0413b8769b.json",
            extruded: false,
            beforeId: "places_locality",
            getHexagon: (d) => d.h3Index,
            getElevation: 0,
            getFillColor: (d) => {
              const ratio = Math.sqrt(d.totalCount / 500);
              const clampedRatio = Math.min(ratio, 1);

              return [255, (1 - clampedRatio) * 255, 0, 180];
            },
            parameters: {
              blendFunc: [0, 768],
              blendEquation: 32774,
            },
          }),
        ]
      : [
          new MVTLayer({
            id: "fiber-layer",
            sourceLayer: "output",
            data: ["/tiles/output-2fc8a9b91c/{z}/{x}/{y}"],
            minZoom: 0,
            maxZoom: 18,
            filled: true,
            stroked: true,
            pickable: true,
            autoHighlight: true,
            getFillColor: (feature: any) => {
              if (feature.properties.type == "town") {
                return [0, 0, 0, 0];
              }
              const grantee: string = feature.properties.grantee;
              const fillAlpha = 128;
              switch (grantee) {
                case "TELEFONICA DE ESPAÑA, S.A.":
                case "TELEFÓNICA DE ESPAÑA S.A.":
                  return [1, 157, 244, fillAlpha];
                case "ORANGE ESPAÑA COMUNICACIONES FIJAS S.L.U.":
                case "ORANGE ESPAGNE S.A.":
                  return [255, 94, 14, fillAlpha];
                case "AVATEL TELECOM S.A.":
                case "AVATEL & WIKIKER TELECOM S.L.":
                case "WIKIKER BROADBAND, S.L.":
                case "TELEAST DIGITAL, S.L.":
                case "TVHORADADA MULTIMEDIA, S.L.":
                case "TVHORADADA MAR MENOR, S.L.":
                case "CIUDAD SIN CABLES TELECOM SL":
                case "TELPLAY S.L.":
                case "CABLEUNIÓN MEDIA, S.L.":
                case "CABLEMURCIA S.L":
                case "A2Z TELECOMUNICACIONES, S.L.":
                case "LEBRIJA TV, S.L.":
                case "FIBRAMED NETWORKS, S.L.":
                case "WIFIBYTES, S.L.":
                case "WIVA TELECOM, S.L.":
                case "UNION DE REDES DE FIBRA OPTICA, SL":
                case "TELE ALHAMA, S.L.":
                case "TELEDISTRIBUCIÓN TOTANA S.L.":
                case "CABLE ALBUDEITE S.L.":
                case "REDFIBRA COMUNICACIONES SL":
                case "ALBACETE SISTEMAS Y SERVICIOS S.L.":
                case "WIFINITY GLOBAL NETWORK, S.L.":
                case "OPEGAL TELECOMUNICACIONS S.L.":
                case "SERVICIO TELEC. PUENTE GENIL":
                case "RUSCABLE S.L.":// La Cala fibra sl ?
                case "WIFI LA VALL SL":
                case "VOZPLUS TELECOMUNICACIONES, S.L.L.":
                case "INGERTV":
                  return [160, 94, 181, fillAlpha];
                case "ADAMO TELECOM IBERIA SA":
                  return [43, 195, 110, fillAlpha];
                case "ASTEO RED NEUTRA SL":
                  return [36, 114, 183, fillAlpha];
                case "VENTO REDE, S.L.":
                  return [59, 156, 63, fillAlpha];
                case "MASMOVIL BROADBAND S.A.UNIPERSONAL":
                case "MASMOVIL BROADBAND SA":
                case "EMBOU NUEVAS TECNOLOGIAS SL.":
                case "MAS MOVIL TELECOM 3.0 S.A.":
                case "XTRA TELECOM, S.A.U":
                case "MASMOVIL IBERCOM SA":
                  return [255, 222, 33, fillAlpha];
                case "TELECABLE DE ASTURIAS, S.A":
                case "R CABLE Y TELECOMUNICACIONES GALICIA, S.A.":
                case "EUSKALTEL":
                case "EUSKALTEL, S.A.":
                  return [0, 85, 120, fillAlpha];
                case "VODAFONE ESPAÑA S.A.":
                  return [230, 0, 0, fillAlpha];
                case "LYNTIA NETWORKS, S.A.":
                  return [230, 0, 126, fillAlpha];
              }
              return [112, 128, 144, fillAlpha];
            },
            getLineColor: [254, 0, 0, 255],
            lineWidthMinPixels: 0.5,
            onClick: handleLayerClick,
            pointType: "circle+text",
            getPointRadius: MARKER_ICON_SIZE_METERS / 2,
            getTextSize: MARKER_ICON_SIZE_METERS,
            radiusUnits: "meters",
            pointRadiusMinPixels: MARKER_SIZE_MIN_PIXELS / 2,
            pointRadiusMaxPixels: MARKER_SIZE_MAX_PIXELS / 2,
            getText: () => "\ue0c8",
            textFontFamily: "Material Icons",
            textCharacterSet: ["\ue0c8"],
            textSizeUnits: "meters",
            textSizeMinPixels: MARKER_SIZE_MIN_PIXELS,
            textSizeMaxPixels: MARKER_SIZE_MAX_PIXELS,
            getTextColor: (feature: any) => {
              const grantee: string = feature.properties.grantee;
              const fillAlpha = 128;
              switch (grantee) {
                case "TELEFONICA DE ESPAÑA, S.A.":
                case "TELEFÓNICA DE ESPAÑA S.A.":
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
            getTextAnchor: "middle",
            getTextAlignmentBaseline: "center",
            updateTriggers: {
              getText: fontLoaded,
            },
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
            centroidLatitude={popupInfo.centroidLatitude}
            centroidLongitude={popupInfo.centroidLongitude}
            data={popupInfo.data}
            onClose={() => setPopupInfo(null)}
          />
        )}
      </Map>
    </div>
  );
}

export default App;
