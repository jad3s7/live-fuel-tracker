# South Africa Fuel Price Tracker
WTC-VGVK395B


A comprehensive data engineering project that demonstrates the complete lifecycle of data engineering: **Extract, Transform, Load (ETL)**, with automated reporting, comprehensive testing, and live data capabilities through web scraping.

## Project Overview

This project is a South African Fuel Price tracker that:
- Fetches and monitors South African fuel prices (Petrol 95, Petrol 93, Diesel 50ppm, Diesel 500ppm) across Inland and Coastal regions
- Supports multiple data sources: APIs (zaref.dev, fuelsa.co.za), web scraping, and simulated data
- Stores data in a SQLite database
- Transforms and cleans the data (validating prices, normalizing fuel types and regions)
- Generates PDF reports for fuel price trends
- Supports automated pipeline execution, moving averages, rate change analysis, and outlier detection
- Includes comprehensive testing with pytest
- **New: Live data extraction via web scraping from official DMRE sources**

## Tech Stack

- **Language**: Python 3.11 / 3.12
- **Database**: SQLite3
- **Data Processing**: Pandas
- **API Extraction**: Requests
- **Web Scraping**: BeautifulSoup4, lxml
- **PDF Generation**: ReportLab
- **Testing**: Pytest with coverage
- **Configuration**: python-dotenv
- **Build Automation**: Make

## Project Structure

```
live-fuel-tracker/
├── src/
│   ├── data/
│   │   ├── extract.py         # Fuel price extraction (Inland/Coastal, Petrol, Diesel)
│   │   └── transform.py       # Data cleaning, validation, and transformations
│   ├── database/
│   │   └── storage_db.py      # SQLite fuel database operations
│   ├── automation/
│   │   └── pipeline.py        # Complete ETL pipeline orchestration
│   ├── reports/
│   │   └── generate_report.py # PDF report generation
│   ├── visualization/
│   │   └── dashboard.py       # Gradio-based interactive dashboard
│   └── utils/
│       └── config.py          # Configuration management
├── tests/
│   ├── conftest.py            # Pytest configuration and fixtures
│   ├── test_extraction.py     # Tests for extraction module
│   ├── test_database.py       # Tests for database module
│   ├── test_transform.py      # Tests for transformation module
│   └── test_configtest.py     # Tests for configuration
├── reports/                   # Generated PDF reports
├── Makefile                   # Build automation commands
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Pytest configuration
├── .env                       # Environment variables (not in git)
└── README.md                  # This file
```

## Installation & Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Make (optional, for build automation)

### Local Installation

1. **Navigate to the project directory**:
```bash
cd live-fuel-tracker
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

The requirements.txt includes all necessary dependencies including:
- `beautifulsoup4==4.12.2` - For web scraping HTML parsing
- `lxml==4.9.3` - Fast XML/HTML parser for BeautifulSoup
- `requests==2.31.0` - For HTTP requests
- `pandas==2.1.1` - For data processing
- `plotly==5.17.0` - For interactive charts
- `gradio==4.29.0` - For the web dashboard
- `reportlab==4.0.4` - For PDF generation
- `pytest==7.4.2` - For testing

Or use the Makefile:
```bash
make install
```

3. **Set up environment variables**:
Create a `.env` file in the project root with the following configuration:

```bash
# Database
DATABASE_PATH=fuel_rates.db

# Fuel Price API Configuration
# Options: 'simulated' (default), 'zaref', 'fuelsa', 'scrape'
FUEL_API_PROVIDER=simulated
FUEL_API_KEY=
FUEL_API_BASE_URL=
API_TIMEOUT=10

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password

# Dashboard Configuration
DASHBOARD_PORT=8501
DASHBOARD_HOST=localhost

