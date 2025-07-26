import re
import pandas
import geojson
from geojson import FeatureCollection, Feature, Point
import math
import numpy as np
from .models import AreaProperties, AreaPropertiesPEBA

PROJECTS_COLUMN_INDEX = 2
GRANTEES_COLUMN_INDEX = 4

PROJECTS_COLUMN_INDEX_OLD = 3
GRANTEES_COLUMN_INDEX_OLD = 2

def _ensure_leading_zero_project(value: str) -> str:
    return re.sub(r'-(?!0)(\d+)$', r'-0\1', value)

def _remove_leading_zero_project(value: str) -> str:
    return re.sub(r'-(\d+)$', lambda m: f"-{int(m.group(1))}", value)

def _grantee_from_project(project: str, project_to_grantee: dict[str, str]) -> str:
    if project in project_to_grantee:
        return project_to_grantee[project]
    project_with_leading_zero = _ensure_leading_zero_project(project)
    if project_with_leading_zero in project_to_grantee:
        return project_to_grantee[project_with_leading_zero]
    return project_to_grantee[_remove_leading_zero_project(project)]

def awarded_areas(awarded_projects_file_path: str, entities_file_path: str) -> list[AreaProperties]:
    excel_file = pandas.ExcelFile(awarded_projects_file_path)

    excel_df = excel_file.parse(sheet_name=1, header=None)
    cols_to_ffill = [
        col for col in excel_df.columns 
        if not excel_df[col].dropna().empty and
            excel_df[col].dropna().iloc[0] not in ['Código zona de excepción', 'Nombre zona de excepción']
    ]
    excel_df[cols_to_ffill] = excel_df[cols_to_ffill].ffill()
    excel_projects_df = excel_file.parse(sheet_name=0, header=None)

    is_old_peba = excel_file.sheet_names[1] == "Ámbito Geográfico"

    projects_column = PROJECTS_COLUMN_INDEX if not is_old_peba else PROJECTS_COLUMN_INDEX_OLD
    projects = excel_projects_df[projects_column].dropna().iloc[1:]

    if not is_old_peba:
        grantees = excel_projects_df[GRANTEES_COLUMN_INDEX].dropna().iloc[1:]
    else:
        grantees = excel_projects_df[GRANTEES_COLUMN_INDEX_OLD].ffill().dropna().iloc[1:]

    code_to_coordinates = ine_code_to_coordinates(entities_file_path)
    project_to_grantee=dict(zip(projects, grantees))

    return map_awarded_areas(excel_df, project_to_grantee, code_to_coordinates, is_old_peba)

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
    code_to_coordinates: dict[int, tuple[float, float]],
    is_old_peba: bool
) -> FeatureCollection:
    if df.shape[1] < 9:
        for i in range(df.shape[1], 9):
            df[i] = np.nan
    
    features = []
    for row in df.itertuples(name=None):
        if (not is_old_peba and row[0] < 2) or (is_old_peba and row[0] < 1):
            continue

        properties = create_properties(row, project_to_grantee, is_old_peba)
        ine_code_column = 7 if not is_old_peba else 8
        ine_code = row[ine_code_column]
        try:
            coordinates = code_to_coordinates[int(ine_code)]
            features.append(to_geojson(properties, coordinates))
        except Exception:
            print("error: " + ine_code)

    return FeatureCollection(features)

def create_properties(
    row: tuple, 
    project_to_grantee: dict[str, str], 
    is_old_peba: bool
) -> AreaProperties:
    exception_code_value = row[8] if not is_old_peba else None
    exception_name_value = row[9] if not is_old_peba else None

    return AreaPropertiesPEBA(
        autonomous_community=row[3 if not is_old_peba else 4],
        province=row[4 if not is_old_peba else 5],
        municipality=row[5 if not is_old_peba else 7],
        project=(proj := row[2]),
        grantee=_grantee_from_project(proj, project_to_grantee),
        town=row[6 if not is_old_peba else 9],
        exception_zone_code=None if exception_code_value is None or (isinstance(exception_code_value, float) and math.isnan(exception_code_value)) else exception_code_value,
        exception_zone_name=None if exception_name_value is None or (isinstance(exception_name_value, float) and math.isnan(exception_name_value)) else exception_name_value,
    )

def to_geojson(properties: AreaProperties, coordinates: tuple[float, float]) -> Feature:
    point = Point((coordinates[1], coordinates[0]))
    return Feature(geometry=point, properties={**properties.__dict__, 'program_type': properties.program_type})

def write_awarded_areas(output_file_path: str, collection: FeatureCollection):
    with open(output_file_path, "w") as f:
        geojson.dump(collection, f)

def execute(awarded_projects_file_path: str, entities_file_path: str, output_file_path: str):
    areas_geojson = awarded_areas(awarded_projects_file_path, entities_file_path)
    write_awarded_areas(output_file_path, areas_geojson)