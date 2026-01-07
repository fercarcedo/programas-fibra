import { useControl } from "react-map-gl/maplibre";
import { type ControlPosition, type IControl } from "maplibre-gl";
import { useState } from "react";
import { createPortal } from "react-dom";

const LayersIcon = () => {
    return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
        <polyline points="2 17 12 22 22 17"></polyline>
        <polyline points="2 12 12 17 22 12"></polyline>
    </svg>;
};

export type LegendControlProps = {
  isOpen?: boolean;
  onClick: () => void;
  position: ControlPosition;
};

function LegendControl(props: LegendControlProps) {
  const [container, setContainer] = useState<HTMLDivElement | null>(null);

  useControl(
    () => ({
      onAdd: () => {
        const div = document.createElement('div');
        div.className = 'maplibregl-ctrl maplibregl-ctrl-group';
        setContainer(div);
        return div;
      },
      onRemove: () => {
        setContainer(null);
      },
      getDefaultPosition: () => props.position
    } as IControl),
    {
      position: props.position
    }
  );

  if (!container) return null;

  return createPortal(
    <button
      type="button"
      className="custom-legend-btn"
      onClick={props.onClick}
      title="Leyenda y capas"
      style={{
        width: '29px',
        height: '29px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'none',
        border: 'none',
        cursor: 'pointer',
        color: props.isOpen ? '#3b82f6' : '#4b5563'
      }}
    >
      <LayersIcon />
    </button>,
    container
  );
}

export default LegendControl;
