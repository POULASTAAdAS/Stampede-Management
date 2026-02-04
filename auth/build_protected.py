"""
Automated Build Script for Protected Executable
Run this to build your protected application
FIXED VERSION - Better PyInstaller detection
CROSS-PLATFORM - Supports Windows and macOS
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def get_platform_info():
    """Get current platform information"""
    system = platform.system()
    is_windows = system == 'Windows'
    is_mac = system == 'Darwin'
    is_linux = system == 'Linux'

    return {
        'system': system,
        'is_windows': is_windows,
        'is_mac': is_mac,
        'is_linux': is_linux,
        'separator': ';' if is_windows else ':'
    }


def check_dependencies():
    """Check if required packages are installed"""
    plat = get_platform_info()
    print(f"Checking dependencies on {plat['system']}...")
    print(f"Platform: {plat['system']}")

    # Check tkinter
    try:
        import tkinter
        print(f"  ✓ tkinter")
    except ImportError:
        print(f"  ✗ tkinter - MISSING")
        print("\ntkinter is required but not available.")
        return False

    # Check pyinstaller using subprocess (works even if not in Python path)
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"  ✓ pyinstaller (version: {version})")
            return True
        else:
            print(f"  ✗ pyinstaller - MISSING")
            print(f"\nPyInstaller not found.")
            print("Install with: pip install pyinstaller")
            print("\nOr if already installed, try:")
            print("  python -m pip install --user pyinstaller")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"  ✗ pyinstaller - MISSING ({e})")
        print(f"\nPyInstaller not found.")
        print("Install with: pip install pyinstaller")
        print("\nOr if already installed, try:")
        print("  python -m pip install --user pyinstaller")
        return False


def verify_secret_salt():
    """Verify that secret salt has been changed"""
    print("\nVerifying secret salt...")

    with open('license_manager.py', 'r') as f:
        content = f.read()

    if 'YOUR_SECRET_SALT_HERE_CHANGE_THIS' in content:
        print("  ✗ WARNING: Default secret salt detected!")
        print("  Please change the secret_salt in license_manager.py")
        response = input("  Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return False
    else:
        print("  ✓ Secret salt has been customized")

    return True


def clean_build():
    """Clean previous build artifacts"""
    print("\nCleaning previous builds...")

    dirs_to_remove = ['build', 'dist', '__pycache__']

    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")

    print("  ✓ Cleanup complete")


def build_executable():
    """Build the executable using PyInstaller"""
    print("\nBuilding executable...")

    plat = get_platform_info()

    # Check if spec file exists
    spec_file = 'crowd_monitor_protected.spec'

    if os.path.exists(spec_file):
        print(f"  Using {spec_file}")
        print(f"  Note: Spec file includes proper pkg_resources handling for DeepSort")
        # Use python -m PyInstaller to ensure it's found
        cmd = [sys.executable, '-m', 'PyInstaller', spec_file, '--clean']
    else:
        print("  Using direct PyInstaller command")

        # Build platform-specific command
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--name', 'CrowdMonitor',
            '--clean',
            '--add-data', f'license_manager.py{plat["separator"]}.',
            '--hidden-import', 'license_manager',
            # Don't exclude pkg_resources - DeepSort needs it
            # Instead, we'll handle the Lorem ipsum error differently
        ]

        # Add system_conf.json if it exists
        system_conf_path = Path('../system_conf.json')
        if system_conf_path.exists():
            cmd.extend(['--add-data', f'../system_conf.json{plat["separator"]}.'])
            print(f"  Including system_conf.json in build")

        # Add --noconsole for GUI applications (works better on Windows)
        if plat['is_windows']:
            cmd.insert(4, '--noconsole')
        elif plat['is_mac']:
            # For macOS, use --windowed instead (equivalent to --noconsole)
            cmd.insert(4, '--windowed')
            # Optionally add icon for macOS
            # cmd.extend(['--icon', 'icon.icns'])

        # Add the main script
        cmd.append('../config_gui.py')  # Assuming we're in auth/ folder

    try:
        print(f"  Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("  ✓ Build successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Build failed:")
        print(e.stderr)
        return False


def create_distribution_package():
    """Create a distribution package"""
    print("\nCreating distribution package...")

    plat = get_platform_info()

    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("  ✗ dist/ directory not found")
        return False

    # Find the executable based on platform
    exe_file = None

    if plat['is_windows']:
        # Look for .exe files on Windows
        exe_files = list(dist_dir.glob('*.exe'))
        if exe_files:
            exe_file = exe_files[0]
    elif plat['is_mac']:
        # Look for .app bundles or executables without extension on macOS
        app_bundles = list(dist_dir.glob('*.app'))
        if app_bundles:
            exe_file = app_bundles[0]
        else:
            # Look for executable files without extension
            for item in dist_dir.iterdir():
                if item.is_file() and os.access(item, os.X_OK) and not item.suffix:
                    exe_file = item
                    break
    else:
        # Linux or other Unix-like systems
        for item in dist_dir.iterdir():
            if item.is_file() and os.access(item, os.X_OK):
                exe_file = item
                break

    if not exe_file:
        print(f"  ✗ No executable found in dist/ for {plat['system']}")
        return False

    print(f"  Found: {exe_file.name}")

    # Create distribution folder
    package_name = f'CrowdMonitor_Package_{plat["system"]}'
    package_dir = Path(package_name)
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()

    # Copy executable (handle .app bundles differently)
    if exe_file.suffix == '.app':
        # Copy entire .app bundle
        shutil.copytree(exe_file, package_dir / exe_file.name)
    else:
        shutil.copy(exe_file, package_dir / exe_file.name)
        # On Unix-like systems, ensure executable permission
        if not plat['is_windows']:
            os.chmod(package_dir / exe_file.name, 0o755)

    # Copy YOLO model file if it exists
    model_path = Path('../model/yolov8n.pt')
    if model_path.exists():
        # Create model directory in package
        model_dir = package_dir / 'model'
        model_dir.mkdir(exist_ok=True)
        shutil.copy(model_path, model_dir / 'yolov8n.pt')
        print(f"  Copied model file: yolov8n.pt")
    else:
        print(f"  ⚠ Warning: YOLO model not found at {model_path}")
        print(f"    Customers will need to provide their own model file")

    # Copy system_conf.json if it exists
    system_conf_path = Path('../system_conf.json')
    if system_conf_path.exists():
        shutil.copy(system_conf_path, package_dir / 'system_conf.json')
        print(f"  Copied configuration file: system_conf.json")
    else:
        print(f"  ⚠ Warning: system_conf.json not found (using defaults)")

    # Create platform-specific README for customers
    if plat['is_windows']:
        readme_content = """# CrowdMonitor Installation Guide (Windows)

