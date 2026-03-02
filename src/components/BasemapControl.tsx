import { useState } from "react";
import { createPortal } from "react-dom";
import { type ControlPosition, type IControl } from "maplibre-gl";
import { useControl } from "react-map-gl/maplibre";

export type BasemapControlProps = {
  basemap: "map" | "satellite";
  onToggle: () => void;
  position: ControlPosition;
};

function BasemapControl(props: BasemapControlProps) {
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
    }
  );

  if (!container) return null;

  return createPortal(
    <button
      type="button"
      onClick={props.onToggle}
      title={`Cambiar a ${props.basemap === "map" ? "satélite" : "mapa"}`}
      className="h-[29px] px-3 rounded-full border border-gray-200 bg-white/95 shadow-md text-xs font-semibold leading-none text-gray-800 flex items-center gap-2 hover:border-gray-300"
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
          Satélite
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
          Mapa
        </>
      )}
    </button>,
    container
  );
}

export default BasemapControl;
