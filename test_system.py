"""
Test script to verify all systems are working
"""
import os
import sys


def test_imports():
    """Test if all imports work"""
    print("Testing imports...")
    try:
        sys.path.insert(0, 'auth')
        from license_manager import LicenseManager
        print("  [OK] license_manager imported")
    except Exception as e:
        print(f"  [FAIL] license_manager import failed: {e}")
        return False

    try:
        from config import MonitoringConfig
        print("  [OK] config imported")
    except Exception as e:
        print(f"  [FAIL] config import failed: {e}")
        return False

    try:
        import tkinter
        print("  [OK] tkinter available")
    except Exception as e:
        print(f"  [FAIL] tkinter not available: {e}")
        return False

    return True


def test_license_manager():
    """Test license manager functionality"""
    print("\nTesting license manager...")
    try:
        sys.path.insert(0, 'auth')
        from license_manager import LicenseManager

        license_path = os.path.join('auth', 'license.dat')
        manager = LicenseManager(license_file=license_path)

        # Test MAC address
        mac = manager.get_mac_address()
        print(f"  [OK] MAC Address: {mac}")

        # Test Machine ID
        machine_id = manager.get_machine_id()
        print(f"  [OK] Machine ID: {machine_id[:32]}...")

        # Test license validation
        is_valid, message = manager.validate_license()
        if is_valid:
            print(f"  [OK] License valid: {message}")
        else:
            print(f"  [INFO] License not found or invalid: {message}")
            print("  [INFO] Run 'python generate_dev_license.py' to create a license")

        return True
    except Exception as e:
        print(f"  [FAIL] License manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_import():
    """Test if GUI can be imported"""
    print("\nTesting GUI import...")
    try:
        from config_gui import ConfigurationGUI
        print("  [OK] config_gui imported successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] config_gui import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_import():
    """Test if main.py can be imported"""
    print("\nTesting main.py import...")
    try:
        import main
        print("  [OK] main.py imported successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] main.py import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_files():
    """Check if required files exist"""
    print("\nChecking required files...")
    files = [
        'config_gui.py',
        'main.py',
        'config.py',
        'auth/license_manager.py',
        'auth/license_generator_tool.py',
        'auth/build_protected.py',
        'generate_dev_license.py',
        'START_HERE.md',
        'LICENSE_GUIDE.md',
        'README.md'
    ]

    all_exist = True
    for file in files:
        if os.path.exists(file):
            print(f"  [OK] {file}")
        else:
            print(f"  [FAIL] {file} missing")
            all_exist = False

    return all_exist


def main():
    print("=" * 60)
    print("  Crowd Monitoring System - System Test")
    print("=" * 60)
    print()

    results = []

    # Run tests
    results.append(("Files Check", check_files()))
    results.append(("Imports", test_imports()))
    results.append(("License Manager", test_license_manager()))
    results.append(("GUI Import", test_gui_import()))
    results.append(("Main Import", test_main_import()))

    # Summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    print()
    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("\n[SUCCESS] All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("  1. Run: python generate_dev_license.py")
        print("  2. Run: python config_gui.py")
        print("  3. Or use: run_gui.bat")
    else:
        print("\n[WARNING] Some tests failed. Please review the errors above.")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
