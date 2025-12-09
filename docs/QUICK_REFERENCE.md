# Quick Reference Guide

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default settings
python main.py

# Run with video file
python main.py --source video.mp4

# Run with custom grid size
python main.py --cell-width 1.5 --cell-height 1.5
```

## Module Import Cheat Sheet

```python
# Configuration
from config import MonitoringConfig, TrackData

# Detection
from detector import PersonDetector

# Tracking
from trackers import SimpleCentroidTracker, DeepSortTracker

# Geometry
from geometry import GeometryProcessor

# Calibration
from calibration import CameraCalibrator

# Occupancy
from occupancy import OccupancyGrid

# Visualization
from visualizer import MonitorVisualizer

# Main System
from monitor import CrowdMonitor

# Logging
from logger_config import get_logger
```

## Common Tasks

### 1. Run Basic Monitoring

```bash
python main.py --source 0
```

### 2. Adjust Detection Sensitivity

```bash
# Lower confidence = more detections
python main.py --conf 0.3

# Higher confidence = fewer false positives
python main.py --conf 0.5
```

### 3. Change Grid Size

```bash
# Smaller cells (more detailed)
python main.py --cell-width 1.0 --cell-height 1.0

# Larger cells (less detailed)
python main.py --cell-width 3.0 --cell-height 3.0
```

### 4. Adjust Person Capacity

```bash
# More space per person
python main.py --person-radius 0.8

# Less space per person
python main.py --person-radius 0.4
```

### 5. Performance Tuning

```bash
# Faster (detect less often)
python main.py --detect-every 5

# More accurate (detect more often)
python main.py --detect-every 1
```

### 6. Use DeepSort Tracking

```bash
pip install deep-sort-realtime
python main.py --use-deepsort
```

## Keyboard Controls

| Key | Action |
|-----|--------|
| `1` | Raw camera view |
| `2` | Grid overlay view |
| `3` | Detection view (bboxes) |
| `4` | Full monitoring view |
| `5` | Split view (quad) |
| `s` | Save screenshot |
| `g` | Toggle grid size |
| `r` | Reset grid |
| `f` | Toggle FPS display |
| `q` | Quit |

## Code Templates

### Template 1: Basic Usage

```python
from config import MonitoringConfig
from monitor import CrowdMonitor

config = MonitoringConfig(source="0")
monitor = CrowdMonitor(config)
monitor.initialize()
```

### Template 2: Custom Detection

```python
from detector import PersonDetector
from config import MonitoringConfig

config = MonitoringConfig(
    confidence_threshold=0.4,
    min_bbox_area=2000
)
detector = PersonDetector(config)
detector.load_model()

# Use detector
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
detections = detector.detect_persons(frame)
```

### Template 3: Custom Tracking

```python
from trackers import SimpleCentroidTracker

tracker = SimpleCentroidTracker(
    max_age=30,
    distance_threshold=80.0
)

# Update with detections
tracks = tracker.update_tracks(detections, frame)
```

### Template 4: Occupancy Monitoring

```python
from occupancy import OccupancyGrid
from config import MonitoringConfig

config = MonitoringConfig(
    cell_width=2.0,
    cell_height=2.0,
    person_radius=0.5
)

grid = OccupancyGrid(config, geometry_processor, 10.0, 8.0)
grid.update(tracks, dt=0.1)

# Check for alerts
if grid.notified.any():
    print("Overcapacity alert!")
```

### Template 5: Custom Visualization

```python
from visualizer import MonitorVisualizer
from config import MonitoringConfig

config = MonitoringConfig()
viz = MonitorVisualizer(config, 640, 480)

# Draw on frame
viz.draw_grid_overlay(frame, geo_processor, occupancy_grid)
viz.draw_track_annotation(frame, track, occupancy_grid)
```

## Configuration Options

### Video Source

- `--source 0` - Default camera
- `--source 1` - Secondary camera
- `--source video.mp4` - Video file
- `--source rtsp://...` - Network stream

### Model Selection

- `--model yolov8n.pt` - Nano (fastest)
- `--model yolov8s.pt` - Small
- `--model yolov8m.pt` - Medium
- `--model yolov8l.pt` - Large
- `--model yolov8x.pt` - Extra large (most accurate)

### Detection Parameters

- `--conf 0.35` - Confidence threshold (0.0-1.0)
- `--detect-every 3` - Detection frequency (frames)
- `--min-bbox-area 1500` - Minimum detection size (pixels²)

### Tracking Parameters

- `--max-age 30` - Max frames to keep track
- `--n-init 1` - Frames to confirm track
- `--use-deepsort` - Enable DeepSort

### Grid Parameters

- `--cell-width 2.0` - Cell width (meters)
- `--cell-height 2.0` - Cell height (meters)
- `--person-radius 0.6` - Person radius (meters)

