# South Africa Fuel vs Rand Tracker

A comprehensive data engineering project that demonstrates the complete lifecycle of data engineering: **Extract, Transform, Load (ETL)**, with automated reporting, visualization, and fullstack deployment.

## Project Overview

This project is a live South African Fuel Price tracker (Fuel vs Rand - ZAR) that:
- Fetches and monitors South African fuel prices (Petrol 95, Petrol 93, Diesel 50ppm, Diesel 500ppm) across Inland and Coastal regions
- Stores data in a SQLite database
- Transforms and cleans the data (validating prices, normalizing fuel types and regions)
- Visualizes data through an interactive Streamlit dashboard and a modern React + FastAPI fullstack interface
- Supports automated pipeline execution, moving averages, rate change analysis, and outlier detection
- Includes comprehensive testing and CI/CD automation

## Tech Stack

- **Language**: Python 3.11 / 3.12
- **Database**: SQLite3
- **Dashboards**: Streamlit & React (Vite + Chart.js)
- **Backend API**: FastAPI + Uvicorn
- **Data Processing**: Pandas
- **API Extraction**: Requests
- **PDF Generation**: ReportLab
- **Testing**: Pytest
- **Containerization**: Docker
- **Build Automation**: Make

## Project Structure

```
live-usd-zar-tracker/
├── src/
│   ├── data/
│   │   ├── extract_data.py    # Fuel price extraction (Inland/Coastal, Petrol, Diesel)
│   │   └── transform_data.py  # Data cleaning, validation, and transformations
│   ├── database/
│   │   └── storage_db.py      # SQLite fuel database operations
│   ├── visualization/
│   │   └── dashboard.py       # Streamlit interactive web dashboard
│   ├── automation/
│   │   └── pipeline.py        # Complete ETL pipeline orchestration
│   └── utils/
│       └── config.py          # Configuration management
├── backend/
│   └── main.py                # FastAPI REST backend for frontend integration
├── frontend/                  # React + Vite dashboard
│   ├── src/
│   │   ├── App.jsx            # React fuel dashboard component with charts
│   │   └── index.css          # Styling & glassmorphism theme
├── tests/
│   ├── test_extraction.py     # Tests for extraction module
│   ├── test_database.py       # Tests for database module
│   └── test_transformation.py # Tests for transformation module
├── reports/                   # Generated reports
├── logs/                      # Application logs
├── Dockerfile                 # Docker container definition
├── Makefile                   # Build automation commands
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation & Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Node.js & npm (optional, for React frontend)
- Docker (optional, for containerization)
- Make (optional, for build automation)

### Local Installation

1. **Navigate to the project directory**:
```bash
cd live-usd-zar-tracker
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
```bash
cp .env.example .env
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

### Docker Installation

1. **Build the Docker image**:
```bash
make docker-build
```

2. **Run the container**:
```bash
make docker-run
```

The dashboard will be available at `http://localhost:8501`

## Usage

### Running the Streamlit Dashboard

Start the interactive web dashboard:

```bash
streamlit run src/visualization/dashboard.py
```

Or using Make:
```bash
make dashboard
```

### Running the Fullstack React + FastAPI App

Start the FastAPI backend:
```bash
make backend
```

Start the React frontend:
```bash
make frontend
```

Or start both in parallel:
```bash
make fullstack
```

### Running the ETL Pipeline

Execute the complete data pipeline:

```bash
python src/automation/pipeline.py
```

Or using Make:
```bash
make pipeline
```

### Loading Historical Data

Load sample historical fuel price data for testing:

```bash
make load-data
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
make dashboard     # Start the Streamlit dashboard
make backend       # Start FastAPI server
make frontend      # Start React frontend
make fullstack     # Start both frontend and backend
make pipeline      # Run ETL pipeline
make load-data     # Load sample historical fuel data
make docker-build  # Build Docker image
make docker-run    # Run Docker container
make clean         # Clean generated files
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
python -c "from src.data.extract_data import FuelExtractor; e = FuelExtractor(); print(e.get_current_prices())"

# Test with zaref (will fall back if no payment setup)
python -c "from src.data.extract_data import FuelExtractor; e = FuelExtractor(api_provider='zaref'); print(e.get_current_prices())"

# Test with fuelsa (requires valid API key)
python -c "from src.data.extract_data import FuelExtractor; e = FuelExtractor(api_provider='fuelsa', api_key='your_key'); print(e.get_current_prices())"
```

## Data Engineering Concepts Demonstrated

### 1. **Extract (Data Extraction)**
- Fetching fuel price data across South African fuel types (Petrol 95, Petrol 93, Diesel 50ppm, Diesel 500ppm) and regions (Inland, Coastal)
- Multiple API provider support (zaref.dev, fuelsa.co.za, simulated fallback)
- Error handling, timeouts, and automatic fallback to simulated data
- JSON data formatting and regional comparisons

**Key File**: [extract_data.py](file:///home/jades/WeThinkCode/Data/live-usd-zar-tracker/src/data/extract_data.py)

### 2. **Transform (Data Transformation)**
- Cleaning and validating prices against realistic South African thresholds
- Normalizing fuel types and regional locations (Inland, Coastal, Gauteng, Western Cape, etc.)
- Calculating derived metrics (moving averages, price differences, percentage changes)
- Outlier detection with z-scores and data quality metrics

**Key File**: [transform_data.py](file:///home/jades/WeThinkCode/Data/live-usd-zar-tracker/src/data/transform_data.py)

### 3. **Load (Data Storage)**
- SQLite database design and schema creation (`fuel_rates` table with index on timestamp, fuel_type, and location)
- Batch insertion for performance
- Querying by date range, fuel type, and location
- Aggregating statistics (min, max, average fuel prices)

**Key File**: [storage_db.py](file:///home/jades/WeThinkCode/Data/live-usd-zar-tracker/src/database/storage_db.py)

### 4. **Visualization**
- Interactive dashboards using Streamlit and React
- Time series charts, distribution histograms, moving average overlays
- Dynamic filters for fuel type and location

**Key Files**: [dashboard.py](file:///home/jades/WeThinkCode/Data/live-usd-zar-tracker/src/visualization/dashboard.py), [App.jsx](file:///home/jades/WeThinkCode/Data/live-usd-zar-tracker/frontend/src/App.jsx)

### 5. **Automation**
- Orchestrated ETL pipeline execution
- Automated metrics logging and database population

**Key File**: [pipeline.py](file:///home/jades/WeThinkCode/Data/live-usd-zar-tracker/src/automation/pipeline.py)

### 6. **Testing**
- Comprehensive unit tests with pytest
- Fixtures, edge case tests, quality assertions

**Key Files**: `tests/test_*.py`

## License

This project is created for educational and demonstration purposes. Fuel prices in South Africa are regulated by the Department of Mineral Resources and Energy (DMRE).