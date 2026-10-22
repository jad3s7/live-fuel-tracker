"""
ETL Pipeline script
This script orchestrates the complete Extract, Transform, Load pipeline for South African fuel price data.
"""

import sys
import os

# add parent directory to path for imports.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.extract import FuelExtractor
from src.data.transform import DataTransformer
from src.database.storage_db import FuelDatabase
from src.utils.config import config

def run_etl_pipeline():
    """
    Execute the complete ETL pipelin:
    1. Extract fuel price data.
    2. Transform and clean the data.
    3. Load data into SQLite Database.
    """
    print('=' * 50)
    print("Starting South African Fuel Price Tracker ETL Pipeline")
    print('=' * 50)

    # Initialize components
    extractor = FuelExtractor(
        api_provider=config.fuel_api_provider,
        api_key=config.fuel_api_key,
        base_url=config.fuel_api_base_url
    )
    transformer = DataTransformer()
    db = FuelDatabase(config.get_database_path())
    



if __name__ == '__main__':
    success = run_etl_pipeline()

    if success:
        print("\n ETL Pipeline completed successfully!")
        sys.exit(0)
    else:
        print("\n ETL Pipeline failed!")
        sys.exit(1)