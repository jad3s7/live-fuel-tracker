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
from bs4 import BeautifulSoup


class FuelExtractor:
    """
    A class to extract South African fuel price data from APIs.
    This is the 'Extract' part of ETL (Extract, Transform, Load).

    Supported fuel types:
    - Petrol 95 (Unleaded)
    - Petrol 93 (Unleaded)
    - Diesel 50ppm (0.005% sulphur)
    - Diesel 500ppm (0.05% sulphur)

    Supported regions:
    - Inland (Gauteng, Free State, etc.)
    - Coastal (Western Cape, Eastern Cape, KwaZulu-Natal)

    Supported API providers:
    - zaref.dev: https://zaref.dev/docs/fuel-price-api (paid, $0.005/call)
    - fuelsa.co.za: https://www.fuelsa.co.za/ (subscription, R59/1000 calls)
    - scrape: Web scraping from DMRE/official sources (free, may be fragile)
    - simulated: Fallback for demonstration
    """
    def __init__(self, api_provider: str, api_key: str, base_url: str) -> None:
        """
        This initializes the FuelExtractor.

        Args:
            api_provider: API provider to use ('zaref', 'fuelsa', or 'simulated')
            api_key: Optional API key for authentication
            base_url: Optional custom base URL (overrides default for provider)
        """
        self.api_provider = api_provider.lower() if api_provider else 'simulated'
        self.api_key = api_key
        self.base_url = base_url or self._get_default_base_url()
        self.fuel_types = ['petrol_95', 'petrol_93', 'diesel_50ppm', 'diesel_500ppm']
        self.regions = ['inland', 'coastal']

        # Base fuel prices in R/litre (official DMRE prices as of August 2024)
        # Source: https://www.dmre.gov.za - updated monthly on first Wednesday
        self.base_prices = {
            'petrol_95': {'inland': 23.11, 'coastal': 22.32},  # August 2024
            'petrol_93': {'inland': 22.71, 'coastal': 21.92},  # August 2024
            'diesel_50ppm': {'inland': 20.74, 'coastal': 20.38},  # August 2024 (0.005%)
            'diesel_500ppm': {'inland': 20.38, 'coastal': 20.38}  # August 2024 (0.05%)
        }

    def _get_default_base_url(self) -> str:
        """Get the default base URL for the configured API provider."""
        if self.api_provider == 'zaref':
            return 'https://zaref.dev/v1'
        elif self.api_provider == 'fuelsa':
            return 'https://api.fuelsa.co.za/v1'
        else:
            return ''

    def get_current_prices(self) -> dict:
        """
        Fetches the current South African fuel prices.

        Returns:
            Dict: Contains fuel price data for all fuel types and regions.
            Example: {
                'petrol_95': {'inland': 22.95, 'coastal': 22.15},
                'petrol_93': {'inland': 22.45, 'coastal': 21.65},
                'diesel_50ppm': {'inland': 21.30, 'coastal': 20.50},
                'diesel_500ppm': {'inland': 21.10, 'coastal': 20.30},
                'timestamp': '2026-09-27 10:30:00',
                'source': 'zaref' or 'fuelsa' or 'simulated'
            }
            Returns None if API fails.
        """
        try:
            # Try to fetch from real API based on provider
            if self.api_provider in ['zaref', 'fuelsa', 'scrape']:
                if self.api_provider == 'zaref':
                    api_data = self._fetch_from_zaref()
                elif self.api_provider == 'fuelsa':
                    api_data = self._fetch_from_fuelsa()
                elif self.api_provider == 'scrape':
                    # Try oilprices.co.za first (more reliable)
                    api_data = self._fetch_from_oilprices()
                    if not api_data:
                        # Fallback to DMRE
                        api_data = self._fetch_from_scrape()

                if api_data:
                    return api_data
                else:
                    print(f"Data fetch failed for {self.api_provider}, falling back to simulated data")

            # Fallback to simulated data
            return self._generate_simulated_data()

        except requests.exceptions.RequestException as error:
            print(f"Error fetching data from API: {error}")
            print("Falling back to simulated data")
            return self._generate_simulated_data()
        except json.JSONDecodeError as error:
            print(f"There was an error parsing the JSON response: {error}")
            print("Falling back to simulated data")
            return self._generate_simulated_data()
        except Exception as error:
            print(f"Unexpected error: {error}")
            print("Falling back to simulated data")
            return self._generate_simulated_data()

    def _fetch_from_zaref(self) -> dict:
        """
        Fetch current fuel prices from zaref.dev API.

        Returns:
            Dict with parsed fuel prices or None if failed.
        """
        try:
            url = f"{self.base_url}/fuel-prices"
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            response = requests.get(url, headers=headers, timeout=10)

            # zaref uses 402 Payment Required for paid endpoints
            if response.status_code == 402:
                print("zaref.dev requires payment (x402 protocol). Falling back to simulated data.")
                return None
            elif response.status_code == 200:
                data = response.json()
                return self._parse_zaref_response(data)
            else:
                print(f"zaref API request failed with status code: {response.status_code}")
                return None

        except Exception as error:
            print(f"Error fetching from zaref: {error}")
            return None

    def _fetch_from_fuelsa(self) -> dict:
        """
        Fetch current fuel prices from fuelsa.co.za API.

        Returns:
            Dict with parsed fuel prices or None if failed.
        """
        try:
            url = f"{self.base_url}/current"
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                headers['X-API-Key'] = self.api_key

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return self._parse_fuelsa_response(data)
            elif response.status_code == 401:
                print("fuelsa.co.za authentication failed. Check API key.")
                return None
            else:
                print(f"fuelsa API request failed with status code: {response.status_code}")
                return None

        except Exception as error:
            print(f"Error fetching from fuelsa: {error}")
            return None

    def _fetch_from_scrape(self) -> dict:
        """
        Scrape fuel prices from official DMRE website.

        Returns:
            Dict with parsed fuel prices or None if failed.
        """
        try:
            # DMRE fuel prices page (fixed URL)
            url = "https://www.dmre.gov.za/Services/Petroleum-Resources/Fuel-Prices"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }

            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                print(f"DMRE website returned status code: {response.status_code}")
                return None

            soup = BeautifulSoup(response.content, 'lxml')

            # Try to find fuel price data in the page
            # Look for price patterns in the HTML
            result = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'dmre_scrape',
                'prices': {}
            }

            # Attempt 1: Look for table with fuel prices
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        # Look for fuel type names
                        row_text = ' '.join([cell.get_text(strip=True) for cell in cells])
                        if any(fuel in row_text.lower() for fuel in ['petrol', 'diesel']):
                            # Try to extract prices from this row
                            prices_found = self._extract_prices_from_text(row_text)
                            if prices_found:
                                result['prices'].update(prices_found)

            # Attempt 2: Look for price values in the page (fallback)
            if not result['prices']:
                all_text = soup.get_text()
                prices_found = self._extract_prices_from_text(all_text)
                if prices_found:
                    result['prices'] = prices_found

            # If scraping failed, try to get from the latest PDF link
            if not result['prices']:
                pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
                if pdf_links:
                    print(f"Found {len(pdf_links)} PDF links, but PDF parsing not implemented")

            # Return result if we found prices, otherwise None
            return result if result['prices'] else None

        except Exception as error:
            print(f"Error scraping DMRE website: {error}")
            return None

    def _fetch_from_oilprices(self) -> dict:
        """
        Scrape fuel prices from oilprices.co.za (reliable HTML table source).

        Returns:
            Dict with parsed fuel prices or None if failed.
        """
        try:
            url = "https://oilprices.co.za/fuel-price"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }

            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                print(f"OilPrices.co.za returned status code: {response.status_code}")
                return None

            soup = BeautifulSoup(response.content, 'lxml')

            result = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'oilprices_scrape',
                'prices': {}
            }

            # Find the fuel price table
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        row_text = ' '.join([cell.get_text(strip=True) for cell in cells])

                        # Extract fuel type and prices
                        if 'Petrol 95' in row_text:
                            prices = self._extract_prices_from_row(row_text, 'petrol_95')
                            if prices:
                                result['prices'].update(prices)
                        elif 'Petrol 93' in row_text:
                            prices = self._extract_prices_from_row(row_text, 'petrol_93')
                            if prices:
                                result['prices'].update(prices)
                        elif 'Diesel 0.05%' in row_text:
                            prices = self._extract_prices_from_row(row_text, 'diesel_500ppm')
                            if prices:
                                result['prices'].update(prices)
                        elif 'Diesel 0.005%' in row_text:
                            prices = self._extract_prices_from_row(row_text, 'diesel_50ppm')
                            if prices:
                                result['prices'].update(prices)

            return result if result['prices'] else None

        except Exception as error:
            print(f"Error scraping oilprices.co.za: {error}")
            return None

    def _extract_prices_from_row(self, row_text: str, fuel_type: str) -> dict:
        """Extract inland and coastal prices from a table row."""
        import re

        prices = {}
        # Match RXX.XX format
        price_matches = re.findall(r'R(\d{1,3}\.\d{2})', row_text)

        if len(price_matches) >= 2:
            prices[fuel_type] = {
                'inland': float(price_matches[0]),
                'coastal': float(price_matches[1])
            }
        elif len(price_matches) == 1:
            prices[fuel_type] = {
                'inland': float(price_matches[0]),
                'coastal': float(price_matches[0])  # Assume same if only one
            }

        return prices

    def _extract_prices_from_text(self, text: str) -> dict:
        """
        Extract fuel prices from text using regex patterns.

        Args:
            text: Text to search for prices

        Returns:
            Dict with fuel prices found
        """
        import re

        prices = {}

        # Pattern to match prices like R22.95 or 22.95
        price_pattern = r'R?(\d{1,2}\.\d{2})'

        # Look for fuel type and price combinations
        fuel_patterns = {
            'petrol_95': [r'petrol\s*95', r'95\s*ulp', r'95\s*unleaded'],
            'petrol_93': [r'petrol\s*93', r'93\s*ulp', r'93\s*unleaded'],
            'diesel_50ppm': [r'diesel\s*50ppm', r'diesel\s*0\.005%', r'diesel\s*50\s*ppm'],
            'diesel_500ppm': [r'diesel\s*500ppm', r'diesel\s*0\.05%', r'diesel\s*500\s*ppm'],
        }

        region_patterns = {
            'inland': [r'inland', r'gauteng', r'reef'],
            'coastal': [r'coastal', r'coast', r'cape'],
        }

        # Try to find fuel prices
        for fuel_type, fuel_regexes in fuel_patterns.items():
            for fuel_regex in fuel_regexes:
                fuel_match = re.search(fuel_regex, text, re.IGNORECASE)
                if fuel_match:
                    # Look for prices near this fuel type
                    context_start = max(0, fuel_match.start() - 200)
                    context_end = min(len(text), fuel_match.end() + 200)
                    context = text[context_start:context_end]

                    # Find all prices in context
                    price_matches = re.findall(price_pattern, context)

                    if len(price_matches) >= 2:
                        # Assume first is inland, second is coastal
                        if fuel_type not in prices:
                            prices[fuel_type] = {}
                        prices[fuel_type]['inland'] = float(price_matches[0])
                        prices[fuel_type]['coastal'] = float(price_matches[1])
                        break
                    elif len(price_matches) == 1:
                        # Only one price found, might need region context
                        if fuel_type not in prices:
                            prices[fuel_type] = {}
                        # Check if context has region info
                        for region, region_regexes in region_patterns.items():
                            for region_regex in region_regexes:
                                if re.search(region_regex, context, re.IGNORECASE):
                                    prices[fuel_type][region] = float(price_matches[0])
                                    break

        return prices

    def _parse_zaref_response(self, data: dict) -> dict:
        """
        Parse zaref.dev API response.

        Args:
            data: Raw API response from zaref.dev

        Returns:
            Dict with standardized fuel price format
        """
        try:
            result = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'zaref',
                'prices': {}
            }

            # zaref response structure (based on docs):
            # { petrol_95_inland: 22.95, petrol_95_coastal: 22.15, ... }
            # Note: Actual structure may vary, this is a template

            # Map zaref field names to our internal format
            mapping = {
                'petrol_95_inland': ('petrol_95', 'inland'),
                'petrol_95_coastal': ('petrol_95', 'coastal'),
                'petrol_93_inland': ('petrol_93', 'inland'),
                'petrol_93_coastal': ('petrol_93', 'coastal'),
                'diesel_50ppm_inland': ('diesel_50ppm', 'inland'),
                'diesel_50ppm_coastal': ('diesel_50ppm', 'coastal'),
                'diesel_500ppm_inland': ('diesel_500ppm', 'inland'),
                'diesel_500ppm_coastal': ('diesel_500ppm', 'coastal'),
            }

            for api_field, (fuel_type, region) in mapping.items():
                if api_field in data:
                    if fuel_type not in result['prices']:
                        result['prices'][fuel_type] = {}
                    result['prices'][fuel_type][region] = float(data[api_field])

            # If no data parsed, fall back to structure with alternative field names
            if not result['prices']:
                # Try alternative zaref structure
                if 'petrol' in data:
                    for fuel in data.get('petrol', {}):
                        # Handle nested structure if present
                        pass

            return result if result['prices'] else None # type: ignore

        except Exception as error:
            print(f"Error parsing zaref response: {error}")
            return None

    def _parse_fuelsa_response(self, data: dict) -> dict:
        """
        Parse fuelsa.co.za API response.

        Args:
            data: Raw API response from fuelsa.co.za

        Returns:
            Dict with standardized fuel price format
        """
        try:
            result = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'fuelsa',
                'prices': {}
            }

            # fuelsa response structure (based on their API docs):
            # Note: Actual structure may vary, this is a template

            # Try to parse common fuelsa structures
            if 'petrol' in data:
                petrol_data = data['petrol']
                for fuel_grade in ['95', '93']:
                    if fuel_grade in petrol_data:
                        grade_data = petrol_data[fuel_grade]
                        fuel_type = f'petrol_{fuel_grade}'
                        result['prices'][fuel_type] = {}

                        if 'inland' in grade_data or 'reef' in grade_data:
                            inland_price = grade_data.get('inland', grade_data.get('reef'))
                            result['prices'][fuel_type]['inland'] = float(inland_price)

                        if 'coastal' in grade_data or 'coast' in grade_data:
                            coastal_price = grade_data.get('coastal', grade_data.get('coast'))
                            result['prices'][fuel_type]['coastal'] = float(coastal_price)

            if 'diesel' in data:
                diesel_data = data['diesel']
                for ppm in ['50ppm', '500ppm', '50_ppm', '500_ppm']:
                    if ppm in diesel_data:
                        ppm_data = diesel_data[ppm]
                        fuel_type = f'diesel_{ppm.replace("_", "")}'
                        result['prices'][fuel_type] = {}

                        if 'inland' in ppm_data or 'reef' in ppm_data:
                            inland_price = ppm_data.get('inland', ppm_data.get('reef'))
                            result['prices'][fuel_type]['inland'] = float(inland_price)

                        if 'coastal' in ppm_data or 'coast' in ppm_data:
                            coastal_price = ppm_data.get('coastal', ppm_data.get('coast'))
                            result['prices'][fuel_type]['coastal'] = float(coastal_price)

            return result if result['prices'] else None # type: ignore

        except Exception as error:
            print(f"Error parsing fuelsa response: {error}")
            return None

    def _generate_simulated_data(self) -> dict:
        """
        Generate simulated fuel price data for demonstration.

        Returns:
            Dict with simulated fuel prices
        """
        result = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'simulated',
            'prices': {}
        }

        for fuel_type in self.fuel_types:
            result['prices'][fuel_type] = {}
            for region in self.regions:
                # Add small random variation to simulate real-time changes
                base_price = self.base_prices[fuel_type][region]
                variation = random.uniform(-0.05, 0.05)
                result['prices'][fuel_type][region] = round(base_price + variation, 2)

        return result

    @staticmethod
    def _normalize_fuel_type(fuel_type: str) -> str:
        f = str(fuel_type).strip().lower().replace('-', '_').replace(' ', '_')
        mapping = {
            'petrol_95': 'Petrol 95',
            'petrol95': 'Petrol 95',
            '95': 'Petrol 95',
            'petrol_93': 'Petrol 93',
            'petrol93': 'Petrol 93',
            '93': 'Petrol 93',
            'diesel_50ppm': 'Diesel 50ppm',
            'diesel50ppm': 'Diesel 50ppm',
            'diesel_50': 'Diesel 50ppm',
            'diesel_500ppm': 'Diesel 500ppm',
            'diesel500ppm': 'Diesel 500ppm',
            'diesel_500': 'Diesel 500ppm',
            'diesel': 'Diesel 50ppm',
        }
        return mapping.get(f, str(fuel_type).strip().title())

    @staticmethod
    def _to_raw_fuel_type(norm_fuel: str) -> str:
        s = norm_fuel.lower()
        if '93' in s:
            return 'petrol_93'
        if '500' in s:
            return 'diesel_500ppm'
        if 'diesel' in s:
            return 'diesel_50ppm'
        return 'petrol_95'

    @staticmethod
    def _normalize_region(region: str) -> str:
        r = str(region).strip().lower().replace('_', ' ')
        coastal_locations = {'coastal', 'western cape', 'eastern cape', 'kwazulu-natal', 'kzn'}
        if r in coastal_locations:
            return 'Coastal'
        return 'Inland'

    def _get_fuel_price_by_type(self, fuel_type: str = 'Petrol 95', region: str = 'inland') -> dict:
        """
        Fetches the current price for a specific fuel type and region.

        Args:
            fuel_type: Type of fuel (petrol_95, petrol_93, diesel_50ppm, diesel_500ppm)
            region: Region (inland or coastal)

        Returns:
            Dict: Contains price data for the specific fuel type and region.
        """
        norm_fuel = self._normalize_fuel_type(fuel_type)
        norm_region = self._normalize_region(region)
        raw_fuel = self._to_raw_fuel_type(norm_fuel)
        raw_region = norm_region.lower()

        all_prices = self.get_current_prices()

        if all_prices and 'prices' in all_prices:
            price = all_prices['prices'].get(raw_fuel, {}).get(raw_region)
            if price is None:
                price = self.base_prices.get(raw_fuel, {}).get(raw_region, 22.95)

            return {
                'fuel_type': norm_fuel,
                'location': norm_region,
                'region': norm_region,
                # Fixed: Changed from 'price_per_liter' to 'price_per_litre' for consistency with British spelling
                # This ensures consistency across the ETL pipeline with transform.py
                'price_per_litre': price,
                'price': price,
                'rate': price,
                'timestamp': all_prices['timestamp'],
                'source': all_prices.get('source', 'simulated')
            }

        return None

    def _get_current_price(self, fuel_type: str = 'Petrol 95', location: str = 'Inland') -> dict:
        """
        Fetches the current fuel price record for a given fuel type and location.
        Compatible with previous get_current_rate interface.
        """
        return self._get_fuel_price_by_type(fuel_type=fuel_type, region=location)

    def _get_historical_data(self, days: int = 30, fuel_type: str = 'Petrol 95', location: str = 'Inland') -> list:
        """
        Fetches historical fuel price data for the specified number of days.

        Args:
            days: Number of days for historical data to fetch (default: 30)
            fuel_type: Optional fuel type (default: 'Petrol 95')
            location: Optional location (default: 'Inland')

        Returns:
            List of dicts containing historical fuel price data.
        """
        if days <= 0:
            return []

        norm_fuel = self._normalize_fuel_type(fuel_type)
        norm_region = self._normalize_region(location)
        raw_fuel = self._to_raw_fuel_type(norm_fuel)
        raw_region = norm_region.lower()
        base_price = self.base_prices[raw_fuel][raw_region]

        historical_data = []
        for day in range(days):
            timestamp = datetime.now() - timedelta(days=days - day)
            daily_variation = random.uniform(-0.30, 0.30)
            price = round(base_price + daily_variation, 2)
            day_data = {
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'fuel_type': norm_fuel,
                'location': norm_region,
                'region': norm_region,
                # Fixed: Changed from 'price_per_liter' to 'price_per_litre' for consistency with British spelling
                # This ensures consistency across the ETL pipeline with transform.py
                'price_per_litre': price,
                'price': price,
                'rate': price,
                'source': 'simulated'
            }
            for ft in self.fuel_types:
                for rg in self.regions:
                    bp = self.base_prices[ft][rg]
                    day_data[f"{ft}_{rg}"] = round(bp + daily_variation, 2)

            historical_data.append(day_data)

        return historical_data

    def _get_price_comparison(self) -> dict:
        """
        Returns a comparison of fuel prices across all types and regions.
        
        Returns:
            Dict: Price comparison data including differences between regions.
        """
        current_data = self.get_current_prices()
        
        if not current_data or 'prices' not in current_data:
            return None #type: ignore
        
        comparison = {
            'timestamp': current_data['timestamp'],
            'source': current_data['source'],
            'prices': current_data['prices'],
            'regional_differences': {},
            'cheapest_fuel': None,
            'most_expensive_fuel': None
        }
        
        all_prices = []
        
        for fuel_type in self.fuel_types:
            inland_price = current_data['prices'][fuel_type]['inland']
            coastal_price = current_data['prices'][fuel_type]['coastal']
            
            difference = round(inland_price - coastal_price, 2)
            comparison['regional_differences'][fuel_type] = {
                'inland': inland_price,
                'coastal': coastal_price,
                'difference': difference
            }
            
            all_prices.append({
                'fuel_type': fuel_type,
                'inland': inland_price,
                'coastal': coastal_price
            })
        
        # Find cheapest and most expensive (using inland prices for comparison)
        cheapest_fuel = all_prices[0]
        most_expensive_fuel = all_prices[0]
        for prices in all_prices:
            if prices['inland'] < cheapest_fuel['inland']:
                cheapest_fuel = prices
            if prices['inland'] > most_expensive_fuel['inland']:
                most_expensive_fuel = prices
        comparison['cheapest_fuel'] = cheapest_fuel['fuel_type']
        comparison['most_expensive_fuel'] = most_expensive_fuel['fuel_type']

        return comparison


