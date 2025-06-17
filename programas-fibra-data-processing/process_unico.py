import ijson
import pandas
import argparse
import simplejson as json
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum
from typing import BinaryIO, TextIO, Generator, Any

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

@dataclass
class ProgramAreas:
    area_to_project: dict[str, str]
    project_to_grantee: dict[str, str]

class ProgramType(Enum):
    UNICO = 'UNICO'
    PEBA = 'PEBA'

@dataclass
class AreaProperties:
    program_type: ProgramType
    autonomous_community: str
    province: str
    municipality: str
    area_code: str
    building_count: int
    house_count: int
    project: str
    grantee: str

AREA_CODES_COLUMN_INDEX = 5
PROJECTS_COLUMN_INDEX = 0
GRANTEES_COLUMN_INDEX = 2

def read_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Process GeoJSON files from the UNICO fiber programs to only include awarded areas"
    )
    parser.add_argument(
        "-e",
        "--eligible-areas",
        type=str,
        help="Path of the GeoJSON file with the eligible areas",
        required=True,
    )
    parser.add_argument(
        "-a",
        "--awarded-areas",
        type=str,
        help="Path of the Excel file with the awarded areas",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=str,
        help="Name of the result file",
        default="out.geojson",
        required=False,
    )

    return parser.parse_args()

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
            'properties': AreaProperties(
                program_type=ProgramType.UNICO.value,
                autonomous_community=area['properties']['Comunidad_'],
                province=area['properties']['Provincia'],
                municipality=area['properties']['Municipio'],
                area_code=(code := area['properties']['CodigoZona']),
                building_count=area['properties']['UIs'],
                house_count=area['properties']['Viviendas'],
                project=(proj := program_areas.area_to_project[code]),
                grantee=program_areas.project_to_grantee[proj],
            ).__dict__
        }
        for area in areas
    ]

def process_eligible_areas(eligible_areas_file_path: str, awarded_areas: ProgramAreas, output_file_path: str):
    with open(eligible_areas_file_path, "rb") as f:
        with open(output_file_path, "w", encoding='utf-8') as out:
            areas = filter_awarded_areas(f, awarded_areas)
            write_awarded_areas(out, map_areas(areas, awarded_areas))


def main():
    args = read_args()
    awarded_areas = read_awarded_areas(args.awarded_areas)
    process_eligible_areas(args.eligible_areas, awarded_areas, args.output_file)


if __name__ == "__main__":
    main()
