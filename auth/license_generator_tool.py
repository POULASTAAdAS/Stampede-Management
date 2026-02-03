"""
License Generation Tool (ADMIN ONLY) - FIXED VERSION WITH MAC BINDING
Use this to generate license keys for customers
"""

import hashlib
import hmac
import json
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk, messagebox, scrolledtext

from license_manager import LicenseManager


class LicenseGeneratorGUI:
    """GUI for generating customer licenses"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("License Generator (ADMIN)")
        self.root.geometry("750x700")

        self.manager = LicenseManager()
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        # Title
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=20, pady=20)

        ttk.Label(title_frame,
                  text="License Generator Tool",
                  font=("", 16, "bold")).pack()

        ttk.Label(title_frame,
                  text="Generate license keys for customers",
                  font=("", 10)).pack()

        # Customer info section
        info_frame = ttk.LabelFrame(self.root, text="Customer Information", padding=15)
        info_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)

        # Machine ID (REQUIRED)
        ttk.Label(info_frame, text="Machine ID (Required):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.machine_id_entry = ttk.Entry(info_frame, width=50)
        self.machine_id_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)

        # MAC Address (REQUIRED)
        ttk.Label(info_frame, text="MAC Address (Required):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.mac_entry = ttk.Entry(info_frame, width=50)
        self.mac_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)

        # Username (REQUIRED)
        ttk.Label(info_frame, text="Username (Required):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(info_frame, width=50)
        self.username_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=10)

        # Customer name (optional)
        ttk.Label(info_frame, text="Customer Name:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.customer_entry = ttk.Entry(info_frame, width=50)
        self.customer_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=10)

        # Validity period
        ttk.Label(info_frame, text="Valid for (days):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.days_spinbox = ttk.Spinbox(info_frame, from_=1, to=3650, width=15)
        self.days_spinbox.set(365)
        self.days_spinbox.grid(row=4, column=1, sticky=tk.W, pady=5, padx=10)

        # Info label
        info_label = ttk.Label(info_frame,
                               text="Customer must provide: Machine ID, MAC Address, and Username\n"
                                    "from the activation dialog",
                               font=("", 8, "italic"),
                               foreground="gray")
        info_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        # Generate button
        ttk.Button(info_frame, text="Generate License",
                   command=self._generate_license).grid(row=6, column=0, columnspan=2, pady=15)

        # Output section
        output_frame = ttk.LabelFrame(self.root, text="Generated License", padding=15)
        output_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)

        self.output_text = scrolledtext.ScrolledText(output_frame, height=10, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Button frame
        button_frame = ttk.Frame(output_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Copy to Clipboard",
                   command=self._copy_to_clipboard).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Clear",
                   command=lambda: self.output_text.delete(1.0, tk.END)).pack(side=tk.RIGHT, padx=5)

    def _generate_license(self):
        """Generate a license key with customer's MAC/username"""
        machine_id = self.machine_id_entry.get().strip()
        mac_address = self.mac_entry.get().strip()
        username = self.username_entry.get().strip()

        if not machine_id:
            messagebox.showerror("Error", "Machine ID is required")
            return

        if not mac_address:
            messagebox.showerror("Error", "MAC Address is required")
            return

        if not username:
            messagebox.showerror("Error", "Username is required")
            return

        try:
            days = int(self.days_spinbox.get())
            customer_name = self.customer_entry.get().strip() or ""

            # Create license data with CUSTOMER's information
            now = datetime.now()
            expires = now + timedelta(days=days)

            license_data = {
                'machine_id': machine_id,
                'mac_address': mac_address.upper(),  # Customer's MAC
                'username': username,  # Customer's username
                'customer_name': customer_name,
                'created': now.isoformat(),
                'expires': expires.isoformat(),
                'valid': True
            }

            # Generate signature using the SAME method as LicenseManager
            signature = self._generate_signature(license_data)
            license_data['signature'] = signature

            # Convert to JSON
            license_json = json.dumps(license_data, indent=2)

            # Display the license
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, license_json)

            # Show summary
            summary = f"""
License Generated Successfully!

Customer: {customer_name or 'N/A'}
Machine ID: {machine_id[:32]}...
MAC Address: {mac_address}
Username: {username}
Valid Until: {expires.strftime('%Y-%m-%d')}
Days: {days}

IMPORTANT:
- This license is bound to MAC address: {mac_address}
- This license is bound to username: {username}
- Copy the ENTIRE JSON text above and send it to the customer
- Customer should paste the ENTIRE JSON (including curly braces) into the activation dialog
"""
            messagebox.showinfo("Success", summary)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate license: {e}")

    def _generate_signature(self, data):
        """Generate HMAC signature - MUST match LicenseManager.generate_signature()"""
        # Remove signature if present
        data_copy = {k: v for k, v in data.items() if k != 'signature'}

        # Use same method as LicenseManager
        data_str = json.dumps(data_copy, sort_keys=True)
        signature = hmac.new(
            self.manager.secret_salt,
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _copy_to_clipboard(self):
        """Copy license to clipboard"""
        license_text = self.output_text.get(1.0, tk.END).strip()

        if not license_text:
            messagebox.showwarning("Warning", "No license to copy")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(license_text)
        messagebox.showinfo("Success", "License copied to clipboard!\n\n"
                                       "Send this ENTIRE JSON to the customer.")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = LicenseGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()