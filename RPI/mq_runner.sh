#!/bin/bash
# Script to automatically enter the virtual environment and run the MQ135 sensor code
# Save this as run_sensor.sh and make it executable with: chmod +x run_sensor.sh

# Display a welcome banner
echo "========================================"
echo "  MQ135 CO2 Sensor Automatic Launcher  "
echo "========================================"

# Change to the directory where the script is located
# Uncomment and modify this if your scripts are in a different directory
# cd /home/thala/sensor_project

# Check if virtual environment exists
if [ ! -d "mq_read_env" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv mq_read_env
    echo "Virtual environment created successfully."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source mq_read_env/bin/activate

# Check if required packages are installed
echo "Checking required packages..."
pip_result=$(pip list | grep smbus)
if [ -z "$pip_result" ]; then
    echo "Installing required packages..."
    pip install smbus-cffi
else
    echo "Required packages already installed."
fi

# Run the MQ135 sensor code
echo "Starting MQ135 CO2 sensor monitoring..."
echo "Press Ctrl+C to stop the monitoring."
echo ""

# Run the sensor code
python3 mq_read.py

# Deactivate the virtual environment when done
deactivate

echo "Sensor monitoring ended."