## Installation

1. Extract all files from this folder to a location on your computer
2. The folder should contain:
   - CrowdMonitor.exe
   - model/yolov8n.pt (YOLO model file)
3. Run CrowdMonitor.exe

## First Run

On first run, you will be prompted to activate with a license key.

1. Click "Request License" to see your Machine ID
2. Send your Machine ID to support@yourcompany.com
3. Paste the license key you receive
4. Click "Activate"

## License Information

- Your license is tied to this computer
- If you upgrade your hardware, contact support for a new license
- Check license status: Click "License Info" button in the application

## System Requirements

- Windows 10 or later
- Webcam or video file for monitoring
- YOLO model file included (model/yolov8n.pt)

## Model File

The application includes a pre-trained YOLOv8n model for person detection.
Default location: model/yolov8n.pt

If you need to use a different model:
1. Open the application
2. Go to "Video Source" tab
3. Click "Browse" next to "Model Path"
4. Select your custom .pt model file

## Support

Email: support@yourcompany.com
Website: www.yourcompany.com

## Troubleshooting

**License activation fails:**
- Verify you copied the entire license key
- Check your internet connection (if using online validation)
- Contact support with your Machine ID

**Application won't start:**
- Ensure the model folder with yolov8n.pt exists
- Check that your video source (camera/file) is accessible
- Run as Administrator if necessary

