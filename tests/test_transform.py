"""
Tests for the Data Transformation Module
These tests verify that South African fuel price cleaning and transformation work correctly.
"""
import pytest
import pandas as pd
from src.data.transform import DataTransformer

class TestDataTransformer:
    """
    Test classs for the transformation of fuel price data.
    """
    @pytest.fixture
    def transformer(self):
        """ Creates a DataTransformer instance for testing."""
        return DataTransformer()
    

    