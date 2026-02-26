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
import { DataFilterExtension } from '@deck.gl/extensions';
import type { Feature, Geometry } from "geojson";
import type { AreaProperties } from "./api/areas/types";
import AreaPopup from "./components/AreaPopup";
import centroid from "@turf/centroid";
import { getOperatorColor, getProgramColor, getOperatorNames } from "./map/colors";
import LegendControl from "./components/LegendControl";
import { AnimatePresence } from 'motion/react';
import LegendPanel from "./components/LegendPanel";
import { useProjectsStatus } from "./api/projects";
import type { ProjectStatus } from "./api/projects/types";

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
  const [isLegendOpen, setLegendOpen] = useState(false);
  const [selectedOperators, setSelectedOperators] = useState<Set<string>>(new Set());
  const [selectedPrograms, setSelectedPrograms] = useState<Set<string>>(new Set());
  const [selectedStatus, setSelectedStatus] = useState<string | null>(null);
  const selectedOperatorsNames = new Set(
    Array.from(selectedOperators).map(op => getOperatorNames(op)).flat()
  );
  const { data: statusSummary } = useProjectsStatus();

  useEffect(() => {
    document.fonts.load("24px 'Material Icons'").then(() => {
      setFontLoaded(true);
    });
  }, []);

  const MARKER_ICON_SIZE_METERS = 100;
  const MARKER_SIZE_MIN_PIXELS = 20;
  const MARKER_SIZE_MAX_PIXELS = 200;

  const getH3Value = (d: any, selectedOperators: Set<string>, selectedPrograms: Set<string>, selectedStatus: string | null) => {
    const allOpsSize = 11; // Hardcoded or passed from props
    const allProgsSize = 13;

    // --- FAST PATH ---------------------------------------
    // Check if we are showing EVERYTHING (either via empty set or full set)
    const isAllOperators = selectedOperators.size === 0 || selectedOperators.size === allOpsSize;
    const isAllPrograms = selectedPrograms.size === 0 || selectedPrograms.size === allProgsSize;
    const isAllStatus = !selectedStatus;

    if (isAllOperators && isAllPrograms && isAllStatus) {
      return d.totalCount;
    }

    // --- SLOW PATH (Filtering active) --------------------
    let sum = 0;

    // Iterate over the grantees (keys of 'counts')
    for (const opName in d.counts) {
      // 1. Check Operator Filter
      const opVisible = selectedOperators.size === 0 || selectedOperatorsNames.has(opName);

      if (opVisible) {
        const programs = d.counts[opName];

        // 2. Iterate over Programs
        for (const progName in programs) {
          // Check Program Filter
          const progVisible = selectedPrograms.size === 0 || selectedPrograms.has(progName.toUpperCase().replace(" ", "_"));

          if (progVisible) {
            const programData = programs[progName];

            // 3. Filter by status if selected
            if (selectedStatus) {
              const statusCount = programData.statuses?.[selectedStatus] || 0;
              sum += statusCount;
            } else {
              sum += programData.total;
            }
          }
        }
      }
    }

    return sum;
  }

  const mapLayers =
    viewState.zoom < 9
      ? [
          new H3HexagonLayer({
            id: "hexagon-layer",
            data: "/data/aggregated.json",
            extruded: false,
            beforeId: "places_locality",
            getHexagon: (d) => d.h3Index,
            getElevation: 0,
            getFillColor: (d) => {
              const val = getH3Value(d, selectedOperators, selectedPrograms, selectedStatus);

              if (val === 0) {
                return [0, 0, 0, 0];
              }

              const ratio = Math.sqrt(val / 500);
              const clampedRatio = Math.min(ratio, 1);

              return [255, (1 - clampedRatio) * 255, 0, 180];
            },
            parameters: {
              blendFunc: [0, 768],
              blendEquation: 32774,
            },
            updateTriggers: {
              getFillColor: [selectedOperators, selectedPrograms, selectedStatus],
            }
          }),
        ]
      : [
          new MVTLayer({
            id: "fiber-layer",
            sourceLayer: "output",
            data: ["https://tiles.programasfibra.es/output-b018afb40a/{z}/{x}/{y}"],
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
              return getOperatorColor(feature.properties.grantee, 128);
            },
            getLineColor: (feature: any) => getProgramColor(feature.properties.program_name, 128),
            lineWidthMinPixels: 0.5,
            lineWidthUnits: "meters",
            getLineWidth: 2,
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
            getTextColor: (feature: any) => getOperatorColor(feature.properties.grantee, 128),
            getTextAnchor: "middle",
            getTextAlignmentBaseline: "center",
            extensions: [new DataFilterExtension({filterSize: 1})],
            getFilterValue: (feature: any) => {
              const enabledOperator = selectedOperatorsNames.size === 0 ||
                                      selectedOperatorsNames.has(feature.properties.grantee);

              const enabledProgram = selectedPrograms.size === 0 ||
                                    selectedPrograms.has(feature.properties.program_name?.toUpperCase().replace(" ", "_"));

              let enabledProjectStatus = true;

              if (selectedStatus && statusSummary) {
                const projectId = feature.properties.project;
                const projectData = statusSummary[projectId];

                enabledProjectStatus = projectData?.status === selectedStatus;
              }

              return (enabledOperator && enabledProgram && enabledProjectStatus) ? 1 : 0;
            },
            filterRange: [1, 1],
            updateTriggers: {
              getText: fontLoaded,
              getFilterValue: [selectedOperators, selectedPrograms, selectedStatus],
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
            `${window.location.origin}/map-assets/fonts/v1/{fontstack}/{range}.pbf`,
          sprite:
            `${window.location.origin}/map-assets/sprites/v4.1/grayscale`,
          sources: {
            protomaps: {
              type: "vector",
              tiles: [
                "https://tiles.programasfibra.es/map-3a858e9500/{z}/{x}/{y}",
              ],
              maxzoom: 15,
            },
          },
          layers: [
            ...layers("protomaps", namedFlavor("grayscale"), { lang: "es" }),
          ],
        }}
        attributionControl={{
          customAttribution: [
            '<a href="https://protomaps.com/" target="_blank">© Protomaps</a>',
            '<a href="https://www.openstreetmap.org/copyright" target="_blank">© OpenStreetMap</a>',
            '<a href="https://avance.digital.gob.es/banda-ancha/ayudas/Paginas/ayudas-publicas.aspx" target="_blank">Datos: SETELECO</a>'
          ].join(' | '),
          compact: true
        }}
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
        <LegendControl position="top-right" isOpen={isLegendOpen} onClick={() => {setLegendOpen(!isLegendOpen)}} />

        <AnimatePresence>
          {isLegendOpen && <LegendPanel onClose={() => setLegendOpen(false)} selectedOperators={selectedOperators} setSelectedOperators={setSelectedOperators} selectedPrograms={selectedPrograms} setSelectedPrograms={setSelectedPrograms} selectedStatus={selectedStatus} setSelectedStatus={setSelectedStatus} />}
        </AnimatePresence>

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
