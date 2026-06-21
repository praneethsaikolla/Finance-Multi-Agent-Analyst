#!/bin/bash
set -e

echo "Setting up Financial Research Agent..."

# Create virtual environment
python3 -m venv venv

# Activate and install requirements
source venv/bin/activate
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.template .env
    echo "Created .env file. Please fill in your API keys."
fi

echo "Setup complete! Run 'source venv/bin/activate' to activate."
