from process_peba import (
    ine_code_to_coordinates,
    create_properties,
    to_geojson,
    write_awarded_areas,
    map_awarded_areas,
    AreaProperties,
    AreaPropertiesPEBA,
)
import pandas as pd
from io import BytesIO
from typing import NamedTuple
import math
from geojson import FeatureCollection, Feature, Point
import geojson
from unittest.mock import patch, mock_open, MagicMock, call
import numpy as np
from test_data_peba import (AREAS_DF, AREAS_DF_WITHOUT_EXCEPTION_ZONE, ENTITIES_DF)
import pytest

class IsNaN:
    def __eq__(self, other):
        return np.isnan(other)
    
def test_ine_code_to_coordinates():
    buffer = BytesIO()
    ENTITIES_DF.to_csv(buffer, sep=";", index=False, encoding="latin1")
    buffer.seek(0)

    coordinates = ine_code_to_coordinates(buffer)
    assert coordinates == {
        1001000000: (42.83981158, -2.51243731),
        1001000100: (42.83981158, -2.51243731),
        1001000101: (42.83981158, -2.51243731),
        1001000199: (42.83981158, -2.51243731),
        1001000200: (42.80973927, -2.53530168),
    }

def test_create_properties_with_no_exception_zone():
    project_to_grantee = {
        "TSI-061000-2018-0001": "INFORMATICA FUENTEALBILLA S.L."
    }
    row = (1, math.nan, "TSI-061000-2018-0001", "CASTILLA LA MANCHA", "ALBACETE", "Casas de Juan Núñez", "CASAS DE JUAN NÚÑEZ", "02021000100", math.nan, math.nan)
    properties = create_properties(row, project_to_grantee)
    expected_area_properties = AreaPropertiesPEBA("CASTILLA LA MANCHA", "ALBACETE", "Casas de Juan Núñez", "TSI-061000-2018-0001", "INFORMATICA FUENTEALBILLA S.L.", "CASAS DE JUAN NÚÑEZ", None, None)
    assert properties == expected_area_properties

def test_create_properties_with_exception_zone():
    project_to_grantee = {
        "TSI-061000-2018-0004": "REDES ÓPTICAS SALMANTINAS S.L."
    }
    row = (5, math.nan, "TSI-061000-2018-0004", "CASTILLA LEON", "SALAMANCA", "Castellanos de Moriscos", "POLÍGONO INDUSTRIAL", "37092000400", "37092000400-2018-zona01", "POLÍGONO INDUSTRIAL CASTELLANOS DE MORISCOS")
    properties = create_properties(row, project_to_grantee)
    expected_area_properties = AreaPropertiesPEBA("CASTILLA LEON", "SALAMANCA", "Castellanos de Moriscos", "TSI-061000-2018-0004", "REDES ÓPTICAS SALMANTINAS S.L.", "POLÍGONO INDUSTRIAL", "37092000400-2018-zona01", "POLÍGONO INDUSTRIAL CASTELLANOS DE MORISCOS")
    assert properties == expected_area_properties

def test_to_geojson():
    row = (5, math.nan, "TSI-061000-2018-0004", "CASTILLA LEON", "SALAMANCA", "Castellanos de Moriscos", "POLÍGONO INDUSTRIAL", "37092000400", "37092000400-2018-zona01", "POLÍGONO INDUSTRIAL CASTELLANOS DE MORISCOS")
    properties = AreaPropertiesPEBA("CASTILLA LEON", "SALAMANCA", "Castellanos de Moriscos", "TSI-061000-2018-0004", "REDES ÓPTICAS SALMANTINAS S.L.", "POLÍGONO INDUSTRIAL", "37092000400-2018-zona01", "POLÍGONO INDUSTRIAL CASTELLANOS DE MORISCOS")
    coordinates = (41.00852887, -5.61116793)
    feature = to_geojson(row, properties, coordinates)
    assert feature == Feature(
        geometry = Point((-5.61116793, 41.00852887)),
        properties = {
            "autonomous_community": "CASTILLA LEON",
            "province": "SALAMANCA",
            "municipality": "Castellanos de Moriscos",
            "project": "TSI-061000-2018-0004",
            "grantee": "REDES ÓPTICAS SALMANTINAS S.L.",
            "town": "POLÍGONO INDUSTRIAL",
            "exception_zone_code": "37092000400-2018-zona01",
            "exception_zone_name": "POLÍGONO INDUSTRIAL CASTELLANOS DE MORISCOS",
            "program_type": "peba"
        }
    )

@patch("builtins.open", new_callable=mock_open)
def test_write_awarded_areas(mock_open_func):
    features = [
        Feature(geometry=Point((1.0, 2.0)), properties={"name": "A"}),
        Feature(geometry=Point((3.0, 4.0)), properties={"name": "B"})
    ]
    collection = FeatureCollection(features)

    write_awarded_areas("out.geojson", collection)

    mock_open_func.assert_called_once_with("out.geojson", "w")
    handle = mock_open_func()
    written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
    loaded = geojson.loads(written_data)

    assert loaded["type"] == "FeatureCollection"
    assert len(loaded["features"]) == 2
    assert loaded["features"][0]["properties"]["name"] == "A"
    assert loaded["features"][1]["properties"]["name"] == "B"

