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
    
    def test_extraction_initialization(self) -> None:
            pass

if __name__== '__main__':
    pytest.main([__file__])