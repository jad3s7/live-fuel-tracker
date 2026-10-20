"""
This script handles all database operations for storing and retrieving South African fuel price data.
It's the 'Load' part of ETL (Extract, Transform, Load).
"""

import sqlite3
from datetime import datetime

class FuelDatabase:
    """
    A class to manage SQLite database operations for SA fuel price data.
    This stores the transformed data.
    """

    def __init__(self, db_path: str):
        """
        Initialize the database connection and creates tables if there is none.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self._create_fuel_data_tables()

    def close(self):
        """
        Close the database connection.
        This method should be called when done with the database.
        """
        if self.connection:
            self.connection.close()

    def _create_fuel_data_tables(self):
        """
        Creates the fuel data table if it does not exist.
        This method is called during initialization.
        """
        cursor = self.connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                fuel_type TEXT NOT NULL,
                price_per_liter REAL NOT NULL,
                location TEXT NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # C