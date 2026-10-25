# Variables:
PYTHON := venv/bin/python
PIP := $(PYTHON) -m pip
PROJECT_NAME := live-fuel-tracker

BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[0;33m
NC := \033[0m 

help:
	@echo "$(BLUE)SOUTH AFRICAN FUEL PRICE TRACKER - Available Commands:$(NC)"
	@echo ""
	@echo "$(GREEN)Development Commands:$(NC)"
	@echo "  make install       - Install Python dependencies"
	@echo "  make test          - Run pytest tests"
	@echo "  make test-verbose  - Run tests with verbose output"
	@echo ""
	@echo "$(GREEN)Pipeline Commands:$(NC)"
	@echo "  make pipeline      - Run ETL pipeline"
	@echo "  make update        - Run one-time fuel price update"
	@echo ""
	@echo "$(GREEN)Dashboard Commands:$(NC)"
	@echo "  make dashboard     - Launch Gradio dashboard"
	@echo ""
	@echo "$(GREEN)Scheduling Commands:$(NC)"
	@echo "  make setup-cron    - Set up cron job for automated updates"
	@echo "  make show-cron     - Show current cron jobs"
	@echo "  make remove-cron   - Remove fuel price tracker cron job"
	@echo ""
	@echo "$(GREEN)Monitoring Commands:$(NC)"
	@echo "  make stats         - Show database statistics"

# Install dependencies
install:
	@echo "$(BLUE)Installing Project / Python dependencies ...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

# Run tests
test:
	@echo "$(BLUE)Running tests...$(NC)"
	$(PYTHON) -m pytest tests/ -v
	@echo "$(GREEN)Tests completed!$(NC)"

# Run tests with verbose output
test-verbose:
	@echo "$(BLUE)Running tests with verbose output...$(NC)"
	$(PYTHON) -m pytest tests/ -vv --tb=short
	@echo "$(GREEN)Test completed!$(NC)"

# Run ETL pipeline
pipeline:
	@echo "$(BLUE)Running ETL pipeline...$(NC)"
	$(PYTHON) src/automation/pipeline.py
	@echo "$(GREEN)Pipeline completed!$(NC)"

# Run one-time update
update:
	@echo "$(BLUE)Running fuel price update...$(NC)"
	$(PYTHON) src/automation/pipeline.py
	@echo "$(GREEN)Update completed!$(NC)"

# Launch dashboard
dashboard:
	@echo "$(BLUE)Launching Gradio dashboard...$(NC)"
	$(PYTHON) src/visualization/dashboard.py

# Set up cron job
setup-cron:
	@echo "$(BLUE)Setting up cron job...$(NC)"
	@if [ -f scripts/setup_cron.sh ]; then \
		bash scripts/setup_cron.sh; \
	else \
		echo "$(RED)Error: scripts/setup_cron.sh not found$(NC)"; \
		exit 1; \
	fi

# Show current cron jobs
show-cron:
	@echo "$(BLUE)Current cron jobs:$(NC)"
	@crontab -l 2>/dev/null || echo "No cron jobs found"

# Remove cron job
remove-cron:
	@echo "$(BLUE)Removing fuel price tracker cron job...$(NC)"
	@crontab -l 2>/dev/null | grep -v "fuel.*pipeline" | crontab - || true
	@echo "$(GREEN)Cron job removed (if it existed)$(NC)"

# Show database statistics
stats:
	@echo "$(BLUE)Database statistics:$(NC)"
	$(PYTHON) -c "from src.database.storage_db import FuelDatabase; from src.utils.config import config; db = FuelDatabase(config.get_database_path()); stats = db._get_statistics(); print(f\"Total records: {stats['total_records']}\"); print(f\"Average price: R{stats['avg_price']:.2f}/L\"); print(f\"Min price: R{stats['min_price']:.2f}/L\"); print(f\"Max price: R{stats['max_price']:.2f}/L\")"