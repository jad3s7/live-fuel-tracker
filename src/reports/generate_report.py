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


    # Build the document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Customize the document
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#4a4e69'),
        spaceAfter=12
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#0f3460'),
        spaceBefore=12,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#22223b')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1a1a2e'),
        alignment=1
    )

    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
    )

    story = []


    # Header Title
    story.append(Paragraph("South African Fuel Tracker Price Report (ZAR)", title_style))
    now_str = datetime.now().strftime('%d %B %Y, %H:%M:%S')
    story.append(Paragraph(f"Official & Regulated Benchmark Tracking: Generated_ {now_str}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0343ce"), spaceAfter=14)
    
    
    # Executive Summary Box: Contains analysis
    story.append(Paragraph("1: Executive Summary & National Overview", section_heading))

    total_records = overall_stats.get('total_records', 0)
    avg_price = overall_stats.get('avg_price', 0.0)
    min_price = overall_stats.get('min_price', 0.0)
    max_price = overall_stats.get('max_price', 0.0)

    exec_data = [
        [
            Paragraph("<b>Total Tracked Records</b>", table_header_style),
            Paragraph("<b>National Average</b>", table_header_style),
            Paragraph("<b>Lowest Recorded Price</b>", table_header_style),
            Paragraph("<b>Highest Recorded Price</b>",table_header_style)
        ],
        [
            Paragraph(f"{total_records}", table_cell_style),
            Paragraph(f"R{avg_price:.2f} / L", table_cell_style),
            Paragraph(f"R{min_price:.2f} / L", table_cell_style),
            Paragraph(f"R{max_price:.2f} / L", table_cell_style)
        ]
    ]

    kpi_table = Table(kpi_data, colWidths=[130, 130, 130, 130])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f0f4f8')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 14))
)


def _generate_pdf_report(db_path = None, output_dir = None) -> str:
    pass

if __name__ == '__main__':
    print("Generating South African Fuel Price Rand PDF Report...")
    pdf_path = _generate_pdf_report()
    print(f"Report generated successfully: {pdf_path}")