# Automation
AUTO_REFRESH_MINUTES=60
ENABLE_EMAIL_ALERTS=false
```

4. **Configure API provider (optional)**:
By default, the project uses simulated data. To use real fuel price APIs or web scraping, edit `.env`:

```bash
# Options: 'simulated' (default), 'zaref', 'fuelsa', 'scrape'
FUEL_API_PROVIDER=simulated
FUEL_API_KEY=your_api_key_here  # Required for fuelsa.co.za
FUEL_API_BASE_URL=  # Optional custom URL
```

**API Providers:**
- **simulated** (default): Uses demo data, no API key needed
- **zaref.dev**: Paid API ($0.005/call), uses x402 payment protocol
- **fuelsa.co.za**: Subscription API (R59/1000 calls), requires API key
- **scrape**: Web scraping from official DMRE website (free, experimental)

Note: If the API or scraping is unavailable or fails, the system automatically falls back to simulated data.

## Web Scraping Feature

### Overview

The project now includes web scraping capabilities to extract fuel prices directly from the official Department of Mineral Resources and Energy (DMRE) website. This provides a free alternative to paid APIs while still accessing official government data.

### How Web Scraping Works

The web scraping feature:
- Fetches the DMRE fuel prices page (https://www.dmpr.gov.za/Services/Petroleum-Resources/Fuel-Prices)
- Parses HTML content using BeautifulSoup4 with the lxml parser
- Extracts fuel prices using regex patterns to identify fuel types and prices
- Attempts multiple extraction strategies (table parsing, text search, PDF link detection)
- Falls back to simulated data if scraping fails

### Enabling Web Scraping

To enable web scraping, update your `.env` file:

```bash
FUEL_API_PROVIDER=scrape
```

No API key is required for web scraping.

### Dependencies

Web scraping requires the following dependencies (already included in requirements.txt):
- `beautifulsoup4==4.12.2` - HTML parsing library
- `lxml==4.9.3` - Fast XML/HTML parser

### Limitations and Considerations

**Important Limitations:**
- **PDF-based sources**: The DMRE website often publishes fuel prices in PDF format. The current scraper cannot parse PDFs and will fall back to simulated data if prices are only available in PDFs.
- **Fragility**: Web scraping is inherently fragile. Changes to the DMRE website structure, HTML layout, or URL can break the scraper without notice.
- **Rate limiting**: Excessive scraping may trigger rate limiting or IP blocking from the DMRE website.
- **Update frequency**: Official fuel prices are updated monthly (first Wednesday of each month), so frequent scraping is unnecessary.

**Best Practices:**
- Use web scraping only for personal, non-commercial use
- Respect the website's terms of service and robots.txt
- Implement reasonable delays between requests if running frequent checks
- Monitor scraper logs for failures and be prepared to update parsing logic
- Consider using paid APIs (zaref.dev, fuelsa.co.za) for production use

### Troubleshooting Web Scraping Issues

If web scraping fails:

1. **Check the logs**: The pipeline will log specific error messages when scraping fails
2. **Verify website accessibility**: Ensure the DMRE website is accessible and not blocked
3. **Check for structural changes**: The website may have changed its HTML structure
4. **Fallback behavior**: The system automatically falls back to simulated data if scraping fails
5. **Update extraction logic**: If the website structure changed, you may need to update the regex patterns in `src/data/extract.py`
6. **Try alternative providers**: Switch to zaref.dev, fuelsa.co.za, or simulated data in your `.env` file

Common error messages:
- `DMRE website returned status code: XXX` - Website access issue
- `Error scraping DMRE website: ...` - Parsing or network error
- `Found X PDF links, but PDF parsing not implemented` - Data only available in PDFs

## Usage

### Running the ETL Pipeline

Execute the complete data pipeline:

```bash
python src/automation/pipeline.py
```

Or using Make:
```bash
make pipeline
```

### Running the Dashboard

Launch the interactive Gradio dashboard:

```bash
python src/visualization/dashboard.py
```

The dashboard will be available at http://localhost:8501 (or the port configured in `.env`).

### Running Tests

Execute the test suite:

```bash
pytest tests/ -v
```

Or using Make:
```bash
make test
```

### Available Make Commands

```bash
make help          # Show all available commands
make install       # Install Python dependencies
make test          # Run tests
make test-verbose  # Run tests with verbose output
make pipeline      # Run ETL pipeline
```

## API Configuration

### Supported API Providers

The project supports four data sources for South African fuel prices:

#### 1. **Simulated Data (Default)**
- No API key required
- Uses realistic base prices with small random variations
- Perfect for development, testing, and demonstration
- Always available

#### 2. **zaref.dev**
- Cost: $0.005 per call
- Data: Official South African fuel prices (petrol 93/95, diesel 50ppm/500ppm)
- Payment: Uses x402 payment protocol (cryptocurrency-based micro-payments)
- Frequency: Updates monthly (first Wednesday of each month)
- Setup: No traditional API key needed, but requires x402 client for payment
- Documentation: https://zaref.dev/docs/fuel-price-api

#### 3. **fuelsa.co.za**
- Cost: R59 per 1,000 requests/month
- Data: Historical and current fuel prices since 2008
- Payment: Subscription-based with API key authentication
- Frequency: Real-time updates
- Setup: Requires API key from fuelsa.co.za account
- Documentation: https://www.fuelsa.co.za/

#### 4. **Web Scraping (New)**
- Cost: Free
- Data: Official fuel prices from DMRE website
- Source: https://www.dmpr.gov.za/Services/Petroleum-Resources/Fuel-Prices
- Frequency: Updates monthly (first Wednesday of each month)
- Setup: No API key required, just set `FUEL_API_PROVIDER=scrape`
- Limitations: May fail if data is only in PDF format or website structure changes
- Dependencies: beautifulsoup4, lxml

### Configuration Steps

1. **Edit `.env` file:**
```bash
# Choose your API provider
FUEL_API_PROVIDER=simulated  # Options: simulated, zaref, fuelsa, scrape