def _create_point(coordinates: tuple[float, float], properties: AreaProperties) -> Feature:
    return Feature(
        geometry=Point((-1.55853519, 39.10267748)),
        properties={**properties.__dict__, 'program_type': 'peba'}
    )

@pytest.mark.parametrize("df", [AREAS_DF, AREAS_DF_WITHOUT_EXCEPTION_ZONE])
@patch('process_peba.create_properties')
@patch('process_peba.to_geojson')
def test_map_awarded_areas(mock_to_geojson, mock_create_properties, df):
    project_to_grantee = {
        "TSI-061000-2018-0001": "INFORMATICA FUENTEALBILLA S.L.",
        "TSI-061000-2018-0002": "INFORMATICA FUENTEALBILLA S.L.",
        "TSI-061000-2018-0003": "INFORMATICA FUENTEALBILLA S.L.",
    }
    code_to_coordinates = {
        2021000100: (39.10267748, -1.55853519),
        2003000100: (38.91810162, -1.92043947),
        46212000100: (39.33552389, -0.60948808),
    }

    properties_list = [
        AreaPropertiesPEBA("CASTILLA LA MANCHA", "ALBACETE", "Casas de Juan Núñez", "TSI-061000-2018-0001", "INFORMÁTICA FUENTEALBILLA S.L.", "CASAS DE JUAN NÚÑEZ"),
        AreaPropertiesPEBA("CASTILLA LA MANCHA", "ALBACETE", "Albacete", "TSI-061000-2018-0002", "INFORMÁTICA FUENTEALBILLA S.L.", "AGUAS NUEVAS"),
        AreaPropertiesPEBA("C.VALENCIANA", "VALENCIA / VALÈNCIA", "Real", "TSI-061000-2018-0003", "INFORMÁTICA FUENTEALBILLA S.L.", "REAL"),
    ]
    points = [
        _create_point((-1.55853519, 39.10267748), properties_list[0]),
        _create_point((-1.92043947, 38.91810162), properties_list[1]),
        _create_point((-0.60948808, 39.33552389), properties_list[2]),
    ]

    mock_create_properties.side_effect = properties_list
    mock_to_geojson.side_effect = points

    collection = map_awarded_areas(df, project_to_grantee, code_to_coordinates)

    assert collection == FeatureCollection(points)

    assert mock_create_properties.call_count == 3

    expected_rows = [
        (2, IsNaN(), 'TSI-061000-2018-0001', 'CASTILLA LA MANCHA', 'ALBACETE', 'Casas de Juan Núñez', 'CASAS DE JUAN NÚÑEZ', '02021000100', IsNaN(), IsNaN()),
        (3, IsNaN(), 'TSI-061000-2018-0002', 'CASTILLA LA MANCHA', 'ALBACETE', 'Albacete', 'AGUAS NUEVAS', '02003000100', IsNaN(), IsNaN()),
        (4, IsNaN(), 'TSI-061000-2018-0003', 'C.VALENCIANA', 'VALENCIA / VALÈNCIA', 'Real', 'REAL', '46212000100', IsNaN(), IsNaN())
    ]

    mock_create_properties.assert_any_call(expected_rows[0], project_to_grantee)
    mock_create_properties.assert_any_call(expected_rows[1], project_to_grantee)
    mock_create_properties.assert_any_call(expected_rows[2], project_to_grantee)

    assert mock_to_geojson.call_count == 3
    
    mock_to_geojson.assert_any_call(expected_rows[0], AreaPropertiesPEBA(autonomous_community='CASTILLA LA MANCHA', province='ALBACETE', municipality='Casas de Juan Núñez', project='TSI-061000-2018-0001', grantee='INFORMÁTICA FUENTEALBILLA S.L.', town='CASAS DE JUAN NÚÑEZ', exception_zone_code=None, exception_zone_name=None), (39.10267748, -1.55853519))
    mock_to_geojson.assert_any_call(expected_rows[1], AreaPropertiesPEBA(autonomous_community='CASTILLA LA MANCHA', province='ALBACETE', municipality='Albacete', project='TSI-061000-2018-0002', grantee='INFORMÁTICA FUENTEALBILLA S.L.', town='AGUAS NUEVAS', exception_zone_code=None, exception_zone_name=None), (38.91810162, -1.92043947))
    mock_to_geojson.assert_any_call(expected_rows[2], AreaPropertiesPEBA(autonomous_community='C.VALENCIANA', province='VALENCIA / VALÈNCIA', municipality='Real', project='TSI-061000-2018-0003', grantee='INFORMÁTICA FUENTEALBILLA S.L.', town='REAL', exception_zone_code=None, exception_zone_name=None), (39.33552389, -0.60948808))