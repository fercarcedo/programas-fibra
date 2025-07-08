import ijson
import pandas
import simplejson as json
from decimal import Decimal
from dataclasses import dataclass
from typing import BinaryIO, TextIO, Generator, Any
from .models import AreaPropertiesUNICO

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
    excel_df = pandas.read_excel(file_path, sheet_name="Ámbito", header=None)
    excel_projects_df = pandas.read_excel(file_path, sheet_name="Proyectos", header=None)

    area_codes = excel_df[AREA_CODES_COLUMN_INDEX].dropna().iloc[1:]
    area_projects = excel_df[PROJECTS_COLUMN_INDEX].dropna().iloc[5:]

    projects = excel_projects_df[PROJECTS_COLUMN_INDEX].dropna().iloc[5:]
    grantees = excel_projects_df[GRANTEES_COLUMN_INDEX].dropna().iloc[1:]

    return ProgramAreas(
        area_to_project=dict(zip(area_codes, area_projects)),
        project_to_grantee=dict(zip(projects, grantees)),
    )


def filter_awarded_areas(f: BinaryIO, awarded_areas: ProgramAreas) -> Generator[dict[str, Any], None, None]:
    records = ijson.items(f, "features.item")
    return (r for r in records if r["properties"]["CodigoZona"] in awarded_areas.area_to_project)


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

def map_areas(areas: list[dict[str, Any]], program_areas: ProgramAreas) -> list[dict[str, Any]]:
    return [
        {
            **area,
            'properties': {
                **(area_properties := AreaPropertiesUNICO(
                    autonomous_community=area['properties']['Comunidad_'],
                    province=area['properties']['Provincia'],
                    municipality=area['properties']['Municipio'],
                    area_code=(code := area['properties']['CodigoZona']),
                    building_count=area['properties']['UIs'],
                    house_count=area['properties']['Viviendas'],
                    project=(proj := program_areas.area_to_project[code]),
                    grantee=program_areas.project_to_grantee[proj],
                )).__dict__, 
                'program_type': area_properties.program_type
            }
        }
        for area in areas
    ]

def process_eligible_areas(eligible_areas_file_path: str, awarded_areas: ProgramAreas, output_file_path: str):
    with open(eligible_areas_file_path, "rb") as f:
        with open(output_file_path, "w", encoding='utf-8') as out:
            areas = filter_awarded_areas(f, awarded_areas)
            write_awarded_areas(out, map_areas(areas, awarded_areas))

def execute(awarded_areas_file_path: str, eligible_areas_file_path: str, output_file_path: str):
    awarded_areas = read_awarded_areas(awarded_areas_file_path)
    process_eligible_areas(eligible_areas_file_path, awarded_areas, output_file_path)