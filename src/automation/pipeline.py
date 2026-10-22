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



if __name__ == '__main__':
    success = run_etl_pipeline()

    if success:
        print("\n ETL Pipeline completed successfully!")
        sys.exit(0)
    else:
        print("\n ETL Pipeline failed!")
        sys.exit(1)