# Enhanced Crowd Monitoring System - File Index

## 📖 Start Here!

New to the project? Read these in order:

1. **PROJECT_SUMMARY.md** - High-level overview (5 min read)
2. **README.md** - Usage guide (10 min read)
3. **QUICK_REFERENCE.md** - Command cheat sheet (quick reference)
4. Run: `python main.py --source 0`

## 🗂️ Complete File Index

### 🚀 Executable Files

| File | Purpose | When to Use |
|------|---------|-------------|
| `main.py` | **NEW** entry point | Use this for all new projects |
| `PromisingTest.py` | **DEPRECATED** monolithic version | Legacy support only |
| `example_usage.py` | Code examples | Learn how to use components |

**Quick Start:**

```bash
python main.py --source 0
```

---

### ⚙️ Core System Modules

| Module | Lines | Purpose | Depends On |
|--------|-------|---------|------------|
| `config.py` | 55 | Configuration & data structures | None |
| `logger_config.py` | 23 | Logging setup | None |
| `geometry.py` | 69 | Coordinate transformations | config |
| `detector.py` | 162 | Person detection (YOLO) | config, logger_config |
| `trackers.py` | 243 | Object tracking | config, logger_config |
| `calibration.py` | 227 | Camera calibration | geometry, logger_config |
| `occupancy.py` | 177 | Grid management & alerts | config, geometry, logger_config |
| `visualizer.py` | 381 | Display rendering | config, geometry, occupancy, trackers |
| `monitor.py` | 442 | System orchestrator | All above modules |
| `main.py` | 140 | Entry point & CLI | config, monitor, logger_config |

**Dependency Order (Bottom-up):**

```
config.py, logger_config.py (base)
    ↓
geometry.py
    ↓
detector.py, trackers.py, calibration.py
    ↓
occupancy.py
    ↓
visualizer.py
    ↓
monitor.py
    ↓
main.py
```

---

### 📚 Documentation Files

| File | Pages | Purpose | Read When... |
|------|-------|---------|--------------|
| **PROJECT_SUMMARY.md** | 9 | Overall project overview | Starting out |
| **README.md** | 6 | General documentation | Need usage info |
| **QUICK_REFERENCE.md** | 9 | Command cheat sheet | Need quick help |
| **ARCHITECTURE.md** | 13 | Technical deep-dive | Want to understand internals |
| **MIGRATION_GUIDE.md** | 9 | Upgrade guide | Migrating from old version |
| **MODULE_DIAGRAM.txt** | 16 | Visual architecture | Need big picture |
| **INDEX.md** | - | This file! | Finding your way around |

**Reading Guide:**

```
For Users:
  README.md → QUICK_REFERENCE.md

For Developers:
  PROJECT_SUMMARY.md → ARCHITECTURE.md → MODULE_DIAGRAM.txt

For Migrating:
  MIGRATION_GUIDE.md
```

---

### 📦 Configuration Files

| File | Purpose | Edit When... |
|------|---------|-------------|
| `requirements.txt` | Python dependencies | Adding new libraries |

**Install dependencies:**

```bash
pip install -r requirements.txt
```

---

### 🔧 Runtime Generated Files

These are created automatically when you run the system:

| File | Created By | Purpose |
|------|-----------|---------|
| `crowd_monitor.log` | logger_config.py | Application logs |
| `yolov8n.pt` | detector.py | YOLO model (auto-downloaded) |
| `calibration_frame.jpg` | calibration.py | Reference image for calibration |
| `crowd_monitor_*.jpg` | monitor.py | Screenshots (press 's') |

**Don't commit these to version control!**

---

## 🎯 Quick Navigation

### I want to...

#### Run the System

→ `python main.py`  
→ Read: `README.md`, `QUICK_REFERENCE.md`

#### Understand How It Works

→ Read: `ARCHITECTURE.md`, `MODULE_DIAGRAM.txt`  
→ Look at: `monitor.py`, `main.py`

#### Modify Detection

→ Edit: `detector.py`  
→ Read: `ARCHITECTURE.md` (Detection Layer)

#### Customize Tracking

→ Edit: `trackers.py`  
→ Example: `example_usage.py` (Example 4)

#### Change Grid Behavior

→ Edit: `occupancy.py`  
→ Read: `ARCHITECTURE.md` (Processing Layer)

#### Modify Visualization

→ Edit: `visualizer.py`  
→ Read: `ARCHITECTURE.md` (Presentation Layer)

#### Add New Features

→ Read: `ARCHITECTURE.md` (Extension Points)  
→ Look at: `example_usage.py`

#### Debug Issues

→ Check: `crowd_monitor.log`  
→ Read: `QUICK_REFERENCE.md` (Troubleshooting)

#### Migrate from Old Version

→ Read: `MIGRATION_GUIDE.md`  
→ Use: `main.py` instead of `PromisingTest.py`

---

## 📊 Module Complexity Matrix

| Module | Complexity | Lines | Functions | Dependencies |
|--------|-----------|-------|-----------|--------------|
| `config.py` | ⭐ Simple | 55 | 2 | 0 |
| `logger_config.py` | ⭐ Simple | 23 | 1 | 0 |
| `geometry.py` | ⭐⭐ Easy | 69 | 3 | 2 |
| `detector.py` | ⭐⭐ Easy | 162 | 3 | 3 |
| `trackers.py` | ⭐⭐⭐ Medium | 243 | 12 | 2 |
| `calibration.py` | ⭐⭐⭐ Medium | 227 | 5 | 3 |
| `occupancy.py` | ⭐⭐⭐ Medium | 177 | 5 | 4 |
| `visualizer.py` | ⭐⭐⭐⭐ Complex | 381 | 15 | 5 |
| `monitor.py` | ⭐⭐⭐⭐ Complex | 442 | 20 | 9 |
| `main.py` | ⭐⭐ Easy | 140 | 2 | 3 |

