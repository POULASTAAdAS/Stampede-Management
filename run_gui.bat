@echo off
echo ============================================
echo   Crowd Monitoring System
echo ============================================
echo.

REM Check if license exists
if not exist "auth\license.dat" (
    echo License not found. Generating development license...
    echo.
    python generate_dev_license.py
    echo.
    echo Press any key to start the application...
    pause >nul
)

echo Starting GUI...
echo.
python config_gui.py

if errorlevel 1 (
    echo.
    echo Error occurred. Press any key to exit...
    pause >nul
)
