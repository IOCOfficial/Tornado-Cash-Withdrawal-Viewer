#!/bin/bash

# Tornado Cash Withdrawal Viewer - Setup and Run Script
# A tool by intelligenceonchain.com

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
VIEWER_SCRIPT="$SCRIPT_DIR/tornado_viewer.py"

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║       TORNADO CASH WITHDRAWAL VIEWER - SETUP               ║"
echo "║                 intelligenceonchain.com                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed or not in PATH${NC}"
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Found Python $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}→${NC} Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✓${NC} Virtual environment created"
    
    # Activate and install dependencies
    echo -e "${YELLOW}→${NC} Installing dependencies..."
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip -q
    pip install -r "$REQUIREMENTS_FILE" -q
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
    source "$VENV_DIR/bin/activate"
    
    # Check if dependencies need updating
    echo -e "${YELLOW}→${NC} Checking dependencies..."
    pip install -r "$REQUIREMENTS_FILE" -q
    echo -e "${GREEN}✓${NC} Dependencies up to date"
fi

echo

# Run the viewer with any passed arguments
python "$VIEWER_SCRIPT" "$@"
