import argparse
import warnings
import pandas
from typing import Optional, NamedTuple
from abc import abstractmethod
from dataclasses import dataclass
from enum import StrEnum, auto
import geojson
from geojson import FeatureCollection, Feature, Point
import math

PROJECTS_COLUMN_INDEX = 2
GRANTEES_COLUMN_INDEX = 4

class ProgramType(StrEnum):
    UNICO = auto()
    PEBA = auto()

@dataclass
class AreaProperties:
    autonomous_community: str
    province: str
    municipality: str
    project: str
    grantee: str

    @property
    @abstractmethod
    def program_type(self) -> ProgramType:
        pass


@dataclass
class AreaPropertiesUNICO(AreaProperties):
    area_code: str
    building_count: int
    house_count: int

    @property
    def program_type(self) -> ProgramType:
        return ProgramType.UNICO

@dataclass
class AreaPropertiesPEBA(AreaProperties):
    town: str
    exception_zone_code: Optional[str] = None
    exception_zone_name: Optional[str] = None

    @property
    def program_type(self) -> ProgramType:
        return ProgramType.PEBA
    

def read_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Process Excel files from the PEBA-NGA fiber programs to generate a GeoJSON file"
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Path of the Excel file",
        required=True,
    )
    parser.add_argument(
        "-e",
        "--entities",
        type=str,
        help="Path of the entities csv file from the CNIG",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Name of the result file",
        default="out.geojson",
        required=False,
    )

    return parser.parse_args()

def awarded_areas(awarded_projects_file_path: str, entities_file_path: str) -> list[AreaProperties]:
    excel_df = pandas.read_excel(awarded_projects_file_path, sheet_name="Ámbito geográfico actuación", header=None)
    excel_projects_df = pandas.read_excel(awarded_projects_file_path, sheet_name=0, header=None)

    projects = excel_projects_df[PROJECTS_COLUMN_INDEX].dropna().iloc[1:]
    grantees = excel_projects_df[GRANTEES_COLUMN_INDEX].dropna().iloc[1:]

    code_to_coordinates = ine_code_to_coordinates(entities_file_path)
    project_to_grantee=dict(zip(projects, grantees))

    return map_awarded_areas(excel_df, project_to_grantee, code_to_coordinates)

def ine_code_to_coordinates(entities_file_path: str) -> dict[int, tuple[float, float]]:
    entities_df = pandas.read_csv(entities_file_path, encoding="latin1", sep=";")
    ine_codes_cnig = entities_df["CODIGOINE"]
    longitude = entities_df["LONGITUD_ETRS89"]
    longitude = longitude.str.replace(",", ".", regex=False).astype(float)
    latitude = entities_df["LATITUD_ETRS89"]
    latitude = latitude.str.replace(",", ".", regex=False).astype(float)
    return dict(zip(ine_codes_cnig, zip(latitude, longitude)))

def map_awarded_areas(
    df: pandas.DataFrame, 
    project_to_grantee: dict[str, str], 
    code_to_coordinates: dict[int, tuple[float, float]]
) -> FeatureCollection:
    if df.shape[1] < 9:
        for i in range(df.shape[1], 9):
            df[i] = None

    features = []
    for row in df.itertuples(name=None):
        if row[0] < 2:
            continue

        properties = create_properties(row, project_to_grantee)
        ine_code = row[7]
        try:
            coordinates = code_to_coordinates[int(ine_code)]
            features.append(to_geojson(row, properties, coordinates))
        except Exception as e:
            print("error: " + ine_code + " " + str(e))

    return FeatureCollection(features)

def create_properties(row: tuple, project_to_grantee: dict[str, str]) -> AreaProperties:
    exception_code_value = row[8]
    exception_name_value = row[9]

    return AreaPropertiesPEBA(
        autonomous_community=row[3],
        province=row[4],
        municipality=row[5],
        project=(proj := row[2]),
        grantee=project_to_grantee[proj],
        town=row[6],
        exception_zone_code=None if exception_code_value is None or (isinstance(exception_code_value, float) and math.isnan(exception_code_value)) else exception_code_value,
        exception_zone_name=None if exception_name_value is None or (isinstance(exception_name_value, float) and math.isnan(exception_name_value)) else exception_name_value,
    )

def to_geojson(row: tuple, properties: AreaProperties, coordinates: tuple[float, float]) -> Feature:
    point = Point((coordinates[1], coordinates[0]))
    return Feature(geometry=point, properties={**properties.__dict__, 'program_type': properties.program_type})

def write_awarded_areas(output_file_path: str, collection: FeatureCollection):
    with open(output_file_path, "w") as f:
        geojson.dump(collection, f)

def main():
    args = read_args()
    areas_geojson = awarded_areas(args.file, args.entities)
    write_awarded_areas(args.output, areas_geojson)

if __name__ == '__main__':
    main()