# Add API key (required for fuelsa.co.za)
FUEL_API_KEY=your_api_key_here

# Optional: Custom API base URL
FUEL_API_BASE_URL=
```

2. **For zaref.dev:**
- Set `FUEL_API_PROVIDER=zaref`
- The API uses x402 payment protocol
- First requests will return HTTP 402 with payment instructions
- You'll need an x402 client to handle payments automatically
- See: https://zaref.dev/docs/x402

3. **For fuelsa.co.za:**
- Set `FUEL_API_PROVIDER=fuelsa`
- Sign up at https://www.fuelsa.co.za/ for an account
- Get your API key from the dashboard
- Set `FUEL_API_KEY=your_actual_api_key`
- The system will authenticate using Bearer token

4. **For Web Scraping:**
- Set `FUEL_API_PROVIDER=scrape`
- No API key required
- Ensure beautifulsoup4 and lxml are installed (included in requirements.txt)
- The scraper will attempt to extract prices from the DMRE website
- Falls back to simulated data if scraping fails

### Fallback Behavior

The system is designed to be resilient:
- If the API or scraping is unavailable, it automatically falls back to simulated data
- Invalid API responses are handled gracefully
- Network timeouts trigger fallback to simulated data
- Logs indicate when fallback occurs

### Testing API Configuration

Test your API configuration:

```bash
# Test with simulated data (default)
python -c "from src.data.extract import FuelExtractor; e = FuelExtractor(api_provider='simulated', api_key='', base_url=''); print(e.get_current_prices())"

# Test with zaref (will fall back if no payment setup)
python -c "from src.data.extract import FuelExtractor; e = FuelExtractor(api_provider='zaref', api_key='', base_url=''); print(e.get_current_prices())"

# Test with fuelsa (requires valid API key)
python -c "from src.data.extract import FuelExtractor; e = FuelExtractor(api_provider='fuelsa', api_key='your_key', base_url=''); print(e.get_current_prices())"

# Test with web scraping
python -c "from src.data.extract import FuelExtractor; e = FuelExtractor(api_provider='scrape', api_key='', base_url=''); print(e.get_current_prices())"
```

## Automation and Scheduling

### Overview

To keep your fuel price data up-to-date, you can automate the ETL pipeline to run on a regular schedule. Since South African fuel prices are officially updated on the first Wednesday of each month, a monthly schedule is recommended.

### Recommended Update Frequency

**Best Practice**: Run the pipeline monthly on the first Wednesday of the month, as this is when the Department of Mineral Resources and Energy (DMRE) officially updates fuel prices.

Alternative schedules:
- **Weekly**: Run every Wednesday to catch any mid-month adjustments
- **Daily**: Only necessary if using real-time APIs (fuelsa.co.za)
- **On-demand**: Run manually when needed

### Setting Up Cron Jobs (Linux/macOS)

1. **Open your crontab**:
```bash
crontab -e
```

2. **Add a cron job** to run the pipeline monthly on the first Wednesday at 9:00 AM:
```bash
0 9 1-7 * Wed python /path/to/live-fuel-tracker/src/automation/pipeline.py >> /path/to/live-fuel-tracker/logs/cron.log 2>&1
```

This runs:
- At 9:00 AM (0 9)
- On days 1-7 of the month (1-7)
- Only on Wednesdays (Wed)
- Logs output to `logs/cron.log`

3. **For weekly execution (every Wednesday at 9:00 AM)**:
```bash
0 9 * * Wed python /path/to/live-fuel-tracker/src/automation/pipeline.py >> /path/to/live-fuel-tracker/logs/cron.log 2>&1
```

4. **For daily execution (every day at 9:00 AM)**:
```bash
0 9 * * * python /path/to/live-fuel-tracker/src/automation/pipeline.py >> /path/to/live-fuel-tracker/logs/cron.log 2>&1
```

**Important**: Ensure you use absolute paths in cron jobs and that the Python environment has all required dependencies installed.

### Setting Up Task Scheduler (Windows)

1. **Open Task Scheduler**:
   - Press `Win + R`, type `taskschd.msc`, and press Enter

2. **Create a new task**:
   - Click "Create Task" in the right panel
   - Name: "Fuel Price Tracker ETL Pipeline"
   - Description: "Automated fuel price data extraction and storage"

3. **Configure the trigger**:
   - Go to the "Triggers" tab
   - Click "New"
   - For monthly on first Wednesday:
     - Select "Monthly"
     - Set "Start" on the first Wednesday of each month
     - Set the desired time (e.g., 9:00 AM)
   - Click OK

4. **Configure the action**:
   - Go to the "Actions" tab
   - Click "New"
   - Action: "Start a program"
   - Program/script: `C:\Python311\python.exe` (or your Python path)
   - Add arguments: `C:\path\to\live-fuel-tracker\src\automation\pipeline.py`
   - Start in: `C:\path\to\live-fuel-tracker`
   - Click OK

5. **Save the task**:
   - Click OK to save the task
   - Test by right-clicking and selecting "Run"

### Alternative: Using Python Scripts

You can also create a Python script to handle scheduling:

```python
# scheduler.py
import schedule
import time
import subprocess
import sys
import os

