# South Africa Fuel Price Tracker
WTC-VGVK395B


A comprehensive data engineering project that demonstrates the complete lifecycle of data engineering: **Extract, Transform, Load (ETL)**, with automated reporting and comprehensive testing.

## Project Overview

This project is a South African Fuel Price tracker that:
- Fetches and monitors South African fuel prices (Petrol 95, Petrol 93, Diesel 50ppm, Diesel 500ppm) across Inland and Coastal regions
- Stores data in a SQLite database
- Transforms and cleans the data (validating prices, normalizing fuel types and regions)
- Generates PDF reports for fuel price trends
- Supports automated pipeline execution, moving averages, rate change analysis, and outlier detection
- Includes comprehensive testing with pytest

## Tech Stack

- **Language**: Python 3.11 / 3.12
- **Database**: SQLite3
- **Data Processing**: Pandas
- **API Extraction**: Requests
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
# Options: 'simulated' (default), 'zaref', 'fuelsa'
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
By default, the project uses simulated data. To use real fuel price APIs, edit `.env`:

```bash
# Options: 'simulated' (default), 'zaref', 'fuelsa'
FUEL_API_PROVIDER=simulated
FUEL_API_KEY=your_api_key_here  # Required for fuelsa.co.za
FUEL_API_BASE_URL=  # Optional custom URL
```

**API Providers:**
- **simulated** (default): Uses demo data, no API key needed
- **zaref.dev**: Paid API ($0.005/call), uses x402 payment protocol
- **fuelsa.co.za**: Subscription API (R59/1000 calls), requires API key

Note: If the API is unavailable or fails, the system automatically falls back to simulated data.

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

The project supports three data sources for South African fuel prices:

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

### Configuration Steps

1. **Edit `.env` file:**
```bash
# Choose your API provider
FUEL_API_PROVIDER=simulated  # Options: simulated, zaref, fuelsa

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

### Fallback Behavior

The system is designed to be resilient:
- If the API is unavailable, it automatically falls back to simulated data
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
```

## Data Engineering Concepts Demonstrated

### 1. **Extract (Data Extraction)**
- Fetching fuel price data across South African fuel types (Petrol 95, Petrol 93, Diesel 50ppm, Diesel 500ppm) and regions (Inland, Coastal)
- Multiple API provider support (zaref.dev, fuelsa.co.za, simulated fallback)
- Error handling, timeouts, and automatic fallback to simulated data
- JSON data formatting and regional comparisons

**Key File**: <ref_file file="/home/jades/WeThinkCode/Data/live-fuel-tracker/src/data/extract.py" />

### 2. **Transform (Data Transformation)**
- Cleaning and validating prices against realistic South African thresholds
- Normalizing fuel types and regional locations (Inland, Coastal, Gauteng, Western Cape, etc.)
- Calculating derived metrics (moving averages, price differences, percentage changes)
- Outlier detection with z-scores and data quality metrics

**Key File**: <ref_file file="/home/jades/WeThinkCode/Data/live-fuel-tracker/src/data/transform.py" />

### 3. **Load (Data Storage)**
- SQLite database design and schema creation (`fuel_data` table with indexes on timestamp, fuel_type, and location)
- Batch insertion for performance
- Querying by date range, fuel type, and location
- Aggregating statistics (min, max, average fuel prices)

**Key File**: <ref_file file="/home/jades/WeThinkCode/Data/live-fuel-tracker/src/database/storage_db.py" />

### 4. **Reporting**
- PDF report generation for fuel price trends
- Professional formatting with ReportLab

**Key File**: <ref_file file="/home/jades/WeThinkCode/Data/live-fuel-tracker/src/reports/generate_report.py" />

### 5. **Automation**
- Orchestrated ETL pipeline execution
- Automated metrics logging and database population

**Key File**: <ref_file file="/home/jades/WeThinkCode/Data/live-fuel-tracker/src/automation/pipeline.py" />

### 6. **Testing**
- Comprehensive unit tests with pytest
- Fixtures, edge case tests, quality assertions
- Test coverage reporting

**Key Files**: <ref_file file="/home/jades/WeThinkCode/Data/live-fuel-tracker/tests/test_extraction.py" />, <ref_file file="/home/jades/WeThinkCode/Data/live-fuel-tracker/tests/test_transform.py" />, <ref_file file="/home/jades/WeThinkCode/Data/live-fuel-tracker/tests/test_database.py" />

### 7. **Configuration Management**
- Centralized configuration through environment variables
- Database path, API settings, email configuration, dashboard settings
- Email alert configuration and automation settings

**Key File**: <ref_file file="/home/jades/WeThinkCode/Data/live-fuel-tracker/src/utils/config.py" />

## License

This project is created for educational and demonstration purposes. Fuel prices in South Africa are regulated by the Department of Mineral Resources and Energy (DMRE).