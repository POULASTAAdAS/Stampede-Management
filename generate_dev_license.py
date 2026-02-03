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
    machine_id = manager.get_machine_id()
    print(f"Machine ID: {machine_id}")

    # Generate 365-day license (fixed: use generate_license, not generate_license_key)
    license_key = manager.generate_license(
        machine_id=machine_id,
        validity_days=365,
        customer_name="Development"
    )
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
