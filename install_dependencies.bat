@echo off
REM Installation script for Python 3.14+ on Windows
REM This script installs dependencies using pre-built wheels to avoid compilation

echo Installing dependencies for Stampede Management System...
echo.

echo Step 1: Upgrading pip...
pip install --upgrade pip
echo.

echo Step 2: Installing NumPy (pre-built wheel)...
pip install --only-binary :all: numpy
echo.

echo Step 3: Installing core packages without dependencies...
pip install --no-deps opencv-python ultralytics shapely
echo.

echo Step 4: Installing remaining dependencies (pre-built wheels)...
pip install --only-binary :all: matplotlib pillow pyyaml requests scipy torch torchvision psutil polars ultralytics-thop
echo.

echo Step 5: Verifying installation...
python -c "import cv2; import numpy; import ultralytics; import shapely; print('All imports successful!'); print(f'OpenCV: {cv2.__version__}'); print(f'NumPy: {numpy.__version__}')"
echo.

echo Installation complete!
pause
