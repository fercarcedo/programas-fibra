from data.page_html import UNICO_2023_PAGE, UNICO_2024_PAGE
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
    elif isinstance(url, MockRequest):
        if url.url == "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Documents/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2023_01_08_2025.xlsx":
            return MockResponse(
                body=None,
                status=200,
                headers={
                    'last-modified': 'Fri, 01 Aug 2025 09:09:10 GMT'
                }
            )
        elif url.url == "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Documents/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2024.xlsx":
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