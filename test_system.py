"""
Test Script - License Activation Dialog
Run this to see the fixed activation dialog with all buttons visible
"""

import os
import sys

from auth.license_manager import LicenseManager

# Add the parent directory to path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Test the activation dialog"""
    print("=" * 60)
    print("TESTING LICENSE ACTIVATION DIALOG")
    print("=" * 60)

    manager = LicenseManager()

    print("\nYour Machine Information:")
    print(f"  MAC Address: {manager.get_mac_address()}")
    print(f"  Machine ID: {manager.get_machine_id()}")

    print("\nOpening activation dialog...")
    print("You should see:")
    print("  ✓ Machine Information section")
    print("  ✓ License Key text area")
    print("  ✓ Copy Machine ID button (green)")
    print("  ✓ Activate License button (blue)")
    print("  ✓ License Info button (orange)")
    print("  ✓ Exit button (red)")

    # Show the dialog
    success = manager.show_activation_dialog()

    print("\n" + "=" * 60)
    if success:
        print("✓ Dialog test complete - Activation successful!")
    else:
        print("✗ Dialog closed without activation")
    print("=" * 60)


if __name__ == "__main__":
    main()