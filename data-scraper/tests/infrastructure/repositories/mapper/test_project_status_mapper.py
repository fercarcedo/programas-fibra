from infrastructure.repositories.mapper.project_status_mapper import to_entity
from domain.projects_status import ProjectsStatus, ProjectStatusInfo
from domain.program_data import ProgramStatus
from infrastructure.entity.projects_status_entity import ProgramStatusEntity, ProjectStatusInfoEntity
from datetime import date

def test_to_entity_converts_projects_status_to_entity():
    projects_status: ProjectsStatus = {
        "TSI-061400-2021-0001": ProjectStatusInfo(
            status=ProgramStatus.FINISHED,
            deadline=date(2024, 12, 31),
        ),
        "TSI-061400-2021-0002": ProjectStatusInfo(
            status=ProgramStatus.IN_PROGRESS,
            deadline=date(2025, 6, 30),
        ),
    }
    
    entity_map = to_entity(projects_status)
    
    assert len(entity_map) == 2
    assert "TSI-061400-2021-0001" in entity_map
    assert "TSI-061400-2021-0002" in entity_map
    
    assert entity_map["TSI-061400-2021-0001"].status == ProgramStatusEntity.FINISHED
    assert entity_map["TSI-061400-2021-0001"].deadline == date(2024, 12, 31)
    
    assert entity_map["TSI-061400-2021-0002"].status == ProgramStatusEntity.IN_PROGRESS
    assert entity_map["TSI-061400-2021-0002"].deadline == date(2025, 6, 30)

def test_to_entity_handles_empty_projects_status():
    projects_status: ProjectsStatus = {}
    
    entity_map = to_entity(projects_status)
    
    assert len(entity_map) == 0

def test_to_entity_converts_all_status_types():
    projects_status: ProjectsStatus = {
        "TSI-061400-2021-0001": ProjectStatusInfo(
            status=ProgramStatus.FINISHED,
            deadline=date(2024, 12, 31),
        ),
        "TSI-061400-2021-0002": ProjectStatusInfo(
            status=ProgramStatus.IN_PROGRESS,
            deadline=date(2025, 6, 30),
        ),
        "TSI-061400-2021-0003": ProjectStatusInfo(
            status=ProgramStatus.CANCELLED,
            deadline=date(2023, 12, 31),
        ),
    }
    
    entity_map = to_entity(projects_status)
    
    assert len(entity_map) == 3
    assert entity_map["TSI-061400-2021-0001"].status == ProgramStatusEntity.FINISHED
    assert entity_map["TSI-061400-2021-0002"].status == ProgramStatusEntity.IN_PROGRESS
    assert entity_map["TSI-061400-2021-0003"].status == ProgramStatusEntity.CANCELLED

def test_to_entity_handles_none_deadline():
    projects_status: ProjectsStatus = {
        "TSI-061400-2021-0001": ProjectStatusInfo(
            status=ProgramStatus.CANCELLED,
            deadline=None,
        ),
    }
    
    entity_map = to_entity(projects_status)
    
    assert len(entity_map) == 1
    assert entity_map["TSI-061400-2021-0001"].status == ProgramStatusEntity.CANCELLED
    assert entity_map["TSI-061400-2021-0001"].deadline is None

def test_to_entity_returns_correct_entity_type():
    projects_status: ProjectsStatus = {
        "TSI-061400-2021-0001": ProjectStatusInfo(
            status=ProgramStatus.FINISHED,
            deadline=date(2024, 12, 31),
        ),
    }
    
    entity_map = to_entity(projects_status)
    
    assert isinstance(entity_map, dict)
    assert isinstance(entity_map["TSI-061400-2021-0001"], ProjectStatusInfoEntity)
