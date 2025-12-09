# Migration Guide: Monolithic → Modular Architecture

## Overview

The Enhanced Crowd Monitoring System has been refactored from a single monolithic file (`PromisingTest.py`) into a
modular architecture with role-specific files.

## What Changed?

### Before (Monolithic)

```
PromisingTest.py (1487 lines)
  ├─ All configuration
  ├─ All logging
  ├─ All geometry
  ├─ All detection
  ├─ All tracking
  ├─ All calibration
  ├─ All occupancy management
  ├─ All visualization
  └─ Main entry point
```

### After (Modular)

```
main.py              (150 lines)  - Entry point
config.py            (50 lines)   - Configuration
logger_config.py     (25 lines)   - Logging
geometry.py          (70 lines)   - Coordinate transforms
detector.py          (150 lines)  - Person detection
trackers.py          (250 lines)  - Object tracking
calibration.py       (200 lines)  - Camera calibration
occupancy.py         (180 lines)  - Grid management
visualizer.py        (450 lines)  - Rendering
monitor.py           (400 lines)  - Orchestration
```

## Benefits

✅ **Better Organization**: Each module has a single responsibility
✅ **Easier Testing**: Test individual components in isolation
✅ **Better Reusability**: Import only what you need
✅ **Easier Maintenance**: Find and fix bugs faster
✅ **Better Collaboration**: Multiple developers can work on different modules
✅ **Clearer Dependencies**: Explicit imports show relationships

## API Compatibility

### Old Usage (Still Works!)

```python
# Old way - still supported
python PromisingTest.py --source 0 --cell-width 2.0
```

### New Usage (Recommended)

```python
# New way - modular
python main.py --source 0 --cell-width 2.0
```

**Note**: Both scripts accept identical command-line arguments!

## Code Changes

### Importing Components

#### Before (Monolithic)

```python
# Everything was in one file
from PromisingTest import (
    MonitoringConfig,
    GeometryProcessor,
    SimpleCentroidTracker,
    EnhancedCrowdMonitor
)
```

#### After (Modular)

```python
# Import from specific modules
from config import MonitoringConfig, TrackData
from geometry import GeometryProcessor
from trackers import SimpleCentroidTracker, DeepSortTracker
from monitor import CrowdMonitor
```

### Using as a Library

#### Before (Monolithic)

```python
from PromisingTest import EnhancedCrowdMonitor, MonitoringConfig

config = MonitoringConfig(
    source="video.mp4",
    cell_width=2.0,
    cell_height=2.0
)

monitor = EnhancedCrowdMonitor(config)
monitor.initialize()
```

#### After (Modular)

```python
from config import MonitoringConfig
from monitor import CrowdMonitor

config = MonitoringConfig(
    source="video.mp4",
    cell_width=2.0,
    cell_height=2.0
)

monitor = CrowdMonitor(config)
monitor.initialize()
```

### Custom Detector Example

#### After (Modular) - Easy Extension

```python
from detector import PersonDetector
from config import MonitoringConfig

class CustomDetector(PersonDetector):
    def detect_persons(self, frame):
        # Your custom detection logic
        detections = []
        # ... custom processing ...
        return detections

# Use in system
config = MonitoringConfig()
detector = CustomDetector(config)
detector.load_model()
```

### Custom Tracker Example

#### After (Modular) - Easy Extension

```python
from trackers import SimpleCentroidTracker
from config import TrackData

class MyCustomTracker:
    def update_tracks(self, detections, frame=None):
        # Your custom tracking logic
        tracks = []
        # ... custom processing ...
        return tracks

# Register in monitor.py
self.tracker = MyCustomTracker()
```

## File Mapping

| Old Location (PromisingTest.py) | New Location | Lines |
|--------------------------------|--------------|-------|
| `MonitoringConfig` class | `config.py` | 12-73 |
| `TrackData` class | `config.py` | 76-84 |
| Logging setup | `logger_config.py` | 14-23 |
| `download_yolo_model()` | `detector.py` | 18-47 |
| `GeometryProcessor` class | `geometry.py` | 14-46 |
| `SimpleCentroidTracker` class | `trackers.py` | 26-124 |
| `DeepSortTracker` class | `trackers.py` | 127-212 |
| Calibration methods | `calibration.py` | All |
| `OccupancyGrid` functionality | `occupancy.py` | All |
| Visualization methods | `visualizer.py` | All |
| `EnhancedCrowdMonitor` class | `monitor.py` | All |
| `parse_arguments()` | `main.py` | 18-100 |
| `main()` function | `main.py` | 103-142 |

