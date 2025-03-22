#!/bin/bash
cd "$(dirname "$0")"

# Activate virtual environment if you're using one
# source /path/to/your/venv/bin/activate

while true; do
    echo "Starting Office Tracker application..."
    python3 app.py
    
    # If the app crashes, wait 10 seconds before restarting
    echo "Application crashed or stopped. Restarting in 10 seconds..."
    sleep 10
done
