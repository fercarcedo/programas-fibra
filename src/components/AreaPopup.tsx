import { Popup } from "react-map-gl/maplibre";
import type { AreaProperties } from "../api/areas/types";

export type AreaPopupProps = {
  latitude: number;
  longitude: number;
  data: AreaProperties;
  onClose: () => void;
};

export type AreaPropertyRowProps = {
  name: string;
  value: string;
};

function AreaPropertyRow(props: AreaPropertyRowProps) {
  return (
    <tr>
      <th className="text-left font-bold pr-4 pb-4 leading-[1.25]">
        {props.name}
      </th>
      <td className="pb-4 leading-[1.25]">{props.value}</td>
    </tr>
  );
}

function AreaPopup(props: AreaPopupProps) {
  return (
    <Popup
      className="z-50"
      latitude={props.latitude}
      longitude={props.longitude}
      onClose={props.onClose}
      closeOnClick={false}
      style={{ padding: "0.5rem" }}
    >
      <div>
        <h2 className="text-lg font-semibold">{props.data.grantee}</h2>
        <h3 className="text-base font-medium pb-4">
          {props.data.program_name}
        </h3>
        <table className="w-full">
          <tbody>
            <AreaPropertyRow
              name="COMUNIDAD AUTÓNOMA"
              value={props.data.autonomous_community}
            />
            <AreaPropertyRow name="PROVINCIA" value={props.data.province} />
            <AreaPropertyRow name="MUNICIPIO" value={props.data.municipality} />
            <AreaPropertyRow name="PROYECTO" value={props.data.project} />
            <AreaPropertyRow name="CÓDIGO ZONA" value={props.data.area_code} />
            {props.data.building_count && (
              <AreaPropertyRow
                name="EDIFICIOS ZONA"
                value={props.data.building_count.toString()}
              />
            )}
            {props.data.house_count && (
              <AreaPropertyRow
                name="VIVIENDAS ZONA"
                value={props.data.house_count.toString()}
              />
            )}
            {props.data.town && (
              <AreaPropertyRow name="LOCALIDAD" value={props.data.town} />
            )}
            {props.data.exception_zone_code && (
              <AreaPropertyRow
                name="CÓDIGO ZONA DE EXCEPCIÓN"
                value={props.data.exception_zone_code}
              />
            )}
            {props.data.exception_zone_name && (
              <AreaPropertyRow
                name="NOMBRE ZONA DE EXCEPCIÓN"
                value={props.data.exception_zone_name}
              />
            )}
          </tbody>
        </table>
      </div>
    </Popup>
  );
}

export default AreaPopup;
