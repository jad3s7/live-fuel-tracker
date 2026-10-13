"""
Test file for conftest.py fixtures
path is handled by pytest.ini
"""
import pytest 

def test_sample_data_fixture(sample_data: dict[str, str]):
    """ Test that the sample data fixture works."""

    assert sample_data is not None
    assert isinstance(sample_data, dict)
    assert sample_data == {"key": "value"}
    assert "key" in sample_data
    assert sample_data["key"] == "value"

def test_sample_data_is_mutable(sample_data: dict[str, str]):
    """Test to check if each test fixture gets a new copy."""

    sample_data["new_key"] = "new_value"
    assert "new_key" in sample_data