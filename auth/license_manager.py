"""
MAC Address-based License Management System
Provides hardware-bound authentication for the application
"""

import getpass
import hashlib
import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple


class LicenseManager:
    """Manages MAC address-based licensing"""

    def __init__(self, license_file: str = "license.dat"):
        """
        Initialize the license manager.
        
        Args:
            license_file: Path to encrypted license file
        """
        self.license_file = license_file
        self.secret_salt = b"xK9mP2vQ8nL5rT7wY4uE1jH6fD3sA0zC"

    def get_mac_address(self) -> str:
        """
        Get the primary MAC address of the machine.
        
        Returns:
            MAC address as string
        """
        try:
            # Get MAC address using uuid.getnode()
            mac = uuid.getnode()
            mac_str = ':'.join(['{:02x}'.format((mac >> elements) & 0xff)
                                for elements in range(0, 8 * 6, 8)][::-1])
            return mac_str
        except Exception as e:
            raise RuntimeError(f"Failed to get MAC address: {e}")

    def get_machine_id(self) -> str:
        """
        Get a unique machine identifier combining MAC address and username.
        This makes it harder to bypass by spoofing MAC alone.
        
        Returns:
            Hashed machine ID
        """
        try:
            mac = self.get_mac_address()
            username = getpass.getuser()
            machine_info = f"{mac}_{username}".encode()

            # Create a hash of the machine info
            machine_hash = hashlib.sha256(machine_info + self.secret_salt).hexdigest()
            return machine_hash
        except Exception as e:
            raise RuntimeError(f"Failed to generate machine ID: {e}")

    def generate_license_key(self, days_valid: int = 365) -> str:
        """
        Generate a license key for the current machine.
        
        Args:
            days_valid: Number of days the license is valid
            
        Returns:
            License key string
        """
        machine_id = self.get_machine_id()
        expiry_date = datetime.now() + timedelta(days=days_valid)

        license_data = {
            'machine_id': machine_id,
            'mac_address': self.get_mac_address(),
            'username': getpass.getuser(),
            'created': datetime.now().isoformat(),
            'expires': expiry_date.isoformat(),
            'valid': True
        }

        # Create signature
        signature = self._create_signature(license_data)
        license_data['signature'] = signature

        return json.dumps(license_data)

    def _create_signature(self, license_data: dict) -> str:
        """
        Create a signature for license data.
        
        Args:
            license_data: License information
            
        Returns:
            Signature hash
        """
        # Combine critical fields
        data_str = f"{license_data['machine_id']}_{license_data['expires']}_{license_data['valid']}"
        signature = hashlib.sha256(data_str.encode() + self.secret_salt).hexdigest()
        return signature

    def _verify_signature(self, license_data: dict) -> bool:
        """
        Verify the signature of license data.
        
        Args:
            license_data: License information with signature
            
        Returns:
            True if signature is valid
        """
        stored_signature = license_data.get('signature', '')

        # Create expected signature
        temp_data = license_data.copy()
        temp_data.pop('signature', None)
        expected_signature = self._create_signature(temp_data)

        return stored_signature == expected_signature

    def save_license(self, license_key: str) -> bool:
        """
        Save license key to file with obfuscation.
        
        Args:
            license_key: License key to save
            
        Returns:
            True if successful
        """
        try:
            # Simple XOR obfuscation (you can use stronger encryption)
            obfuscated = self._obfuscate(license_key.encode())

            with open(self.license_file, 'wb') as f:
                f.write(obfuscated)

            # Make file hidden on Windows
            if os.name == 'nt':
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(self.license_file, 0x02)  # FILE_ATTRIBUTE_HIDDEN
                except:
                    pass

            return True
        except Exception as e:
            print(f"Failed to save license: {e}")
            return False

    def load_license(self) -> Optional[dict]:
        """
        Load and decrypt license from file.
        
        Returns:
            License data dict or None if invalid
        """
        try:
            if not os.path.exists(self.license_file):
                return None

            with open(self.license_file, 'rb') as f:
                obfuscated = f.read()

            # Deobfuscate
            license_str = self._deobfuscate(obfuscated).decode()
            license_data = json.loads(license_str)

            return license_data
        except Exception as e:
            print(f"Failed to load license: {e}")
            return None

    def _obfuscate(self, data: bytes) -> bytes:
        """Simple XOR obfuscation (replace with AES for production)"""
        key = hashlib.sha256(self.secret_salt).digest()
        return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])

    def _deobfuscate(self, data: bytes) -> bytes:
        """Reverse XOR obfuscation"""
        return self._obfuscate(data)  # XOR is reversible

    def validate_license(self) -> Tuple[bool, str]:
        """
        Validate the current license.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Load license
        license_data = self.load_license()

        if not license_data:
            return False, "No license found. Please contact support for a license key."

        # Verify signature
        if not self._verify_signature(license_data):
            return False, "License file has been tampered with. Please contact support."

        # Check if license is marked as valid
        if not license_data.get('valid', False):
            return False, "License has been revoked. Please contact support."

        # Check machine ID
        current_machine_id = self.get_machine_id()
        if license_data.get('machine_id') != current_machine_id:
            return False, "This license is not valid for this computer. Please contact support."

        # Check expiry
        try:
            expiry_date = datetime.fromisoformat(license_data['expires'])
            if datetime.now() > expiry_date:
                return False, f"License expired on {expiry_date.strftime('%Y-%m-%d')}. Please renew."
        except Exception as e:
            return False, f"Invalid license expiry date: {e}"

        # All checks passed
        return True, "License is valid"

    def get_license_info(self) -> Optional[dict]:
        """
        Get information about the current license.
        
        Returns:
            Dictionary with license information or None
        """
        license_data = self.load_license()
        if not license_data:
            return None

        try:
            expiry_date = datetime.fromisoformat(license_data['expires'])
            days_remaining = (expiry_date - datetime.now()).days

            return {
                'mac_address': license_data.get('mac_address', 'Unknown'),
                'username': license_data.get('username', 'Unknown'),
                'created': license_data.get('created', 'Unknown'),
                'expires': license_data.get('expires', 'Unknown'),
                'days_remaining': max(0, days_remaining),
                'is_valid': days_remaining > 0
            }
        except:
            return None


# Standalone license generator script
def generate_license_for_machine():
    """Generate a license for the current machine"""
    print("=" * 60)
    print("LICENSE KEY GENERATOR")
    print("=" * 60)

    manager = LicenseManager()

    print(f"\nMachine Information:")
    print(f"  MAC Address: {manager.get_mac_address()}")
    print(f"  Username: {getpass.getuser()}")
    print(f"  Machine ID: {manager.get_machine_id()}")

    days = input("\nEnter license validity (days) [default: 365]: ").strip()
    days = int(days) if days else 365

    license_key = manager.generate_license_key(days_valid=days)

    print(f"\nGenerated License Key:")
    print("-" * 60)
    print(license_key)
    print("-" * 60)

    save = input("\nSave license to file? (y/n): ").strip().lower()
    if save == 'y':
        if manager.save_license(license_key):
            print(f"✓ License saved to {manager.license_file}")
        else:
            print("✗ Failed to save license")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    generate_license_for_machine()
