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

    def _get_latest_prices(self, limit: int = 10, fuel_type: str = None, location: str = None ) -> list:
        """ 
        Retrieves the most recent fuel prices from the database.

        Args:
            limit: max number of records to return.
        
        Returns:
            List of dictionaries containing fuel price data.
        """
        try:
            cursor = self.connection.cursor()

            query = "SELECT timestamp, fuel_type, price_per_liter, location, source FROM fuel_data"
            params: list = []
            conditions: list = []

            if fuel_type:
                conditions.append("fuel-type = ?")
                params.append(fuel_type)
            if location:
                conditions.append("location = ?")
                params.append(location)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

            result = [
                {
                    'timestamp': row[0],
                    'fuel_type': row[1],
                    'price_per_liter': row[2],
                    'rate': row[2],
                    'price': row[2],
                    'location': row[3],
                    'region': row[3],
                    'source': row[4],
                    'currency': 'ZAR'

                }
                for row in rows
            ]
            return result

        except Exception as error:
            print(f"Error getting latest fuel prices: {error}")
            return []

    def _get_prices_by_date_range(self, start_date: str, end_date: str, fuel_type: str = None, location: str = None) -> list:
        """ 
        Retrieves fuel prices within a specific date range.

        Args:
            start_date: start date in 'YYYY-MM-DD' or timestamp format
            end_date: end date in 'YYYY-MM-DD' or timestamp format
            fuel_type: filter by fuel type
            location: filter by location or region

        Returns:
            List of dicts containing fuel price information.    
        """

        try:
            cursor = self.connection.cursor()

            query = "SELECT timestamp, fuel_type, price_per_liter, location, source FROM fuel_data WHERE timestamp >= ? AND timestamp <= ?"
            params: list = [start_date, end_date]

            if fuel_type:
                query += " AND fuel_type = ?"
                params.append(fuel_type)

            if location:
                query += " AND location = ?"
                params.append(location)

            query += " ORDER BY timestamp ASC"
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
    
            result = [
                {
                    'timestamp': row[0],
                    'fuel_type': row[1],
                    'price_per_liter': row[2],
                    'rate': row[2],
                    'price': row[2],
                    'location': row[3],
                    'region': row[3],
                    'source': row[4],
                    'currency': 'ZAR'
                }
                for row in rows
            ]
            return result

        except Exception as error:
            print(f"Error getting fuel prices by date range: {error}")
            return []

    def _get_statistics(self, fuel_type: str = None, location: str = None) -> dict:
        """
        Calculate and return statistics about the stored fuel prices.

        Args: 
            fuel_type: filter by fuel type
            location: filter by location / region

        Returns:
            Dict containing stats (
            total_records, min_price, 
            max_price, avg_price)
        """
        try: 
            cursor = self.connection.cursor()

            query = '''
                SELECT
                    COUNT(*) as total_records,
                    MIN(price_per_liter) as min_price,
                    MAX(price_per_liter) as max_price,
                    AVG(price_per_liter) as avg_price,
                FROM fuel_data
            '''
            params: list = []
            conditions: list = []

            if fuel_type:
                conditions.append("fuel_type = ?")
                params.append(fuel_type)

            if location:
                conditions.append("location = ?")
                params.append(location)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            cursor.execute(query, tuple(params))
            row = cursor.fetchone()

            total_records = row[0] if row and row[0] is not None else 0
            min_val = row[1] if row and row[1] is not None else 0.0
            max_val = row[2] if row and row[2] is not None else 0.0
            avg_val = round(row[3], 4) if row and row[3] is not None else 0.0

            statistics = {
                'total_records': total_records,
                'min_price': min_val,
                'max_price': max_val,
                'avg_price': avg_val,
                'min_rate': min_val,
                'max_rate': min_val,
                'avg_rate': avg_val
            }
            return statistics
        except Exception as error:
            print(f"Error getting statistics: {error}")
            return {
                'total_records': 0,
                'min_price': 0.0,
                'max_price': 0.0,
                'avg_price': 0.0,
                'min_rate': 0.0,
                'max_rate': 0.0,
                'avg_rate': 0.0,
            }

    def close(self):
            """
            Close the database connection.
            This method should be called when done with the database.
            """
            if self.connection:
                self.connection.close()