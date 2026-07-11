from data.page_html import UNICO_2021_PAGE, PEBA_2021_PAGE, PAGE_WITHOUT_MAIN_WITH_XLSX, PAGE_WITHOUT_MAIN_WITHOUT_XLSX, PAGE_WITH_DECOYS_OUTSIDE_CMP_TEXT
from unittest.mock import MagicMock, AsyncMock, patch

from application.use_cases.check_updated_programs_use_case import CheckUpdatedProgramsUseCase
from domain.program_update_result import ProgramUpdateResult
from domain.renderers.page_renderer import PageRenderer
from domain.repositories.config_repository import ConfigRepository
from domain.repositories.program_repository import ProgramRepository
from domain.fetchers.xlsx_fetcher import XlsxFetcher

UNICO_2021_URL = "https://digital.gob.es/telecomunicaciones-infraestructuras-digitales/areas-interes/banda-ancha/ayudas-publicas/ayudas-publicas-unico/convocatoria-2021-unico"
PEBA_2021_URL = "https://digital.gob.es/telecomunicaciones-infraestructuras-digitales/areas-interes/banda-ancha/ayudas-publicas/banda-ancha-generacion-2013-2021/convocatoria-2021"
BROKEN_URL = "https://digital.gob.es/telecomunicaciones-infraestructuras-digitales/areas-interes/banda-ancha/ayudas-publicas/broken"
NO_XLSX_URL = "https://digital.gob.es/telecomunicaciones-infraestructuras-digitales/areas-interes/banda-ancha/ayudas-publicas/no-xlsx"
ERROR_URL = "https://digital.gob.es/telecomunicaciones-infraestructuras-digitales/areas-interes/banda-ancha/ayudas-publicas/error"
DECOYS_URL = "https://digital.gob.es/telecomunicaciones-infraestructuras-digitales/areas-interes/banda-ancha/ayudas-publicas/decoys"

UNICO_2021_XLSX_URL = (
    "https://digital.gob.es/content/dam/portal-mtdfp/avance-digital/telecomunicacion-e-infraestructuras-digitales/"
    "areas_interes/banda-ancha/banda-ancha/ayudas/unico-5g/documents/"
    "Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2021_29-04-2026-2.xlsx"
)
PEBA_2021_XLSX_URL = (
    "https://digital.gob.es/content/dam/portal-mtdfp/avance-digital/telecomunicacion-e-infraestructuras-digitales/"
    "areas_interes/banda-ancha/banda-ancha/ayudas/ayudas-publicas-pebang/Relacion-proyectos-aprobados-2021.xlsx"
)
BROKEN_PAGE_XLSX_URL = "https://digital.gob.es/banda-ancha/ayudas/UNICO-Banda-Ancha/Documents/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2024.xlsx"

# UNICO_2021_PAGE has "Fecha de actualización: 29/04/2026" -> 1777420800.
UNICO_2021_LAST_UPDATED = 1777420800

_PAGE_HTML_MAP = {
    UNICO_2021_URL: UNICO_2021_PAGE,
    PEBA_2021_URL: PEBA_2021_PAGE,
    BROKEN_URL: PAGE_WITHOUT_MAIN_WITH_XLSX,
    NO_XLSX_URL: PAGE_WITHOUT_MAIN_WITHOUT_XLSX,
    ERROR_URL: RuntimeError("IA renderer error"),
    DECOYS_URL: PAGE_WITH_DECOYS_OUTSIDE_CMP_TEXT,
}

class MockPageRenderer(PageRenderer):
    async def render(self, url: str) -> str:
        result = _PAGE_HTML_MAP[url]
        if isinstance(result, Exception):
            raise result
        return result

MOCK_URL_MAP = {
    "UNICO 2021": UNICO_2021_URL,
    "PEBA 2021": PEBA_2021_URL,
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

    xlsx_fetcher = _make_xlsx_fetcher({PEBA_2021_XLSX_URL: "PEBA_DIGEST"})

    expected_updated_projects = [
        ProgramUpdateResult(
            file_url=UNICO_2021_XLSX_URL,
            page_url=UNICO_2021_URL,
            program_name="UNICO 2021",
            last_updated=UNICO_2021_LAST_UPDATED,
        ),
        ProgramUpdateResult(
            file_url=PEBA_2021_XLSX_URL,
            page_url=PEBA_2021_URL,
            program_name="PEBA 2021",
            last_updated=1747000000,
        ),
    ]
    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository, MockPageRenderer(), xlsx_fetcher)

    result = await use_case.execute()

    assert result.updated == expected_updated_projects
    assert result.skipped == []


