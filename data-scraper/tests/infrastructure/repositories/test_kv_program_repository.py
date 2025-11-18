from infrastructure.repositories.kv_program_repository import KVProgramRepository
from unittest.mock import Mock, AsyncMock, patch
from domain.program_data import ProjectData, ProgramStatus
from infrastructure.entity.project_entity import ProjectEntity, ProgramStatus as ProgramStatusEntity
from datetime import date
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

    mock_config.put.assert_called_once_with(project.project, json.dumps(project_entity.to_dict()))

    