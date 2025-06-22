#!/bin/bash

VENV_DIR="dht_env"

echo "? Creating virtual environment (if not already created)..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

echo "? Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "? Installing dependencies inside the virtual environment..."
sudo apt update
sudo apt install -y libgpiod2 python3-dev build-essential

pip install --upgrade pip
pip install adafruit-circuitpython-dht

echo "? Running temp_record.py in virtual environment..."
if [ ! -f temp_record.py ]; then
    echo "? temp_record.py not found!"
    exit 1
fi
while true; do
	python temp_record.py
	sleep 1
done
