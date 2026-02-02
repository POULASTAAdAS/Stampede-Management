# Crowd Monitoring System

Professional crowd monitoring with MAC address-based license protection.

## Quick Start

### 1. First Time Setup

```bash
# Generate your development license
python generate_dev_license.py
```

### 2. Run the Application

```bash
# GUI (Recommended)
python config_gui.py

# Or use the launcher
run_gui.bat

# Command line
python main.py --source 0
```

### 3. Verify System

```bash
python test_system.py
```

Expected: All 5 tests pass ✓

---

## Features

- **License Protection**: MAC address-based hardware binding
- **Time-Limited Licenses**: Configurable expiration (default: 365 days)
- **Professional UI**: GUI with tabs for all settings
- **Real-time Monitoring**: Crowd detection and tracking
- **Grid Analysis**: Spatial occupancy calculations
- **Calibration System**: Perspective transformation
- **Alert System**: Threshold-based warnings

---

## File Structure

```
├── config_gui.py              # Main GUI (START HERE)
├── main.py                    # Command-line version
├── generate_dev_license.py    # Generate licenses
├── test_system.py            # Verify installation
├── run_gui.bat               # Windows launcher
├── auth/                     # License system
│   ├── license_manager.py
│   ├── license_generator_tool.py
│   ├── build_protected.py
│   └── license.dat          # Your license (auto-created)
├── model/
│   └── yolov8n.pt           # YOLO model
└── docs/                    # Additional documentation
```

---

## For Administrators

### Generate Customer Licenses

```bash
cd auth
python license_generator_tool.py
```

Workflow:

1. Customer sends Machine ID
2. Enter in tool
3. Set validity period (365 days for annual)
4. Generate license key
5. Send to customer

### Build Executable for Distribution

```bash
cd auth
python build_protected.py
```

Output: `dist/CrowdMonitor.exe` and `CrowdMonitor_Distribution.zip`

---

## Customer License Activation

**Customer**:

1. Run CrowdMonitor.exe
2. Click "Request License"
3. Copy Machine ID → Email to support
4. Receive license key
5. Paste in dialog → Click "Activate"

**You**:

1. Open `auth/license_generator_tool.py`
2. Paste customer's Machine ID
3. Generate license
4. Send key to customer

---

## Configuration

### Secret Salt (IMPORTANT!)

Before building for production, change the secret salt in `auth/license_manager.py` line 27:

```python
self.secret_salt = b"YOUR_UNIQUE_RANDOM_STRING_HERE"
```

**Current**: Already changed to custom value ✓

### License File Location

Default: `auth/license.dat` (auto-created)

---

## Requirements

```bash
pip install -r requirements.txt
```

Key dependencies:

- Python 3.8+
- OpenCV
- Ultralytics (YOLO)
- tkinter (GUI)
- PyInstaller (for building exe)

---

## Documentation

- **START_HERE.md** - Detailed quick start guide
- **LICENSE_SETUP_GUIDE.md** - Complete licensing documentation
- **docs/** - Architecture, migration guides, etc.

---

## Troubleshooting

| Problem            | Solution                             |
|--------------------|--------------------------------------|
| "No license found" | Run `python generate_dev_license.py` |
| "License expired"  | Generate new license                 |
| GUI won't start    | Run `python test_system.py`          |
| Import errors      | Check you're in correct directory    |
| Build fails        | `pip install --upgrade pyinstaller`  |

### Common Commands

```bash
# Regenerate license
python generate_dev_license.py

# Test system
python test_system.py

# Check license status
python -c "import sys, os; sys.path.insert(0, 'auth'); from license_manager import LicenseManager; lm = LicenseManager(license_file=os.path.join('auth', 'license.dat')); print(lm.validate_license())"
```

---

## Security

- **Hardware Binding**: MAC address + username
- **Encryption**: XOR-obfuscated license files
- **Digital Signatures**: Tamper protection
- **Periodic Validation**: Every 5 minutes
- **Hidden Files**: License file hidden on Windows

**Before Distribution**:

1. Change secret salt to unique value
2. Test on clean machine
3. Verify license activation works

---

## Support

For issues:

1. Run `python test_system.py` - should pass 5/5 tests
2. Check `crowd_monitor.log` for errors
3. Review documentation in `docs/`
4. Regenerate license if needed

---

## License System Details

### Features:

- Time-based expiration
- Hardware-locked (MAC + username)
- Tamper-resistant
- Professional activation dialog
- Status display in GUI
- Admin tools for customer licenses

### Admin Tools:

- `license_generator_tool.py` - GUI for generating customer licenses
- `license_manager.py` - Command-line license generation
- `build_protected.py` - Build executable with protection

### File: `auth/license.dat`

- Encrypted license storage
- Auto-created on activation
- Hidden on Windows
- Don't commit to version control

---

## Build Process

```bash
# 1. Verify secret salt changed
# 2. Build executable
cd auth
python build_protected.py

# 3. Test
cd dist
.\CrowdMonitor.exe

# 4. Distribute
# Send CrowdMonitor_Distribution.zip to customers
```

---

## Development

### Test Changes

```bash
python test_system.py  # Verify all systems working
python config_gui.py   # Test GUI
python main.py --source 0  # Test CLI
```

### Add New Features

Core files:

- `config_gui.py` - GUI interface
- `main.py` - Entry point
- `monitor.py` - Monitoring logic
- `detector.py` - Person detection
- `visualizer.py` - Display
- `calibration.py` - Perspective transform

---

## Quick Reference

**Run Application**:

```bash
python config_gui.py
```

**Generate License**:

```bash
python generate_dev_license.py
```

**Test System**:

```bash
python test_system.py
```

**Build Executable**:

```bash
cd auth && python build_protected.py
```

**Generate Customer License**:

```bash
cd auth && python license_generator_tool.py
```

---

## System Status

✅ License system integrated
✅ GUI protected
✅ CLI protected  
✅ Admin tools ready
✅ Build script ready
✅ Documentation complete
✅ Test suite passing (5/5)

**Status**: Production Ready

---

**Version**: 1.0
**Last Updated**: February 2026
**Platform**: Windows 10+
**Python**: 3.8+