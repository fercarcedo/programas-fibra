from process_unico import (
    read_awarded_area_codes,
    filter_awarded_areas,
    write_awarded_areas,
    process_eligible_areas,
)
import pandas as pd
import numpy as np
from io import BytesIO, StringIO
from test_data import ELIGIBLE_AREAS_GEO_JSON, AWARDED_AREAS, AWARDED_AREAS_JSON
from unittest.mock import patch, mock_open, MagicMock

def test_read_awarded_area_codes():
    df = pd.DataFrame(
        {
            0: [
                np.nan,
                np.nan,
                "Expediente",
                "TSI-061400-2021-0113",
                "TSI-061400-2021-0113",
            ],
            1: [np.nan, np.nan, "Comunidad Autónoma", "RIOJA (LA)", "RIOJA (LA)"],
            2: [np.nan, np.nan, "Provincia", "RIOJA (LA)", "RIOJA (LA)"],
            3: [np.nan, np.nan, "Municipio", "Zarratón", "Zarratón"],
            4: [np.nan, np.nan, "Código INE del municipio", 26180, 26180],
            5: [
                np.nan,
                np.nan,
                "Identificación  zona (Código  Referencia - 23  cifras)",
                "26180000000-2021-000005",
                "26180000003-2021-000004",
            ],
            6: [np.nan, np.nan, "Tipo de zona", "Blanca", "Blanca"],
        }
    )
    buffer = BytesIO()
    df.to_excel(buffer, sheet_name="Ámbito", index=False, header=False)
    buffer.seek(0)

    area_codes = read_awarded_area_codes(buffer)
    assert area_codes == set(["26180000000-2021-000005", "26180000003-2021-000004"])


def test_filter_awarded_areas():
    buffer = BytesIO(ELIGIBLE_AREAS_GEO_JSON.encode("utf-8"))
    awarded_areas = list(
        filter_awarded_areas(
            buffer, set(["01002000000-2024-000002", "01002000000-2024-000005"])
        )
    )
    assert len(awarded_areas) == 2
    assert awarded_areas[0]["properties"]["CodigoZona"] == "01002000000-2024-000002"
    assert awarded_areas[1]["properties"]["CodigoZona"] == "01002000000-2024-000005"


def test_write_awarded_areas():
    output = StringIO()

    write_awarded_areas(output, AWARDED_AREAS)

    result = output.getvalue()

    assert result.replace(" ", "").replace("\n", "") == AWARDED_AREAS_JSON.replace(" ", "").replace("\n", "")

@patch('builtins.open')
@patch('process_unico.write_awarded_areas')
@patch('process_unico.filter_awarded_areas')
def test_process_eligible_areas(mock_filter, mock_write, mock_open_func):
    mock_input_file = MagicMock()
    mock_output_file = MagicMock()

    mock_open_func.side_effect = [
        mock_input_file,
        mock_output_file
    ]

    mock_filtered_areas = AWARDED_AREAS
    mock_filter.return_value = mock_filtered_areas
    
    eligible_areas_file = "input.geojson"
    awarded_area_codes = ["26180000000-2021-000005", "26180000003-2021-000004"]
    output_file = "out.geojson"
    
    process_eligible_areas(eligible_areas_file, awarded_area_codes, output_file)
    
    mock_open_func.assert_any_call(eligible_areas_file, "rb")
    mock_open_func.assert_any_call(output_file, "w", encoding='utf-8')    
    mock_filter.assert_called_once_with(mock_input_file.__enter__.return_value, awarded_area_codes)
    mock_write.assert_called_once_with(mock_output_file.__enter__.return_value, mock_filtered_areas)