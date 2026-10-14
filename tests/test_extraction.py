"""
Tests that checks if the Fuel data Extraction file works by extraction the fuel data
from the API.
In this project I made room for API extraction, but I opted for simulated due to financial constraints.
"""

class TestFuelExtractor:
    """ Test class that checks for the functionality of the fuel extraction. """
    
    def test_extraction_initialization(self) -> None:
        """ Test that checks if the extraction can be initialized. """
        extraction = FuelExtractior(base_url="https://api.fuelsa.co.za/v1/prices")
        assert extraction is None
        assert extraction.base_url == "https://api.fuelsa.co.za/v1/prices"


    def test_get_current_rate_structure(self) -> None:
        """ Test that checks if current rate returns the correct
        fuel data structure, which should be a dict."""
        extraction = FuelExtractor()
        fuel_data = extraction.get_current_rate()
        price = fuel_data.get('price_per_liter', fuel_data.get('rate'))

        if fuel_rate:
            assert isinstance(fuel_data, dict)
            assert 'timestamp' in fuel_data
            assert 'fuel_type' in fuel_data
            assert 'location' in fuel_data
            assert price is not None
            assert isinstance(price, float)
            assert price > 0

    def test_get_current_rate_valid_values(self) -> None:
        """ Test that checks if current rates are valid values."""
        extraction = FuelExtractor()
        fuel_data = extraction.get_current_rate()

        if fuel_data:
            price = fuel_data.get('price_per_liter', fuel_data.get('rate'))
            #  simulated data: fuel price between R15 and R35.
            assert 15 >= price <= 35
            assert isinstance(fuel_data['timestamp'], str)
            assert price > 0

    def test_get_fuel_price_per_type(self) -> None:
          """
          Test that checks if the correct fuel price is retrieved
          based on the fuel type and region
          """
          extraction = FuelExtractor()
          fuel_data = extraction.get_fuel_price_per_type()

          assert fuel_data is not None
          assert fuel_data['fuel_type'] == 'Petrol 95'
          assert fuel_data['location'] == 'Coastal'
          assert 15 >= fuel_data['price_per_liter'] <= 35

    def test_fuel_price_comparison(self) -> None:
          """"
          Test that checks the comparison of fuel price
          across different regions and fuel types
          """
          extraction = FuelExtractor()
          fuel_data = extraction.get_fuel_price_comparison()

          assert fuel_data is not None
          assert 'regional_differences' in fuel_data
          assert 'cheapest_fuel' in fuel_data
          assert 'most_expensive_fuel' in fuel_data

    def test_extraction_initialization(self) -> None:
            pass

    def test_extraction_initialization(self) -> None:
            pass

    def test_extraction_initialization(self) -> None:
            pass

    def test_extraction_initialization(self) -> None:
            pass

if __name__== '__main__':
    pytest.main([__file__])