import { getOperatorColors, getProgramColors } from "../map/colors";
import { BottomSheet } from "./BottomSheet";
import { useProjectsStatus } from "../api/projects";
import type { ProjectStatus } from "../api/projects/types";
import { STATUS_LABELS } from "../constants/project_status";

const OPERATOR_LEGENDS: Record<string, string> = {
  TELEFONICA: "Movistar",
  ORANGE: "Orange",
  AVATEL: "Avatel y adquiridas",
  ADAMO: "Adamo",
  ASTEO: "Asteo",
  VENTO: "Vento Rede (Rede Aberta)",
  MASMOVIL: "MásMóvil, Embou",
  EUSKALTEL: "Euskaltel/R/Telecable",
  VODAFONE: "Vodafone",
  LYNTIA: "Lyntia",
  OTHER: "Otros",
};

export type LegendPanelProps = {
  onClose: () => void;
  selectedOperators: Set<string>;
  setSelectedOperators: (operators: Set<string>) => void;
  selectedPrograms: Set<string>;
  setSelectedPrograms: (programs: Set<string>) => void;
  selectedStatus: string | null;
  setSelectedStatus: (status: string) => void;
};

const LegendHeader = ({ onClose }: { onClose: () => void }) => (
  <div className="p-4 border-b flex justify-between items-center bg-gray-50">
    <h2 className="font-bold text-gray-800">Leyenda y filtros</h2>
    <button onClick={onClose} className="p-1 hover:bg-gray-200 rounded">
      ✕
    </button>
  </div>
);

const VisualGuide = () => (
  <div className="bg-blue-50 p-4 rounded-xl space-y-4 border border-blue-100">
    <div className="flex items-center gap-4">
      <div
        className="relative w-10 h-10 flex-shrink-0 bg-orange-500 border-[3px] border-magenta-500 rounded-md shadow-sm"
        title="Representación de polígonos"
      />
      <div className="text-[11px] text-blue-900 leading-tight">
        <p className="font-bold mb-0.5">Zonas (Polígonos)</p>
        <p className="opacity-80">Relleno: Operador</p>
        <p className="opacity-80">Borde: Programa</p>
      </div>
    </div>

    <div className="flex items-center gap-4">
      <div className="relative w-10 h-10 flex-shrink-0 flex items-center justify-center">
        <div className="absolute inset-0 rounded-full bg-magenta-500/20 border border-magenta-500" />

        <span
          className="material-icons text-[40px] -translate-y-[8px] z-10 text-orange-500"
          style={{ fontFamily: "Material Icons", fontStyle: "normal" }}
        >
          &#xe0c8;
        </span>
      </div>
      <div className="text-[11px] text-blue-900 leading-tight">
        <p className="font-bold mb-0.5">Localidades (Puntos)</p>
        <p className="opacity-80">Pin: Operador</p>
        <p className="opacity-80">Círculo: Programa</p>
      </div>
    </div>
  </div>
);

const OperatorLegend = ({
  selectedOperators,
  setSelectedOperators,
}: {
  selectedOperators: Set<string>;
  setSelectedOperators: (operators: Set<string>) => void;
}) => {
  const handleChange = (operatorKey: string) => {
    const newSelected = new Set(selectedOperators);
    if (newSelected.has(operatorKey)) {
      newSelected.delete(operatorKey);
    } else {
      newSelected.add(operatorKey);
    }
    setSelectedOperators(newSelected);
  };

  return (
    <div>
      <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">
        Operadores
      </h3>
      <div className="grid grid-cols-1 gap-2">
        {Object.entries(getOperatorColors()).map(([name, rgb]) => {
          const legend = OPERATOR_LEGENDS[name];
          return (
            <div key={legend} className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={selectedOperators.has(name)}
                onChange={() => handleChange(name)}
              />
              <div
                className="w-4 h-4 rounded shadow-sm"
                style={{ background: `rgb(${rgb.join(",")})` }}
              ></div>
              <span className="text-sm text-gray-700">{legend}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const ProgramLegend = ({
  selectedPrograms,
  setSelectedPrograms,
}: {
  selectedPrograms: Set<string>;
  setSelectedPrograms: (programs: Set<string>) => void;
}) => {
  const handleChange = (programKey: string) => {
    const newSelected = new Set(selectedPrograms);
    if (newSelected.has(programKey)) {
      newSelected.delete(programKey);
    } else {
      newSelected.add(programKey);
    }
    setSelectedPrograms(newSelected);
  };

  return (
    <div>
      <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">
        Programas
      </h3>
      <div className="space-y-2">
        {Object.entries(getProgramColors()).map(([year, rgb]) => (
          <div key={year} className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={selectedPrograms.has(year)}
              onChange={() => handleChange(year)}
            />
            <div
              className="w-5 h-5 bg-gray-50 border-[3px] rounded-sm shadow-sm"
              style={{ borderColor: `rgb(${rgb.join(",")})` }}
            ></div>
            <span className="text-sm text-gray-700">
              {year.replace("_", " ")}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

const StatusFilter = ({
  selectedStatus,
  setSelectedStatus,
}: {
  selectedStatus: string | null;
  setSelectedStatus: (status: string) => void;
}) => {
  const { isLoading } = useProjectsStatus();
  const statusOptions = Object.entries(STATUS_LABELS).map(([value, label]) => ({
    value: value as ProjectStatus,
    label,
  }));

  return (
    <div className="mb-4">
      <label
        htmlFor="status-select"
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        Estado
      </label>
      <select
        id="status-select"
        value={selectedStatus ?? ""}
        disabled={isLoading}
        onChange={(e) => setSelectedStatus(e.target.value)}
        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm disabled:opacity-60"
      >
        <option value="">Todos</option>
        {statusOptions.map((status) => {
          return (
            <option key={status.value} value={status.value}>
              {status.label}
            </option>
          );
        })}
      </select>
    </div>
  );
};

const LegendPanel = ({
  onClose,
  selectedOperators,
  setSelectedOperators,
  selectedPrograms,
  setSelectedPrograms,
  selectedStatus,
  setSelectedStatus,
}: LegendPanelProps) => {
  return (
    <BottomSheet onClose={onClose} header={<LegendHeader onClose={onClose} />}>
      <VisualGuide />
      <StatusFilter
        selectedStatus={selectedStatus}
        setSelectedStatus={setSelectedStatus}
      />
      <OperatorLegend
        selectedOperators={selectedOperators}
        setSelectedOperators={setSelectedOperators}
      />
      <ProgramLegend
        selectedPrograms={selectedPrograms}
        setSelectedPrograms={setSelectedPrograms}
      />
    </BottomSheet>
  );
};

export default LegendPanel;
