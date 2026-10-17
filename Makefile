PYTHON := python3
PIP := pip3
PROJECT_NAME := live-fuel-tracker

BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m

help:
	@echo "$(BLUE)LIVE FUEL TRACKER FOR SOUTH AFRICA - Available Commands:$(NC)"
	@echo ""
	@echo "$(GREEN)Development Commands:$(NC)"
	@echo " make install			- Install Python dependencies"
	@echo " make test				- Run pytest tests"

install:
	@echo "$(BLUE)Installing Project dependencies ...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Tests completed!$(NC)"

test:
	@echo "$(BLUE)Running tests ...$(BLUE)"
	$(PYTHON) -m pytest tests/ -vv
	@echo "$(GREEN)Test completed.$(GREEN)"