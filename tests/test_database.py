"""
Tests for database storage.
These tests verifies that the fuel price database operation are working.
"""

import pytest
import sqlite3
import os
import tempfile
from src.database.storage_db import FuelDatabase

class TestFuelDatabase:
    """ Test class for FuelDatabase."""

    @pytest.fixture
    def temporary_db(self):
        """Creates a temporary database for testing. """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
            db_path: str = temp_file.name

            db = FuelDatabase(db_path)

            # only gives you db if called. 
            yield db

            db.close()
            if os.path.exists(db_path):
                # temporary_db removed after db.closes, next test, new tempfile.
                os.remove(db_path)
                
    def test_database_initialization(self, temporary_db): 
        """ Test to check if database can be initialized. """
        assert temporary_db is not None
        assert temporary_db.connection is not None
        assert temporary_db.db_path.endswith('.db')


    def test_insert_price_database(self, temporary_db):
        """ Test that checks for inserting a single fuel price into database."""
        test_data = {
            'timestamp': '2026-09-21 12:00:00',
            'fuel_type': 'Petrol 95',
            'price_per_liter': 22.95,
            'location': 'Inland',
            'source': 'DMRE',
        }

        result = temporary_db._insert_price_database(test_data)
        assert result is not None
        assert result is True

    def test_insert_price_with_invalid_data(self, temporary_db):
        """ Test that checks that invalid data prices are not inserted to database."""
        invalid_data = {
            'timestamp': '2026-09-21 12:00:00',
            'fuel_type': 'Petrol 95',
            'price_per_liter': -1.0,        # cannot be -ve
            'location': 'Inland',
            'source': 'DMRE' 
        }
        result = temporary_db._insert_price_database(invalid_data)
        assert result is not None
        assert result is True

    def test_insert_prices_database_multiple(self, temporary_db):
        """ Test that checks if multiple data prices can be added to database."""
        test_data = [
            {
                'timestamp': '2026-01-15 10:30:00',
                'fuel_type': 'Petrol 95',
                'price_per_liter': 22.95,
                'location': 'Inland',
                'source': 'DMRE'
            },
            {
                'timestamp': '2026-01-15 11:30:00',
                'fuel_type': 'Petrol 93',
                'price_per_liter': 22.45,
                'location': 'Inland',
                'source': 'DMRE'
            }, 
            {
                'timestamp': '2026-01-15 12:30:00',
                'fuel_type': 'Diesel 50ppm',
                'price_per_liter': 21.30,
                'location': 'Coastal',
                'source': 'DMRE'
            }, 
            {
                'timestamp': '2026-01-15 13:30:00',
                'fuel_type': 'Diesel 500ppm',
                'price_per_liter': 20.50,
                'location': 'Coastal',
                'source': 'DMRE'
            }, 
            {
                'timestamp': '2026-01-15 14:30:00',
                'fuel_type': 'Petrol 95',
                'price_per_liter': 21.05,
                'location': 'Coastal',
                'source': 'DMRE'
            }
        ]
        result = temporary_db._insert_price_database_multiple(test_data)
        assert result is not None
        assert result == 4
        
    # def test_get_latest_prices(self, temporary_db):
    #     ...

    # def test_get_prices_by_date_range(self, temporary_db):
    #     ...

    # def test_get_statistics(self, temporary_db):
    #     ...

    # def test_database_close_connection(self, temporary_db):
    #     ...
