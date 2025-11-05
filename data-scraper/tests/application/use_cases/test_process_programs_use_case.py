from datetime import date
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

    async def bytes(self):
        return self.body.encode()

async def mock_fetch(url, **kwargs):
    return MockResponse(
        body="",
        status=200
    )

mock_workers = MagicMock()
mock_workers.fetch = AsyncMock(side_effect=mock_fetch)
mock_workers.Request = MockRequest
mock_workers.Response = MockResponse
sys.modules['workers'] = mock_workers

from application.use_cases.process_programs_use_case import ProcessProgramsUseCase
from domain.program_update_result import ProgramUpdateResult
from data.unico import UNICO_DATA, UNICO_EXPECTED_PROGRAM_DATA
from data.peba2020 import PEBA_2020_DATA, PEBA_2020_EXPECTED_PROGRAM_DATA
from data.peba2013 import PEBA_2013_DATA, PEBA_2013_EXPECTED_PROGRAM_DATA

async def test_execute_unico():
    mock_sheet_reader = Mock()
    mock_sheet_reader.read.return_value = UNICO_DATA

    use_case = ProcessProgramsUseCase(mock_sheet_reader)

    result = ProgramUpdateResult(
        file_url="",
        program_name="",
        last_updated=0
    )
    
    data = await use_case.execute(result)
    assert data.projects == UNICO_EXPECTED_PROGRAM_DATA.projects

async def test_execute_peba_2020_2021():
    mock_sheet_reader = Mock()
    mock_sheet_reader.read.return_value = PEBA_2020_DATA

    use_case = ProcessProgramsUseCase(mock_sheet_reader)

    result = ProgramUpdateResult(
        file_url="",
        program_name="",
        last_updated=0
    )
    
    data = await use_case.execute(result)
    assert data.projects == PEBA_2020_EXPECTED_PROGRAM_DATA.projects

async def test_execute_peba_2013():
    mock_sheet_reader = Mock()
    mock_sheet_reader.read.return_value = PEBA_2013_DATA

    use_case = ProcessProgramsUseCase(mock_sheet_reader)

    result = ProgramUpdateResult(
        file_url="",
        program_name="",
        last_updated=0
    )
    
    data = await use_case.execute(result)
    assert data.projects == PEBA_2013_EXPECTED_PROGRAM_DATA.projects