# Crowd Monitoring System - Quick Start Guide

## First Time Setup (2 minutes)

### Step 1: Generate Your License (One-Time)

```bash
python generate_dev_license.py
```

Expected output:

```
Generating development license...
MAC Address: e8:48:b8:c8:20:00
Machine ID: 9537115eb67e76adf096ad2108fc19ca2307f778f9fef38d5685e11f663395ee

License generated!
[OK] License saved to auth\license.dat
[OK] License validated: License is valid

You can now run the application!
```

### Step 2: Run the Application

#### Option A: GUI Version (Recommended)

```bash
python config_gui.py
```

This opens the full configuration GUI with:

- Visual configuration of all parameters
- Tabs for different settings
- License info display
- One-click monitoring start

#### Option B: Command Line Version

```bash
python main.py --source 0
```

This runs the monitoring system directly with command-line parameters.

### Step 3: Check License Status

In the GUI, click the **"License Info"** button to see:

- MAC Address
- Username
- License creation date
- Expiration date
- Days remaining

---

## Common Tasks

### Generate a New License

```bash
python generate_dev_license.py
```

### Check If License is Valid

```bash
python -c "import sys, os; sys.path.insert(0, 'auth'); from license_manager import LicenseManager; lm = LicenseManager(license_file=os.path.join('auth', 'license.dat')); print(lm.validate_license())"
```

### Get Your Machine ID

```bash
python -c "import sys; sys.path.insert(0, 'auth'); from license_manager import LicenseManager; lm = LicenseManager(); print(f'Machine ID: {lm.get_machine_id()}')"
```

### Generate Licenses for Customers (Admin)

```bash
cd auth
python license_generator_tool.py
```

This opens a GUI where you can:

1. Enter customer's Machine ID
2. Set validity period (days)
3. Generate license key
4. Copy and send to customer

---

## File Locations

```
E:/Stampede-Management/
├── config_gui.py                    ← Main GUI (run this)
├── main.py                          ← Command-line version
├── generate_dev_license.py          ← Generate license quickly
├── auth/
│   ├── license.dat                  ← Your license file (auto-created)
│   ├── license_manager.py          ← Core licensing system
│   └── license_generator_tool.py   ← Admin tool
├── START_HERE.md                    ← This file
├── LICENSE_SETUP_GUIDE.md           ← Full documentation
└── AUTH_QUICKSTART_CARD.md          ← Quick reference
```

---

## Troubleshooting

### "No license found"

**Solution**: Run `python generate_dev_license.py`

### "License expired"

**Solution**: Generate a new license with `python generate_dev_license.py`

### "Import Error: license_manager"

**Solution**: Make sure you're in the `E:/Stampede-Management` directory

### GUI Won't Start

**Solution**:

```bash
# Check for errors
python config_gui.py

# Or check imports
python -c "from config_gui import ConfigurationGUI; print('OK')"
```

### "Permission denied: license.dat"

**Solution**:

- Close any open applications using the file
- Delete `auth/license.dat`
- Run `python generate_dev_license.py` again

---

## Building Executable for Distribution

### Step 1: Verify Secret Salt (CRITICAL!)

Open `auth/license_manager.py` line 27:

```python
# Should NOT be default:
self.secret_salt = b"xK9mP2vQ8nL5rT7wY4uE1jH6fD3sA0zC"  # ✓ Good
# NOT:
self.secret_salt = b"YOUR_SECRET_SALT_HERE_CHANGE_THIS"  # ✗ Bad
```

### Step 2: Build

```bash
cd auth
python build_protected.py
```

### Step 3: Test

```bash
cd dist
.\CrowdMonitor.exe
```

### Step 4: Distribute

Send customers `CrowdMonitor_Distribution.zip`

---

## Customer License Workflow

### Customer Side:

1. Run `CrowdMonitor.exe`
2. Click "Request License"
3. Copy Machine ID
4. Email to you

### Your Side:

1. Run `auth/license_generator_tool.py`
2. Paste customer's Machine ID
3. Set validity (365 days for annual)
4. Generate license
5. Send license key to customer

### Customer Side:

1. Paste license key in activation dialog
2. Click "Activate"
3. Application unlocks

---

## Documentation

- **This File**: Quick start guide
- **LICENSE_SETUP_GUIDE.md**: Comprehensive 800+ line guide
- **AUTH_QUICKSTART_CARD.md**: Printable reference card
- **auth/README.md**: Auth folder documentation
- **SETUP_VERIFICATION.md**: Setup verification checklist

---

## Support

For detailed information, see:

- `LICENSE_SETUP_GUIDE.md` - Complete documentation
- `AUTH_QUICKSTART_CARD.md` - Quick reference
- `auth/README.md` - Auth system details

---

## System Status

✅ **License System**: Integrated
✅ **GUI**: License-protected
✅ **Command-Line**: License-protected
✅ **Build Script**: Ready
✅ **Admin Tools**: Available
✅ **Documentation**: Complete

**Everything is ready to use!**

---

## Next Steps

1. ✅ License generated → Run `python generate_dev_license.py`
2. ✅ Test GUI → Run `python config_gui.py`
3. ✅ Configure settings → Use the GUI tabs
4. ✅ Start monitoring → Click "▶ Run Monitor"
5. ⬜ Build executable → When ready for distribution

**Happy Monitoring!** 🎥📊