import ijson
import pandas
import simplejson as json
from decimal import Decimal
from dataclasses import dataclass
from typing import BinaryIO, TextIO, Generator, Any
from .models import AreaPropertiesArea
from .centroid_calculator import write_centroids


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


@dataclass
class ProgramAreas:
    area_to_project: dict[str, str]
    project_to_grantee: dict[str, str]


AREA_CODES_COLUMN_INDEX = 5
PROJECTS_COLUMN_INDEX = 0
GRANTEES_COLUMN_INDEX = 2


def read_awarded_areas(file_path: str) -> ProgramAreas:
    excel_df = pandas.read_excel(file_path, sheet_name=1, header=None)
    excel_projects_df = pandas.read_excel(file_path, sheet_name=0, header=None)

    area_codes_column = excel_df[AREA_CODES_COLUMN_INDEX].dropna()
    if area_codes_column.iloc[0] != "Código INE de la ESP":
        area_codes = area_codes_column.iloc[1:]
    else:
        area_codes = excel_df[AREA_CODES_COLUMN_INDEX + 1].dropna().iloc[1:]

    area_projects = excel_df[PROJECTS_COLUMN_INDEX].dropna().iloc[5:]

    projects = excel_projects_df[PROJECTS_COLUMN_INDEX].dropna().iloc[5:]
    grantees = excel_projects_df[GRANTEES_COLUMN_INDEX].dropna().iloc[1:]

    return ProgramAreas(
        area_to_project=dict(zip(area_codes, area_projects)),
        project_to_grantee=dict(zip(projects, grantees)),
    )


def get_area_code(record: dict) -> str:
    properties = record["properties"]
    return (
        properties.get("CodigoZona")
        or properties.get("CodZona")
        or properties.get("Cod_Zona")
        or properties.get("Codigo_Zon")
    )


def remove_area_type_suffix(area_code: str) -> str:
    if area_code.endswith(("-B", "-G")):
        return area_code[:-2]

    return area_code


def is_awarded(record: dict, awarded_map: dict[str, str]):
    area = get_area_code(record)

    return remove_area_type_suffix(area) in awarded_map


def filter_awarded_areas(
    f: BinaryIO, awarded_areas: ProgramAreas
) -> Generator[dict[str, Any], None, None]:
    records = ijson.items(f, "features.item")

    return (r for r in records if is_awarded(r, awarded_areas.area_to_project))


def write_awarded_areas(f: TextIO, areas: list[dict[str, Any]]):
    f.write('{"type": "FeatureCollection", "features": [')

    first_feature = True
    for area in areas:
        if not first_feature:
            f.write(",")
        else:
            first_feature = False
        json.dump(area, f, use_decimal=True, ensure_ascii=False)

    f.write("]}")


def map_areas(
    areas: list[dict[str, Any]], program_areas: ProgramAreas, program_name: str
) -> list[dict[str, Any]]:
    return [
        {
            **area,
            "properties": {
                **(
                    area_properties := AreaPropertiesArea(
                        autonomous_community=(properties := area["properties"]).get(
                            "Comunidad_"
                        )
                        or properties.get("CCAA"),
                        province=properties["Provincia"],
                        municipality=properties["Municipio"],
                        area_code=(code := get_area_code(area)),
                        building_count=properties.get("UIs"),
                        house_count=properties.get("Viviendas")
                        or properties.get("Viv_Zona"),
                        town=properties.get("Nombre_ESP"),
                        project=(
                            proj := program_areas.area_to_project[
                                remove_area_type_suffix(code)
                            ]
                        ),
                        grantee=program_areas.project_to_grantee[proj],
                        program_name=program_name,
                    )
                ).__dict__,
                "type": str(area_properties.type),
            },
        }
        for area in areas
    ]


def process_eligible_areas(
    eligible_areas_file_path: str,
    awarded_areas: ProgramAreas,
    output_file_path: str,
    program_name: str,
):
    with open(eligible_areas_file_path, "rb") as f:
        with open(output_file_path, "w", encoding="utf-8") as out:
            areas = filter_awarded_areas(f, awarded_areas)
            write_awarded_areas(out, map_areas(areas, awarded_areas, program_name))


def execute(
    awarded_areas_file_path: str,
    eligible_areas_file_path: str,
    output_file_path: str,
    program_name: str,
):
    awarded_areas = read_awarded_areas(awarded_areas_file_path)
    process_eligible_areas(
        eligible_areas_file_path, awarded_areas, output_file_path, program_name
    )
    write_centroids(output_file_path, f"centroids.{output_file_path}")
