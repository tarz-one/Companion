#!/bin/bash

# Color output for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Setting up Python 3.11 Virtual Environment ===${NC}"

# Check if Python 3.11 is installed
if ! command -v python3.11 &> /dev/null; then
    echo -e "${RED}Python 3.11 is not installed!${NC}"
    echo -e "${YELLOW}Install it using Homebrew:${NC}"
    echo "  brew install python@3.11"
    exit 1
fi

# Navigate to python directory
cd "$(dirname "$0")" || exit 1

# Remove old venv if it exists
if [ -d ".venv" ]; then
    echo -e "${YELLOW}Removing existing virtual environment...${NC}"
    rm -rf .venv
fi

# Create new virtual environment with Python 3.11
echo -e "${GREEN}Creating virtual environment with Python 3.11...${NC}"
python3.11 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip, setuptools, and wheel
echo -e "${GREEN}Upgrading pip, setuptools, and wheel...${NC}"
pip install --upgrade pip setuptools wheel

# Install requirements
echo -e "${GREEN}Installing requirements...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${YELLOW}To activate the environment, run:${NC}"
echo "  source python/.venv/bin/activate"
echo -e "${YELLOW}To deactivate, run:${NC}"
echo "  deactivate"
