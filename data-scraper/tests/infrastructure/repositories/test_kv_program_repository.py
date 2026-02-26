from infrastructure.repositories.kv_program_repository import KVProgramRepository
from unittest.mock import Mock, AsyncMock, patch
from domain.program_data import ProjectData, ProgramStatus
from domain.projects_status import ProjectsStatus
from infrastructure.entity.project_entity import ProjectEntity, ProgramStatus as ProgramStatusEntity
from datetime import date, datetime, timezone
import pytest
import json

async def test_get_last_update():
    mock_env = Mock()
    mock_config = Mock()
    mock_config.get = AsyncMock(return_value="1734421875")
    mock_env.PROJECTS = mock_config

    repository = KVProgramRepository(mock_env)

    last_update = await repository.get_last_update("UNICO 2024")
    assert last_update == 1734421875

async def test_get_last_update_returns_none_if_no_result():
    mock_env = Mock()
    mock_config = Mock()
    mock_config.get = AsyncMock(return_value="")
    mock_env.PROJECTS = mock_config

    repository = KVProgramRepository(mock_env)

    last_update = await repository.get_last_update("UNICO 2024")
    assert last_update == None

async def test_get_last_update_throws_valueerror_when_not_a_number():
    mock_env = Mock()
    mock_config = Mock()
    mock_config.get = AsyncMock(return_value="Foo")
    mock_env.PROJECTS = mock_config

    repository = KVProgramRepository(mock_env)

    with pytest.raises(ValueError) as e_info:
        await repository.get_last_update("UNICO 2024")

