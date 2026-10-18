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
    
