@echo off
REM Setup script for SEO Agent (Windows)

echo ======================================
echo SEO Agent - Setup Script
echo ======================================

REM Check Python version
echo Checking Python version...
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ======================================
echo Setup complete!
echo ======================================
echo.
echo Next steps:
echo 1. Configure .env file with your API keys
echo 2. Download OAuth credentials as credentials.json
echo 3. Run: python test_setup.py
echo.
pause