def run_pipeline():
    """Run the ETL pipeline"""
    try:
        result = subprocess.run(
            [sys.executable, 'src/automation/pipeline.py'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running pipeline: {e}")
        return False

# Schedule the pipeline
# Run every Wednesday at 9:00 AM
schedule.every().wednesday.at("09:00").do(run_pipeline)

# Or run on the first Wednesday of the month
def first_wednesday():
    from datetime import datetime
    today = datetime.now()
    if today.weekday() == 2 and today.day <= 7:  # Wednesday (2) and day 1-7
        return run_pipeline()
    return False

schedule.every().day.at("09:00").do(first_wednesday)

print("Scheduler started. Press Ctrl+C to exit.")
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

Run this with:
```bash
python scheduler.py
```

Note: This requires the `schedule` package (`pip install schedule`).

### Monitoring Automated Runs

To monitor your automated pipeline runs:

1. **Check logs**: The pipeline outputs to stdout/stderr, which you can redirect to a log file
2. **Database inspection**: Check the database for new records after each run
3. **Email alerts**: Configure email alerts in `.env` to receive notifications:
   ```bash
   ENABLE_EMAIL_ALERTS=true
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_password
   ```

## Data Engineering Concepts Demonstrated

### 1. **Extract (Data Extraction)**
- Fetching fuel price data across South African fuel types (Petrol 95, Petrol 93, Diesel 50ppm, Diesel 500ppm) and regions (Inland, Coastal)
- Multiple data source support: APIs (zaref.dev, fuelsa.co.za), web scraping, and simulated fallback
- Web scraping with BeautifulSoup4 and lxml for HTML parsing
- Error handling, timeouts, and automatic fallback to simulated data
- JSON data formatting and regional comparisons

**Key File**: `src/data/extract.py`

### 2. **Transform (Data Transformation)**
- Cleaning and validating prices against realistic South African thresholds
- Normalizing fuel types and regional locations (Inland, Coastal, Gauteng, Western Cape, etc.)
- Calculating derived metrics (moving averages, price differences, percentage changes)
- Outlier detection with z-scores and data quality metrics

**Key File**: `src/data/transform.py`

### 3. **Load (Data Storage)**
- SQLite database design and schema creation (`fuel_data` table with indexes on timestamp, fuel_type, and location)
- Batch insertion for performance
- Querying by date range, fuel type, and location
- Aggregating statistics (min, max, average fuel prices)

**Key File**: `src/database/storage_db.py`

### 4. **Reporting**
- PDF report generation for fuel price trends
- Professional formatting with ReportLab

**Key File**: `src/reports/generate_report.py`

### 5. **Automation**
- Orchestrated ETL pipeline execution
- Automated metrics logging and database population
- Support for scheduled execution via cron or task scheduler

**Key File**: `src/automation/pipeline.py`

### 6. **Visualization**
- Interactive Gradio-based dashboard with dark theme
- Real-time filtering by fuel type and region
- Interactive charts using Plotly
- Statistics cards with dynamic updates

**Key File**: `src/visualization/dashboard.py`

### 7. **Testing**
- Comprehensive unit tests with pytest
- Fixtures, edge case tests, quality assertions
- Test coverage reporting

**Key Files**: `tests/test_extraction.py`, `tests/test_transform.py`, `tests/test_database.py`

### 8. **Configuration Management**
- Centralized configuration through environment variables
- Database path, API settings, email configuration, dashboard settings
- Email alert configuration and automation settings
- Support for multiple data providers including web scraping

**Key File**: `src/utils/config.py`

## License

This project is created for educational and demonstration purposes. Fuel prices in South Africa are regulated by the Department of Mineral Resources and Energy (DMRE).
