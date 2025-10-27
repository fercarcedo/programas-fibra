from application.use_cases.process_programs_use_case import ProcessProgramsUseCase
from unittest.mock import MagicMock
from domain.program_update_result import ProgramUpdateResult

async def test_execute():
    mock_sheet_reader = MagicMock()

    use_case = ProcessProgramsUseCase(mock_sheet_reader)

    result = ProgramUpdateResult(
        file_url="",
        program_name="",
        last_updated=0
    )
    await use_case.execute(result)