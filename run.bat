@echo off
:: Tornado Cash Withdrawal Viewer - Windows Setup and Run Script
:: A tool by intelligenceonchain.com

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║       TORNADO CASH WITHDRAWAL VIEWER - SETUP               ║
echo ║                 intelligenceonchain.com                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found Python %PYTHON_VERSION%

:: Check if virtual environment exists
if not exist "venv" (
    echo [..] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    
    :: Activate and install dependencies
    echo [..] Installing dependencies...
    call venv\Scripts\activate.bat
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    echo [OK] Dependencies installed
) else (
    echo [OK] Virtual environment already exists
    call venv\Scripts\activate.bat
    
    :: Check if dependencies need updating
    echo [..] Checking dependencies...
    pip install -r requirements.txt -q
    echo [OK] Dependencies up to date
)

echo.

:: Run the viewer with any passed arguments
python tornado_viewer.py %*

:: Pause if no arguments were passed (interactive mode)
if "%~1"=="" (
    echo.
    pause
)
