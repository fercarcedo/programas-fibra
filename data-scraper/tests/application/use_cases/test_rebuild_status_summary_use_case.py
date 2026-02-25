from unittest.mock import MagicMock, AsyncMock
from application.use_cases.rebuild_status_summary_use_case import RebuildStatusSummaryUseCase
from domain.repositories.program_repository import ProgramRepository
from domain.program_data import ProjectData, ProgramStatus
from domain.projects_status import ProjectStatusInfo, ProjectsStatus
from datetime import date

async def test_execute_builds_and_stores_projects_status():
    mock_program_repository = MagicMock(spec=ProgramRepository)
    
    project_1 = ProjectData(
        project="TSI-061400-2021-0001",
        status=ProgramStatus.FINISHED,
        eligible_budget=1000,
        funding=800,
        subsidy=None,
        loan=None,
        funding_percentage=80,
        technology="FTTH",
        deadline=date(2024, 12, 31),
    )
    project_2 = ProjectData(
        project="TSI-061400-2021-0002",
        status=ProgramStatus.IN_PROGRESS,
        eligible_budget=2000,
        funding=1600,
        subsidy=None,
        loan=None,
        funding_percentage=80,
        technology="FTTH",
        deadline=date(2025, 12, 31),
    )
    
    mock_program_repository.find_projects = AsyncMock(return_value=[project_1, project_2])
    mock_program_repository.put_projects_status = AsyncMock()
    
    use_case = RebuildStatusSummaryUseCase(mock_program_repository)
    
    await use_case.execute()
    
    mock_program_repository.find_projects.assert_called_once()
    mock_program_repository.put_projects_status.assert_called_once()
    
    call_args = mock_program_repository.put_projects_status.call_args[0][0]
    assert len(call_args) == 2
    assert call_args["TSI-061400-2021-0001"].status == ProgramStatus.FINISHED
    assert call_args["TSI-061400-2021-0001"].deadline == date(2024, 12, 31)
    assert call_args["TSI-061400-2021-0002"].status == ProgramStatus.IN_PROGRESS
    assert call_args["TSI-061400-2021-0002"].deadline == date(2025, 12, 31)

async def test_execute_handles_empty_projects_list():
    mock_program_repository = MagicMock(spec=ProgramRepository)
    
    mock_program_repository.find_projects = AsyncMock(return_value=[])
    mock_program_repository.put_projects_status = AsyncMock()
    
    use_case = RebuildStatusSummaryUseCase(mock_program_repository)
    
    await use_case.execute()
    
    mock_program_repository.find_projects.assert_called_once()
    mock_program_repository.put_projects_status.assert_called_once()
    
    call_args = mock_program_repository.put_projects_status.call_args[0][0]
    assert len(call_args) == 0
