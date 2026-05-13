import sys
from unittest.mock import MagicMock

mock_workers = MagicMock()
sys.modules['workers'] = mock_workers
sys.modules['js'] = MagicMock()
sys.modules['pyodide'] = MagicMock()
sys.modules['pyodide.ffi'] = MagicMock()

from infrastructure.workflows.workflow import _build_skip_alert_subject, _format_skip_summary
from domain.check_updated_programs_result import SkippedProgram


async def test_build_skip_alert_subject_all_failed():
    assert _build_skip_alert_subject(skipped_count=5, total_count=5) == "[data-scraper] all 5 programs skipped"


async def test_build_skip_alert_subject_some_failed():
    assert _build_skip_alert_subject(skipped_count=3, total_count=10) == "[data-scraper] 3 of 10 programs skipped"


async def test_build_skip_alert_subject_one_of_many_failed():
    assert _build_skip_alert_subject(skipped_count=1, total_count=8) == "[data-scraper] 1 of 8 programs skipped"


async def test_format_skip_summary():
    skipped = [
        SkippedProgram(program_name="PEBA 2020", url="https://example.com/peba2020", reason="non-2xx status=503"),
        SkippedProgram(program_name="UNICO 2023", url="https://example.com/unico2023", reason="missing xlsx anchor"),
    ]

    summary = _format_skip_summary(skipped)

    assert summary.startswith("The following programs were skipped during scraping:")
    assert "- PEBA 2020 (https://example.com/peba2020): non-2xx status=503" in summary
    assert "- UNICO 2023 (https://example.com/unico2023): missing xlsx anchor" in summary
