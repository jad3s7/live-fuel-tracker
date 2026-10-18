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
    

    def test_transformer_initialization(self, transformer):
        """ Test that checks if transformer can be initialized."""
        assert transformer is not None
        assert 'Petrol 95' in transformer.valid_fuel_types
        assert 'Petrol 93' in transformer.valid_fuel_types
        assert 'Diesel 500ppm' in transformer.valid_fuel_types
        assert 'Diesel 50ppm' in transformer.valid_fuel_types
        assert 'Inland' in transformer.valid_locations
        assert 'Coastal' in transformer.valid_locations
        assert 'Eastern Cape' in transformer.valid_locations
        assert 'Western Cape' in transformer.valid_locations


    def test_clean_price_data_valid(self, transformer):
        """
        Test that checks for if cleaning of fuel price data is valid.
        """
        valid_fuel_data = {
            'price_per_litre': 22.95,
            'timestamp': '2026-09-21 10:00:00',
            'fuel_type': 'Petrol 95',
            'location': 'Gauteng',
            'source': 'DMRE',
        }

        result = transformer._clean_price_data_valid(valid_fuel_data)

        assert result is not None
        assert result['price_per_litre'] == 22.95
        assert result['fuel_type'] == 'Petrol 95'
        assert result['location'] == 'Gauteng'

        
    def test_clean_price_data_invalid(self, transformer):
        """Test cleaning data with invalid prices, -ve price, out of range prices."""
        invalid_fuel_data = {
            'price_per_litre': -5,
            'timestamp': '2026-09-21 10:00:00',
            'fuel_type': 'Petrol 95',
            'location': 'Gauteng',
            'source': 'DMRE',
        }
        result = transformer._clean_price_data_valid(invalid_fuel_data)
        assert result is None

        price_out_range = {
            'price_per_litre': 120.0,
            'timestamp': '2026-09-21 10:00:00',
            'fuel_type': 'Petrol 95',
            'location': 'Gauteng',
            'source': 'DMRE',
        }
        assert transformer._clean_price_data_valid(price_out_range) is None

    def test_clean_price_data_missing(self, transformer):
        """ Test that checks cleaning of data with missing fields."""
        missing_fields = {
            'price_per_litre': 22.95,
            'timestamp': '2026-09-21 10:00:00'
            # fuel_type and location missing
        }
        result = transformer._clean_price_data_valid(missing_fields)
        assert result is None

    def test_clean_price_data_invalid_fuel_type(self, transformer):
        """ Test that checks cleaning data with invalid fuel type. """
        invalid_fuel_type = {
            'price_per_litre': 22.95,
            'timestamp': '2026-09-21 10:00:00',
            'fuel_type': 'RocketFuel',
            'location': 'Gauteng',
            'source': 'DMRE',
        }
        result = transformer._clean_price_data_valid(invalid_fuel_type)
        assert result is None

    def test_clean_rate_data_invalid_location(self, transformer):
        """Test cleaning data with invalid location."""
        invalid_loc = {
            'price_per_liter': 22.95,
            'timestamp': '2026-09-21 10:00:00',
            'fuel_type': 'Petrol 95',
            'location': 'Mars',
            'source': 'DMRE'
        }
        result = transformer._clean_price_data_valid(invalid_loc)
        assert result is None

    def test_clean_price_data_case_insensitive(self, transformer):
        """Test that checks if the fuel price data is case insensitive."""
        data_insensitive = {
            'price_per_litre': 22.95,
            'timestamp': '2026-09-21 10:00:00',
            'fuel_type': 'petrol 95',
            'location': 'gauteng',
            'source': 'DRME' 
        }
        result = transformer._clean_price_data_valid(data_insensitive)
        assert result is not None
        assert result['fuel_type'] == 'Petrol 95'
        assert result['location'] == 'Gauteng'

    # def test_transform_data_to_dataframe(self, transformer):
    #     pass

    # def test_transform_to_dataframe_empty(self, transformer ):
    #     pass

    # def test_add_moving_average(self, transformer):
    #     pass

    # def test_add_rate_change(self, transformer):
    #     pass

    # def test_detect_outliers(self, transformer):
    #     pass

    # def test_aggregate_data(self, transformer):
    #     pass

    # def test_validate_data_quality(self, transformer):
    #     pass
    

    if __name__ == "__main__":
        pytest.main([__file__, "-vv"])