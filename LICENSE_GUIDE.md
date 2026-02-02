# License System Guide

Complete guide for the MAC address-based license protection system.

## Overview

The system binds your application to specific hardware (MAC address + username) to prevent unauthorized distribution.

**Features**:

- Hardware binding (MAC + username)
- Time-limited licenses (configurable expiration)
- Digital signatures (tamper protection)
- Professional activation dialog
- Admin GUI for generating customer licenses
- Automated build script

---

## Quick Setup (5 Minutes)

### 1. Configure Secret Salt (CRITICAL!)

Open `auth/license_manager.py` line 27 and change:

```python
# FROM (default - insecure):
self.secret_salt = b"YOUR_SECRET_SALT_HERE_CHANGE_THIS"

# TO (random unique value):
self.secret_salt = b"xK9mP2vQ8nL5rT7wY4uE1jH6fD3sA0zC"
```

**Why?** This secret is used to sign licenses. Default value = anyone can generate valid licenses!

**Status**: ✅ Already changed

### 2. Generate Development License

```bash
python generate_dev_license.py
```

Creates `auth/license.dat` valid for 365 days.

### 3. Test

```bash
python test_system.py
```

Should show: `Tests Passed: 5/5`

### 4. Run

```bash
python config_gui.py
# Or
run_gui.bat
```

Done! System is ready.

---

## Customer License Workflow

### End User Journey

1. **Receives Application** → Gets `CrowdMonitor.exe`
2. **First Launch** → Sees activation dialog
3. **Requests License** → Clicks "Request License", copies Machine ID
4. **Sends to Support** → Emails Machine ID
5. **Receives Key** → Gets license key via email
6. **Activates** → Pastes key, clicks "Activate"
7. **Uses Application** → Full access

### Administrator Workflow

1. **Receives Request** → Customer emails Machine ID
2. **Generates License**:
   ```bash
   cd auth
   python license_generator_tool.py
   ```
3. **Enters Details**:
    - Paste customer's Machine ID
    - Set validity (e.g., 365 days for annual subscription)
    - Enter customer name (optional, for tracking)
4. **Generate** → Click "Generate License"
5. **Copy Key** → Click "Copy to Clipboard"
6. **Send to Customer** → Email license key

### Email Template

```
Subject: Your CrowdMonitor License Key

Dear [Customer],

To activate CrowdMonitor:

1. Run CrowdMonitor.exe
2. Paste this license key:

[PASTE LICENSE KEY HERE]

3. Click "Activate"

Your license expires: [DATE]

Support: support@yourcompany.com
```

---

## Building for Distribution

### Step 1: Verify Configuration

```bash
# Check secret salt is NOT default
grep "secret_salt" auth/license_manager.py
# Should NOT show: YOUR_SECRET_SALT_HERE_CHANGE_THIS
```

### Step 2: Build

```bash
cd auth
python build_protected.py
```

**Output**:

- `dist/CrowdMonitor.exe` - Protected executable
- `CrowdMonitor_Distribution.zip` - Ready-to-distribute package

### Step 3: Test Build

```bash
cd dist
.\CrowdMonitor.exe
```

Should show license activation dialog (no license yet).

### Step 4: Distribute

Send `CrowdMonitor_Distribution.zip` to customers.

---

## Admin Tools

### License Generator GUI

```bash
cd auth
python license_generator_tool.py
```

**Features**:

- Enter customer's Machine ID
- Set validity period (days)
- Add customer info for tracking
- Generate license key
- Copy to clipboard

### Command-Line Generation

```bash
cd auth
python license_manager.py
```

Interactive prompt for generating licenses.

---

## License Management

### Check License Status

```bash
python -c "import sys, os; sys.path.insert(0, 'auth'); from license_manager import LicenseManager; lm = LicenseManager(license_file=os.path.join('auth', 'license.dat')); print(lm.validate_license())"
```

### Get Machine ID

```bash
python -c "import sys; sys.path.insert(0, 'auth'); from license_manager import LicenseManager; lm = LicenseManager(); print(lm.get_machine_id())"
```

### Regenerate License

```bash
python generate_dev_license.py
```

---

## Troubleshooting

### "License is not valid for this computer"

**Cause**: Machine ID doesn't match

**Solution**:

1. Get correct Machine ID from customer
2. Generate new license with correct ID
3. Send to customer

### "License expired on [date]"

**Cause**: License reached expiration

**Solution**:

1. Generate new license (same Machine ID)
2. Send to customer
3. Customer re-activates

### "License file has been tampered with"

**Cause**: Corrupted or modified `license.dat`

**Solution**:

1. Delete `license.dat`
2. Re-activate with original key
3. If problem persists, generate new license

### "No license found"

**Cause**: First run or file deleted

**Solution**:

- Run `python generate_dev_license.py` (development)
- Activate with license key (customers)

---

## Security Best Practices

### 1. Protect Secret Salt

