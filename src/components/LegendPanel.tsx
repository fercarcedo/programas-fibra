import { motion } from "motion/react";
import { getOperatorColors, getProgramColors } from "../map/colors";
import { useState } from "react";

const OPERATOR_LEGENDS: Record<string, string> = {
  TELEFONICA: "Movistar",
  ORANGE:     "Orange",
  AVATEL:     "Avatel y adquiridas",
  ADAMO:      "Adamo",
  ASTEO:      "Asteo",
  VENTO:      "Vento Rede (Rede Aberta)",
  MASMOVIL:   "MásMóvil, Embou",
  EUSKALTEL:  "Euskaltel/R/Telecable",
  VODAFONE:   "Vodafone",
  LYNTIA:     "Lyntia",
  OTHER:      "Otros"
};

export type LegendPanelProps = {
  onClose: () => void;
};

const LegendHeader = ({onClose}: LegendPanelProps) => (
    <div className="p-4 border-b flex justify-between items-center bg-gray-50">
        <h2 className="font-bold text-gray-800">Leyenda</h2>
        <button onClick={onClose} className="p-1 hover:bg-gray-200 rounded">✕</button>
    </div>
)

const VisualGuide = () => (
  <div className="bg-blue-50 p-4 rounded-xl space-y-4 border border-blue-100">
    <div className="flex items-center gap-4">
      <div className="relative w-10 h-10 flex-shrink-0 bg-orange-500 border-[3px] border-magenta-500 rounded-md shadow-sm" title="Representación de polígonos" />
      <div className="text-[11px] text-blue-900 leading-tight">
        <p className="font-bold mb-0.5">Zonas (Polígonos) - Plan UNICO</p>
        <p className="opacity-80">Relleno: Operador | Borde: Programa</p>
      </div>
    </div>

    <div className="flex items-center gap-4">
      <div className="relative w-10 h-10 flex-shrink-0 flex items-center justify-center">
        <div className="absolute inset-0 rounded-full bg-magenta-500/20 border border-magenta-500" />

        <span
          className="material-icons text-[40px] -translate-y-[8px] z-10 text-orange-500"
          style={{ fontFamily: 'Material Icons', fontStyle: 'normal' }}
        >
          &#xe0c8;
        </span>
      </div>
      <div className="text-[11px] text-blue-900 leading-tight">
        <p className="font-bold mb-0.5">Localidades (Puntos) - Plan PEBA</p>
        <p className="opacity-80">Pin: Operador | Círculo: Programa</p>
      </div>
    </div>
  </div>
);

const OperatorLegend = () => (
    <div>
        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Operadores</h3>
        <div className="grid grid-cols-1 gap-2">
            {Object.entries(getOperatorColors()).map(([name, rgb]) => {
                const legend = OPERATOR_LEGENDS[name];
                return (
                    <div key={legend} className="flex items-center gap-3">
                        <div className="w-4 h-4 rounded shadow-sm" style={{ background: `rgb(${rgb.join(',')})` }}></div>
                        <span className="text-sm text-gray-700">{legend}</span>
                    </div>
                );
            })}
        </div>
    </div>
);

const ProgramLegend = () => (
    <div>
        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Programas</h3>
        <div className="space-y-2">
            {Object.entries(getProgramColors()).map(([year, rgb]) => (
            <div key={year} className="flex items-center gap-3">
                <div className="w-5 h-5 bg-gray-50 border-[3px] rounded-sm shadow-sm" style={{ borderColor: `rgb(${rgb.join(',')})` }}></div>
                <span className="text-sm text-gray-700">{year.replace('_', ' ')}</span>
            </div>
            ))}
        </div>
    </div>
);

const LegendPanel = ({onClose}: LegendPanelProps) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;
    const windowHeight = typeof window !== 'undefined' ? window.innerHeight : 800;
    const variants = {
      mobile: {
        closed: { y: windowHeight },
        collapsed: { y: windowHeight * 0.4 },
        expanded: { y: 0 }
      },
      desktop: {
        closed: { x: "100%", y: 0 },
        open: { x: 0, y: 0 }
      }
    };
    return <motion.div
        initial={isMobile ? "closed" : "closed"}
        animate={isMobile
          ? (isExpanded ? "expanded" : "collapsed")
          : "open"
        }
        exit="closed"
        variants={isMobile ? variants.mobile : variants.desktop}

        transition={{
          type: "spring",
          damping: 30,
          stiffness: 300,
          mass: 0.8
        }}

        drag={isMobile ? "y" : false}
        dragConstraints={{ top: 0, bottom: windowHeight }}
        dragElastic={0.05}
        onDragEnd={(_, info) => {
          if (!isMobile) return;
          const dragDistance = info.offset.y;
          const dragVelocity = info.velocity.y;

          if (dragDistance < -100 || dragVelocity < -500) setIsExpanded(true);
          else if (dragDistance > 100 || dragVelocity > 500) {
            if (isExpanded) setIsExpanded(false);
            else onClose();
          }
        }}

        className="absolute bottom-0 left-0 right-0 z-[60] bg-white rounded-t-3xl shadow-2xl
                    flex flex-col h-[100dvh]
                    md:h-full md:top-0 md:bottom-0 md:right-0 md:left-auto md:w-80 md:rounded-t-none md:rounded-l-3xl overflow-hidden"
        >
        <div className="w-12 h-1.5 bg-gray-200 rounded-full mx-auto my-3 md:hidden flex-shrink-0" />

        <LegendHeader onClose={onClose} />

        <div className="flex-1 overflow-y-auto p-5 space-y-8"
          onPointerDown={(e) => isMobile && e.stopPropagation()}
          style={{
            paddingBottom: isMobile && !isExpanded ? "calc(40vh + 20px)" : "20px"
          }}>
            <VisualGuide />
            <OperatorLegend />
            <ProgramLegend />
        </div>
    </motion.div>;
}

export default LegendPanel;