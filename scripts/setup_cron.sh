#!/bin/bash

# Setup script for fuel price tracker cron job
# This script configures automated scheduling of the ETL pipeline

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PROJECT_DIR}/venv/bin/python"
LOG_DIR="${PROJECT_DIR}/logs"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Fuel Price Tracker - Cron Job Setup${NC}"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo -e "${RED}Error: Virtual environment not found at $PROJECT_DIR/venv${NC}"
    echo "Please create a virtual environment first:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Create logs directory
mkdir -p "$LOG_DIR"
echo -e "${GREEN}✓${NC} Created logs directory at $LOG_DIR"

# Determine which pipeline to use
PIPELINE_SCRIPT="${PROJECT_DIR}/src/automation/pipeline.py"
echo -e "${GREEN}✓${NC} Using pipeline at $PIPELINE_SCRIPT"

# Ask for schedule preference
echo ""
echo "Select schedule frequency:"
echo "  1) Daily at 9:00 AM"
echo "  2) Daily at 6:00 PM"
echo "  3) Weekly (Wednesday at 9:00 AM - when SA fuel prices change)"
echo "  4) Every 6 hours"
echo "  5) Custom schedule"
read -p "Enter choice [1-5]: " schedule_choice

case $schedule_choice in
    1)
        CRON_EXPR="0 9 * * *"
        SCHEDULE_DESC="Daily at 9:00 AM"
        ;;
    2)
        CRON_EXPR="0 18 * * *"
        SCHEDULE_DESC="Daily at 6:00 PM"
        ;;
    3)
        CRON_EXPR="0 9 * * 3"
        SCHEDULE_DESC="Weekly (Wednesday at 9:00 AM)"
        ;;
    4)
        CRON_EXPR="0 */6 * * *"
        SCHEDULE_DESC="Every 6 hours"
        ;;
    5)
        read -p "Enter cron expression (e.g., '0 9 * * *' for daily at 9 AM): " CRON_EXPR
        SCHEDULE_DESC="Custom: $CRON_EXPR"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}✓${NC} Schedule: $SCHEDULE_DESC"

# Create cron job entry
CRON_JOB="${CRON_EXPR} cd ${PROJECT_DIR} && ${PYTHON_BIN} ${PIPELINE_SCRIPT} >> ${LOG_DIR}/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "fuel.*pipeline"; then
    echo ""
    read -p "Existing cron job found. Replace it? [y/N]: " replace
    if [[ $replace =~ ^[Yy]$ ]]; then
        # Remove existing job
        crontab -l 2>/dev/null | grep -v "fuel.*pipeline" | crontab -
        echo -e "${GREEN}✓${NC} Removed existing cron job"
    else
        echo "Setup cancelled"
        exit 0
    fi
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
echo -e "${GREEN}✓${NC} Cron job added successfully"

echo ""
echo "=================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo ""
echo "Cron job details:"
echo "  Schedule: $SCHEDULE_DESC"
echo "  Command: $PYTHON_BIN $PIPELINE_SCRIPT"
echo "  Log file: $LOG_DIR/cron.log"
echo ""
echo "To view cron jobs: crontab -l"
echo "To remove cron job: crontab -e (delete the line)"
echo "To view logs: tail -f $LOG_DIR/cron.log"
echo ""
echo "For email notifications, set these in your .env file:"
echo "  ENABLE_EMAIL_ALERTS=true"
echo "  SENDER_EMAIL=your_email@gmail.com"
echo "  SENDER_PASSWORD=your_app_password"
