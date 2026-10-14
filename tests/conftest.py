"""
Minimal conftest.py - path handled by pytest.ini (venv)
"""
import pytest

@pytest.fixture
def sample_data()-> dict[str, str]:
    return {"key": "value"} 