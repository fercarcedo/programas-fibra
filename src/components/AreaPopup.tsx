import { Popup } from "react-map-gl/maplibre";
import type { AreaProperties } from "../api/areas/types";
import { useProjectAward, useProjectsStatus } from "../api/projects";
import { useState, type ReactNode } from "react";
import type { ProjectsStatusSummary } from "../api/projects/types";
import { STATUS_LABELS } from "../constants/project_status";
import { normalizeGeoName } from "../formatters/normalizeGeoName";

export type AreaPopupProps = {
  latitude: number;
  longitude: number;
  centroidLatitude: number;
  centroidLongitude: number;
  data: AreaProperties;
  onClose: () => void;
};

export type AreaPropertyRowProps = {
  name: string;
  value: string;
  expandable?: boolean;
  children?: ReactNode;
};

function AreaPropertyRow(props: AreaPropertyRowProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToggle = () => {
    if (props.expandable) {
      setIsExpanded(!isExpanded);
    }
  };

  return (
    <>
      <tr
        onClick={handleToggle}
        className={props.expandable ? "cursor-pointer hover:bg-gray-50" : ""}
      >
        <th className="text-left font-bold pr-4 pb-4 leading-[1.25]">
          {props.name}
        </th>
        <td className="pb-4 leading-[1.25] text-right">
          <div className="flex items-center justify-end">
            <span className="mr-2">{props.value}</span>
            {props.expandable && (
              <svg
                className={`transition-transform duration-300 transform ${isExpanded ? "rotate-180" : "rotate-0"}`}
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                {/* Chevron icon: Points Down by default (Collapsed) */}
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            )}
          </div>
        </td>
      </tr>
      {props.expandable && (
        <tr>
          {/* This cell spans the entire width of the table */}
          <td colSpan={2} className="p-0">
            <div
              className={`overflow-hidden transition-all duration-300 ease-in-out ${isExpanded ? "max-h-96 opacity-100 py-2" : "max-h-0 opacity-0"}`}
            >
              {props.children}
            </div>
          </td>
        </tr>
      )}
    </>
  );
}


const getProjectStatus = (id: string, projectsStatusData: ProjectsStatusSummary) => {
  if (projectsStatusData[id]) return projectsStatusData[id];

  const parts = id.split('-');
  if (parts.length > 0) {
    parts[parts.length - 1] = parts[parts.length - 1].replace(/^0+/, '');
    const normalizedId = parts.join('-');

    return projectsStatusData[normalizedId];
  }

  return undefined;
};

function AreaPopup(props: AreaPopupProps) {
  const { isPending, error, data } = useProjectAward(props.data.project);
  const {
    isPending: isPendingProjectsStatus,
    error: projectsStatusError,
    data: projectsStatusData
  } = useProjectsStatus();

  const autonomousCommunity = normalizeGeoName(props.data.autonomous_community);
  const province = normalizeGeoName(props.data.province);
  const town = normalizeGeoName(props.data.town);

  const projectStatus = projectsStatusData ? getProjectStatus(props.data.project, projectsStatusData) : null;

  return (
    <Popup
      className="z-50 min-w-[280px] p-2"
      maxWidth="none"
      latitude={props.latitude}
      longitude={props.longitude}
      onClose={props.onClose}
      closeOnClick={false}
    >
      <div>
        <h2 className="text-lg font-semibold max-w-[240px]">{props.data.grantee}</h2>
        <h3 className="text-base font-medium pb-4">
          {props.data.program_name}
        </h3>
        <table className="w-full max-w-[240px]">
          <tbody>
            <AreaPropertyRow
              name="Comunidad Autónoma"
              value={autonomousCommunity}
            />
            <AreaPropertyRow name="Provincia" value={province} />
            <AreaPropertyRow name="Municipio" value={props.data.municipality} />
            {props.data.area_code && (
              <AreaPropertyRow
                name="Código zona"
                value={props.data.area_code}
              />
            )}
            {!!props.data.building_count && (
              <AreaPropertyRow
                name="Edificios zona"
                value={props.data.building_count.toString()}
              />
            )}
            {!!props.data.house_count && (
              <AreaPropertyRow
                name="Viviendas zona"
                value={props.data.house_count.toString()}
              />
            )}
            {props.data.town && (
              <AreaPropertyRow name="Localidad" value={town} />
            )}
            {props.data.exception_zone_code && (
              <AreaPropertyRow
                name="Código zona de excepción"
                value={props.data.exception_zone_code}
              />
            )}
            {props.data.exception_zone_name && (
              <AreaPropertyRow
                name="Nombre zona de excepción"
                value={props.data.exception_zone_name}
              />
            )}
            <tr>
              <td colSpan={2} className="pb-4">
                <div className="flex justify-center">
                  <a
                    href={`https://www.google.com/maps/search/?api=1&query=${props.centroidLatitude},${props.centroidLongitude}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Ver en Maps
                  </a>
                </div>
              </td>
            </tr>
            <AreaPropertyRow
              name="Proyecto"
              value={props.data.project}
              expandable={true}
            >
              {(isPending || isPendingProjectsStatus) ? (
                <p>Cargando...</p>
              ) : (error || projectsStatusError) ? (<span>Error al cargar los datos del proyecto</span>) : (
                <div className="p-4 bg-gray-50 border-t">
                  <table className="w-full">
                    <tbody>
                      {projectStatus?.status && (
                        <AreaPropertyRow name="Estado" value={STATUS_LABELS[projectStatus.status]} />
                      )}
                      <AreaPropertyRow
                        name="Presupuesto financiable"
                        value={data.eligible_budget}
                      />
                      <AreaPropertyRow name="Ayuda" value={data.funding} />
                      {data.subsidy && (
                        <AreaPropertyRow
                          name="Subvención"
                          value={data.subsidy}
                        />
                      )}
                      {data.loan && (
                        <AreaPropertyRow name="Préstamo" value={data.loan} />
                      )}
                      <AreaPropertyRow
                        name="Porcentaje de financiación"
                        value={data.funding_percentage}
                      />
                      <AreaPropertyRow
                        name="Tecnología"
                        value={data.technology}
                      />
                      {projectStatus?.deadline && (
                        <AreaPropertyRow
                          name="Fecha límite"
                          value={projectStatus.deadline}
                        />
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </AreaPropertyRow>
          </tbody>
        </table>
      </div>
    </Popup>
  );
}

export default AreaPopup;