@patch("infrastructure.repositories.kv_program_repository.to_entity")
async def test_put_project_puts_project_as_json(to_entity_mock):
    mock_env = Mock()
    mock_config = Mock()
    mock_config.get = AsyncMock(return_value="Foo")
    mock_config.put = AsyncMock()
    mock_env.PROJECTS = mock_config


    repository = KVProgramRepository(mock_env)

    project = ProjectData(
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
    project_entity = ProjectEntity(
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

    to_entity_mock.return_value = project_entity

    await repository.put_project(project)

    mock_config.put.assert_called_once_with(project.project, json.dumps(project_entity.to_dict(), ensure_ascii=False))

@patch("infrastructure.repositories.kv_program_repository.datetime")
@patch("infrastructure.repositories.kv_program_repository.project_status_to_entity")
@patch("infrastructure.repositories.kv_program_repository.projects_status_to_dict")
async def test_put_projects_status_puts_status_as_json(projects_status_to_dict_mock, project_status_to_entity_mock, datetime_mock):
    mock_env = Mock()
    mock_config = Mock()
    mock_config.put = AsyncMock()
    mock_env.PROJECTS = mock_config

    repository = KVProgramRepository(mock_env)

    projects_status = {
        "TSI-061400-2019-0023": {"status": "in_progress", "deadline": "25/02/2026"},
        "TSI-061400-2019-0024": {"status": "finished", "deadline": "31/12/2024"}
    }
    projects_status_entity = Mock()
    status_dict = {
        "TSI-061400-2019-0023": {"status": "in_progress", "deadline": "25/02/2026"},
        "TSI-061400-2019-0024": {"status": "finished", "deadline": "31/12/2024"}
    }

    project_status_to_entity_mock.return_value = projects_status_entity
    projects_status_to_dict_mock.return_value = status_dict

    fixed_datetime = datetime(2026, 2, 25, 20, 51, 57, tzinfo=timezone.utc)
    datetime_mock.now.return_value = fixed_datetime

    await repository.put_projects_status(projects_status)

    assert mock_config.put.call_count == 2
    first_call = mock_config.put.call_args_list[0]
    assert first_call[0][0] == "projects-status"
    assert first_call[0][1] == json.dumps(status_dict)

    second_call = mock_config.put.call_args_list[1]
    assert second_call[0][0] == "projects-status:last-modified"
    assert second_call[0][1] == "Wed, 25 Feb 2026 20:51:57 GMT"

@patch("infrastructure.repositories.kv_program_repository.ProjectEntity")
@patch("infrastructure.repositories.kv_program_repository.from_entity")
async def test_find_projects_returns_list_of_projects(from_entity_mock, project_entity_mock):
    mock_env = Mock()
    mock_config = Mock()

    mock_key_item_1 = Mock()
    mock_key_item_1.name = "TSI-061400-2021-0001"

    mock_key_item_2 = Mock()
    mock_key_item_2.name = "TSI-061400-2021-0002"

    mock_list_result = Mock()
    mock_list_result.keys = [mock_key_item_1, mock_key_item_2]
    mock_list_result.list_complete = True

    project_entity_1 = ProjectEntity(
        status=ProgramStatusEntity.FINISHED,
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
        eligible_budget=1000,
        funding=800,
        subsidy=None,
        loan=None,
        funding_percentage=80,
        technology="FTTH",
        deadline=date(2024, 12, 31),
    )

    project_entity_2 = ProjectEntity(
        status=ProgramStatusEntity.IN_PROGRESS,
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
        eligible_budget=2000,
        funding=1600,
        subsidy=None,
        loan=None,
        funding_percentage=80,
        technology="FTTH",
        deadline=date(2025, 12, 31),
    )

    mock_config.list = AsyncMock(return_value=mock_list_result)
    mock_config.get = AsyncMock(side_effect=[
        json.dumps(project_entity_1.to_dict()),
        json.dumps(project_entity_2.to_dict())
    ])
    mock_env.PROJECTS = mock_config

    project_entity_mock.from_dict = Mock(side_effect=[project_entity_1, project_entity_2])

    repository = KVProgramRepository(mock_env)

    project_1 = ProjectData(
        project="TSI-061400-2021-0001",
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
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
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
        status=ProgramStatus.IN_PROGRESS,
        eligible_budget=2000,
        funding=1600,
        subsidy=None,
        loan=None,
        funding_percentage=80,
        technology="FTTH",
        deadline=date(2025, 12, 31),
    )

    from_entity_mock.side_effect = [project_1, project_2]

    result = await repository.find_projects()

    assert len(result) == 2
    assert result[0] == project_1
    assert result[1] == project_2
    mock_config.list.assert_called_once_with(prefix="TSI-", cursor=None)
    assert mock_config.get.call_count == 2

@patch("infrastructure.repositories.kv_program_repository.ProjectEntity")
@patch("infrastructure.repositories.kv_program_repository.from_entity")
async def test_find_projects_handles_pagination(from_entity_mock, project_entity_mock):
    mock_env = Mock()
    mock_config = Mock()

    mock_key_item_1 = Mock()
    mock_key_item_1.name = "TSI-061400-2021-0001"

    mock_key_item_2 = Mock()
    mock_key_item_2.name = "TSI-061400-2021-0002"

    mock_key_item_3 = Mock()
    mock_key_item_3.name = "TSI-061400-2021-0003"

    mock_list_result_1 = Mock()
    mock_list_result_1.keys = [mock_key_item_1, mock_key_item_2]
    mock_list_result_1.list_complete = False
    mock_list_result_1.cursor = "next_cursor"

    mock_list_result_2 = Mock()
    mock_list_result_2.keys = [mock_key_item_3]
    mock_list_result_2.list_complete = True

    project_entity_1 = ProjectEntity(
        status=ProgramStatusEntity.FINISHED,
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
        eligible_budget=1000,
        funding=800,
        subsidy=None,
        loan=None,
        funding_percentage=80,
        technology="FTTH",
        deadline=date(2024, 12, 31),
    )

    project_entity_2 = ProjectEntity(
        status=ProgramStatusEntity.IN_PROGRESS,
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
        eligible_budget=2000,
        funding=1600,
        subsidy=None,
        loan=None,
        funding_percentage=80,
        technology="FTTH",
        deadline=date(2025, 12, 31),
    )

    project_entity_3 = ProjectEntity(
        status=ProgramStatusEntity.FINISHED,
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
        eligible_budget=3000,
        funding=2400,
        subsidy=None,
        loan=None,
        funding_percentage=80,
        technology="FTTH",
        deadline=date(2026, 12, 31),
    )

    mock_config.list = AsyncMock(side_effect=[mock_list_result_1, mock_list_result_2])
    mock_config.get = AsyncMock(side_effect=[
        json.dumps(project_entity_1.to_dict()),
        json.dumps(project_entity_2.to_dict()),
        json.dumps(project_entity_3.to_dict())
    ])
    mock_env.PROJECTS = mock_config

    project_entity_mock.from_dict = Mock(side_effect=[project_entity_1, project_entity_2, project_entity_3])

    repository = KVProgramRepository(mock_env)

    project_1 = ProjectData(
        project="TSI-061400-2021-0001",
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
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
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
        status=ProgramStatus.IN_PROGRESS,
        eligible_budget=2000,
        funding=1600,
        subsidy=None,
        loan=None,
        funding_percentage=80,
        technology="FTTH",
        deadline=date(2025, 12, 31),
    )
    project_3 = ProjectData(
        project="TSI-061400-2021-0003",
        grantee="TELEFONICA DE ESPAÑA, S.A.",
        program_name="UNICO 2021",
        status=ProgramStatus.FINISHED,
        eligible_budget=3000,
        funding=2400,
        subsidy=None,
        loan=None,
        funding_percentage=80,
        technology="FTTH",
        deadline=date(2026, 12, 31),
    )

    from_entity_mock.side_effect = [project_1, project_2, project_3]

    result = await repository.find_projects()

    assert len(result) == 3
    assert result[0] == project_1
    assert result[1] == project_2
    assert result[2] == project_3
    assert mock_config.list.call_count == 2
    mock_config.list.assert_any_call(prefix="TSI-", cursor=None)
    mock_config.list.assert_any_call(prefix="TSI-", cursor="next_cursor")
    assert mock_config.get.call_count == 3


async def test_put_aggregated_validates_project_belongs_to_hexagon():
    mock_env = Mock()
    mock_bucket = Mock()
    mock_env.BUCKET_GEO = mock_bucket

    # Mock aggregated.json response
    aggregated_data = [
        {
            "h3Index": "852834b7fffffff",
            "totalCount": 2,
            "counts": {
                "TELEFONICA": {
                    "UNICO 2021": {
                        "total": 0,
                        "statuses": {}
                    }
                }
            }
        }
    ]
    
    # Mock hexagons_projects.json response with point counts
    hexagons_projects = {
        "852834b7fffffff": {
            "TSI-061400-2021-0001": 3,
            "TSI-061400-2021-0002": 5
        }
    }

    mock_aggregated = AsyncMock()
    mock_aggregated.text = AsyncMock(return_value=json.dumps(aggregated_data))
    
    mock_hexagons = AsyncMock()
    mock_hexagons.text = AsyncMock(return_value=json.dumps(hexagons_projects))
    
    mock_bucket.get = AsyncMock(side_effect=[mock_aggregated, mock_hexagons])
    mock_bucket.put = AsyncMock()

    repository = KVProgramRepository(mock_env)

    # Create projects - one in hexagon, one NOT in hexagon
    project_1 = ProjectData(
        project="TSI-061400-2021-0001",
        grantee="TELEFONICA",
        program_name="UNICO 2021",
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
        project="TSI-061400-2021-0999",  # Not in hexagon
        grantee="TELEFONICA",
        program_name="UNICO 2021",
        status=ProgramStatus.IN_PROGRESS,
        eligible_budget=2000,
        funding=1600,
        subsidy=None,
        loan=None,
        funding_percentage=80,
        technology="FTTH",
        deadline=date(2025, 12, 31),
    )

    await repository.put_aggregated([project_1, project_2])

    # Verify bucket.get was called twice (aggregated.json and hexagons_projects.json)
    assert mock_bucket.get.call_count == 2
    
    # Verify put was called once with updated data
    mock_bucket.put.assert_called_once()
    
    # Check that only project_1 was counted (project_2 is not in hexagon)
    call_args = mock_bucket.put.call_args
    updated_data = json.loads(call_args[0][1])
    
    assert updated_data[0]["counts"]["TELEFONICA"]["UNICO 2021"]["total"] == 3
    assert "finished" in updated_data[0]["counts"]["TELEFONICA"]["UNICO 2021"]["statuses"]
    assert updated_data[0]["counts"]["TELEFONICA"]["UNICO 2021"]["statuses"]["finished"] == 3
