# Files Overview - Essential Files Only

## Core Application Files ✅

### Main Files

- **config_gui.py** - GUI application with license protection
- **main.py** - Command-line version with license protection
- **config.py** - Configuration dataclass
- **monitor.py** - Core monitoring logic
- **detector.py** - Person detection (YOLO)
- **trackers.py** - Object tracking (DeepSort/Centroid)
- **visualizer.py** - Display and visualization
- **calibration.py** - Perspective transformation
- **occupancy.py** - Grid occupancy calculations
- **geometry.py** - Geometric utilities
- **logger_config.py** - Logging configuration

### Support Files

- **requirements.txt** - Python dependencies
- **system_conf.json** - System configuration
- **install_dependencies.bat** - Dependency installer (Windows)

---

## License System Files ✅

### Auth Folder (`auth/`)

- **license_manager.py** - Core licensing system
- **license_generator_tool.py** - Admin GUI for generating customer licenses
- **build_protected.py** - Automated build script
- **crowd_monitor_protected.spec** - PyInstaller configuration
- **license.dat** - License file (auto-created, gitignored)

### License Tools (Root)

- **generate_dev_license.py** - Quick development license generator
- **test_system.py** - System verification script
- **run_gui.bat** - Windows launcher

---

## Documentation ✅

- **README.md** - Main documentation (start here)
- **START_HERE.md** - Quick start guide
- **LICENSE_GUIDE.md** - Complete licensing documentation
- **FILES_OVERVIEW.md** - This file

---

## Model Files

- **model/yolov8n.pt** - YOLO model (6.2MB)

---

## Supporting Folders

### docs/

Original project documentation:

- ARCHITECTURE.md - System architecture
- INDEX.md - Documentation index
- MIGRATION_GUIDE.md - Migration guide
- PROJECT_SUMMARY.md - Project overview
- QUICK_REFERENCE.md - Quick reference
- README.md - Docs readme

### examples/

- example_usage.py - Usage examples
- test sample 1.jpg - Test image
- test sample 2.jpg - Test image

---

## Configuration Files

- **.gitignore** - Git ignore rules (license files, logs, etc.)

---

## What Was Removed ❌

**Deleted for cleaner codebase**:

- auth/gui_protected.py (duplicate - config_gui.py is already protected)
- auth/LICENSE_SETUP_GUIDE.md (duplicate)
- auth/QUICK_START.md (consolidated to START_HERE.md)
- auth/README.md (consolidated to README.md)
- SETUP_VERIFICATION.md (test_system.py provides verification)
- SYSTEM_READY.md (redundant)
- AUTH_QUICKSTART_CARD.md (consolidated to LICENSE_GUIDE.md)
- LICENSE_SETUP_GUIDE.md (replaced with LICENSE_GUIDE.md)
- *.log files (gitignored)
- Duplicate license.dat in root (kept in auth/)

---

## File Count Summary

**Essential Application**: 12 Python files
**License System**: 4 Python files + 1 spec file
**Documentation**: 4 MD files
**Support**: 3 files (requirements.txt, system_conf.json, bat file)
**Model**: 1 file (yolov8n.pt)

**Total Essential Files**: ~25 files (excluding docs/ and examples/)

---

## Quick Commands

### Run Application

```bash
python config_gui.py
# or
run_gui.bat
```

### Generate License

```bash
python generate_dev_license.py
```

### Test System

```bash
python test_system.py
```

### Build Executable

```bash
cd auth
python build_protected.py
```

### Generate Customer Licenses

```bash
cd auth
python license_generator_tool.py
```

---

## Directory Structure

```
E:/Stampede-Management/
│
├── Core Application (12 files)
│   ├── config_gui.py
│   ├── main.py
│   ├── config.py
│   ├── monitor.py
│   ├── detector.py
│   ├── trackers.py
│   ├── visualizer.py
│   ├── calibration.py
│   ├── occupancy.py
│   ├── geometry.py
│   ├── logger_config.py
│   └── (support files)
│
├── License System (auth/)
│   ├── license_manager.py
│   ├── license_generator_tool.py
│   ├── build_protected.py
│   ├── crowd_monitor_protected.spec
│   └── license.dat (auto-created)
│
├── Tools & Scripts (3 files)
│   ├── generate_dev_license.py
│   ├── test_system.py
│   └── run_gui.bat
│
├── Documentation (4 files)
│   ├── README.md
│   ├── START_HERE.md
│   ├── LICENSE_GUIDE.md
│   └── FILES_OVERVIEW.md
│
├── Model (model/)
│   └── yolov8n.pt
│
├── Docs (docs/) - Optional reference
│   └── (original documentation)
│
└── Examples (examples/) - Optional reference
    └── (usage examples)
```

---

## What to Keep in Version Control

**Keep**:

- All .py files
- Documentation (.md files)
- requirements.txt
- system_conf.json
- .spec file
- .bat file
- .gitignore

**Don't Commit** (in .gitignore):

- *.dat (license files)
- *.log (log files)
- __pycache__/
- dist/
- build/
- *.exe
- model/*.pt (too large)

---

## Clean Codebase Status

✅ Removed duplicate documentation
✅ Removed example protected GUI (using integrated version)
✅ Removed redundant guides
✅ Consolidated documentation
✅ Clean .gitignore
✅ Removed log files
✅ Removed duplicate license files

**Result**: Lean, professional codebase with only essential files.

---

## For New Developers

**Read First**:

1. README.md - Overview and quick start
2. START_HERE.md - Detailed setup
3. LICENSE_GUIDE.md - License system (if customizing)

**Run This**:

```bash
python test_system.py  # Verify everything works
```

**Then**:

```bash
python config_gui.py  # Start using the application
```

---

## Maintenance

### Adding Features

- Edit core .py files as needed
- Test with `python test_system.py`
- Update documentation if significant changes

### Updating License System

- Modify `auth/license_manager.py`
- Update secret salt for new major versions
- Test license generation and validation

### Building New Version

```bash
cd auth
python build_protected.py
```

---

**Current State**: Clean, production-ready codebase with essential files only.

**Total Files**: ~25 essential + docs/ and examples/ (optional)