if __name__ == '__main__':
    extraction = FuelExtractor(api_provider="simulated", api_key="", base_url="")

    print("Fetching current South African fuel prices...")
    # Fixed: Changed from _get_current_price() to get_current_prices() to get all fuel types
    # _get_current_price() returns a single fuel type record, not the full structure with 'prices' key
    current_data = extraction.get_current_prices()

    if current_data and 'prices' in current_data:
        print("\n=== Current Fuel Prices ===")
        print(f"Timestamp: {current_data['timestamp']}")
        print(f"Source: {current_data['source']}, API unavailable.")
        print("\nPrices (R/litre):")

        for fuel_type, prices in current_data['prices'].items():
            print(f"  {fuel_type}:")
            print(f"    Inland:  R{prices['inland']}/litre")
            print(f"    Coastal: R{prices['coastal']}/litre")
    else:
        print("Failed to fetch current fuel prices")

    print("\n" + "="*50)

    print("Fetching specific fuel price")
    specific_price_95 = extraction._get_fuel_price_by_type('petrol_95', 'inland')
    # fetching petrol 95
    if specific_price_95:
        print("=== Petrol 95 ===")
        print(f"Price: R{specific_price_95['price']}/litre")
        print(f"Timestamp: {specific_price_95['timestamp']}")
    
    print("\n" + "="*50)
    print("Fetching price comparison...")
    comparison = extraction._get_price_comparison()
    if comparison:
        print(f"Cheapest fuel: {comparison['cheapest_fuel']}")
        print(f"Most expensive fuel: {comparison['most_expensive_fuel']}")
        print("\nRegional differences:")
        for fuel_type, diff in comparison['regional_differences'].items():
            print(f"  {fuel_type}: Inland is R{diff['difference']} higher than coastal")
    
    print("\n" + "="*50)
    print("Fetching historical data (last 5 days)...")
    historical_data = extraction._get_historical_data(days=5)
    print(f"Retrieved {len(historical_data)} historical data points")
    if historical_data:
        print(f"Sample entry: {historical_data[0]}")