**"Model not found" error:**
- Verify model/yolov8n.pt exists in the same folder as the executable
- Browse for the model file manually in the Video Source tab
"""
    elif plat['is_mac']:
        readme_content = """# CrowdMonitor Installation Guide (macOS)

## Installation

1. Extract all files from this folder to a location on your computer
2. The folder should contain:
   - CrowdMonitor.app (or CrowdMonitor executable)
   - model/yolov8n.pt (YOLO model file)
3. Double-click CrowdMonitor.app (or run CrowdMonitor executable)

## First Run

On first run, you may need to allow the application to run:
1. If macOS blocks the app, go to System Preferences → Security & Privacy
2. Click "Open Anyway" to allow CrowdMonitor to run

You will be prompted to activate with a license key:
1. Click "Request License" to see your Machine ID
2. Send your Machine ID to support@yourcompany.com
3. Paste the license key you receive
4. Click "Activate"

## License Information

- Your license is tied to this computer
- If you upgrade your hardware, contact support for a new license
- Check license status: Click "License Info" button in the application

## System Requirements

- macOS 10.13 (High Sierra) or later
- Webcam or video file for monitoring
- YOLO model file included (model/yolov8n.pt)

## Model File

The application includes a pre-trained YOLOv8n model for person detection.
Default location: model/yolov8n.pt

If you need to use a different model:
1. Open the application
2. Go to "Video Source" tab
3. Click "Browse" next to "Model Path"
4. Select your custom .pt model file

## Permissions

The application may request permission to:
- Access your camera (for live monitoring)
- Access files (for video file monitoring)

## Support

Email: support@yourcompany.com
Website: www.yourcompany.com

## Troubleshooting

**License activation fails:**
- Verify you copied the entire license key
- Check your internet connection (if using online validation)
- Contact support with your Machine ID

**Application won't start:**
- Right-click the app and select "Open" instead of double-clicking
- Ensure the model folder with yolov8n.pt exists
- Check that your video source (camera/file) is accessible
- Check System Preferences → Security & Privacy for blocked apps

**"App is damaged" error:**
- This is a Gatekeeper issue. Run this command in Terminal:
  xattr -cr /path/to/CrowdMonitor.app

**"Model not found" error:**
- Verify model/yolov8n.pt exists in the same folder as the application
- Browse for the model file manually in the Video Source tab
"""
    else:
        readme_content = """# CrowdMonitor Installation Guide (Linux)

## Installation

1. Extract all files from this folder to a location on your computer
2. The folder should contain:
   - CrowdMonitor (executable)
   - model/yolov8n.pt (YOLO model file)
3. Make the executable runnable: chmod +x CrowdMonitor
4. Run: ./CrowdMonitor

## First Run

On first run, you will be prompted to activate with a license key.

1. Click "Request License" to see your Machine ID
2. Send your Machine ID to support@yourcompany.com
3. Paste the license key you receive
4. Click "Activate"

## License Information

- Your license is tied to this computer
- If you upgrade your hardware, contact support for a new license
- Check license status: Click "License Info" button in the application

## System Requirements

- Modern Linux distribution
- Webcam or video file for monitoring
- YOLO model file included (model/yolov8n.pt)

## Model File

The application includes a pre-trained YOLOv8n model for person detection.
Default location: model/yolov8n.pt

If you need to use a different model:
1. Open the application
2. Go to "Video Source" tab
3. Click "Browse" next to "Model Path"
4. Select your custom .pt model file

## Support

Email: support@yourcompany.com
Website: www.yourcompany.com

## Troubleshooting

