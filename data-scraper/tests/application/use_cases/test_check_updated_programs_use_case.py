from data.page_html import UNICO_2023_PAGE, UNICO_2024_PAGE, PAGE_WITHOUT_COL_CONTENIDO_WITH_XLSX, PAGE_WITHOUT_COL_CONTENIDO_WITHOUT_XLSX, UNICO_2021_PAGE_NEW_CMS, PEBA_2021_PAGE_NEW_CMS
from unittest.mock import MagicMock, AsyncMock, patch

from application.use_cases.check_updated_programs_use_case import CheckUpdatedProgramsUseCase
from domain.program_update_result import ProgramUpdateResult
from domain.renderers.page_renderer import PageRenderer
from domain.repositories.config_repository import ConfigRepository
from domain.repositories.program_repository import ProgramRepository
from domain.fetchers.xlsx_fetcher import XlsxFetcher

UNICO_2024_XLSX_URL = "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Documents/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2024.xlsx"
UNICO_2024_DIGEST = "ABCDEF1234567890UNICO2024"

_PAGE_HTML_MAP = {
    "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx": UNICO_2023_PAGE,
    "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO.aspx": UNICO_2024_PAGE,
    "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO-broken.aspx": PAGE_WITHOUT_COL_CONTENIDO_WITH_XLSX,
    "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO-no-xlsx.aspx": PAGE_WITHOUT_COL_CONTENIDO_WITHOUT_XLSX,
    "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO-error.aspx": RuntimeError("IA renderer error"),
    "https://digital.gob.es/telecomunicaciones-infraestructuras-digitales/areas-interes/banda-ancha/ayudas-publicas/ayudas-publicas-unico/convocatoria-2021-unico": UNICO_2021_PAGE_NEW_CMS,
    "https://digital.gob.es/telecomunicaciones-infraestructuras-digitales/areas-interes/banda-ancha/ayudas-publicas/banda-ancha-generacion-2013-2021/convocatoria-2021": PEBA_2021_PAGE_NEW_CMS,
}

PEBA_2021_NEW_CMS_XLSX_URL = (
    "https://digital.gob.es/content/dam/portal-mtdfp/avance-digital/telecomunicacion-e-infraestructuras-digitales/"
    "areas_interes/banda-ancha/banda-ancha/ayudas/ayudas-publicas-pebang/Relacion-proyectos-aprobados-2021.xlsx"
)

class MockPageRenderer(PageRenderer):
    async def render(self, url: str) -> str:
        result = _PAGE_HTML_MAP[url]
        if isinstance(result, Exception):
            raise result
        return result

MOCK_URL_MAP = {
    "UNICO 2023": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx",
    "UNICO 2024": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO.aspx",
}


def _make_xlsx_fetcher(digest_for_url: dict[str, str | None]) -> MagicMock:
    fetcher = MagicMock(spec=XlsxFetcher)
    async def get_latest_digest(page_url, xlsx_url):
        return digest_for_url.get(xlsx_url)
    fetcher.get_latest_digest = AsyncMock(side_effect=get_latest_digest)
    return fetcher


@patch("application.use_cases.check_updated_programs_use_case.time")
async def test_execute(mock_time):
    mock_time.time.return_value = 1747000000

    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = MOCK_URL_MAP

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_update.return_value = None
    mock_program_repository.get_last_xlsx_digest.return_value = None

    xlsx_fetcher = _make_xlsx_fetcher({UNICO_2024_XLSX_URL: UNICO_2024_DIGEST})

    expected_updated_projects = [
        ProgramUpdateResult(
            file_url="https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Documents/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2023_01_08_2025.xlsx",
            page_url="https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx",
            program_name="UNICO 2023",
            last_updated=1754006400,
        ),
        ProgramUpdateResult(
            file_url=UNICO_2024_XLSX_URL,
            page_url="https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO.aspx",
            program_name="UNICO 2024",
            last_updated=1747000000,
        ),
    ]
    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository, MockPageRenderer(), xlsx_fetcher)

    result = await use_case.execute()

    assert result.updated == expected_updated_projects
    assert result.skipped == []


@patch("application.use_cases.check_updated_programs_use_case.time")
async def test_execute_with_some_not_updated_projects(mock_time):
    mock_time.time.return_value = 1747000000

    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = MOCK_URL_MAP

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_update.return_value = 1734421875
    mock_program_repository.get_last_xlsx_digest.return_value = UNICO_2024_DIGEST

    xlsx_fetcher = _make_xlsx_fetcher({UNICO_2024_XLSX_URL: UNICO_2024_DIGEST})

    expected_updated_projects = [
        ProgramUpdateResult(
            file_url="https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Documents/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2023_01_08_2025.xlsx",
            page_url="https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx",
            program_name="UNICO 2023",
            last_updated=1754006400,
        )
    ]
    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository, MockPageRenderer(), xlsx_fetcher)

    result = await use_case.execute()

    assert result.updated == expected_updated_projects
    assert result.skipped == []


