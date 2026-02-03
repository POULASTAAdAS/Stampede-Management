"""
Test script to verify license generation and validation work correctly
"""

import json
import os
import sys

# Add auth directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'auth'))

from license_manager import LicenseManager


def test_license_generation_and_validation():
    """Test the complete license workflow"""

    print("=" * 60)
    print("LICENSE GENERATION AND VALIDATION TEST")
    print("=" * 60)

    # Create manager instance
    manager = LicenseManager(license_file='auth/test_license.dat')

    # Get current machine info
    machine_id = manager.get_machine_id()
    mac_address = manager.get_mac_address()

    print(f"\n1. Current Machine Info:")
    print(f"   Machine ID: {machine_id}")
    print(f"   MAC Address: {mac_address}")

    # Generate a license using the manager's method
    print(f"\n2. Generating license using LicenseManager.generate_license()...")
    license_json = manager.generate_license(
        machine_id=machine_id,
        validity_days=365,
        customer_name="Test Customer"
    )

    print(f"   Generated license:")
    license_data = json.loads(license_json)
    print(f"   - Machine ID: {license_data.get('machine_id')}")
    print(f"   - Customer: {license_data.get('customer_name')}")
    print(f"   - Expires: {license_data.get('expires')}")
    print(f"   - Signature: {license_data.get('signature')[:32]}...")

    # Save the license
    print(f"\n3. Saving license to file...")
    if manager.save_license(license_json):
        print(f"   [OK] License saved successfully")
    else:
        print(f"   [FAIL] Failed to save license")
        return False

    # Validate the license
    print(f"\n4. Validating license...")
    valid, message = manager.validate_license()

    if valid:
        print(f"   [OK] {message}")
    else:
        print(f"   [FAIL] {message}")
        return False

    # Test with manual generation (simulating license_generator_tool.py)
    print(f"\n5. Testing manual generation (like license_generator_tool.py)...")

    from datetime import datetime, timedelta
    import hmac
    import hashlib

    expiry_date = datetime.now() + timedelta(days=365)

    manual_license_data = {
        'machine_id': machine_id,
        'mac_address': mac_address,
        'username': os.getenv('USERNAME') or os.getenv('USER') or 'unknown',
        'customer_name': "Manual Test Customer",  # Key: customer_name
        'created': datetime.now().isoformat(),
        'expires': expiry_date.isoformat(),
        'valid': True
    }

    # Generate signature using HMAC method
    data_str = json.dumps(manual_license_data, sort_keys=True)
    signature = hmac.new(
        manager.secret_salt,
        data_str.encode(),
        hashlib.sha256
    ).hexdigest()
    manual_license_data['signature'] = signature

    manual_license_json = json.dumps(manual_license_data, indent=2)

    print(f"   Generated manual license:")
    print(f"   - Machine ID: {manual_license_data.get('machine_id')}")
    print(f"   - Customer: {manual_license_data.get('customer_name')}")
    print(f"   - Signature: {signature[:32]}...")

    # Save and validate manual license
    print(f"\n6. Validating manually generated license...")
    if manager.save_license(manual_license_json):
        valid, message = manager.validate_license()
        if valid:
            print(f"   [OK] {message}")
        else:
            print(f"   [FAIL] {message}")
            return False
    else:
        print(f"   [FAIL] Failed to save manual license")
        return False

    # Clean up test file
    if os.path.exists('auth/test_license.dat'):
        os.remove('auth/test_license.dat')
        print(f"\n7. Cleaned up test license file")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED [OK]")
    print("=" * 60)
    print("\nThe license generation and validation are now working correctly!")
    print("You can now use license_generator_tool.py to generate licenses.")

    return True


if __name__ == "__main__":
    success = test_license_generation_and_validation()
    sys.exit(0 if success else 1)
