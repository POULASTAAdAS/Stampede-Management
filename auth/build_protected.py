"""
Automated Build Script for Protected Executable
Run this to build your protected application
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    """Check if required packages are installed"""
    print("Checking dependencies...")

    required = ['pyinstaller', 'tkinter']
    missing = []

    for package in required:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)

    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Install with: pip install " + ' '.join(missing))
        return False

    return True


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
    files_to_remove = ['*.spec'] if os.path.exists('crowd_monitor_protected.spec') else []

    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")

    print("  ✓ Cleanup complete")


def build_executable():
    """Build the executable using PyInstaller"""
    print("\nBuilding executable...")

    # Check if spec file exists
    spec_file = 'crowd_monitor_protected.spec'

    if os.path.exists(spec_file):
        print(f"  Using {spec_file}")
        cmd = ['pyinstaller', spec_file, '--clean']
    else:
        print("  Using direct PyInstaller command")
        cmd = [
            'pyinstaller',
            '--onefile',
            '--noconsole',
            '--name', 'CrowdMonitor',
            '--clean',
            '--add-data', 'license_manager.py;.',
            '--hidden-import', 'license_manager',
            'gui.py'
        ]

    try:
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

    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("  ✗ dist/ directory not found")
        return False

    # Find the executable
    exe_files = list(dist_dir.glob('*.exe'))
    if not exe_files:
        print("  ✗ No executable found in dist/")
        return False

    exe_file = exe_files[0]
    print(f"  Found: {exe_file.name}")

    # Create distribution folder
    package_dir = Path('CrowdMonitor_Package')
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()

    # Copy executable
    shutil.copy(exe_file, package_dir / exe_file.name)

    # Create README for customers
    readme_content = """# CrowdMonitor Installation Guide

## Installation

1. Extract all files from this folder
2. Run CrowdMonitor.exe

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
- YOLO model file (yolov8n.pt or similar)

## Support

Email: support@yourcompany.com
Website: www.yourcompany.com

## Troubleshooting

**License activation fails:**
- Verify you copied the entire license key
- Check your internet connection (if using online validation)
- Contact support with your Machine ID

**Application won't start:**
- Ensure you have the required YOLO model file
- Check that your video source (camera/file) is accessible
- Run as Administrator if necessary
"""

    with open(package_dir / 'README.txt', 'w') as f:
        f.write(readme_content)

    # Create ZIP archive
    archive_name = 'CrowdMonitor_Distribution'
    shutil.make_archive(archive_name, 'zip', package_dir)

    print(f"  ✓ Distribution package created: {archive_name}.zip")
    print(f"  ✓ Package contents in: {package_dir}/")

    return True


def display_summary():
    """Display build summary and next steps"""
    print("\n" + "=" * 60)
    print("BUILD COMPLETE!")
    print("=" * 60)

    print("\nFiles created:")
    print("  • dist/CrowdMonitor.exe - Protected executable")
    print("  • CrowdMonitor_Distribution.zip - Customer package")
    print("  • CrowdMonitor_Package/ - Unzipped package folder")

    print("\nNext steps:")
    print("  1. Test the executable on a clean Windows machine")
    print("  2. Generate licenses using license_generator_tool.py")
    print("  3. Distribute CrowdMonitor_Distribution.zip to customers")

    print("\nRemember:")
    print("  • Keep your secret_salt private and secure")
    print("  • Maintain a database of issued licenses")
    print("  • Provide good customer support for license issues")

    print("\n" + "=" * 60)


def main():
    """Main build process"""
    print("=" * 60)
    print("CROWD MONITOR - PROTECTED BUILD SCRIPT")
    print("=" * 60)

    # Step 1: Check dependencies
    if not check_dependencies():
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