async def test_execute_with_some_not_updated_projects():
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = MOCK_URL_MAP

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_update.return_value = 1734421875
    mock_program_repository.get_last_xlsx_digest.return_value = "PEBA_DIGEST"

    xlsx_fetcher = _make_xlsx_fetcher({PEBA_2021_XLSX_URL: "PEBA_DIGEST"})

    expected_updated_projects = [
        ProgramUpdateResult(
            file_url=UNICO_2021_XLSX_URL,
            page_url=UNICO_2021_URL,
            program_name="UNICO 2021",
            last_updated=UNICO_2021_LAST_UPDATED,
        )
    ]
    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository, MockPageRenderer(), xlsx_fetcher)

    result = await use_case.execute()

    assert result.updated == expected_updated_projects
    assert result.skipped == []


@patch("application.use_cases.check_updated_programs_use_case.time")
async def test_missing_main_falls_back_to_digest(mock_time):
    mock_time.time.return_value = 1747000000

    url_map = {
        "Broken page": BROKEN_URL,
    }
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = url_map

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_update.return_value = None
    mock_program_repository.get_last_xlsx_digest.return_value = None

    xlsx_fetcher = _make_xlsx_fetcher({BROKEN_PAGE_XLSX_URL: "FRESHDIGEST"})

    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository, MockPageRenderer(), xlsx_fetcher)
    result = await use_case.execute()

    assert len(result.updated) == 1
    assert result.updated[0].program_name == "Broken page"
    assert result.updated[0].file_url == BROKEN_PAGE_XLSX_URL
    assert result.updated[0].page_url == BROKEN_URL
    assert result.updated[0].last_updated == 1747000000
    assert result.skipped == []


async def test_missing_main_skips_when_digest_unchanged():
    url_map = {
        "Broken page": BROKEN_URL,
    }
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = url_map

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_xlsx_digest.return_value = "SAMEDIGEST"

    xlsx_fetcher = _make_xlsx_fetcher({BROKEN_PAGE_XLSX_URL: "SAMEDIGEST"})

    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository, MockPageRenderer(), xlsx_fetcher)
    result = await use_case.execute()

    assert result.updated == []
    assert result.skipped == []


async def test_missing_main_skips_when_digest_fetch_fails():
    url_map = {
        "Broken page": BROKEN_URL,
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
        "UNICO 2021": UNICO_2021_URL,
        "No xlsx": NO_XLSX_URL,
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
    assert result.updated[0].program_name == "UNICO 2021"

    assert len(result.skipped) == 1
    assert result.skipped[0].program_name == "No xlsx"
    assert result.skipped[0].reason == "missing xlsx anchor"


async def test_parses_peba_page_without_date_falls_back_to_digest():
    url_map = {
        "PEBA 2021": PEBA_2021_URL,
    }
    mock_config_repository = MagicMock(spec=ConfigRepository)
    mock_config_repository.get_fiber_program_to_url_map.return_value = url_map

    mock_program_repository = MagicMock(spec=ProgramRepository)
    mock_program_repository.get_last_xlsx_digest.return_value = "OLDDIGEST"

    xlsx_fetcher = _make_xlsx_fetcher({PEBA_2021_XLSX_URL: "NEWDIGEST"})

    use_case = CheckUpdatedProgramsUseCase(mock_config_repository, mock_program_repository, MockPageRenderer(), xlsx_fetcher)
    result = await use_case.execute()

    assert result.skipped == []
    assert len(result.updated) == 1
    updated = result.updated[0]
    assert updated.program_name == "PEBA 2021"
    assert updated.file_url == PEBA_2021_XLSX_URL


async def test_ignores_xlsx_link_and_date_outside_cmp_text():
    url_map = {
        "Decoys": DECOYS_URL,
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
    # Must pick the link/date inside the cmp-text content block, not the
    # decoy .xlsx link or "Fecha de actualización" in the sidebar nav.
    assert updated.file_url == "https://digital.gob.es/documents/Relacion_proyectos_aprobados_CORRECT.xlsx"
    assert updated.last_updated == 1781481600  # 15/06/2026


async def test_renderer_error_skips_program():
    url_map = {
        "UNICO 2021": UNICO_2021_URL,
        "Error page": ERROR_URL,
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
    assert result.updated[0].program_name == "UNICO 2021"

    assert len(result.skipped) == 1
    assert result.skipped[0].program_name == "Error page"
    assert "unhandled error" in result.skipped[0].reason
