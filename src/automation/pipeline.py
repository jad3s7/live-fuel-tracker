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
    print('=' * 54)
    print("Starting South African Fuel Price Tracker ETL Pipeline")
    print('=' * 54)

    # Initialize components
    extractor = FuelExtractor(
        api_provider=config.fuel_api_provider,
        api_key=config.fuel_api_key,
        base_url=config.fuel_api_base_url
    )
    transformer = DataTransformer()
    db = FuelDatabase(config.get_database_path())

    try:
        # Extract.
        print("\n[1/3] Extracting fuel price data from source/API...")
        all_raw_data = []

        # Extract current fuel prices for major fuel types in South Africa.
        fuel_types = [
            'Petrol 95',
            'Petrol 93',
            'Diesel 50ppm',
            'Diesel 500ppm',
        ]
        regions = ['Inland', 'Coastal']
        for fueltype in fuel_types:
            for region in regions:
                current_price = extractor._get_current_price(fuel_type=fueltype, location=region)
                if current_price:
                    all_raw_data.append(current_price)

        if not all_raw_data:
            print("Error: Failed to extract current fuel prices.")
            return False

        sample_price = all_raw_data[0]
        print(f"Extracted current price: {sample_price['fuel_type']} ({sample_price['location']}) -R{sample_price['price_per_litre']:.2f}/L")


        # retrieve the historical data for each fuel type and region.
        for fueltype in fuel_types:
            for region in regions:
                historical_data = extractor._get_historical_data(days=7, fuel_type=fueltype, location=region)
                all_raw_data.extend(historical_data)

        print(f"Total extracted raw records: {len(all_raw_data)}")

        # Transform
        print("\n[2/3] Transforming and cleaning fuel price data...")
        cleaned_data = []

        for data in all_raw_data:
            cleaned= transformer._clean_price_data_valid(data)
            if cleaned:
                cleaned_data.append(cleaned)
        print(f"Cleaned {len(cleaned_data)} valid data points")

        if not cleaned_data:
            print("Error: No valid data after transformation")
            return False

        # Load
        print("\n[3/3] Loading data into database...")
        inserted_count = db._insert_price_database_multiple(cleaned_data)

        if inserted_count > 0:
            print(f"Successfully inserted {inserted_count} records into database.")
        else:
            print("Warning: No records inserted into database")

        #  Get Statistics
        stats = db._get_statistics()
        print("\n" + "=" * 50)
        print("Fuel Price Pipeline Statistics:")
        print(f"Total records in database: {stats['total_records']}")
        print(f"Average price: R{stats['avg_price']:.2f}/L")
        print(f"Min price: R{stats['min_price']:.2f}/L")
        print(f"Max price: R{stats['max_price']:.2f}/L")
        print("=" * 50)

        return True

    except Exception as error:
        print(f"Error during ETL pipeline: {error}")
        return False


if __name__ == '__main__':
    success = run_etl_pipeline()

    if success:
        print("\n ETL Pipeline completed successfully!")
        sys.exit(0)
    else:
        print("\n ETL Pipeline failed!")
        sys.exit(1)