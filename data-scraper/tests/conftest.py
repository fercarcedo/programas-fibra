from pathlib import Path
import pytest

TESTS_ROOT = Path(__file__).parent

@pytest.fixture
def tests_root():
    """Provide the tests root directory."""
    return TESTS_ROOT

@pytest.fixture
def test_resource():
    """Factory fixture to get test resource files."""
    def _get_resource(filename):
        return TESTS_ROOT / "resources" / filename
    return _get_resource