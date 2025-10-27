from infrastructure.repositories.kv_config_repository import KVConfigRepository
from unittest.mock import Mock, AsyncMock

MOCK_URL_MAP_JSON = """
{
    "UNICO 2023": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx",
    "UNICO 2024": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO.aspx"
}
"""

MOCK_URL_MAP = {
    "UNICO 2023": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx",
    "UNICO 2024": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO.aspx"
}

async def test_get_fiber_program_to_url_map():
    mock_env = Mock()
    mock_config = Mock()
    mock_config.get = AsyncMock(return_value=MOCK_URL_MAP_JSON)
    mock_env.CONFIG = mock_config

    repository = KVConfigRepository(mock_env)
    
    program_url_map = await repository.get_fiber_program_to_url_map()
    assert program_url_map == MOCK_URL_MAP