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
    pass
