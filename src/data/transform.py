"""
This file handles the cleaning and transforming of raw South African fuel price data.
"""

import pandas as pd
from datetime import datetime

class DataTransformer:
    """
    Class that cleans and transforms the SA fuel price data.
    Ensures that data has quality before being used for analysis or visualizationss.
    """

    def __init__(self): 
        """
        This initializes the DataTransformer.
        """
        self.valid_fuel_types: list = [
            'Petrol 95',
            'Petrol 93',
            'Diesel 50ppm',
            'Diesel 500ppm'
        ]
        self.valid_locations: list = [
            'Inland', 'Coastal', 'Gauteng', 'KwaZulu-Natal', 'Western Cape',
            'Eastern Cape', 'Limpopo', 'Mpumalanga', 'North West', 'Free State',
            'Northern Cape'
        ]

    def _normalize_fuel_type(self, fuel_type: str):

        if not fuel_type:
            return None
        norm_fuel = str(fuel_type).strip().lower().replace('-','_').replace(' ', '_')
        fuel_mapping = {
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
        }
        for valid_fuel_type in self.valid_fuel_types:
            if valid_fuel_type.lower() == str(fuel_type).strip().lower():
                return valid_fuel_type
        return fuel_mapping.get(norm_fuel)

    def _normalize_location(self, location: str):
        if not location:
            return None
        cleaned_loc = str(location).strip().lower()
        for valid_loc in self.valid_locations:
            if valid_loc.lower() == cleaned_loc:
                return valid_loc
        return None

    def clean_the_price_data(self, raw_data: dict):
        """"
        Cleans and validates a single fuel price data point.
        Checks for missing values, invalid data types and out of range prices.

        Args:
            raw_data: Raw dict with fuel price information.

        Returns:
            Cleaned dict or None if data is invalid.
        """
        if not raw_data or not isinstance(raw_data, dict):
            return None

        try:
            # Check the price field
            price = None
            for key in ['price_per_litre', 'rate', 'price']:
                if key in raw_data and raw_data[key] is not None:
                    try:
                        price = float(raw_data[key])
                        break
                    except (ValueError, TypeError):
                        continue

            if price is None:
                print(f"Required field missing: price_per_litre")
                return None

            # Fuel prices in SA, bounds are 0 < price <= R35 per litre (historically.)
            if price <= 0 or price >= 35:
                print(f"Invalid price value: {price}")
                return None

            # Check fuel type
            raw_fuel = raw_data.get('fuel_type') or raw_data.get('fuel')
            if raw_fuel is None:
                print(f"Required field missiing: fuel_type")
                return None
            norm_fuel = self._normalize_fuel_type(raw_fuel)
            if not norm_fuel:
                print(f"Invalid fuel type: {raw_fuel}")
                return None

            # Check the location
            raw_loc = raw_data.get("location") or raw_data.get('region')
            if raw_loc is None:
                print(f"Required field missing: location")
                return None
            norm_loc = self._normalize_location(raw_loc)
            if not norm_loc:
                print(f"Invalid location: {raw_loc}")
                return None

            
