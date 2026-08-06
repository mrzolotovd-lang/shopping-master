#!/bin/bash

# Shopping Master Setup Script

set -e

echo "🛒 Shopping Master - Setup"
echo "=========================="

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo "Creating directories..."
mkdir -p data logs

# Initialize database
echo "Initializing database..."
python -m src.main seed

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate venv: source venv/bin/activate"
echo "  2. Show status:   python -m src.main status"
echo "  3. Show shopping: python -m src.main buy"
echo ""
