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
            extracted_current_rate = extraction.get_current_rate()
            price = extracted_current_rate.get('price_per_liter', extracted_current_rate.get('rate'))

            if extracted_current_rate:
                   assert isinstance(extracted_current_rate, dict)
                   assert 'timestamp' in extracted_current_rate
                   assert 'fuel_type' in extracted_current_rate
                   assert 'location' in extracted_current_rate
                   assert price is not None
                   assert isinstance(price, float)
                   assert price > 0
                   

    def test_extraction_initialization(self) -> None:
            pass
    
    def test_extraction_initialization(self) -> None:
            pass

    def test_extraction_initialization(self) -> None:
            pass

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