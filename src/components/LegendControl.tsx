import { useControl } from "react-map-gl/maplibre";
import { type ControlPosition, type IControl } from "maplibre-gl";
import { useState } from "react";
import { createPortal } from "react-dom";

const LayersIcon = () => {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
      <polyline points="2 17 12 22 22 17"></polyline>
      <polyline points="2 12 12 17 22 12"></polyline>
    </svg>
  );
};

export type LegendControlProps = {
  isOpen?: boolean;
  onClick: () => void;
  basemap: "map" | "satellite";
  onBasemapToggle: () => void;
  position: ControlPosition;
};

function LegendControl(props: LegendControlProps) {
  const [container, setContainer] = useState<HTMLDivElement | null>(null);

  useControl(
    () =>
      ({
        onAdd: () => {
          const div = document.createElement("div");
          div.className = "maplibregl-ctrl";
          setContainer(div);
          return div;
        },
        onRemove: () => {
          setContainer(null);
        },
        getDefaultPosition: () => props.position,
      }) as IControl,
    {
      position: props.position,
    },
  );

  if (!container) return null;

  return createPortal(
    <div className="flex items-center gap-3">
      <button
        type="button"
        onClick={props.onBasemapToggle}
        title={`Cambiar a ${props.basemap === "map" ? "satélite" : "mapa"}`}
        className="pf-map-btn pf-basemap-btn h-[29px] px-3 rounded-full border border-gray-200 bg-white shadow-md text-xs font-semibold leading-none text-gray-800 flex items-center gap-2 hover:border-gray-300"
      >
        {props.basemap === "map" ? (
          <>
            <svg
              className="-mr-0.5"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <circle cx="12" cy="12" r="3" />
              <path d="M5 12a7 7 0 0 1 14 0" />
              <path d="M19 12a7 7 0 0 1-14 0" />
              <path d="M12 3v2M12 19v2" />
            </svg>
            <span className="pf-basemap-label">Satélite</span>
          </>
        ) : (
          <>
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M3 6.5 9 4l6 2.5L21 4v13.5L15 20l-6-2.5L3 20V6.5Z" />
              <path d="M9 4v13.5M15 6.5V20" />
            </svg>
            <span className="pf-basemap-label">Mapa</span>
          </>
        )}
      </button>

      <button
        type="button"
        className="pf-map-btn w-[29px] h-[29px] rounded border border-gray-200 bg-white shadow-md flex items-center justify-center hover:border-gray-300"
        onClick={props.onClick}
        title="Leyenda y filtros"
        style={{
          cursor: "pointer",
          color: props.isOpen ? "#3b82f6" : "#4b5563",
        }}
      >
        <LayersIcon />
      </button>
    </div>,
    container,
  );
}

export default LegendControl;