## Breaking Changes

### None! 🎉

The modular architecture maintains full backward compatibility. The only change is:

```python
# Old class name
EnhancedCrowdMonitor

# New class name  
CrowdMonitor
```

But functionality is identical!

## Migration Steps

### For End Users

**Nothing required!** Just run the new `main.py` instead of `PromisingTest.py`.

```bash
# Old
python PromisingTest.py --source 0

# New
python main.py --source 0
```

### For Developers/Library Users

1. **Update imports** to use specific modules
2. **Change class name** from `EnhancedCrowdMonitor` to `CrowdMonitor`
3. **Test your code** with the new structure

### Example Migration

**Before:**

```python
# old_code.py
from PromisingTest import (
    EnhancedCrowdMonitor,
    MonitoringConfig,
    SimpleCentroidTracker
)

config = MonitoringConfig(source="0")
monitor = EnhancedCrowdMonitor(config)
monitor.initialize()
```

**After:**

```python
# new_code.py
from config import MonitoringConfig
from monitor import CrowdMonitor
from trackers import SimpleCentroidTracker

config = MonitoringConfig(source="0")
monitor = CrowdMonitor(config)
monitor.initialize()
```

## Testing Your Migration

### 1. Run with sample video

```bash
python main.py --source test_video.mp4
```

### 2. Test all display modes

- Press `1` for raw camera
- Press `2` for grid overlay
- Press `3` for detection view
- Press `4` for monitoring view
- Press `5` for split view

### 3. Test interactive features

- Press `s` to save screenshot
- Press `g` to toggle grid size
- Press `r` to reset grid
- Press `f` to show FPS
- Press `q` to quit

### 4. Test with different configurations

```bash
# Test detection parameters
python main.py --conf 0.5 --detect-every 5

# Test tracking
python main.py --use-deepsort --max-age 50

# Test grid settings
python main.py --cell-width 1.5 --cell-height 1.5
```

## Common Issues

### Import Errors

**Problem:**

```python
ImportError: No module named 'config'
```

**Solution:**
Ensure all module files are in the same directory or add to Python path:

```python
import sys
sys.path.append('/path/to/Stampede-Management')
```

### Circular Imports

**Problem:**

```python
ImportError: cannot import name 'X' from partially initialized module
```

**Solution:**
The new architecture avoids circular dependencies. Ensure you're importing from the correct module.

### Missing Dependencies

**Problem:**

```python
ModuleNotFoundError: No module named 'shapely'
```

**Solution:**

```bash
pip install -r requirements.txt
```

## Deprecation Notice

`PromisingTest.py` is now **legacy code**. While it still works, it will not receive updates. Please migrate to the
modular architecture.

## Support

### Questions?

- Check `README.md` for usage documentation
- Check `ARCHITECTURE.md` for technical details
- Review code comments in each module

### Found a Bug?

1. Identify which module it affects
2. Check the module's documentation
3. Review the relevant test cases
4. Submit an issue with module name and error details

## Future Enhancements

The modular architecture enables:

1. **Plugin System**: Drop in custom detectors/trackers
2. **Unit Testing**: Test each component independently
3. **Performance Profiling**: Identify bottlenecks per module
4. **API Server**: Expose functionality via REST API
5. **Database Integration**: Add persistence layer
6. **Multi-camera Support**: Process multiple feeds
7. **Cloud Deployment**: Deploy components as microservices

## Rollback Plan

If you encounter issues, you can always use the original:

```bash
# Rollback to monolithic version
python PromisingTest.py --source 0
```

But please report the issue so we can fix it in the modular version!

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Files** | 1 monolithic | 10 modular |
| **Lines per file** | 1487 | ~50-450 |
| **Testability** | Difficult | Easy |
| **Maintainability** | Hard | Easy |
| **Extensibility** | Limited | Excellent |
| **Reusability** | Poor | Great |
| **Learning Curve** | Steep | Gentle |
| **Performance** | Same | Same |
| **Features** | Same | Same |

## Conclusion

The modular architecture provides the same functionality with better organization, easier maintenance, and improved
extensibility. Migration is straightforward and backward-compatible.

**Recommendation**: Start using `main.py` for all new projects and gradually migrate existing code.
