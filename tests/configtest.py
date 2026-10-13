"""
Pytest configuration file
This file sets up the test environment.
path is now handled by pytest.ini
"""
import pytest

@pytest.fixture
def sample_data():
    return {"key": "value"}
