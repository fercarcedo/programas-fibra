import pytest
from util.date_parser import parse_last_updated

def test_parse_last_updated_dd_mm_yyyy():
    assert 1760400000 == parse_last_updated("14/10/2025")

def test_parse_last_updated_last_modified_header():
    assert 1760400000 == parse_last_updated("Tue, 14 Oct 2025 00:00:00 GMT")

def test_parse_last_updated_not_supported_format():
    with pytest.raises(ValueError, match="Unrecognized date format: 2025-10-14"):
        parse_last_updated("2025-10-14")