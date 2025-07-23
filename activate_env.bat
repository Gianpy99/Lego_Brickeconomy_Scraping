@echo off
REM Windows batch script to activate Python 3.13 virtual environment and run commands

echo 🚀 Activating Python 3.13 Virtual Environment...
echo ================================================

REM Check if virtual environment exists
if not exist "venv_py313\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please run: py -3.13 -m venv venv_py313
    pause
    exit /b 1
)

REM Activate virtual environment
call venv_py313\Scripts\activate.bat

echo ✅ Python 3.13 environment activated!
echo 📦 Python version:
python --version

echo.
echo 📝 Available commands:
echo   python demo.py           - Interactive demonstration
echo   python main.py --help    - Command-line help
echo   python test_imports.py   - Test all modules
echo   python setup.py          - Setup and install dependencies
echo.

REM Start an interactive command prompt in the virtual environment
cmd /k
