"""
Quick script to generate a development license automatically
"""
import os
import sys

from auth.license_manager import LicenseManager

sys.path.insert(0, 'auth')


# from license_manager import LicenseManager

def main():
    print("Generating development license...")
    # Use auth/license.dat path
    license_path = os.path.join('auth', 'license.dat')
    manager = LicenseManager(license_file=license_path)

    print(f"MAC Address: {manager.get_mac_address()}")
    print(f"Machine ID: {manager.get_machine_id()}")

    # Generate 365-day license
    license_key = manager.generate_license_key(days_valid=365)
    print(f"\nLicense generated!")

    # Save it
    if manager.save_license(license_key):
        print(f"[OK] License saved to {manager.license_file}")

        # Verify it works
        is_valid, message = manager.validate_license()
        if is_valid:
            print(f"[OK] License validated: {message}")
            print("\nYou can now run the application!")
        else:
            print(f"[FAIL] License validation failed: {message}")
    else:
        print("[FAIL] Failed to save license")


if __name__ == "__main__":
    main()
