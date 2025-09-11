#!/bin/bash
set -e

# Survey Dashboard Docker Entrypoint
echo "Starting Survey Dashboard..."

# Set default environment variables
export FLASK_ENV=${FLASK_ENV:-production}
export ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
export ADMIN_PASSWORD=${ADMIN_PASSWORD:-surveydash2024}

# Create logs directory
mkdir -p /app/logs

# Change to backend directory
cd /app/backend

# Validate survey data exists
if [ ! -f "data/survey_data.xlsx" ]; then
    echo "ERROR: Survey data file not found at data/survey_data.xlsx"
    exit 1
fi

echo "Survey data file found: $(ls -lh data/survey_data.xlsx)"

# Test data processor
python -c "
from app.enhanced_data_processor import EnhancedSurveyDataProcessor
processor = EnhancedSurveyDataProcessor('data/survey_data.xlsx')
print(f'✓ Data processor initialized: {len(processor.processed_data)} sheets')
print(f'✓ Total responses: {processor.get_summary_stats()[\"total_responses\"]}')
"

echo "✓ Survey Dashboard initialization complete"
echo "✓ Access URL: http://localhost:5000"
echo "✓ Login: $ADMIN_USERNAME / [password hidden]"

# Start the application
exec python app.py