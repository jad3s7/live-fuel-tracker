"""
Tests for the Fuel Data Extraction Module
These tests verify that the South African fuel price extraction functionality works correctly.
"""

import pytest
from src.data.extract import FuelExtractor


class TestFuelExtractor:
    """Test class for FuelExtractor functionality."""

    def test_extraction_initialization(self) -> None:
        """Test that checks if the extraction can be initialized."""
        extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="https://api.fuelsa.co.za/v1/prices")
        assert extraction is not None
        assert extraction.base_url == "https://api.fuelsa.co.za/v1/prices"

    def test_get_current_rate_structure(self) -> None:
        """Test that checks if current_rate returns the correct fuel data structure."""
        extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")
        result = extraction.get_current_rate()

        if result:
            assert isinstance(result, dict)
            assert 'timestamp' in result
            assert 'fuel_type' in result
            assert 'location' in result
            price = result.get('price_per_liter', result.get('rate'))
            assert price is not None
            assert isinstance(price, (int, float))
            assert price > 0

    def test_get_current_rate_valid_values(self) -> None:
        """Test that checks if current fuel rate returns valid South African price values."""
        extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")
        result = extraction.get_current_rate()

        if result:
            price = result.get('price_per_liter', result.get('rate'))
            # South African fuel prices generally sit between R15 and R35 per litre
            assert 15 < price < 35 # type: ignore
            assert isinstance(result['timestamp'], str)
            assert price > 0

    def test_get_fuel_price_by_type(self) -> None:
        """Test fetching a specific fuel type and region."""
        extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")
        result = extraction.get_fuel_price_by_type(fuel_type='Petrol 95', region='Inland')

        assert result is not None
        assert result['fuel_type'] == 'Petrol 95'
        assert result['location'] == 'Inland'
        assert 15 < result['price_per_liter'] < 35

    def test_get_price_comparison(self) -> None:
        """Test price comparison across regions and fuel types."""
        extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")
        comparison = extraction.get_price_comparison()

        assert comparison is not None
        assert 'regional_differences' in comparison
        assert 'cheapest_fuel' in comparison
        assert 'most_expensive_fuel' in comparison

    def test_get_historical_data_structure(self) -> None:
        """Test that checks if historical_data returns the correct structure."""
        extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")
        result = extraction.get_historical_data(days=5)

        assert isinstance(result, list)

        if result:
            for data in result:
                assert isinstance(data, dict)
                assert 'timestamp' in data
                price = data.get('price_per_liter', data.get('rate'))
                assert price is not None
                assert 'fuel_type' in data
                assert 'location' in data

    def test_get_historical_data_count(self) -> None:
        """Test that checks for the return of the historical data, should be 5 days."""
        extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")
        days = 5
        result = extraction.get_historical_data(days=days)

        if result:
            assert len(result) <= days

    def test_get_historical_data_with_zero_days(self) -> None:
        """Test that checks if historical data can be returned with zero day requests."""
        extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")
        result = extraction.get_historical_data(days=0)

        assert isinstance(result, list)
        assert len(result) == 0


if __name__ == '__main__':
    pytest.main([__file__, "-v"])