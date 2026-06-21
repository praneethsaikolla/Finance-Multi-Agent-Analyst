Write-Host "Setting up Financial Research Agent..."

# Create virtual environment
python -m venv venv

# Activate and install requirements
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Create .env if it doesn't exist
if (-not (Test-Path -Path ".env")) {
    Copy-Item -Path ".env.template" -Destination ".env"
    Write-Host "Created .env file. Please fill in your API keys."
}

Write-Host "Setup complete! Run '.\venv\Scripts\Activate.ps1' to activate."
