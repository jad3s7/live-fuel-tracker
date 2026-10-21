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
        self._create_tables()
    
    def close(self):
        """
        Close the database connection.
        This method should be called when done with the database.
        """
        if self.connection:
            self.connection.close()


    def _create_tables(self):
        """
        Creates the fuel data table if it does not exist.
        This method is called during initialization.
        """
        cursor = self.connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_data(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                fuel_type TEXT NOT NULL,
                price_per_liter REAL NOT NULL,
                location TEXT NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create index on timestamp for faster queries.
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON fuel_data(timestamp)
        ''')

        # Create index on fuel_type for faster queries/
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_fuel_type
            ON fuel_data(fuel_type)
        ''')

        # Create index on location for faster queries.
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_location
            ON fuel_data(location)
        ''')

        self.connection.commit()

    def _insert_price_database(self, fuel_data: dict) -> bool:
        """
        Inserts a single fuel price into database.

        Args:
            fuel_data: Dict with fuel information.
            (timestamp, fuel_type, price_per_liter, location and source)

        Returns:
            True if insertion was good g, false otherwise.
        """
        try:
            cursor = self.connection.cursor()

            timestamp = fuel_data.get('timestamp')
            fuel_type = fuel_data.get('fuel_type') or 'Petrol 95'
            price = fuel_data.get('price_per_liter', fuel_data.get('rate', fuel_data.get('price', 0.0)))
            location = fuel_data.get('location') or fuel_data.get('region') or 'Inland'
            source = fuel_data.get('source') or 'DMRE'

            cursor.execute('''
                INSERT INTO fuel_data (timestamp, fuel_type, price_per_liter, location, source)
                VALUES (?, ?, ?, ?, ?)
                ''', (timestamp, fuel_type, price, location, source))
            
            self.connection.commit()
            return True

        except Exception as error:
            print(f"Error inserting fuel price into database: {error}")
            self.connection.rollback()
            return False

    def _insert_price_database_multiple(self, fuel_data_list: list) -> int:
        """
        Insert multiple fuel prices into the database in a single transaction.

        Args:
            fuel_data_list: list of dictionaries containing fuel data.

        Returns:
            Number of successfully insert records.
        """
        if not fuel_data_list:
            return 0

        try:
            cursor = self.connection.cursor()

            insert_data = [
                (
                    fuel.get('timestamp'),
                    fuel.get('fuel_type') or 'Petrol 95',
                    fuel.get('price_per_liter', fuel.get('rate', fuel.get('price', 0.0))),
                    fuel.get('location') or fuel.get('region') or 'Inland',
                    fuel.get('source') or 'DMRE'


                )
                for fuel in fuel_data_list
            ]

            cursor.executemany('''
                INSERT INTO fuel_data(timestamp, fuel_type, price_per_liter, location, source)
                VALUES (?, ?, ?, ?, ?)
                ''', insert_data)
            
            self.connection.commit()
            return cursor.rowcount
        
        # Try and except catches the empty price here.
        except Exception as error:
            print(f'Error inserting multiple fuel prices: {error}')
            return 0
        


        


  