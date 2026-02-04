"""
License Management System with Hardware-Tied Authentication
FIXED VERSION - Supports optional license_file parameter for flexibility
"""

import hashlib
import hmac
import json
import os
import platform
import tkinter as tk
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import messagebox, scrolledtext


class LicenseManager:
    """Handles license generation, validation, and activation UI"""

    def __init__(self, license_file=None):
        """
        Initialize License Manager

        Args:
            license_file: Optional custom path for license file.
                         If not provided, uses default location in user home directory.
        """
        # IMPORTANT: Change this secret salt before distribution!
        # This is used to sign licenses and prevent forgery
        self.secret_salt = b"xK9mP2vQ8nL5rT7wY4uE1jH6fD3sA0zC"

        # License file location
        if license_file:
            # Use custom path if provided
            self.license_file = Path(license_file)
        else:
            # Use default location
            self.license_file = Path.home() / '.crowdmonitor' / 'license.dat'

        # Ensure parent directory exists
        self.license_file.parent.mkdir(parents=True, exist_ok=True)

    def get_mac_address(self):
        """Get the MAC address of the primary network interface"""
        mac = uuid.getnode()
        mac_str = ':'.join(('%012X' % mac)[i:i + 2] for i in range(0, 12, 2))
        return mac_str

    def get_machine_id(self):
        """Generate a unique machine identifier"""
        mac = self.get_mac_address()
        hostname = platform.node()
        username = os.getenv('USERNAME') or os.getenv('USER') or 'unknown'

        # Combine multiple hardware identifiers
        machine_string = f"{mac}-{hostname}-{username}".encode()
        machine_id = hashlib.sha256(machine_string).hexdigest()[:32]

        return machine_id

    def generate_signature(self, data):
        """Generate HMAC signature for license data"""
        data_str = json.dumps(data, sort_keys=True)
        signature = hmac.new(
            self.secret_salt,
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def verify_signature(self, data, signature):
        """Verify HMAC signature"""
        expected = self.generate_signature(data)
        return hmac.compare_digest(expected, signature)

    def generate_license(self, machine_id, validity_days=365, customer_name=""):
        """Generate a new license for a specific machine"""
        now = datetime.now()
        expires = now + timedelta(days=validity_days)

        license_data = {
            'machine_id': machine_id,
            'mac_address': self.get_mac_address(),
            'username': os.getenv('USERNAME') or os.getenv('USER'),
            'customer_name': customer_name,
            'created': now.isoformat(),
            'expires': expires.isoformat(),
            'valid': True
        }

        # Generate signature
        signature = self.generate_signature(license_data)
        license_data['signature'] = signature

        return json.dumps(license_data, indent=2)

    def save_license(self, license_json):
        """Save license to local file"""
        try:
            with open(self.license_file, 'w') as f:
                f.write(license_json)
            return True
        except Exception as e:
            print(f"Error saving license: {e}")
            return False

    def load_license(self):
        """Load license from local file"""
        if not self.license_file.exists():
            return None

        try:
            with open(self.license_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading license: {e}")
            return None

    def validate_license(self):
        """Validate the current license"""
        license_data = self.load_license()

        if not license_data:
            return False, "No license found"

        # Verify signature
        signature = license_data.pop('signature', None)
        if not signature or not self.verify_signature(license_data, signature):
            return False, "Invalid license signature"

        # Check machine ID
        current_machine_id = self.get_machine_id()
        if license_data.get('machine_id') != current_machine_id:
            return False, "License is for a different machine"

        # Check expiration
        expires = datetime.fromisoformat(license_data.get('expires'))
        if datetime.now() > expires:
            return False, "License has expired"

        # Check valid flag
        if not license_data.get('valid', False):
            return False, "License has been revoked"

        # All checks passed
        days_remaining = (expires - datetime.now()).days
        return True, f"License valid ({days_remaining} days remaining)"

    def get_license_info(self):
        """Get detailed license information"""
        license_data = self.load_license()

        if not license_data:
            return None

        # Calculate days remaining
        try:
            expires = datetime.fromisoformat(license_data.get('expires'))
            days_remaining = (expires - datetime.now()).days
        except (ValueError, TypeError):
            days_remaining = 0

        return {
            'customer_name': license_data.get('customer_name', 'N/A'),
            'created': license_data.get('created'),
            'expires': license_data.get('expires'),
            'machine_id': license_data.get('machine_id'),
            'valid': license_data.get('valid', False),
            'days_remaining': days_remaining
        }

    def show_activation_dialog(self, parent=None):
        """
        Show license activation dialog with MAC address and username displayed

        Args:
            parent: Optional parent window for modal dialog
        """
        # Create root or use parent
        if parent:
            root = tk.Toplevel(parent)
        else:
            root = tk.Tk()

        root.title("License Activation Required")
        root.geometry("600x750")
        root.resizable(False, False)

        # Configure styling
        root.configure(bg='#f0f0f0')

        # Create main container with padding
        main_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        # Header
        header_label = tk.Label(
            main_frame,
            text="License Activation Required",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        header_label.pack(pady=(0, 10))

        # Description
        desc_label = tk.Label(
            main_frame,
            text="Please enter your license key to activate the application",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#666666'
        )
        desc_label.pack(pady=(0, 20))

        # Machine Information Section
        info_frame = tk.LabelFrame(
            main_frame,
            text="Your Machine Information",
            font=('Arial', 10, 'bold'),
            bg='#ffffff',
            fg='#333333',
            padx=15,
            pady=15
        )
        info_frame.pack(fill='x', pady=(0, 20))

        # Get machine info
        mac_address = self.get_mac_address()
        machine_id = self.get_machine_id()
        username = os.getenv('USERNAME') or os.getenv('USER') or 'unknown'

        # MAC Address
        mac_label = tk.Label(
            info_frame,
            text=f"MAC Address: {mac_address}",
            font=('Courier', 9),
            bg='#ffffff',
            fg='#333333',
            justify='left'
        )
        mac_label.pack(anchor='w', pady=2)

        # Username
        user_label = tk.Label(
            info_frame,
            text=f"Username: {username}",
            font=('Courier', 9),
            bg='#ffffff',
            fg='#333333',
            justify='left'
        )
        user_label.pack(anchor='w', pady=2)

        # Machine ID
        machine_label = tk.Label(
            info_frame,
            text=f"Machine ID: {machine_id}",
            font=('Courier', 9),
            bg='#ffffff',
            fg='#333333',
            justify='left'
        )
        machine_label.pack(anchor='w', pady=2)

        # Info text
        info_text = tk.Label(
            info_frame,
            text="Send ALL THREE values above to support@yourcompany.com to request a license",
            font=('Arial', 8, 'italic'),
            bg='#ffffff',
            fg='#666666',
            wraplength=500,
            justify='left'
        )
        info_text.pack(anchor='w', pady=(10, 0))

        # License Key Section
        key_frame = tk.LabelFrame(
            main_frame,
            text="License Key:",
            font=('Arial', 10, 'bold'),
            bg='#ffffff',
            fg='#333333',
            padx=15,
            pady=15
        )
        key_frame.pack(fill='both', expand=True, pady=(0, 20))

        # Text area for license key
        license_text = scrolledtext.ScrolledText(
            key_frame,
            height=10,
            width=60,
            font=('Courier', 9),
            wrap=tk.WORD
        )
        license_text.pack(fill='both', expand=True)

        # Button Frame
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=(0, 10))

        # Variable to store result
        activation_result = {'success': False}

        def copy_machine_info():
            """Copy all machine info to clipboard"""
            info_text = f"Machine ID: {machine_id}\nMAC Address: {mac_address}\nUsername: {username}"
            root.clipboard_clear()
            root.clipboard_append(info_text)
            messagebox.showinfo(
                "Copied",
                "Machine information copied to clipboard!\n\n"
                "Send this to support@yourcompany.com to request your license."
            )

        def activate_license():
            """Activate the license"""
            license_key = license_text.get("1.0", tk.END).strip()

            if not license_key:
                messagebox.showerror("Error", "Please enter a license key")
                return

            try:
                # Parse and save license
                license_data = json.loads(license_key)

                # Verify it's for this machine
                if license_data.get('machine_id') != machine_id:
                    messagebox.showerror(
                        "Error",
                        "This license is for a different machine.\n\n"
                        f"Expected Machine ID: {machine_id}\n"
                        f"License Machine ID: {license_data.get('machine_id')}"
                    )
                    return

                # Verify MAC address
                if license_data.get('mac_address', '').upper() != mac_address.upper():
                    messagebox.showerror(
                        "Error",
                        "This license is for a different MAC address.\n\n"
                        f"Your MAC Address: {mac_address}\n"
                        f"License MAC Address: {license_data.get('mac_address')}"
                    )
                    return

                # Verify username
                if license_data.get('username') != username:
                    messagebox.showerror(
                        "Error",
                        "This license is for a different username.\n\n"
                        f"Your Username: {username}\n"
                        f"License Username: {license_data.get('username')}"
                    )
                    return

                # Save license
                with open(self.license_file, 'w') as f:
                    f.write(license_key)

                # Validate
                valid, message = self.validate_license()

                if valid:
                    messagebox.showinfo("Success", "License activated successfully!")
                    activation_result['success'] = True
                    root.quit()
                    root.destroy()
                else:
                    messagebox.showerror("Error", f"License validation failed: {message}")

            except json.JSONDecodeError:
                messagebox.showerror(
                    "Error",
                    "Invalid license format. Please ensure you copied the entire license key."
                )
            except Exception as e:
                messagebox.showerror("Error", f"Activation failed: {str(e)}")

        def show_license_info():
            """Show current license information"""
            license_data = self.load_license()

            if not license_data:
                messagebox.showinfo(
                    "License Information",
                    "No license found.\n\n"
                    "Please activate with a valid license key."
                )
                return

            info = self.get_license_info()
            created = datetime.fromisoformat(info['created']).strftime('%Y-%m-%d %H:%M')
            expires = datetime.fromisoformat(info['expires']).strftime('%Y-%m-%d %H:%M')

            valid, message = self.validate_license()

            info_text = f"""
Current License Information:

Customer: {info['customer_name']}
Created: {created}
Expires: {expires}
Status: {message}

Machine ID: {info['machine_id']}
"""

            messagebox.showinfo("License Information", info_text.strip())

        def exit_application():
            """Exit the application"""
            if messagebox.askyesno(
                    "Exit",
                    "Application requires a valid license to run.\n\n"
                    "Do you want to exit?"
            ):
                activation_result['success'] = False
                root.quit()
                root.destroy()

        # Create buttons with better styling
        btn_style = {
            'font': ('Arial', 10),
            'relief': 'raised',
            'bd': 2,
            'padx': 15,
            'pady': 8,
            'cursor': 'hand2'
        }

        # Row 1: Copy Info and Activate
        row1_frame = tk.Frame(button_frame, bg='#f0f0f0')
        row1_frame.pack(fill='x', pady=5)

        btn_copy = tk.Button(
            row1_frame,
            text="📋 Copy Machine Info",
            command=copy_machine_info,
            bg='#4CAF50',
            fg='white',
            activebackground='#45a049',
            **btn_style
        )
        btn_copy.pack(side='left', expand=True, fill='x', padx=5)

        btn_activate = tk.Button(
            row1_frame,
            text="✓ Activate License",
            command=activate_license,
            bg='#2196F3',
            fg='white',
            activebackground='#0b7dda',
            **btn_style
        )
        btn_activate.pack(side='left', expand=True, fill='x', padx=5)

        # Row 2: License Info and Exit
        row2_frame = tk.Frame(button_frame, bg='#f0f0f0')
        row2_frame.pack(fill='x', pady=5)

        btn_info = tk.Button(
            row2_frame,
            text="ℹ License Info",
            command=show_license_info,
            bg='#FF9800',
            fg='white',
            activebackground='#e68900',
            **btn_style
        )
        btn_info.pack(side='left', expand=True, fill='x', padx=5)

        btn_exit = tk.Button(
            row2_frame,
            text="✗ Exit",
            command=exit_application,
            bg='#f44336',
            fg='white',
            activebackground='#da190b',
            **btn_style
        )
        btn_exit.pack(side='left', expand=True, fill='x', padx=5)

        # Help text at bottom
        help_label = tk.Label(
            main_frame,
            text="Need help? Contact support@yourcompany.com",
            font=('Arial', 8),
            bg='#f0f0f0',
            fg='#888888'
        )
        help_label.pack(pady=(10, 0))

        # Center window on screen
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')

        # Make window modal
        root.grab_set()
        root.focus_force()

        # Start main loop
        root.mainloop()

        return activation_result['success']

    def require_activation(self, parent=None):
        """
        Check license and show activation dialog if needed

        Args:
            parent: Optional parent window for modal dialog

        Returns:
            bool: True if license is valid, False otherwise
        """
        valid, message = self.validate_license()

        if not valid:
            print(f"License validation failed: {message}")
            print("Opening activation dialog...")

            # Show activation dialog
            success = self.show_activation_dialog(parent)

            if not success:
                print("Application requires a valid license to run.")
                return False

        return True


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("LICENSE MANAGER - Interactive Tool")
    print("=" * 60)

    manager = LicenseManager()

    print("\n1. Generate License")
    print("2. Validate Current License")
    print("3. Show License Info")
    print("4. Test Activation Dialog")

    choice = input("\nSelect option (1-4): ").strip()

    if choice == "1":
        print("\n--- Generate New License ---")
        machine_id = input("Enter Machine ID: ").strip()

        if not machine_id:
            print("Error: Machine ID is required")
        else:
            validity_days = input("Enter validity period (days, default 365): ").strip()
            validity_days = int(validity_days) if validity_days else 365

            customer_name = input("Enter customer name (optional): ").strip()

            license_key = manager.generate_license(
                machine_id=machine_id,
                validity_days=validity_days,
                customer_name=customer_name
            )

            print("\n" + "=" * 60)
            print("LICENSE KEY GENERATED:")
            print("=" * 60)
            print(license_key)
            print("=" * 60)
            print("\nSend this license key to your customer.")

    elif choice == "2":
        print("\n--- Validate License ---")
        valid, message = manager.validate_license()

        if valid:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")

    elif choice == "3":
        print("\n--- License Information ---")
        info = manager.get_license_info()

        if info:
            print(f"Customer: {info['customer_name']}")
            print(f"Created: {info['created']}")
            print(f"Expires: {info['expires']}")
            print(f"Machine ID: {info['machine_id']}")
            print(f"Valid: {info['valid']}")
        else:
            print("No license found")

    elif choice == "4":
        print("\n--- Test Activation Dialog ---")
        print(f"Your Machine ID: {manager.get_machine_id()}")
        print(f"Your MAC Address: {manager.get_mac_address()}")
        print("\nOpening activation dialog...")

        success = manager.show_activation_dialog()

        if success:
            print("\n✓ Activation successful!")
        else:
            print("\n✗ Activation cancelled")

    else:
        print("Invalid option")
