# Installation Notes for Python 3.14 on Windows

## Problem

When installing `opencv-python` and its dependencies on Python 3.14 (Windows), you may encounter compilation errors
because:

- NumPy and other packages try to build from source
- Windows doesn't have C compilers (gcc, cl, clang) installed by default
- Pre-built wheels for some numpy versions aren't available for Python 3.14 yet

## Solution

Use **pre-built binary wheels** instead of building from source. This bypasses the need for C compilers.

## Installation Steps

### Option 1: Using the Installation Script (Recommended)

Simply run the batch file:

```batch
install_dependencies.bat
```

### Option 2: Manual Installation

Run these commands in order:

```batch
# 1. Upgrade pip
pip install --upgrade pip

# 2. Install NumPy (pre-built wheel only)
pip install --only-binary :all: numpy

# 3. Install core packages without dependencies
pip install --no-deps opencv-python ultralytics shapely

# 4. Install remaining dependencies (pre-built wheels only)
pip install --only-binary :all: matplotlib pillow pyyaml requests scipy torch torchvision psutil polars ultralytics-thop
```

## Verification

Test that everything works:

```batch
python -c "import cv2; import numpy; import ultralytics; import shapely; print('Success!')"
```

## Installed Versions

- OpenCV: 4.12.0
- NumPy: 2.3.5
- Ultralytics: 8.3.237
- Shapely: 2.1.2
- PyTorch: 2.9.1
- TorchVision: 0.24.1

## Optional Dependencies

To use DeepSort tracking, install:

```batch
pip install deep-sort-realtime
```

## Key Flags Used

- `--only-binary :all:`: Forces pip to use pre-built wheels only (no compilation)
- `--no-deps`: Installs package without its dependencies (useful when dependency resolution conflicts)

## Why This Works

Python 3.14 is very new, and not all package versions have pre-built wheels for it. By:

1. Installing the latest NumPy (2.3.5) which HAS pre-built wheels for Python 3.14
2. Preventing packages from trying to downgrade to versions that need compilation
3. Installing packages without automatic dependency resolution when needed

We avoid all compilation requirements and use only pre-built binary wheels.
