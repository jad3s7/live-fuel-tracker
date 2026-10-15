"""
Data Extraction Module
This module handles fetching South African fuel prices from external sources.
It's the first step in the data engineering pipeline: Extract.

Fuel Price Sources:
- Official: Department of Mineral Resources and Energy (DMRE)
- API Options: zaref.dev (paid, $0.005/call), fuelsa.co.za (subscription, R59/1000 calls)
- Fallback: Simulated data for demonstration purposes if API is unavailable
"""
import requests
import json
import random
from datetime import datetime, timedelta

class FuelExtractor:
    """ 
    Class that extracts the South African fuel price data
    from API or uses simulated data if API requests fails.
    
    Fuel types:
    - Petrol 95 (unleaded)
    - Petrol 93 (unleaded)
    - Diesel 50ppm (0.005% sulphur)
    - Diesel 500ppm (0.05% sulphur)

    Regions:
    - Inland (Gauteng, Free State.)
    - Coastal (Western Cape, Eastern Cape, KZN)
    """

    def __init__(self, api_provider: str, api_key: str, base_url: str) -> None
        """
        Constructor that initializes the FuelExtractor.
        
        Args:
        - api_provider: zaref, fuelsa or default simulated data.
        - api_key: no needed (optional: API key for authentication)
        - base_url: Custom / optional base URL.
        """
        fuel_types: list = ['petrol_95', 'petrol_93', 'diesel_50ppm', 'diesel_500ppm']
        self.api_provider = api_provider.lower() if api_provider else 'simulated' 
        self.api_key = api_key
        self.base_url = base_url
        self.fuel_types = fuel_types
        self.regions = ['inland', 'coastal']



    def get_current_rate(self):
        ...

    def get_fuel_price_per_type(self):
        ...

    def get_fuel_price_comparison(self):
        ...

    def get_historical_fuel_data(self, days):
        ...

    def get_historical_fuel_data_zero_days(self):
        ...
