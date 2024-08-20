#!/bin/bash
# Create a Python virtual environment named 'venv'
python3 -m venv --system-site-packages .env
# Install dependencies from requirements.txt
./.env/bin/pip install -r requirements.txt
echo "Environment setup and dependencies installed."