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
            'Petrol 95', 'Petrol 93', 'Diesel 50ppm', 'Diesel 500ppm', 'Diesel 10ppm', 'Diesel', 'Illuminating Paraffin'
        ]
        self.valid_locations: list = [
            'Inland', 'Coastal', 'Gauteng', 'KwaZulu-Natal', 'Western Cape',
            'Eastern Cape', 'Limpopo', 'Mpumalanga', 'North West', 'Free State', 'Northern Cape'
        ]
    def _normalize_fuel_type(self, fuel_type: str):

        if not fuel_type:
            return None
        norm_fuel = str(fuel_type).strip().lower().replace('-','_').replace(' ', '_')
        fuel_mapping = {
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
            'diesel_10ppm': 'Diesel 10ppm',
            'diesel': 'Diesel',
            'illuminating_paraffin': 'Illuminating Paraffin',
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

    def _clean_price_data_valid(self, raw_data: dict):
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

            # Clean timestamp data
            raw_timestamp = raw_data.get('timestamp')
            if raw_timestamp is None:
                print(f"Required missing field: timestamp")
                return None
            timestamp = self._clean_timestamp(raw_timestamp)
            if not timestamp:
                return None


            source = raw_data.get('source', 'DMRE')

            cleaned_data = {
                'price_per_litre': round(price, 3),
                'rate': round(price, 3),
                'price': round(price, 3),
                'timestamp': timestamp,
                'fuel_type': norm_fuel,
                'location': norm_loc,
                'region': norm_loc,
                'source': source, 
            }
            return cleaned_data
        except (ValueError, TypeError) as error:
            print(f"Error cleaning data: {error}")
            return None

    def _clean_timestamp(self, timestamp: str):
        """
        Clean the timestamp format.

        Args:
            timestamp: raw timestamp string or should be a datetime object.

        Returns:
            Cleaned timestamp string or None if invalid
        """   
        try:
            if isinstance(timestamp, str):
                date_formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d',
                    '%d/%m/%Y %H:%M:%S',
                    '%d/%m/%Y'
                ]
                for format in date_formats:
                    try:
                        dt = datetime.strptime(timestamp.strip(), format)
                        return dt.strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        continue
            elif isinstance(timestamp,datetime):
                return timestamp.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as error:
            print(f"Error cleaning timestamp: {error}")
        return None

    def _transform_to_dataframe(self, data_list: list) -> pd.DataFrame:
        """ 
        Takes a list of dictionaries and creates a pandas Dataframe with it.
        
        Args:
            data_list: List of dicts.

        Returns:
            pandas Dataframe with data.    
        """
        if not data_list:
            return pd.DataFrame()

        try:
            dataframe = pd.DataFrame(data_list)

            # Ensure there isa price column in the df.
            if 'price_per_litre' in dataframe.columns:
                dataframe['price_per_litre'] = pd.to_numeric(dataframe['price_per_litre'], errors="coerce")

                if 'rate' not in dataframe.columns:
                    dataframe['rate'] = dataframe['price_per_litre']
                elif 'rate' in dataframe.columns:
                    dataframe['rate'] = pd.to_numeric(dataframe['rate'], errors="coerce")
                    dataframe['price_per_litre'] = dataframe['rate']

                dataframe['timestamp'] = pd.to_datetime(dataframe['timestamp'], errors='coerce')

            # Drop missing values
            valid_subset = []
            for col in ['price_per_litre', 'timestamp']:
                if col in dataframe.columns:
                    valid_subset.append(col)
            dataframe = dataframe.dropna(subset=valid_subset)

            dataframe = dataframe.sort_values('timestamp')
            dataframe  = dataframe.reset_index(drop=True)

            return dataframe
        except Exception as error:
            print(f"Error transforming the list of dicts to Dataframe: {error}")
            return pd.DataFrame()


    