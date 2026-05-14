from infrastructure.repositories.kv_config_repository import KVConfigRepository
from unittest.mock import Mock, AsyncMock

MOCK_URL_MAP_OLD_JSON = """
{
    "UNICO 2023": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx",
    "UNICO 2024": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO.aspx"
}
"""

MOCK_URL_MAP_NEW_JSON = """
{
    "UNICO 2023": {"url": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx", "active": true},
    "UNICO 2024": {"url": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO.aspx", "active": true},
    "PEBA 2021": {"url": "https://avance.digital.gob.es/banda-ancha/ayudas/PEBA-2021/Paginas/convocatoria.aspx", "active": false}
}
"""

EXPECTED_ACTIVE_MAP = {
    "UNICO 2023": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx",
    "UNICO 2024": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO.aspx",
}


async def test_get_fiber_program_to_url_map_old_format():
    mock_env = Mock()
    mock_config = Mock()
    mock_config.get = AsyncMock(return_value=MOCK_URL_MAP_OLD_JSON)
    mock_env.CONFIG = mock_config

    repository = KVConfigRepository(mock_env)

    program_url_map = await repository.get_fiber_program_to_url_map()
    assert program_url_map == {
        "UNICO 2023": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx",
        "UNICO 2024": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO.aspx",
    }


async def test_get_fiber_program_to_url_map_new_format_filters_inactive():
    mock_env = Mock()
    mock_config = Mock()
    mock_config.get = AsyncMock(return_value=MOCK_URL_MAP_NEW_JSON)
    mock_env.CONFIG = mock_config

    repository = KVConfigRepository(mock_env)

    program_url_map = await repository.get_fiber_program_to_url_map()
    assert program_url_map == EXPECTED_ACTIVE_MAP
    assert "PEBA 2021" not in program_url_map
