from infrastructure.repositories.kv_program_repository import KVProgramRepository
from unittest.mock import Mock, AsyncMock
import pytest

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