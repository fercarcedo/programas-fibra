from infrastructure.repositories.mapper.project_mapper import to_entity, from_entity
from domain.program_data import ProjectData, ProgramStatus
from infrastructure.entity.project_entity import ProjectEntity, ProgramStatus as ProgramStatusEntity
from datetime import date

def test_to_entity_converts_to_project_entity():
    project_data = ProjectData(
        project="TSI-061400-2021-0041",
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
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
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
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

def test_from_entity_converts_to_project_data():
    project_entity = ProjectEntity(
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
        status=ProgramStatusEntity.IN_PROGRESS,
        eligible_budget=1000000,
        funding=800000,
        subsidy=200000,
        loan=None,
        funding_percentage=80,
        technology="FTTH",
        deadline=date(2025, 6, 30),
    )
    project_code = "TSI-061400-2021-0042"

    expected_project_data = ProjectData(
        project=project_code,
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
        status=ProgramStatus.IN_PROGRESS,
        eligible_budget=1000000,
        funding=800000,
        subsidy=200000,
        loan=None,
        funding_percentage=80,
        technology="FTTH",
        deadline=date(2025, 6, 30),
    )

    project_data = from_entity(project_entity, project_code)

    assert project_data == expected_project_data

def test_from_entity_handles_none_deadline():
    project_entity = ProjectEntity(
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
        status=ProgramStatusEntity.CANCELLED,
        eligible_budget=5000000,
        funding=0,
        subsidy=None,
        loan=None,
        funding_percentage=0,
        technology="FTTH",
        deadline=None,
    )
    project_code = "TSI-061400-2021-0043"

    expected_project_data = ProjectData(
        project=project_code,
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
        status=ProgramStatus.CANCELLED,
        eligible_budget=5000000,
        funding=0,
        subsidy=None,
        loan=None,
        funding_percentage=0,
        technology="FTTH",
        deadline=None,
    )

    project_data = from_entity(project_entity, project_code)

    assert project_data == expected_project_data

def test_from_entity_with_all_statuses():
    for status in [ProgramStatusEntity.FINISHED, ProgramStatusEntity.IN_PROGRESS, ProgramStatusEntity.CANCELLED]:
        project_entity = ProjectEntity(
            grantee="TELEFONICA DE ESPAÑA, S.A.",
            program_name="UNICO 2021",
            status=status,
            eligible_budget=2000000,
            funding=1500000,
            subsidy=None,
            loan=500000,
            funding_percentage=75,
            technology="FTTH",
            deadline=date(2024, 12, 31),
        )
        project_code = "TSI-061400-2021-0044"

        project_data = from_entity(project_entity, project_code)

        assert project_data.status == ProgramStatus[status.name]
        assert project_data.project == project_code
