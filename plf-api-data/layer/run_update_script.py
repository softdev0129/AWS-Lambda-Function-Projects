#!/bin/bash

# Set your PostgreSQL connection details as environment variables
export RDS_USERNAME="postgres"
export RDS_PASSWORD="GWtxSGM4swxxhN3fMHRH"
export RDS_ENDPOINT="database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com"
export RDS_DB_NAME="scraper_db"

# Path to your Python script
PYTHON_SCRIPT="download_extract_file.py"

# Activate your Python virtual environment if needed
# source /path/to/your/venv/bin/activate

# Run the Python script
python3 "${PYTHON_SCRIPT}"

