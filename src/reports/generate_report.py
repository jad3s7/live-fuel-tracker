"""
Fuel Price PDF Report Generator
This script generates professional PDF reports for South African Fuel price trends using ReportLab.
"""

import os 
import sys
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle, 
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from src.database.storage_db import FuelDatabase
from src.data.transform import DataTransformer
from src.utils.config import config

class FuelReportGenerator:
    """
    Generates PDF reports summarizing South African fuel price movements,
    regional differentials (Inland vs Coastal), statistics, and data quality metrics.
    """

    def __init__(self, db_path = None, output_dir = None):
        """
        Initializes the report generator.

        Args:
            db_path: Path to SQlite fuel database (defaults to config.database_path)
            output_dir: Directory where generated PDF reports are saved.
        """
        self.db_path = db_path or config.get_database_path()
        self.output_dir = output_dir or config.reports_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.transformer = DataTransformer()

    def _generate_report(self, filename:str = None) -> str:
            """
    Generates the PDF report.

    Args:
        filename: output file (will default to timestamped name)

    Returns:
        Absolute file path to the generated PDF report.
    """
    if not filename: 
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"fuel_report_{timestamp_str}.pdf"
    
    output_path = os.path.join(self.output_dir, filename)

    # Retrieve data from database
    db = FuelDatabase(self.db_path)
    latest_prices = db._get_latest_prices(limit=100)
    overall_stats = db._get_statistics()
    db.close()
    

def _generate_pdf_report(db_path = None, output_dir = None) -> str:
    pass

if __name__ == '__main__':
    print("Generating South African Fuel Price Rand PDF Report...")
    pdf_path = _generate_pdf_report()
    print(f"Report generated successfully: {pdf_path}")

