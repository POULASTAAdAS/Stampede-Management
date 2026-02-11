# Quick Start Guide

Get up and running with the Stampede Management System in 5 minutes!

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [First Run](#first-run)
- [Basic Usage](#basic-usage)
- [Common Tasks](#common-tasks)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.8+** installed
- ✅ **Webcam or video file** for monitoring
- ✅ **4GB RAM** minimum (8GB recommended)
- ✅ **Windows, Linux, or macOS**

Check Python version:

```bash
python --version
```

---

## Installation

### Step 1: Navigate to Project Directory

```bash
cd E:/Stampede-Management
```

### Step 2: Install Dependencies

**Windows (Automated):**

```bash
install_dependencies.bat
```

**Manual Installation (All Platforms):**

```bash
pip install opencv-python numpy ultralytics shapely
pip install deep-sort-realtime  # Optional: for advanced tracking
```

### Step 3: Verify Installation

```bash
python test_system.py
```

You should see: `✅ All systems operational`

---

## First Run

### Method 1: GUI Launcher (Easiest) 🎯

**Windows:**

1. Double-click `run_gui.bat`
2. GUI window opens automatically

**Linux/macOS:**

```bash
python config_gui.py
```

### Method 2: Command Line

```bash
python main.py --source 0
```

---

## Using the GUI

### Step 1: Launch GUI

```bash
python config_gui.py
```

![GUI Interface](https://via.placeholder.com/800x600?text=GUI+Configuration+Interface)

### Step 2: Configure Settings

#### Video Source

- **Webcam**: Select from dropdown (Camera 0, Camera 1, etc.)
- **Video File**: Click "Browse" and select file

#### Grid Settings

```
┌─────────────────────────────────────┐
│ Grid Configuration                   │
├─────────────────────────────────────┤
│ Cell Width:  [2.0] meters           │
│ Cell Height: [2.0] meters           │
│ Person Radius: [0.5] meters         │
└─────────────────────────────────────┘
```

**Recommendations:**

- **Small Venue** (< 50 people): 1.0m × 1.0m cells
- **Medium Venue** (50-200): 2.0m × 2.0m cells
- **Large Venue** (200+): 3.0m × 3.0m cells

#### Detection Settings

```
┌─────────────────────────────────────┐
│ Detection Configuration              │
├─────────────────────────────────────┤
│ Confidence:    [0.35] (0-1)         │
│ Detect Every:  [3] frames           │
│ Min Box Area:  [1500] pixels        │
└─────────────────────────────────────┘
```

**Recommendations:**

- **High Accuracy**: Confidence 0.4, Detect Every 1
- **Balanced**: Confidence 0.35, Detect Every 3
- **High Speed**: Confidence 0.3, Detect Every 5

### Step 3: Start Monitoring

Click **"Start Monitoring"** button

---

## Camera Calibration

### Interactive Calibration

When you first run the system, you'll see the calibration interface:

```
┌────────────────────────────────────────────┐
│  Calibration - Click 4 corners             │
│                                            │
│    1 ●─────────● 2                         │
│      │         │                           │
│      │  AREA   │                           │
│      │         │                           │
│    4 ●─────────● 3                         │
│                                            │
│  Points: 0/4                               │
│  Click corners clockwise                   │
│  'c' to continue, ESC to cancel            │
└────────────────────────────────────────────┘
```

**Steps:**

1. **Click Point 1**: Top-left corner of monitoring area
2. **Click Point 2**: Top-right corner
3. **Click Point 3**: Bottom-right corner
4. **Click Point 4**: Bottom-left corner
5. **Press 'c'**: Confirm calibration
6. **Enter Dimensions**: Type real-world width and height in meters

**Example:**

```
Width (meters): 10
Height (meters): 8
```

### Skip Calibration (Use Defaults)

Add this to command line:

```bash
python main.py --source 0 --auto-calibration --calibration-width 10 --calibration-height 10
```

Or in GUI: Check "Auto Calibration" and set dimensions.

---

## Monitoring Interface

Once calibration is complete, you'll see the monitoring view:

```
┌──────────────────────────────────────────────────────────┐
│  Enhanced Crowd Monitor - Monitoring View                 │
│                                                            │
│  ╔══════════╦══════════╦══════════╗                       │
│  ║  0/5     ║  2/5     ║  1/5     ║                       │
│  ║          ║  [🧍🧍]  ║  [🧍]    ║                       │
│  ╠══════════╬══════════╬══════════╣                       │
│  ║  3/5     ║  6/5❗   ║  0/5     ║                       │
│  ║  [🧍🧍🧍] ║[🧍🧍🧍🧍🧍🧍]║          ║                       │
│  ╚══════════╩══════════╩══════════╝                       │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  People: 12  │  Alerts: 1  │  FPS: 24.5  │  Mode: 4      │
└────────────────────────────────────────────────────────────┘
```

**Color Coding:**

- 🟢 **Green**: Normal (< 80% capacity)
- 🟠 **Orange**: Warning (80-99% capacity)
- 🔴 **Red**: Overcapacity (≥ 100% capacity)

---

## Keyboard Shortcuts

### Display Modes

| Key | Mode            | Description                       |
|-----|-----------------|-----------------------------------|
| `1` | Raw Camera      | Unprocessed camera feed           |
| `2` | Grid Overlay    | Camera view with grid lines       |
| `3` | Detection View  | Bounding boxes only               |
| `4` | Monitoring View | Full monitoring display (default) |
| `5` | Split View      | 4-panel composite view            |

### Controls

| Key   | Action      | Description                  |
|-------|-------------|------------------------------|
| `q`   | Quit        | Exit the application         |
| `s`   | Screenshot  | Save current view to file    |
| `g`   | Toggle Grid | Cycle through grid sizes     |
| `r`   | Reset Grid  | Return to original grid size |
| `f`   | FPS Display | Show/hide FPS counter        |
| `ESC` | Cancel      | Cancel calibration           |

---

## Common Tasks

### Task 1: Monitor a Webcam

```bash
python main.py --source 0
```

### Task 2: Analyze a Video File

```bash
python main.py --source path/to/video.mp4
```

### Task 3: Use High-Precision Settings

```bash
python main.py \
  --source 0 \
  --cell-width 1.0 \
  --cell-height 1.0 \
  --conf 0.4 \
  --detect-every 1 \
  --use-deepsort
```

### Task 4: Use Fast Settings (Low-End Hardware)

```bash
python main.py \
  --source 0 \
  --cell-width 3.0 \
  --cell-height 3.0 \
  --conf 0.3 \
  --detect-every 10
```

### Task 5: Monitor Multiple Cameras

Create a script `monitor_all.py`:

```python
import threading
from config import MonitoringConfig
from monitor import CrowdMonitor

def monitor_camera(camera_id):
    config = MonitoringConfig(source=camera_id)
    monitor = CrowdMonitor(config)
    monitor.initialize()

# Start monitoring for cameras 0 and 1
thread1 = threading.Thread(target=monitor_camera, args=(0,))
thread2 = threading.Thread(target=monitor_camera, args=(1,))

thread1.start()
thread2.start()

thread1.join()
thread2.join()
```

Run:

```bash
python monitor_all.py
```

### Task 6: Save Configuration

The GUI automatically saves your settings to `system_conf.json`.

To load saved settings:

```python
import json
from config import MonitoringConfig

# Load from file
with open('system_conf.json', 'r') as f:
    settings = json.load(f)

# Create config
config = MonitoringConfig(**settings)
```

### Task 7: Export Screenshots Automatically

Add to your code:

```python
import time
import cv2

# In your processing loop
if frame_count % 300 == 0:  # Every 300 frames
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.jpg"
    cv2.imwrite(filename, display_frame)
```

### Task 8: Custom Alert Handling

Override the alert method:

```python
from occupancy import OccupancyGrid

class CustomOccupancyGrid(OccupancyGrid):
    def _update_alerts(self, dt):
        super()._update_alerts(dt)
        
        # Custom alert handling
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if self.notified[row, col]:
                    # Send email, SMS, webhook, etc.
                    send_alert_notification(row, col)

# Use custom grid
monitor.occupancy_grid = CustomOccupancyGrid(...)
```

---

## Understanding the Output

### Log Messages

The system logs to console and `crowd_monitor.log`:

```
[2026-02-12 10:30:15] INFO: === Enhanced Crowd Monitoring System ===
[2026-02-12 10:30:15] INFO: Video source: 0
[2026-02-12 10:30:15] INFO: YOLO model: model/yolov8n.pt
[2026-02-12 10:30:16] INFO: YOLO model loaded successfully
[2026-02-12 10:30:16] INFO: Camera resolution: 1280x720
[2026-02-12 10:30:18] INFO: Calibration completed: 10.0x8.0m
[2026-02-12 10:30:18] INFO: Grid initialized: 4x5 cells, capacity: 5 per cell
[2026-02-12 10:30:18] INFO: Using simple centroid tracker
```

### Alert Messages

When overcapacity is detected:

```
[2026-02-12 10:35:42] WARNING: OVERCAPACITY ALERT - Cell (2,3) occupancy: 6.2/5 at 2026-02-12 10:35:42
```

When alert clears:

```
[2026-02-12 10:36:15] INFO: Alert cleared for cell (2,3)
```

### Screenshots

Screenshots are saved with timestamp:

```
crowd_monitor_20260212_103015.jpg
crowd_monitor_20260212_103530.jpg
```

---

## Troubleshooting

### Problem: "Cannot open video source: 0"

**Solution 1**: Check available cameras

```python
from monitor import CrowdMonitor

cameras = CrowdMonitor.detect_available_cameras()
for cam in cameras:
    print(f"Camera {cam['index']}: {cam['name']}")
```

**Solution 2**: Try different camera index

```bash
python main.py --source 1  # or 2, 3, etc.
```

**Solution 3**: Check camera permissions

On Linux:

```bash
sudo usermod -a -G video $USER
```

---

### Problem: "License check failed"

**Solution**: Generate development license

```bash
python generate_dev_license.py
```

Verify:

```bash
python test_license_fix.py
```

---

### Problem: Low FPS / Slow Performance

**Solution 1**: Reduce detection frequency

```bash
python main.py --source 0 --detect-every 10
```

**Solution 2**: Use smaller YOLO input size

Edit `config.py`:

```python
config = MonitoringConfig(
    yolo_imgsz=320  # Default is 640
)
```

**Solution 3**: Lower camera resolution

```bash
python main.py --source 0 --camera-width 640 --camera-height 480
```

**Solution 4**: Use centroid tracker (not DeepSort)

```bash
python main.py --source 0  # Don't use --use-deepsort flag
```

---

### Problem: "Module not found" Errors

**Solution**: Reinstall dependencies

```bash
pip uninstall opencv-python numpy ultralytics shapely
pip install opencv-python numpy ultralytics shapely
```

For Python 3.14+:

```bash
pip install --only-binary :all: numpy opencv-python
pip install ultralytics shapely
```

---

### Problem: Calibration Not Working

**Solution 1**: Use manual calibration

When calibration window opens, if clicks aren't registering:

1. Press `ESC` to cancel GUI calibration
2. System will fallback to manual mode
3. Enter coordinates manually

**Solution 2**: Use auto-calibration

```bash
python main.py \
  --source 0 \
  --auto-calibration \
  --calibration-width 10 \
  --calibration-height 8
```

---

### Problem: Too Many False Alerts

**Solution**: Increase hysteresis time and adjust EMA

```bash
python main.py \
  --source 0 \
  --hysteresis 5.0 \
  --ema-alpha 0.2
```

This requires overcapacity to persist for 5 seconds and smooths out fluctuations more.

---

### Problem: Not Detecting People

**Solution 1**: Lower confidence threshold

```bash
python main.py --source 0 --conf 0.25
```

**Solution 2**: Check minimum bbox area

```bash
python main.py --source 0 --min-bbox-area 500
```

**Solution 3**: Verify YOLO model

```python
from detector import PersonDetector
from config import MonitoringConfig
import cv2

config = MonitoringConfig()
detector = PersonDetector(config)
detector.load_model()

frame = cv2.imread("test_image.jpg")
detections = detector.detect_persons(frame)
print(f"Detected {len(detections)} people")
```

---

## Next Steps

Now that you're up and running:

1. **Read the full [README.md](README.md)** for comprehensive documentation
2. **Explore [ARCHITECTURE.md](ARCHITECTURE.md)** to understand system design
3. **Check [EXAMPLES.md](EXAMPLES.md)** for advanced use cases
4. **Review code examples** in the `/examples` directory

---

## Quick Reference

### Command Line Cheatsheet

```bash
# Basic usage
python main.py --source 0

# With custom settings
python main.py \
  --source 0 \
  --cell-width 2.0 \
  --cell-height 2.0 \
  --conf 0.35 \
  --detect-every 3

# Video file
python main.py --source video.mp4

# High precision
python main.py --source 0 --use-deepsort --detect-every 1 --conf 0.4

# Fast mode
python main.py --source 0 --detect-every 10 --conf 0.3

# Auto calibration
python main.py \
  --source 0 \
  --auto-calibration \
  --calibration-width 10 \
  --calibration-height 10
```

### Python API Cheatsheet

```python
# Basic usage
from config import MonitoringConfig
from monitor import CrowdMonitor

config = MonitoringConfig(source=0)
monitor = CrowdMonitor(config)
monitor.initialize()

# Custom configuration
config = MonitoringConfig(
    source=0,
    cell_width=2.0,
    cell_height=2.0,
    confidence_threshold=0.35,
    use_deepsort=False
)

# Detect cameras
cameras = CrowdMonitor.detect_available_cameras()
```

---

## Support

If you encounter issues not covered here:

1. Check `crowd_monitor.log` for detailed error messages
2. Run `python test_system.py` to verify installation
3. Review [README.md](README.md) troubleshooting section
4. Contact support with log files

---

**Happy Monitoring! 🎯**
