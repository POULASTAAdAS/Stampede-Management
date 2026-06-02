@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    echo Local virtual environment not found. Creating .venv...
    py -3.12 -m venv "%~dp0.venv"
    if errorlevel 1 python -m venv "%~dp0.venv"
)

echo Installing dependencies for Stampede Management System...
echo.

echo Step 1: Upgrading pip...
"%PYTHON_EXE%" -m pip install --upgrade pip
echo.

echo Step 2: Installing project requirements...
"%PYTHON_EXE%" -m pip install -r requirements.txt
echo.

echo Step 3: Verifying installation...
"%PYTHON_EXE%" -c "import cv2; import numpy; import ultralytics; import shapely; print('All imports successful!'); print(f'OpenCV: {cv2.__version__}'); print(f'NumPy: {numpy.__version__}')"
echo.

echo Installation complete!
pause
