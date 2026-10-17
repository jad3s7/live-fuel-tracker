"""
Data Extraction file
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


    def get_current_prices(self) -> None:
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

            if api_used: # type: ignore
                return api_used # type: ignore
            else: 
                print(f"API request failed for {self.api_provider}, will be using simulated data.")

            return self.generate_simulated_data() # type: ignore

        except requests.exceptions.RequestException as error:
            print(f"Error fetching data from API: {error}")
            print("Using simulated fuel data instead.")
            return self.generate_simulated_data() # type: ignore
         
        except json.JSONDecodeError as error:
            print(f"There was an error parsing the JSON response: {error}")
            print("Using simulated fuel data instead.")
            return self.generate_simulated_data() # type: ignore

        except Exception as error:
            print(f"Unexpected error: {error}")
            print("Using simulated fuel data instead.")
            return self.generate_simulated_data() # type: ignore

    def fetch_data_from_zaref(self) -> dict:
        """
        Fetches the current fuel prices from zaref API

        Returns:
            Dict with parsed fuel prices or None if it failed.
        """

        try:
            url = f"{self.base_url}/fuel-prices"
            response = requests.get(url, timeout=10)
            
            # zaref uses 402 for payment required / kinda like 401 but not.
            if response.status_code == 402:
                print('zaref.dev requires payment. Using simulated data.')
                return None # type: ignore
            
            # successfully requested
            elif response.status_code == 200:
                api_data = response.json()
                return self.parse_zaref_response() # type: ignore
            else:
                print(f"zaref API request failed with status code: {response.status_code}")
                return None # type: ignore
        except Exception as error:
            print(f"Error fetching API from zaref: {error}")
            return None # type: ignore

    def fetch_data_from_fuelsa(self) -> dict: # type: ignore
        """
        Fetches the current fuel prices from fuelsa API.

        Returns:
            Dict with parsed fuel pricess or None if API failed.
        """
        try:
            url = f"{self.base_url}/current"
            response = requests.get(url, timeout=10)

            # successfully requested
            if response.status_code == 200:
                api_data = response.json()
                return api_data
            
            #  Failed API request -> simulated data!
            elif response.status_code == 401:
                print("fuelsa authentication failed. Check API key.")
                return None # type: ignore
        except Exception as error:
            print(f"Error fetching from fuelsa: {error}")
            return None # type: ignore



    def parse_zaref_response(self, api_data: dict) -> dict:
        """
        Parse zaref API response.
        
        Args:
            data: Raw API response from zaref

        Returns:
            Dict with cleaned fuel price format
        """

        try:
            api_result = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'zaref',
                'prices': {}
            }

            # zaref response structure per docs:
            # { petrol_95_inland: 22.95 etc...}

            # Map zaref response to format used here.
            # eg: petrol_95, inland
            mapping = {
                'petrol_95_inland': ('petrol_95', 'inland'),
                'petrol_95_coastal': ('petrol_95', 'coastal'),
                'petrol_93_inland': ('petrol_93', 'inland'),
                'petrol_93_coastal': ('petrol_93', 'coastal'),
                'diesel_50ppm_inland': ('diesel_50ppm', 'inland'),
                'diesel_50ppm_coastal': ('diesel_50ppm', 'coastal'),
                'diesel_500ppm_inland': ('diesel_500ppm', 'inland'),
                'diesel_500ppm_coastal': ('diesel_500ppm', 'coastal')
            }

            for api_field, (fuel_type, region) in mapping.items():
                if api_field in api_data:
                    if fuel_type not in api_result['prices']:
                        api_result['prices'][fuel_type] = {}
                    api_result['prices'][fuel_type][region] = float(api_result[api_field])


            # if no data is parsed: use default structure
            if not api_result['prices']:
                if 'petrol' in api_result:
                    for fuel in api_result.get('petrol', {}):
                        pass
            return api_response if api_response['prices'] else None # type: ignore
       
        except Exception as error:
            print(f"Error parsing zaref API response: {error}")
            return None # type: ignore

    def parse_fuelsa_response(self, api_data: dict) -> dict:
        """
        Parse API response from API provider: fuelsa
        
        Args:
            api_data: raw api response from fuelsa.co.za (api provider)

        Returns:
            Dict with fuel price format (default)
        """
        try:
            api_result = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'fuelsa',
                'prices': {}
            }

            # Attempt to parse common fuelsa api-result-structure for petrol
            # fuel type, region and prices added to api_result
            if 'petrol' in api_data:
                petrol_data = api_data['petrol']
                for fuel_grade in ['95', '93']:
                    if fuel_grade in petrol_data:
                        fuel_grade_data = petrol_data[fuel_grade]
                        fuel_type = f"petrol_{fuel_grade_data}"
                        # petrol_95 or  petrol_93
                        api_result['prices'][fuel_type] = {}

                        # region logic for inland and coastal prices
                        if 'inland' in fuel_grade_data:
                            inland_price = fuel_grade_data.get('inland')
                            api_result['prices'][fuel_type]['inland'] = float(inland_price)

                        if 'coastal' in fuel_grade_data or 'coast' in fuel_grade_data:
                            coastal_price = fuel_grade_data.get('coastal', fuel_grade_data.get('coast'))
                            api_result['prices'][fuel_type][coastal_price] = float(coastal_price)

            # 
            # Attempt to parse common fuelsa api-result-structure for diesel
            # fuel type, region and prices added to api_result
            if 'diesel' in api_data:
                diesel_data = api_data['diesel']
                for ppm in ['50ppm','500ppm', '50_ppm','500_ppm']:
                    if ppm in diesel_data:
                        diesel_grade_data = diesel_data['ppm']
                        fuel_type = f"diesel_{ppm.replace("_", "")}"
                        api_result['prices'][fuel_type] = {}

                        if 'inland' in diesel_grade_data:
                            inland_price = diesel_grade_data.get('inland')
                            api_result['prices'][fuel_type]['inland'] = float(inland_price)

                        if 'coastal' in diesel_grade_data or 'coast' in diesel_grade_data:
                            coastal_price = diesel_grade_data.get('coastal', diesel_grade_data.get('coast'))
                            api_result['prices'][fuel_type]['coastal'] = float(coastal_price)

            return api_result if api_result['prices'] else None # type: ignore
        
        except Exception as error:
            print(f"Error parsing fuelsa api response: {error}")
            return None #type: ignore
    
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
    def convert_fuel_number_to_fuel_type(normalize_fuel_type: str) -> str:
        fuel_string = normalize_fuel_type.lower()
        if '93' in fuel_string:
            return 'petrol_93'
        if '500' in fuel_string:
            return 'diesel_500ppm'
        if '50' in fuel_string:
            return 'diesel_50ppm'
        return 'petrol_95'
    
    @staticmethod
    def normalize_region(region: str) -> str:
        regional = str(region).strip().lower().replace('_', ' ')
        coastal_regions = {
            'coastal',
            'western cape',
            'eastern cape',
            'kzn'
        }
        if region in coastal_regions:
            return 'Coastal'
        return 'Inland'
    
    def get_fuel_price_by_type(self, fuel_type: str = 'Petrol 95', region: str = 'Coastal') -> dict:
        """
        Fetches the fuel price based on the fuel type and region.

        Args:
            fuel_type: Petrol 95, Petrol 93 etc.
            region: inland or coastal

        Returns:
            Dict: Fuel price based on fuel type and region and other related fuel data.
        """
        normalized_fuel = self.normalize_fuel_type(fuel_type)
        normalized_region = self.normalize_region(region)
        raw_fuel = self.convert_fuel_number_to_fuel_type(normalized_fuel)
        raw_region = normalized_region.lower()

        all_prices = self.get_current_prices()

        if all_prices and 'prices' in all_prices:
            price = all_prices['prices'].get(raw_fuel, {}).get(raw_region)
            if price is None:
                price = self.base_prices.get(raw_fuel, {}.get(raw_region, 22.95))

            return {
            'fuel_type': normalized_fuel,
            'location': normalized_region,
            'region': normalized_region,
            'price_per_litre': price,
            'price': price,
            'rate': price,
            'timestamp': all_prices['timestamp'],
            'source': all_prices.get('source', 'simulated'),
        }
        return None

    def get_historical_fuel_data(self, days: int = 30, fuel_type: str = "Petrol 95", location: str = 'Inland') -> list:
        """
        Fetches historical fuel price data for the amount days specified.

        Args:
            days: amount of days for historical data to be fetched (default: 30 days)
            fuel_type: optional, use diesel 50ppm etc (default: Petrol 95)
            region: Inland or Coastal

        Returns:
            List of dicts containing historical fuel price data.
        """

        if days <= 0:
            return []

        normalize_fuel_type = self.normalize_fuel_type(fuel_type)
        normalize_region = self.normalize_region(location)
        raw_fuel = self.convert_fuel_number_to_fuel_type(normalize_fuel_type)
        raw_region = normalize_region.lower()
        base_price = self.base_prices[raw_fuel][raw_region]

        historical_data = []
        for day in range(days):
            timestamp = datetime.now() - timedelta(days=days - day)
            price = base_price
            day_data = {
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'fuel_type': normalize_fuel_type,
                'location': normalize_region,
                'region': normalize_region,
                'price_per_liter': price,
                'price': price,
                'rate': price,
                'source': 'simulated',
            }
            for fueltype in self.fuel_types:
                for reg in self.regions:
                    b_price = self.base_prices[fuel_type][reg]
                    day_data[f"{fuel_type}_{reg}"] = b_price

            historical_data.append(day_data)
        return historical_data


    # def get_fuel_price_comparison(self) -> dict:
    #     """
    #     Returns a comparison of fuel prices across different fuel types and regions

    #     Returns:
    #         Dict: price comparison data including different regions.
    #     """

    #     current_data = self.get_current_prices()