### Alert Parameters

- `--ema-alpha 0.4` - Smoothing factor (0.0-1.0)
- `--hysteresis 3.0` - Alert delay (seconds)

## Troubleshooting

### Issue: No camera found

**Solution:**

```bash
# Try different camera indices
python main.py --source 0
python main.py --source 1
python main.py --source 2
```

### Issue: Low FPS

**Solutions:**

```bash
# Detect less frequently
python main.py --detect-every 5

# Use smaller model
python main.py --model yolov8n.pt

# Disable DeepSort
python main.py  # (DeepSort is off by default)
```

### Issue: Too many false detections

**Solutions:**

```bash
# Increase confidence threshold
python main.py --conf 0.5

# Increase minimum bbox area
python main.py --min-bbox-area 2500
```

### Issue: Missing detections

**Solutions:**

```bash
# Decrease confidence threshold
python main.py --conf 0.25

# Detect more frequently
python main.py --detect-every 1

# Use better model
python main.py --model yolov8m.pt
```

### Issue: Grid too small/large

**Solutions:**

```bash
# Runtime: Press 'g' to toggle
# Or restart with different size:
python main.py --cell-width 1.5 --cell-height 1.5
```

## File Structure

```
.
├── main.py              # Start here!
├── config.py            # Configuration
├── monitor.py           # Main system
├── detector.py          # Person detection
├── trackers.py          # Object tracking
├── calibration.py       # Camera setup
├── occupancy.py         # Grid management
├── geometry.py          # Coordinate math
├── visualizer.py        # Display rendering
├── logger_config.py     # Logging setup
├── requirements.txt     # Dependencies
├── README.md            # Full documentation
├── ARCHITECTURE.md      # Technical details
├── MIGRATION_GUIDE.md   # Upgrade guide
├── QUICK_REFERENCE.md   # This file
└── example_usage.py     # Code examples
```

## Performance Tips

1. **Optimize Detection Frequency**
    - Higher `--detect-every` = faster but less accurate
    - Lower `--detect-every` = slower but more accurate

2. **Choose Right Model**
    - `yolov8n.pt` - Best for real-time on CPU
    - `yolov8s.pt` - Balanced
    - `yolov8m.pt` - Better accuracy, slower
    - `yolov8l.pt` - High accuracy, much slower
    - `yolov8x.pt` - Best accuracy, very slow

3. **Adjust Grid Resolution**
    - Larger cells = faster processing
    - Smaller cells = more detailed monitoring

4. **Disable Unnecessary Features**
    - Use simpler display modes (press `1` or `2`)
    - Disable FPS display (press `f`)

## Best Practices

1. **Calibration**
    - Click corners accurately
    - Choose flat ground reference points
    - Measure dimensions precisely

2. **Grid Sizing**
    - Cell size should match monitoring needs
    - Typically 1.5m - 3.0m per cell
    - Adjust person radius based on expected density

3. **Alert Tuning**
    - Set hysteresis to prevent flickering alerts
    - Adjust capacity calculations for your use case
    - Monitor logs for alert patterns

4. **Performance**
    - Start with default settings
    - Tune based on observed performance
    - Balance accuracy vs speed for your needs

## Common Patterns

### Pattern 1: Video Analysis

```bash
# Process video file and save screenshots
python main.py --source video.mp4 --detect-every 5
# Press 's' to save interesting frames
```

### Pattern 2: Live Monitoring

```bash
# High accuracy live monitoring
python main.py --source 0 --conf 0.45 --detect-every 2
```

### Pattern 3: High-Density Events

```bash
# Fine-grained monitoring for crowds
python main.py --cell-width 1.0 --cell-height 1.0 --person-radius 0.4
```

### Pattern 4: Low-Power Monitoring

```bash
# Optimize for low-end hardware
python main.py --model yolov8n.pt --detect-every 10
```

## Getting Help

1. **Check Documentation**
    - `README.md` - General usage
    - `ARCHITECTURE.md` - Technical details
    - `MIGRATION_GUIDE.md` - Upgrading

2. **Run Examples**
   ```bash
   python example_usage.py 5  # Run example 5
   ```

3. **Check Logs**
   ```bash
   tail -f crowd_monitor.log
   ```

4. **Debug Mode**
    - Check console output for warnings/errors
    - Press `f` to show FPS
    - Monitor system resources

## Resources

- **YOLO Documentation**: https://docs.ultralytics.com/
- **OpenCV Documentation**: https://docs.opencv.org/
- **Shapely Documentation**: https://shapely.readthedocs.io/

## Version Info

Run to check versions:

```bash
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "from ultralytics import YOLO; print('Ultralytics: OK')"
```
