#!/bin/bash



# Create a Python virtual environment named 'venv'
python3 -m venv --system-site-packages .env

# Activate the virtual environment
source .env/bin/activate

# Install dependencies from requirements.txt
pip install -r requirements.txt

echo "Environment setup and dependencies installed."