**"Model not found" error:**
- Verify model/yolov8n.pt exists in the same folder as the executable
- Browse for the model file manually in the Video Source tab
"""

    with open(package_dir / 'README.txt', 'w') as f:
        f.write(readme_content)

    # Create archive (ZIP for Windows, tar.gz for Unix-like systems)
    archive_name = f'CrowdMonitor_Distribution_{plat["system"]}'
    if plat['is_windows']:
        shutil.make_archive(archive_name, 'zip', package_dir)
        archive_ext = '.zip'
    else:
        shutil.make_archive(archive_name, 'gztar', package_dir)
        archive_ext = '.tar.gz'

    print(f"  ✓ Distribution package created: {archive_name}{archive_ext}")
    print(f"  ✓ Package contents in: {package_dir}/")

    return True


def display_summary():
    """Display build summary and next steps"""
    plat = get_platform_info()
    
    print("\n" + "=" * 60)
    print("BUILD COMPLETE!")
    print("=" * 60)

    print(f"\nBuilt for: {plat['system']}")
    print("\nFiles created:")

    if plat['is_windows']:
        print("  • dist/CrowdMonitor.exe - Protected executable")
        print("  • CrowdMonitor_Distribution_Windows.zip - Customer package")
        print("  • CrowdMonitor_Package_Windows/ - Unzipped package folder")
        test_platform = "Windows machine"
    elif plat['is_mac']:
        print("  • dist/CrowdMonitor.app (or CrowdMonitor) - Protected executable")
        print("  • CrowdMonitor_Distribution_Darwin.tar.gz - Customer package")
        print("  • CrowdMonitor_Package_Darwin/ - Unzipped package folder")
        test_platform = "Mac"
    else:
        print("  • dist/CrowdMonitor - Protected executable")
        print("  • CrowdMonitor_Distribution_Linux.tar.gz - Customer package")
        print("  • CrowdMonitor_Package_Linux/ - Unzipped package folder")
        test_platform = "Linux machine"

    print("\nNext steps:")
    print(f"  1. Test the executable on a clean {test_platform}")
    print("     - Verify DeepSort tracker works (if enabled)")
    print("  2. Generate licenses using license_generator_tool.py")
    print(f"  3. Distribute the package to customers")

    print("\nRemember:")
    print("  • Keep your secret_salt private and secure")
    print("  • Maintain a database of issued licenses")
    print("  • Provide good customer support for license issues")
    print("  • DeepSort tracker is included and working (pkg_resources properly bundled)")

    if plat['is_mac']:
        print("\nMac-specific notes:")
        print("  • Users may need to allow the app in Security & Privacy settings")
        print("  • Consider code signing for easier distribution (requires Apple Developer account)")
        print("  • For .app bundles, users should not extract individual files")

    print("\n" + "=" * 60)


def main():
    """Main build process"""
    plat = get_platform_info()
    
    print("=" * 60)
    print("CROWD MONITOR - PROTECTED BUILD SCRIPT")
    print(f"Building for: {plat['system']}")
    print("=" * 60)

    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n✗ Dependency check failed.")
        print("\nIf PyInstaller is already installed but not detected:")
        print("  1. Close and reopen your terminal/PowerShell")
        print("  2. Or run: python -m pip install --user --upgrade pyinstaller")
        print("  3. Or add Python Scripts to PATH:")
        print("     C:\\Users\\poula\\AppData\\Roaming\\Python\\Python314\\Scripts")
        sys.exit(1)

    # Step 2: Verify secret salt
    if not verify_secret_salt():
        sys.exit(1)

    # Step 3: Clean previous builds
    clean_build()

    # Step 4: Build executable
    if not build_executable():
        print("\n✗ Build failed. Please check errors above.")
        sys.exit(1)

    # Step 5: Create distribution package
    if not create_distribution_package():
        print("\n✗ Package creation failed.")
        sys.exit(1)

    # Step 6: Display summary
    display_summary()

    print("\n✓ All done!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)