**Start learning from:** `config.py` → `geometry.py` → `detector.py`

---

## 🔍 Find Specific Functionality

### Detection

- **YOLO model loading**: `detector.py` → `PersonDetector.load_model()`
- **Person detection**: `detector.py` → `PersonDetector.detect_persons()`
- **Detection filtering**: `detector.py` (lines 110-145)

### Tracking

- **Simple tracking**: `trackers.py` → `SimpleCentroidTracker`
- **DeepSort tracking**: `trackers.py` → `DeepSortTracker`
- **Track matching**: `trackers.py` → `_match_tracks_to_detections()`

### Calibration

- **Point selection**: `calibration.py` → `_get_calibration_points()`
- **Dimension input**: `calibration.py` → `_get_world_dimensions()`
- **Homography calc**: `calibration.py` → `calibrate()`

### Geometry

- **Bbox projection**: `geometry.py` → `project_bbox_to_world()`
- **Point transform**: `geometry.py` → `world_to_image_point()`

### Occupancy

- **Grid update**: `occupancy.py` → `OccupancyGrid.update()`
- **Alert logic**: `occupancy.py` → `_update_alerts()`
- **Cell capacity**: `occupancy.py` → `__init__()` (lines 30-33)

### Visualization

- **Grid overlay**: `visualizer.py` → `draw_grid_overlay()`
- **Track boxes**: `visualizer.py` → `draw_track_annotation()`
- **Bird's eye**: `visualizer.py` → `create_birdseye_view()`
- **Info panel**: `visualizer.py` → `create_info_panel()`

### Orchestration

- **Main loop**: `monitor.py` → `_process_video_stream()`
- **Frame processing**: `monitor.py` → `_process_frame()`
- **Mode switching**: `monitor.py` → `_handle_mode_switch()`
- **Screenshot**: `monitor.py` → `_save_screenshot()`

---

## 📈 Code Statistics

```
Total Files:        13 modules + 6 docs + 1 example = 20 files
Total Lines:        ~2,000 (code) + ~1,500 (docs) = ~3,500 lines
Core Modules:       10 files
Documentation:      7 files
Examples:           1 file

Module Breakdown:
  Entry Point:      main.py (140 lines)
  Configuration:    config.py + logger_config.py (78 lines)
  Utilities:        geometry.py (69 lines)
  Detection:        detector.py (162 lines)
  Tracking:         trackers.py (243 lines)
  Calibration:      calibration.py (227 lines)
  Occupancy:        occupancy.py (177 lines)
  Visualization:    visualizer.py (381 lines)
  Orchestration:    monitor.py (442 lines)
```

---

## 🧪 Testing Workflow

### Quick Tests

```bash
# Test basic functionality
python main.py --source 0

# Test with example code
python example_usage.py 5
```

### Component Tests

```bash
# Test detector
python example_usage.py 3

# Test tracker
python example_usage.py 4

# Test geometry
python example_usage.py 5

# Test occupancy
python example_usage.py 6
```

### Integration Tests

```bash
# Full system test with video
python main.py --source sample_video.mp4

# Test different modes (press 1-5)
# Test screenshots (press s)
# Test grid adjustment (press g, r)
```

---

## 🔗 External Resources

- **YOLOv8 Docs**: https://docs.ultralytics.com/
- **OpenCV Docs**: https://docs.opencv.org/
- **Shapely Docs**: https://shapely.readthedocs.io/
- **DeepSort**: https://github.com/levan92/deep_sort_realtime

---

## 📞 Getting Help

1. **Check documentation**: Start with `README.md`
2. **Read examples**: Run `example_usage.py`
3. **Check logs**: View `crowd_monitor.log`
4. **Review architecture**: Read `ARCHITECTURE.md`
5. **Debug**: Use print statements or Python debugger

---

## 🎓 Learning Path

### Beginner (Day 1)

1. Read `PROJECT_SUMMARY.md`
2. Read `README.md`
3. Run `python main.py`
4. Play with keyboard controls

### Intermediate (Day 2-3)

1. Read `QUICK_REFERENCE.md`
2. Try different configurations
3. Run `example_usage.py` examples
4. Read `config.py` and `detector.py`

### Advanced (Week 1)

1. Read `ARCHITECTURE.md`
2. Study `MODULE_DIAGRAM.txt`
3. Read all module source code
4. Modify a module (e.g., add custom tracker)

### Expert (Week 2+)

1. Read `MIGRATION_GUIDE.md`
2. Understand all dependencies
3. Contribute new features
4. Optimize performance

---

## 📝 Notes

- All modules use Python 3.7+
- Type hints used throughout for clarity
- Docstrings follow Google style
- Code formatted for readability
- Error handling at all levels

---

## ✅ Checklist for New Users

- [ ] Read `PROJECT_SUMMARY.md`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run system: `python main.py`
- [ ] Complete calibration
- [ ] Test all 5 display modes (press 1-5)
- [ ] Try screenshot (press s)
- [ ] Read `QUICK_REFERENCE.md`
- [ ] Run examples: `python example_usage.py 5`

---

## 🏁 Quick Command Reference

```bash
# Install
pip install -r requirements.txt

# Run (basic)
python main.py

# Run (with options)
python main.py --source video.mp4 --cell-width 2.0

# Examples
python example_usage.py 5

# Help
python main.py --help
```

---

**Last Updated**: December 2025  
**Version**: 2.0 (Modular Architecture)  
**Replaces**: PromisingTest.py (v1.0 Monolithic)