- ✅ Change from default before production
- ✅ Keep private (don't commit to public repos)
- ✅ Use unique value per application
- ✅ Store securely

### 2. Track Issued Licenses

Keep a spreadsheet or database:

| Customer | Email       | Machine ID | License Key | Issued     | Expires    | Status |
|----------|-------------|------------|-------------|------------|------------|--------|
| John Doe | john@ex.com | abc123...  | xyz789...   | 2024-01-15 | 2025-01-15 | Active |

### 3. Support Legitimate Users

- Provide quick license regeneration
- Support hardware changes (new license)
- Offer grace periods for renewals
- Clear communication about licensing

### 4. Version Control

Add to `.gitignore`:

```
*.dat
auth/license.dat
license.dat
auth/__pycache__/
__pycache__/
```

---

## Advanced Features

### Custom License Duration

Edit `generate_dev_license.py`:

```python
# For trial (14 days)
license_key = manager.generate_license_key(days_valid=14)

# For annual (365 days)
license_key = manager.generate_license_key(days_valid=365)

# For perpetual (10 years)
license_key = manager.generate_license_key(days_valid=3650)
```

### Grace Period for Expired Licenses

Edit `auth/license_manager.py`, add to `validate_license()`:

```python
# Allow 7-day grace period
if datetime.now() > expiry_date:
    days_over = (datetime.now() - expiry_date).days
    if days_over <= 7:
        return True, f"License expired {days_over} days ago. Please renew soon."
```

### Online Validation (Optional)

For enterprise deployments, add server-side validation:

```python
import requests

def validate_online(self, license_data):
    response = requests.post(
        "https://yourapi.com/validate",
        json=license_data
    )
    return response.status_code == 200
```

---

## File Locations

```
auth/
├── license_manager.py           # Core licensing system
├── license_generator_tool.py    # Admin GUI tool
├── build_protected.py          # Build script
├── crowd_monitor_protected.spec # PyInstaller config
└── license.dat                 # License file (auto-created)

Root/
├── generate_dev_license.py     # Quick license generator
├── config_gui.py              # Protected GUI
├── main.py                    # Protected CLI
└── test_system.py             # Verification script
```

---

## Build Configuration

### PyInstaller Spec File

`auth/crowd_monitor_protected.spec` configures:

- Single file executable (`onefile=True`)
- No console window (`console=False`)
- UPX compression (`upx=True`)
- Hidden imports (tkinter, license_manager)
- Icon and version info

### Customizing Build

Edit `crowd_monitor_protected.spec`:

```python
# Add icon
icon='icon.ico'

# Add version info
version='version_info.txt'

# Include data files
datas=[
    ('model/*.pt', 'model'),
    ('config.json', '.'),
]
```

---

## Testing Before Distribution

### Checklist

- [ ] Secret salt changed from default
- [ ] Built executable with `build_protected.py`
- [ ] Tested on clean Windows machine
- [ ] License activation works
- [ ] Application runs after activation
- [ ] License info displays correctly
- [ ] Expiration warnings work
- [ ] Invalid license handling works

### Test Commands

```bash
# Test system
python test_system.py

# Test GUI locally
python config_gui.py

# Build
cd auth && python build_protected.py

# Test executable
cd dist && .\CrowdMonitor.exe
```

---

## Support Workflow

### Customer Support Checklist

1. **Receive Request**
    - Customer name
    - Email
    - Machine ID
    - Purchase date/order number

2. **Verify Purchase** (optional)
    - Check payment records
    - Confirm order

3. **Generate License**
    - Open `license_generator_tool.py`
    - Enter Machine ID
    - Set appropriate duration
    - Generate and copy key

4. **Send License**
    - Use email template
    - Include expiration date
    - Provide support contact

5. **Record in System**
    - Log in tracking spreadsheet
    - Note issue date and expiry

6. **Follow Up** (optional)
    - Confirm activation successful
    - Offer support if needed

---

## FAQ

**Q: Can users share the executable?**
A: Yes, but it won't run without a valid license for their specific machine.

**Q: What if a user upgrades their computer?**
A: Generate a new license with their new Machine ID.

**Q: How do I revoke a license?**
A: Licenses expire automatically. For immediate revocation, implement online validation.

**Q: Can I issue multi-machine licenses?**
A: Not with this system. Each license is for one machine. For site licenses, generate multiple licenses.

**Q: Is this protection unbreakable?**
A: No protection is unbreakable. This protects against casual sharing, not determined attackers.

**Q: Can I change the license duration?**
A: Yes, edit the `days_valid` parameter when generating licenses.

---

## Summary

### What You Get

✅ MAC address + username hardware binding
✅ Time-limited licenses with expiration
✅ Professional activation dialog
✅ Admin GUI for customer licenses
✅ Automated build process
✅ Tamper-resistant license storage
✅ Periodic validation (every 5 minutes)
✅ Complete documentation

### What to Remember

1. **Change secret salt** before production ✅ (Already done)
2. **Track issued licenses** in spreadsheet/database
3. **Support legitimate users** with quick license regeneration
4. **Test thoroughly** before distributing
5. **Keep `.dat` files** out of version control

### Next Steps

**For Development**:

```bash
python generate_dev_license.py  # Already done
python config_gui.py            # Start using
```

**For Production**:

```bash
cd auth
python build_protected.py       # Build executable
# Test, then distribute
```

**For Customers**:

```bash
# They run CrowdMonitor.exe
# Request license → you generate → they activate
```

---

**System Status**: ✅ Production Ready

For quick reference, see `README.md` or `START_HERE.md`.