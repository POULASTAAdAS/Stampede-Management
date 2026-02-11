@echo off
REM Stampede Management - Virtual Environment Activation Script
REM This batch file activates the virtual environment

echo Activating virtual environment...
call "%~dp0.venv\Scripts\activate.bat"

echo.
echo Virtual environment activated successfully!
python --version
echo.
echo You can now run the application with: python main.py
