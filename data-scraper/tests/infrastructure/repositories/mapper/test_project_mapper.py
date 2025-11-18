from infrastructure.repositories.mapper.project_mapper import to_entity
from domain.program_data import ProjectData, ProgramStatus
from infrastructure.entity.project_entity import ProjectEntity, ProgramStatus as ProgramStatusEntity
from datetime import date

def test_to_entity_converts_to_project_entity():
    project_data = ProjectData(
        project="TSI-061400-2021-0041",
        status=ProgramStatus.FINISHED,
        eligible_budget=5228554,
        funding=4147227,
        subsidy=None,
        loan=None,
        funding_percentage=79,
        technology="FTTH",
        deadline=date(2024, 12, 31),
    )
    expected_project_entity = ProjectEntity(
        status=ProgramStatusEntity.FINISHED,
        eligible_budget=5228554,
        funding=4147227,
        subsidy=None,
        loan=None,
        funding_percentage=79,
        technology="FTTH",
        deadline=date(2024, 12, 31),
    )

    project_entity = to_entity(project_data)

    assert project_entity == expected_project_entity