@patch("application.use_cases.check_updated_programs_use_case.time")
async def test_missing_col_contenido_falls_back_to_cdx_digest(mock_time):
    mock_time.time.return_value = 1747000000

    url_map = {
        "UNICO 2024 broken": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO-broken.aspx",
    }
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = url_map

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_update.return_value = None
    mock_program_repository.get_last_xlsx_digest.return_value = None

    xlsx_fetcher = _make_xlsx_fetcher({UNICO_2024_XLSX_URL: "FRESHDIGEST"})

    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository, MockPageRenderer(), xlsx_fetcher)
    result = await use_case.execute()

    assert len(result.updated) == 1
    assert result.updated[0].program_name == "UNICO 2024 broken"
    assert result.updated[0].file_url == UNICO_2024_XLSX_URL
    assert result.updated[0].page_url == "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO-broken.aspx"
    assert result.updated[0].last_updated == 1747000000
    assert result.skipped == []


async def test_missing_col_contenido_skips_when_digest_unchanged():
    url_map = {
        "UNICO 2024 broken": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO-broken.aspx",
    }
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = url_map

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_xlsx_digest.return_value = "SAMEDIGEST"

    xlsx_fetcher = _make_xlsx_fetcher({UNICO_2024_XLSX_URL: "SAMEDIGEST"})

    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository, MockPageRenderer(), xlsx_fetcher)
    result = await use_case.execute()

    assert result.updated == []
    assert result.skipped == []


async def test_missing_col_contenido_skips_when_digest_fetch_fails():
    url_map = {
        "UNICO 2024 broken": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO-broken.aspx",
    }
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = url_map

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_xlsx_digest.return_value = None

    xlsx_fetcher = _make_xlsx_fetcher({})

    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository, MockPageRenderer(), xlsx_fetcher)
    result = await use_case.execute()

    assert result.updated == []
    assert len(result.skipped) == 1
    assert "could not fetch xlsx digest" in result.skipped[0].reason


async def test_missing_xlsx_anchor_skips_program():
    url_map = {
        "UNICO 2023": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx",
        "UNICO 2024 no-xlsx": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO-no-xlsx.aspx",
    }
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = url_map

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_update.return_value = None
    mock_program_repository.get_last_xlsx_digest.return_value = None

    xlsx_fetcher = _make_xlsx_fetcher({})

    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository, MockPageRenderer(), xlsx_fetcher)
    result = await use_case.execute()

    assert len(result.updated) == 1
    assert result.updated[0].program_name == "UNICO 2023"

    assert len(result.skipped) == 1
    assert result.skipped[0].program_name == "UNICO 2024 no-xlsx"
    assert result.skipped[0].reason == "missing xlsx anchor"


async def test_parses_new_cms_page_without_col_contenido_or_file_xlsx_class():
    url_map = {
        "UNICO 2021": "https://digital.gob.es/telecomunicaciones-infraestructuras-digitales/areas-interes/banda-ancha/ayudas-publicas/ayudas-publicas-unico/convocatoria-2021-unico",
    }
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = url_map

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_update.return_value = None
    mock_program_repository.get_last_xlsx_digest.return_value = None

    xlsx_fetcher = _make_xlsx_fetcher({})

    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository, MockPageRenderer(), xlsx_fetcher)
    result = await use_case.execute()

    assert result.skipped == []
    assert len(result.updated) == 1
    updated = result.updated[0]
    assert updated.program_name == "UNICO 2021"
    assert updated.file_url == (
        "https://digital.gob.es/content/dam/portal-mtdfp/avance-digital/telecomunicacion-e-infraestructuras-digitales/"
        "areas_interes/banda-ancha/banda-ancha/ayudas/unico-5g/documents/"
        "Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2021_29-04-2026-2.xlsx"
    )
    # 29/04/2026, not the decoy "Fecha de actualización" found in the page footer.
    assert updated.last_updated == 1777420800


async def test_parses_new_cms_peba_page_falls_back_to_digest_when_no_date():
    url_map = {
        "PEBA 2021": "https://digital.gob.es/telecomunicaciones-infraestructuras-digitales/areas-interes/banda-ancha/ayudas-publicas/banda-ancha-generacion-2013-2021/convocatoria-2021",
    }
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = url_map

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_xlsx_digest.return_value = "OLDDIGEST"

    xlsx_fetcher = _make_xlsx_fetcher({PEBA_2021_NEW_CMS_XLSX_URL: "NEWDIGEST"})

    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository, MockPageRenderer(), xlsx_fetcher)
    result = await use_case.execute()

    assert result.skipped == []
    assert len(result.updated) == 1
    updated = result.updated[0]
    assert updated.program_name == "PEBA 2021"
    assert updated.file_url == PEBA_2021_NEW_CMS_XLSX_URL


async def test_renderer_error_skips_program():
    url_map = {
        "UNICO 2023": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2023-UNICO.aspx",
        "UNICO 2024 error": "https://avance.digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Paginas/convocatoria-2024-UNICO-error.aspx",
    }
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = url_map

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_update.return_value = None
    mock_program_repository.get_last_xlsx_digest.return_value = None

    xlsx_fetcher = _make_xlsx_fetcher({})

    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository, MockPageRenderer(), xlsx_fetcher)
    result = await use_case.execute()

    assert len(result.updated) == 1
    assert result.updated[0].program_name == "UNICO 2023"

    assert len(result.skipped) == 1
    assert result.skipped[0].program_name == "UNICO 2024 error"
    assert "unhandled error" in result.skipped[0].reason
