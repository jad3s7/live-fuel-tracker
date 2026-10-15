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

    def __init__(self, api_provider: str, api_key: str, base_url: str) -> None:
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
        self.base_url = base_url or self.get_base_url()
        self.fuel_types = fuel_types
        self.regions = ['inland', 'coastal']
        
        # Base fuel prices used, R/litre. 
        self.base_prices = {
            'petrol_95': {'inland': 22.95, 'coastal': 22.15},
            'petrol_93': {'inland': 22.45, 'coastal': 21.65},
            'diesel_50ppm': {'inland': 21.30, 'coastal': 20.50},
            'diesel_500ppm': {'inland': 21.10, 'coastal': 20.30}
        }

    def get_base_url(self) -> str:
        """
        Get default base URL for the API provider
        """
        if self.api_provider == 'zaref': return 'https://zaref.dev/v1'
        elif self.api_provider == 'fuelsa': return 'https://api.fuelsa.co.za/v1'
        else: return ''


    def get_current_rate(self) -> None:
        """
        Fetches the current SA fuel price.
        
        Returns:
            - Dict that contains fuel data that has fuel types and regions, timestamp.
        
        Return None if API fails.
        """
        try:
            # First attempt is to fetch data from real API based on provider used.
            if self.api_provider == 'zaref':
                api_used: dict = self.fetch_data_from_zaref()
            elif self.api_provider == 'fuelsa':
                api_used: dict = self.fetch_data_from_fuelsa()

            if api_used:
                return api_used
            else: 
                print(f"API request failed for {self.api_provider}, will be using simulated data.")

            return self.generate_simulated_data()

        except requests.exceptions.RequestException as error:
            print(f"Error fetching data from API: {error}")
            print("Using simulated fuel data instead.")
            return self.generate_simulated_data()
         
        except json.JSONDecodeError as error:
            print(f"There was an error parsing the JSON response: {error}")
            print("Using simulated fuel data instead.")
            return self.generate_simulated_data()

        except Exception as error:
            print(f"Unexpected error: {error}")
            print("Using simulated fuel data instead.")
            return self.generate_simulated_data()

    def fetch_data_from_zaref(self) -> dict:
        """
        Fetches the current fuel prices from zaref API

        Returns:
            Dict with parsed fuel prices or None if it failed.
        """
        ...

    def fetch_data_from_fuelsa(self) -> dict:
        ...

    def parse_zaref_response(self) -> dict:
        ...

    def parse_fuelsa_response(self) -> dict:
        ...

    def generate_simulated_data(self) -> dict:
        """
        Generates simulated fuel price data for demo.

        Returns:
            Dict with simulated fuel prices
        """
        simulated_data: dict = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'simulated',
            'prices': {}
        }

        for fuel_type in self.fuel_types:
            simulated_data['prices'][fuel_type] = {}
            for region in self.regions:
                base_price = self.base_prices[fuel_type][region]
                simulated_data['prices'][fuel_type][region] = base_price

        return simulated_data

    @staticmethod
    def normalize_fuel_type(fuel_type: str) -> str:
        """
        Ensures that all mapping of fuel types are found.
        """
        string_formatter = str(fuel_type).strip().lower().replace('-', '_').replace(' ', '_')

        mapping = {
            'petrol_95':        'Petrol 95',
            'petrol95':         'Petrol 95',
            '95':               'Petrol 95',
            'petrol_93':        'Petrol 93',
            'petrol93':         'Petrol 93',
            '93':               'Petrol 93',
            'diesel_50ppm':     'Diesel 50ppm',
            'diesel50ppm':      'Diesel 50ppm',
            'diesel_50':        'Diesel 50ppm',
            'diesel_500ppm':    'Diesel 500ppm',
            'diesel500ppm':     'Diesel 500ppm',
            'diesel_500':       'Diesel 500ppm',
            'diesel':           'Diesel 50ppm',
        }
        return mapping.get(string_formatter, str(fuel_type).strip().title())

    @staticmethod
    def convert_fueltype_number_to_fuel_type(norm_fuel_type: str) -> str:
        fuel_string = norm_fuel_type.lower()
        if '93' in fuel_string:
            return 'petrol_93'
        if '500' in fuel_string:
            return 'diesel_500ppm'
        if '50' in fuel_string:
            return 'diesel_50ppm'
        return 'petrol_95'
    @