@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    echo Local virtual environment not found. Creating .venv...
    py -3.12 -m venv "%~dp0.venv"
    if errorlevel 1 python -m venv "%~dp0.venv"
)

echo ============================================
echo   Crowd Monitoring System
echo ============================================
echo.

REM Check if license exists
if not exist "auth\license.dat" (
    echo License not found. Generating development license...
    echo.
    "%PYTHON_EXE%" generate_dev_license.py
    echo.
    echo Press any key to start the application...
    pause >nul
)

echo Starting GUI...
echo.
"%PYTHON_EXE%" config_gui.py

if errorlevel 1 (
    echo.
    echo Error occurred. Press any key to exit...
    pause >nul
)
