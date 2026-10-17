"""
Tests that checks if the Fuel data Extraction file works by extraction the fuel data
from the API.
In this project I made room for API extraction, but I opted for simulated due to financial constraints.
"""
import pytest
from src.data.extract import FuelExtractor

class TestFuelExtractor:
    """ Test class that checks for the functionality of the fuel extraction. """

    def test_extraction_initialization(self) -> None:
        """ Test that checks if the extraction can be initialized. """
        extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")
        assert extraction is None
        assert extraction.base_url == "https://api.fuelsa.co.za/v1/prices"


    def test_get_current_price_structure(self) -> None:
        """ Test that checks if current rate returns the correct
        fuel data structure, which should be a dict."""
        extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")
        fuel_data = extraction.get_current_prices()

        if fuel_data:
            assert isinstance(fuel_data, dict)
            assert 'timestamp' in fuel_data
            assert 'fuel_type' in fuel_data
            assert 'location' in fuel_data
            price = fuel_data.get('price_per_liter', fuel_data.get('rate'))
            assert price is not None
            assert isinstance(price, float)
            assert price > 0

    def test_get_current_price_valid_values(self) -> None:
        """ Test that checks if current rates are valid values."""
        extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")
        fuel_data = extraction.get_current_prices()

        if fuel_data:
            price = fuel_data.get('price_per_liter', fuel_data.get('rate'))
            #  simulated data: fuel price between R15 and R35.
            assert 15 > price <= 35
            assert isinstance(fuel_data['timestamp'], str)
            assert price > 0

    def test_get_fuel_price_per_type(self) -> None:
          """
          Test that checks if the correct fuel price is retrieved
          based on the fuel type and region
          """
          extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")
          fuel_data = extraction.get_fuel_price_by_type()

          assert fuel_data is not None
          assert isinstance(fuel_data, dict)
          assert fuel_data['fuel_type'] == 'Petrol 95'
          assert fuel_data['location'] == 'Inland'
          assert 15 >= fuel_data['price_per_liter'] <= 35

    def test_fuel_price_comparison(self) -> None:
          """"
          Test that checks the comparison of fuel price
          across different regions and fuel types
          """
          extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")
          fuel_data = extraction.get_fuel_price_comparison()

          assert fuel_data is not None
          assert isinstance(fuel_data, dict)
          assert 'regional_differences' in fuel_data
          assert 'cheapest_fuel' in fuel_data
          assert 'most_expensive_fuel' in fuel_data

    def test_get_historical_fuel_data_structure(self) -> None:
        """
        Test that checks if historical_fuel_data returns
        the correct structure.
        """
        extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")
        hist_fuel_data: dict = extraction.get_historical_fuel_data(days=5)

        assert hist_fuel_data is not None
        assert isinstance(hist_fuel_data, list)

        if hist_fuel_data:
            for fuel_data in hist_fuel_data:
                assert isinstance(fuel_data, dict)
                assert 'timestamp' in fuel_data
                assert 'location' in fuel_data
                price = hist_fuel_data.get('price_per_liter', hist_fuel_data.get('rate'))
                assert price is not None
                assert 'fuel_type' in fuel_data

    def test_get_historical_fuel_data_count(self) -> None:
        """
        Test that checks if the historical fuel data returns data
        for 5 days historically.
        """
        extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")
        counted_fuel_data = extraction.get_historical_fuel_data(days=5)

        if counted_fuel_data:
            assert len(counted_fuel_data) <= 5

    def test_get_historical_fuel_data_zero_days(self) -> None:
        """
        Test that checks if historical data can be returned using zero day requests.
        """
        extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")
        result: dict = extraction.get_historical_fuel_data_zero_days()

        assert isinstance(result, dict)
        assert result is not None
        assert len(result) == 0



if __name__== '__main__':
    pytest.main([__file__], "-v")