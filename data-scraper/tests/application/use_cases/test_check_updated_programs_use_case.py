from data.page_html import UNICO_2023_PAGE, UNICO_2024_PAGE, PAGE_WITHOUT_COL_CONTENIDO_WITH_XLSX, PAGE_WITHOUT_COL_CONTENIDO_WITHOUT_XLSX
from unittest.mock import Mock, MagicMock, AsyncMock
import sys

class MockRequest:
    def __init__(self, url, method="GET", headers=None, body=None):
        self.url = url
        self.method = method
        self.headers = headers or {}
        self._body = body
        self.json_data = AsyncMock()
        self.text_data = AsyncMock()
    
    async def json(self):
        return self.json_data()
    
    async def text(self):
        return self.text_data()

class MockResponse:
    def __init__(self, body, status=200, headers=None):
        self.body = body
        self.status = status
        self.headers = headers or {}
        self.ok = status < 400
    
    @classmethod
    def json(cls, data, status=200):
        import json
        return cls(json.dumps(data), status=status)
    
    async def json_async(self):
        """For when response.json() is called"""
        import json
        return json.loads(self.body) if isinstance(self.body, str) else self.body
    
    async def text(self):
        return str(self.body)

UNICO_2024_XLSX_URL = "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Documents/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2024.xlsx"

async def mock_fetch(url, **kwargs):
    if url == "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx":
        return MockResponse(
            body=UNICO_2023_PAGE,
            status=200
        )
    elif url == "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO.aspx":
        return MockResponse(
            body=UNICO_2024_PAGE,
            status=200
        )
    elif url == "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO-broken.aspx":
        return MockResponse(body=PAGE_WITHOUT_COL_CONTENIDO_WITH_XLSX, status=200)
    elif url == "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO-no-xlsx.aspx":
        return MockResponse(body=PAGE_WITHOUT_COL_CONTENIDO_WITHOUT_XLSX, status=200)
    elif url == "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO-error.aspx":
        return MockResponse(body="", status=503)
    elif isinstance(url, MockRequest):
        if url.url == "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Documents/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2023_01_08_2025.xlsx":
            return MockResponse(
                body=None,
                status=200,
                headers={
                    'last-modified': 'Fri, 01 Aug 2025 09:09:10 GMT'
                }
            )
        elif url.url == UNICO_2024_XLSX_URL:
            return MockResponse(
                body=None,
                status=200,
                headers={
                    'last-modified': 'Tue, 17 Dec 2024 07:51:15 GMT'
                }
            )

mock_workers = MagicMock()
mock_workers.fetch = AsyncMock(side_effect=mock_fetch)
mock_workers.Request = MockRequest
mock_workers.Response = MockResponse
sys.modules['workers'] = mock_workers

from application.use_cases.check_updated_programs_use_case import CheckUpdatedProgramsUseCase
from domain.program_update_result import ProgramUpdateResult
from domain.repositories.config_repository import ConfigRepository
from domain.repositories.program_repository import ProgramRepository

MOCK_URL_MAP = {
    "UNICO 2023": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx",
    "UNICO 2024": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO.aspx"
}

async def test_execute():
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = MOCK_URL_MAP

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_update.return_value = None

    expected_updated_projects = [
        ProgramUpdateResult(
            file_url="https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Documents/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2023_01_08_2025.xlsx",
            program_name="UNICO 2023",
            last_updated=1754006400
        ),
        ProgramUpdateResult(
            file_url="https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Documents/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2024.xlsx",
            program_name="UNICO 2024",
            last_updated=1734421875
        )
    ]
    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository)

    updated_projects = await use_case.execute()

    assert expected_updated_projects == updated_projects

async def test_execute_with_some_not_updated_projects():
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = MOCK_URL_MAP

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_update.return_value = 1734421875

    expected_updated_projects = [
        ProgramUpdateResult(
            file_url="https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Documents/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2023_01_08_2025.xlsx",
            program_name="UNICO 2023",
            last_updated=1754006400
        )
    ]
    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository)

    updated_projects = await use_case.execute()

    assert expected_updated_projects == updated_projects


async def test_missing_col_contenido_falls_back_to_xlsx_head():
    url_map = {
        "UNICO 2024 broken": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO-broken.aspx",
    }
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = url_map

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_update.return_value = None

    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository)
    results = await use_case.execute()

    assert len(results) == 1
    assert results[0].program_name == "UNICO 2024 broken"
    assert results[0].file_url == UNICO_2024_XLSX_URL
    assert results[0].last_updated == 1734421875


async def test_missing_xlsx_anchor_skips_program_and_logs(capsys):
    url_map = {
        "UNICO 2023": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx",
        "UNICO 2024 no-xlsx": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO-no-xlsx.aspx",
    }
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = url_map

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_update.return_value = None

    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository)
    results = await use_case.execute()

    assert len(results) == 1
    assert results[0].program_name == "UNICO 2023"

    captured = capsys.readouterr()
    assert "[check-updated-programs][ERROR]" in captured.out
    assert "UNICO 2024 no-xlsx" in captured.out
    assert "missing xlsx anchor" in captured.out


async def test_non_2xx_response_skips_program_and_logs(capsys):
    url_map = {
        "UNICO 2023": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx",
        "UNICO 2024 error": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO-error.aspx",
    }
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = url_map

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_update.return_value = None

    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository)
    results = await use_case.execute()

    assert len(results) == 1
    assert results[0].program_name == "UNICO 2023"

    captured = capsys.readouterr()
    assert "[check-updated-programs][ERROR]" in captured.out
    assert "UNICO 2024 error" in captured.out
    assert "non-2xx" in captured.out