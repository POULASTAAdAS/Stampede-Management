# Enhanced Crowd Monitoring System

A modular real-time crowd monitoring and capacity management system using computer vision.

## 📚 **NEW: Comprehensive Beginner-Friendly Documentation!**

We've created extensive documentation perfect for beginners with only basic Python knowledge:

- 🎓 **[BEGINNER_GUIDE.md](read/2_BEGINNER_GUIDE.md)** - Complete introduction (789 lines)
   - Explains every concept in simple terms
   - Perfect for those new to computer vision
   - Includes analogies and step-by-step explanations

- 🔍 **[CODE_WALKTHROUGH.md](read/4_CODE_WALKTHROUGH.md)** - Detailed code explanations (1,115 lines)
   - Line-by-line code breakdowns
   - Best practices and patterns
   - Perfect for understanding implementation

- 🎨 **[VISUAL_CONCEPTS.md](read/3_VISUAL_CONCEPTS.md)** - Visual diagrams (845 lines)
   - ASCII art illustrations
   - Data flow visualizations
   - Perfect for visual learners

- 🎯 **[PRACTICAL_EXAMPLES.md](read/5_PRACTICAL_EXAMPLES.md)** - Real usage examples (1,030 lines)
   - Command-line examples
   - Troubleshooting solutions
   - Customization guides

- 📖 **[DOCUMENTATION_INDEX.md](read/1_DOCUMENTATION_INDEX.md)** - Navigation guide
   - Find the right document for your needs
   - Learning paths for different skill levels
   - Quick reference table

**Total: 3,779 lines of beginner-friendly documentation!**

👉 **Start here:** [DOCUMENTATION_INDEX.md](read/1_DOCUMENTATION_INDEX.md) to find the best learning path for you!

## 🏗️ Project Structure

```
Stampede-Management/
├── main.py                 # Entry point and CLI argument parsing
├── config.py               # Configuration classes and data structures
├── logger_config.py        # Logging setup
├── geometry.py             # Coordinate transformation utilities
├── detector.py             # YOLO-based person detection
├── trackers.py             # Person tracking (Centroid & DeepSort)
├── calibration.py          # Camera calibration and perspective setup
├── occupancy.py            # Grid-based occupancy monitoring
├── visualizer.py           # Visualization and rendering
├── monitor.py              # Main monitoring orchestrator
└── requirements.txt        # Python dependencies
```

## 📦 Module Responsibilities

### `main.py`

- CLI argument parsing
- Application entry point
- Configuration setup

### `config.py`

- `MonitoringConfig`: System configuration dataclass
- `TrackData`: Track information structure

### `logger_config.py`

- Centralized logging configuration
- Log file and console output setup

### `geometry.py`

- `GeometryProcessor`: Handles homography transformations
- Converts between image coordinates (pixels) and world coordinates (meters)

### `detector.py`

- `PersonDetector`: YOLO-based person detection
- Model downloading and loading
- Detection filtering and validation

### `trackers.py`

- `SimpleCentroidTracker`: Fast centroid-based tracking
- `DeepSortTracker`: Advanced appearance-based tracking (optional)

### `calibration.py`

- `CameraCalibrator`: Interactive camera calibration
- GUI and manual calibration modes
- Perspective transformation setup

### `occupancy.py`

- `OccupancyGrid`: Grid-based crowd density management
- Exponential moving average smoothing
- Alert system with hysteresis

### `visualizer.py`

- `MonitorVisualizer`: All rendering operations
- Multiple display modes (raw, grid, detection, monitoring, split)
- Bird's eye view generation
- Info panels and overlays

### `monitor.py`

- `CrowdMonitor`: Main system orchestrator
- Coordinates all components
- Video processing loop
- Interactive controls

## 🚀 Usage

### Basic Usage

```bash
python main.py --source 0 --cell-width 2.0 --cell-height 2.0
```

### With Custom Settings

```bash
python main.py \
    --source video.mp4 \
    --model yolov8n.pt \
    --cell-width 1.5 \
    --cell-height 1.5 \
    --person-radius 0.5 \
    --conf 0.4 \
    --detect-every 3 \
    --use-deepsort
```

### All Options

```bash
python main.py --help
```

## ⌨️ Interactive Controls

| Key | Function |
|-----|----------|
| `1` | Raw Camera view |
| `2` | Grid Overlay view |
| `3` | Detection view |
| `4` | Monitoring view (default) |
| `5` | Split view (quad-split) |
| `s` | Save screenshot |
| `g` | Toggle grid size |
| `r` | Reset grid to original size |
| `f` | Toggle FPS display |
| `q` | Quit application |

## 📋 Requirements

```bash
pip install -r requirements.txt
```

Required packages:

- opencv-python
- numpy
- ultralytics (YOLO)
- shapely
- deep-sort-realtime (optional, for DeepSort tracking)

## 🎯 Features

### Detection & Tracking

- YOLOv8-based person detection
- Multiple tracking algorithms (Centroid/DeepSort)
- Configurable detection frequency
- Confidence threshold filtering

### Spatial Analysis

- Camera calibration with perspective transformation
- Grid-based occupancy monitoring
- Real-time capacity calculation
- World coordinate mapping

### Alerting

- Overcapacity detection
- Hysteresis-based alerts (prevents false alarms)
- Per-cell monitoring
- Automatic alert clearing

### Visualization

- 5 interactive display modes
- Bird's eye view with heatmap
- Real-time occupancy overlay
- Performance metrics (FPS)

### Interactive Features

- Runtime grid adjustment
- Screenshot capture
- Multiple camera fallback
- Manual calibration mode

## 🔧 Configuration

### Grid Settings

- `--cell-width`: Width of grid cells in meters (default: 2.0)
- `--cell-height`: Height of grid cells in meters (default: 2.0)
- `--person-radius`: Radius for capacity calculation (default: 0.6)

### Detection Settings

- `--detect-every`: Run detection every N frames (default: 3)
- `--conf`: Detection confidence threshold (default: 0.35)
- `--min-bbox-area`: Minimum bounding box area (default: 1500)

### Tracking Settings

- `--use-deepsort`: Enable DeepSort tracking
- `--max-age`: Maximum frames to keep track (default: 30)
- `--n-init`: Frames to confirm track (default: 1)

### Alert Settings

- `--ema-alpha`: EMA smoothing factor (default: 0.4)
- `--hysteresis`: Alert delay in seconds (default: 3.0)

## 📊 Workflow

1. **Initialization**: Load YOLO model, connect to camera
2. **Calibration**: User marks 4 ground points and provides dimensions
3. **Processing Loop**:
    - Detect persons (every N frames)
    - Update tracks
    - Project to world coordinates
    - Update occupancy grid
    - Check for overcapacity
    - Render visualization
4. **Interactive Control**: Switch modes, adjust grid, capture screenshots

## 🐛 Troubleshooting

### Camera Not Found

- Check camera connection
- Try different source indices: `--source 0`, `--source 1`, etc.
- Close other applications using the camera

### Model Download Fails

- Check internet connection
- Manually download model from Ultralytics
- Verify model path

### DeepSort Not Available

```bash
pip install deep-sort-realtime
```

### Low FPS

- Increase `--detect-every` value
- Use lighter YOLO model: `yolov8n.pt`
- Reduce camera resolution
- Disable DeepSort tracking

## 📝 License

MIT License - See LICENSE file for details

## 👥 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 🙏 Acknowledgments

- Ultralytics YOLOv8
- DeepSort Real-time
- OpenCV
- Shapely
