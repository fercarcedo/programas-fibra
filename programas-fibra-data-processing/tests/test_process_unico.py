from lib.process_unico import (
    read_awarded_areas,
    filter_awarded_areas,
    write_awarded_areas,
    process_eligible_areas,
    map_areas
)
import pandas as pd
import numpy as np
from io import BytesIO, StringIO
from test_data_unico import AWARDED_AREAS_2020, ELIGIBLE_AREAS_GEO_JSON, AWARDED_AREAS, AWARDED_AREAS_JSON, MAPPED_AWARDED_AREAS, MAPPED_AWARDED_AREAS_2020, PROGRAM_AREAS, PROGRAM_AREAS_2020
from unittest.mock import patch, MagicMock
import pytest

def test_read_awarded_areas():
    df = pd.DataFrame(
        {
            0: [
                *([np.nan] * 4),
                "Programa de Universalización de Infraestructuras Digitales para la Cohesión - Banda Ancha",
                "UNICO - Banda Ancha: Convocatoria 2024",
                "Plan de Recuperación, Transformación y Resiliencia – Financiado por la Unión Europea – NextGenerationEU",
                "Ámbito geográfico de la relación de solicitudes con Resolución de Concesión",
                "EXPEDIENTE",
                "TSI-061400-2024-0008",
                "TSI-061400-2024-0035",
            ],
            1: [*([np.nan] * 8), "Comunidad Autónoma", "PAÍS VASCO/EUSKADI", "PAÍS VASCO/EUSKADI"],
            2: [*([np.nan] * 8), "Provincia", "ÁLAVA", "ÁLAVA"],
            3: [*([np.nan] * 8), "Municipio", "Amurrio", "Amurrio"],
            4: [*([np.nan] * 8), "Código INE del municipio", "01002", "01002"],
            5: [
                *([np.nan] * 8),
                "Identificación  zona (Código  Referencia - 23  cifras)",
                "01002000000-2024-000002",
                "01002000000-2024-000005",
            ],
            6: [*([np.nan] * 8), "Tipo de zona", "Blanca", "Blanca"],
        }
    )
    df2 = pd.DataFrame(
        {
            0: [
                *([np.nan] * 4),
                "Programa de Universalización de Infraestructuras Digitales para la Cohesión - Banda Ancha",
                "UNICO - Banda Ancha: Convocatoria 2024",
                "Plan de Recuperación, Transformación y Resiliencia – Financiado por la Unión Europea – NextGenerationEU",
                "Relación de solicitudes con Resolución de Concesión",
                "EXPEDIENTE",
                "TSI-061400-2024-0008",
                "TSI-061400-2024-0035",
            ],
            1: [
                *([np.nan] * 8),
                "SITUACIÓN",
                "EN EJECUCIÓN",
                "EN EJECUCIÓN",
            ],
            2: [
                *([np.nan] * 8),
                "RAZON SOCIAL",
                "TELEFONICA DE ESPAÑA, S.A.",
                "ORANGE ESPAÑA COMUNICACIONES FIJAS S.L.U.",
            ],
            3: [
                *([np.nan] * 8),
                "COMUNIDAD AUTÓNOMA",
                "PAÍS VASCO/EUSKADI",
                "PAÍS VASCO/EUSKADI",
            ],
            4: [
                *([np.nan] * 8),
                "PROVINCIA",
                "ÁLAVA",
                "ÁLAVA",
            ],
            5: [
                *([np.nan] * 8),
                "PRESUPUESTO FINANCIABLE (€)",
                "179.731,00",
                "544.231,00",
            ],
            6: [
                *([np.nan] * 8),
                "AYUDA (€)",
                "143.784,80",
                "435.384,80",
            ],
            7: [
                *([np.nan] * 8),
                "% AYUDA",
                "80",
                "80",
            ],
            8: [
                *([np.nan] * 8),
                "Tecnología",
                "FTTH",
                "FTTH"
            ],
            9: [
                *([np.nan] * 8),
                "Fecha Finalización",
                "31/12/2025",
                "31/12/2025",
            ],
        }
    )
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df2.to_excel(writer, sheet_name="Proyectos", index=False, header=False)
        df.to_excel(writer, sheet_name="Ámbito", index=False, header=False)
    buffer.seek(0)

    areas = read_awarded_areas(buffer)
    assert areas == PROGRAM_AREAS

def test_filter_awarded_areas():
    buffer = BytesIO(ELIGIBLE_AREAS_GEO_JSON.encode("utf-8"))
    awarded_areas = list(
        filter_awarded_areas(
            buffer, PROGRAM_AREAS
        )
    )
    assert len(awarded_areas) == 2
    assert awarded_areas[0]["properties"]["CodigoZona"] == "01002000000-2024-000002"
    assert awarded_areas[1]["properties"]["CodigoZona"] == "01002000000-2024-000005"

@pytest.mark.parametrize(
    "awarded_areas, program_areas, expected_mapped_areas", 
    [
        (AWARDED_AREAS, PROGRAM_AREAS, MAPPED_AWARDED_AREAS),
        (AWARDED_AREAS_2020, PROGRAM_AREAS_2020, MAPPED_AWARDED_AREAS_2020)
    ]
)
def test_map_areas(awarded_areas, program_areas, expected_mapped_areas):
    mapped_areas = map_areas(awarded_areas, program_areas)
    assert mapped_areas == expected_mapped_areas

def test_write_awarded_areas():
    output = StringIO()

    write_awarded_areas(output, AWARDED_AREAS)

    result = output.getvalue()

    assert result.replace(" ", "").replace("\n", "") == AWARDED_AREAS_JSON.replace(" ", "").replace("\n", "")

@patch('builtins.open')
@patch('lib.process_unico.write_awarded_areas')
@patch('lib.process_unico.filter_awarded_areas')
@patch('lib.process_unico.map_areas')
def test_process_eligible_areas(mock_map, mock_filter, mock_write, mock_open_func):
    mock_input_file = MagicMock()
    mock_output_file = MagicMock()

    mock_open_func.side_effect = [
        mock_input_file,
        mock_output_file
    ]

    mock_filtered_areas = AWARDED_AREAS
    mapped_areas = MAPPED_AWARDED_AREAS
    mock_filter.return_value = mock_filtered_areas
    mock_map.return_value = mapped_areas
    
    eligible_areas_file = "input.geojson"
    output_file = "out.geojson"
    
    process_eligible_areas(eligible_areas_file, PROGRAM_AREAS, output_file)
    
    mock_open_func.assert_any_call(eligible_areas_file, "rb")
    mock_open_func.assert_any_call(output_file, "w", encoding='utf-8')    

    mock_filter.assert_called_once_with(mock_input_file.__enter__.return_value, PROGRAM_AREAS)
    mock_map.assert_called_once_with(mock_filtered_areas, PROGRAM_AREAS)
    mock_write.assert_called_once_with(mock_output_file.__enter__.return_value, mapped_areas)