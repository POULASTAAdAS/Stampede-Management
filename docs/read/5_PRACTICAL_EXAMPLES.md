# 🎯 Practical Examples & Use Cases

This guide shows real-world examples of how to use and customize the Crowd Monitoring System.

---

## 📋 Table of Contents

1. [Getting Started Examples](#getting-started-examples)
2. [Configuration Examples](#configuration-examples)
3. [Common Scenarios](#common-scenarios)
4. [Troubleshooting Examples](#troubleshooting-examples)
5. [Customization Examples](#customization-examples)
6. [Real-World Use Cases](#real-world-use-cases)

---

## 🚀 Getting Started Examples

### Example 1: Basic Startup (Default Settings)

**Scenario:** You want to test the system with default settings using your webcam.

**Command:**

```bash
python main.py
```

**What happens:**

1. System loads with these defaults:
    - Camera: `0` (first webcam)
    - Cell size: `2m × 2m`
    - AI confidence: `35%`
    - Detection: Every `3` frames

2. Calibration window appears
3. Click 4 corners of a known area
4. Enter dimensions (e.g., "10" for width, "8" for height)
5. System starts monitoring

**Expected output:**

```
2025-12-14 13:00:00 - INFO - === Enhanced Crowd Monitoring System ===
2025-12-14 13:00:00 - INFO - Video source: 0
2025-12-14 13:00:00 - INFO - YOLO model: model/yolov8n.pt
2025-12-14 13:00:01 - INFO - Loading YOLO model: model/yolov8n.pt
2025-12-14 13:00:02 - INFO - YOLO model loaded successfully
2025-12-14 13:00:02 - INFO - Connected to camera source: 0
2025-12-14 13:00:02 - INFO - Camera resolution: 1280x720
```

---

### Example 2: Using a Video File

**Scenario:** You want to analyze a pre-recorded video of a crowded event.

**Command:**

```bash
python main.py --source "videos/festival_crowd.mp4"
```

**Advantages:**

- ✅ Can replay and analyze multiple times
- ✅ No real-time pressure
- ✅ Consistent testing conditions

**Example workflow:**

1. Record video of event
2. Run analysis: `python main.py --source event_video.mp4`
3. Review alerts in `crowd_monitor.log`
4. Adjust parameters if needed
5. Re-run analysis

---

### Example 3: Quick Test with Different Camera

**Scenario:** Your default webcam isn't working, try camera 1.

**Command:**

```bash
python main.py --source 1
```

**If that doesn't work, try:**

```bash
python main.py --source 2
```

**System will also auto-fallback:**

```
2025-12-14 13:00:00 - INFO - Trying primary camera source: 0
2025-12-14 13:00:00 - ERROR - Failed to open camera 0
2025-12-14 13:00:01 - INFO - Trying fallback camera source: 1
2025-12-14 13:00:01 - INFO - Connected to fallback camera: 1
```

---

## ⚙️ Configuration Examples

### Example 4: Small Indoor Room (Close Monitoring)

**Scenario:** Monitor a small conference room (6m × 4m).

**Command:**

```bash
python main.py --cell-width 1.0 --cell-height 1.0 --person-radius 0.5
```

**Why these settings:**

- `--cell-width 1.0`: Smaller cells for detailed monitoring
- `--cell-height 1.0`: Matches cell width (square cells)
- `--person-radius 0.5`: Tight personal space (seated people)

**Result:**

- Grid: 6 × 4 = 24 cells
- Each cell: 1m × 1m = 1m²
- Capacity per cell: 1 / (π × 0.5²) ≈ 1 person
- Total capacity: ~24 people

---

### Example 5: Large Outdoor Festival (Wide Area)

**Scenario:** Monitor a large festival ground (30m × 20m).

**Command:**

```bash
python main.py --cell-width 3.0 --cell-height 3.0 --person-radius 1.0
```

**Why these settings:**

- `--cell-width 3.0`: Larger cells for broad monitoring
- `--cell-height 3.0`: Matches cell width
- `--person-radius 1.0`: More personal space (standing, moving)

**Result:**

- Grid: 10 × 7 = 70 cells
- Each cell: 3m × 3m = 9m²
- Capacity per cell: 9 / (π × 1²) ≈ 2-3 people
- Total capacity: ~175 people

---

### Example 6: High Security (Sensitive Detection)

**Scenario:** Maximum sensitivity for security purposes.

**Command:**

```bash
python main.py --conf 0.25 --detect-every 1 --hysteresis 1.0
```

**Why these settings:**

- `--conf 0.25`: Lower confidence threshold (detect more)
- `--detect-every 1`: Run AI every frame (no skipping)
- `--hysteresis 1.0`: Faster alerts (1 second instead of 3)

**Trade-offs:**

- ⚠️ More false positives
- ⚠️ Higher CPU usage
- ✅ Faster response time
- ✅ Catches more people

---

### Example 7: Low Power Mode (Battery/Older PC)

**Scenario:** Running on a laptop or older computer.

**Command:**

```bash
python main.py --detect-every 10 --conf 0.5 --fps 10
```

**Why these settings:**

- `--detect-every 10`: Only detect every 10th frame
- `--conf 0.5`: Higher threshold (fewer detections to process)
- `--fps 10`: Expect 10 FPS (lower frame rate)

**Result:**

- Much lower CPU usage
- Still functional for monitoring
- Slightly delayed tracking

---

### Example 8: Precise Occupancy Tracking

**Scenario:** Need very accurate counts with smooth transitions.

**Command:**

```bash
python main.py --ema-alpha 0.2 --min-bbox-area 2000
```

**Why these settings:**

- `--ema-alpha 0.2`: More smoothing (slower response but stable)
- `--min-bbox-area 2000`: Filter out small false detections

**Formula effect:**

```
Standard (α=0.4): new = 0.4×current + 0.6×old
Smooth (α=0.2):   new = 0.2×current + 0.8×old
                       └─ More weight on history
```

---

## 🎬 Common Scenarios

### Scenario 1: Concert Entrance Monitoring

**Setup:**

```bash
python main.py \
  --source "entrance_camera.mp4" \
  --cell-width 2.0 \
  --cell-height 2.0 \
  --person-radius 0.75 \
  --hysteresis 2.0 \
  --conf 0.4
```

**Physical setup:**

- Camera mounted 5m high
- Looking down at entrance area (12m × 8m)
- People moving through constantly

**Calibration:**

1. Click corners of entrance floor area
2. Enter dimensions: Width=12, Height=8
3. System creates 6×4 grid = 24 cells
4. Each cell ~3 people capacity

**Expected behavior:**

- Detects people entering/exiting
- Alerts if entrance area becomes too crowded
- 2-second hysteresis prevents alerts during normal flow

**Sample output:**

```
13:00:00 - INFO - People: 8 | Capacity: 72 | Grid: 4×6
13:00:15 - WARNING - OVERCAPACITY ALERT - Cell (2,3) occupancy: 4.2/3
13:00:45 - INFO - Alert cleared for cell (2,3)
```

---

### Scenario 2: Retail Store Traffic Analysis

**Setup:**

```bash
python main.py \
  --source 0 \
  --cell-width 2.5 \
  --cell-height 2.5 \
  --detect-every 5 \
  --enable-screenshots
```

**Physical setup:**

- Camera overlooking main shopping floor
- Area: 20m × 15m
- Grid: 8×6 = 48 cells

**Usage pattern:**

1. Start system in morning
2. Run all day
3. Press 's' every hour to save screenshots
4. Review `crowd_monitor.log` for peak times

**Data analysis:**

```bash
# Find peak occupancy times
grep "People:" crowd_monitor.log | sort -k4 -n -r | head -10

# Find all overcapacity alerts
grep "OVERCAPACITY" crowd_monitor.log

# Count alerts per cell
grep "Cell" crowd_monitor.log | cut -d'(' -f2 | cut -d')' -f1 | sort | uniq -c
```

**Insights gained:**

- Which areas get most crowded
- What times are busiest
- Where to add staff or barriers

---

### Scenario 3: School Playground Safety

**Setup:**

```bash
python main.py \
  --source 0 \
  --cell-width 3.0 \
  --cell-height 3.0 \
  --person-radius 1.5 \
  --hysteresis 5.0 \
  --conf 0.35
```

**Physical setup:**

- Camera on building overlooking playground
- Area: 30m × 30m
- Grid: 10×10 = 100 cells

**Why these settings:**

- Larger cells (children move around a lot)
- Larger person radius (children need more space)
- Longer hysteresis (5s) - children cluster temporarily

**Usage:**

- Monitor during recess
- Alert if one area gets too many children
- Identify popular/unpopular zones

---

### Scenario 4: Emergency Evacuation Drill

**Setup:**

```bash
python main.py \
  --source "drill_recording.mp4" \
  --cell-width 1.5 \
  --cell-height 1.5 \
  --detect-every 2 \
  --hysteresis 1.0
```

**Purpose:**

- Analyze evacuation video
- Find bottleneck points
- Measure evacuation time

**Analysis steps:**

1. Record evacuation drill
2. Run analysis: `python main.py --source drill.mp4 ...`
3. Watch for overcrowding alerts
4. Note which cells triggered alerts (bottlenecks)
5. Improve evacuation route

**Questions answered:**

- Where do people cluster?
- How long until area is clear?
- Are exits evenly used?

---

## 🔧 Troubleshooting Examples

### Problem 1: "No camera sources available"

**Error message:**

```
ERROR - No camera sources available
ERROR - Monitoring failed to initialize
```

**Solutions:**

**Solution A: Try different camera index**

```bash
python main.py --source 1
# or
python main.py --source 2
```

**Solution B: Test camera with simple script**

```python
import cv2

# Test cameras 0, 1, 2
for i in range(3):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera {i}: WORKS ✓")
        cap.release()
    else:
        print(f"Camera {i}: FAILED ✗")
```

**Solution C: Use video file instead**

```bash
python main.py --source test_video.mp4
```

---

### Problem 2: "Detection is too slow"

**Symptom:** System runs at 2-5 FPS, very laggy.

**Solutions:**

**Solution A: Reduce detection frequency**

```bash
python main.py --detect-every 10
# Only runs AI every 10 frames instead of every 3
```

**Solution B: Use smaller model (if available)**

```bash
python main.py --model model/yolov8n.pt
# 'n' = nano (fastest but least accurate)
```

**Solution C: Lower camera resolution**

```python
# Add to main.py after line 147:
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Lower from 1280
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Lower from 720
```

---

### Problem 3: "Too many false detections"

**Symptom:** System detects shadows, objects, or partial people.

**Solutions:**

**Solution A: Increase confidence threshold**

```bash
python main.py --conf 0.5
# Require 50% confidence instead of 35%
```

**Solution B: Increase minimum box area**

```bash
python main.py --min-bbox-area 2500
# Ignore small detections (1500 → 2500 pixels)
```

**Solution C: Both together**

```bash
python main.py --conf 0.5 --min-bbox-area 2500
```

---

### Problem 4: "Calibration is difficult"

**Symptom:** Hard to click precise points.

**Solution A: Use manual calibration**

1. Let system save `calibration_frame.jpg`
2. Open in image editor (Paint, Photoshop, GIMP)
3. Hover mouse to see pixel coordinates
4. Write them down
5. Enter manually when prompted

**Example:**

```
Saved calibration frame to: calibration_frame.jpg

Manual calibration mode:
Enter point 1 as 'x,y': 150,50
Enter point 2 as 'x,y': 1130,80
Enter point 3 as 'x,y': 1100,680
Enter point 4 as 'x,y': 180,650

Enter the real-world dimensions:
Width (meters): 10
Height (meters): 8
```

**Solution B: Use larger reference area**

- Instead of small area, use entire visible floor
- Easier to identify corners
- More accurate transformation

---

### Problem 5: "People keep losing tracking IDs"

**Symptom:** Person #17 becomes #18, then #19 (ID keeps changing).

**Causes & Solutions:**

**Cause A: Too strict tracking parameters**

```bash
# Increase distance threshold (edit trackers.py line 43)
self.distance_threshold = 120.0  # Default: 80.0
```

**Cause B: People moving too fast**

```bash
# Detect more frequently
python main.py --detect-every 2
# Detect every 2 frames instead of 3
```

**Cause C: Use better tracker**

```bash
# Install DeepSort
pip install deep-sort-realtime

# Enable it
python main.py --use-deepsort
```

---

## 🎨 Customization Examples

### Customization 1: Change Colors

**File to edit:** `visualizer.py`

**Example: Change grid color from green to blue**

Find line 47:

```python
grid_color = (100, 255, 100)  # Green in BGR
```

Change to:

```python
grid_color = (255, 100, 100)  # Blue in BGR
```

**Color reference (BGR format):**

- Red: `(0, 0, 255)`
- Green: `(0, 255, 0)`
- Blue: `(255, 0, 0)`
- Yellow: `(0, 255, 255)`
- Cyan: `(255, 255, 0)`
- Magenta: `(255, 0, 255)`
- White: `(255, 255, 255)`
- Black: `(0, 0, 0)`

---

### Customization 2: Change Alert Sound

**File to create:** `alert_sound.py`

```python
import winsound  # Windows only


def play_alert():
    # Beep at 1000 Hz for 500 ms
    winsound.Beep(1000, 500)
```

**File to edit:** `occupancy.py`

Add import at top:

```python
from alert_sound import play_alert
```

Modify line 122 (in `_update_alerts`):

```python
if (self.timers[row, col] >= self.config.hysteresis_time and
        not self.notified[row, col]):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    logger.warning(f"OVERCAPACITY ALERT - Cell ({row},{col})")
    self.notified[row, col] = True
    play_alert()  # ← Add this line
```

---

### Customization 3: Export Data to CSV

**File to create:** `export_data.py`

```python
import csv
from datetime import datetime


class DataExporter:
    def __init__(self, filename='crowd_data.csv'):
        self.filename = filename
        self.file = open(filename, 'w', newline='')
        self.writer = csv.writer(self.file)
        # Write header
        self.writer.writerow([
            'timestamp', 'people_count', 'alerts',
            'max_occupancy', 'avg_occupancy'
        ])

    def log_frame(self, tracks, occupancy_grid):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        people_count = len(tracks)
        alerts = int(np.sum(occupancy_grid.notified))
        max_occ = float(np.max(occupancy_grid.ema_counts))
        avg_occ = float(np.mean(occupancy_grid.ema_counts))

        self.writer.writerow([
            timestamp, people_count, alerts, max_occ, avg_occ
        ])

    def close(self):
        self.file.close()
```

**Integrate into monitor.py:**

Add after line 40:

```python
from export_data import DataExporter
```

Add after line 66:

```python
self.exporter = DataExporter('crowd_data.csv')
```

Add in `_process_video_stream` after line 258:

```python
# Log data every 30 frames
if self.frame_count % 30 == 0:
    self.exporter.log_frame(tracks, self.occupancy_grid)
```

**Result:** Creates `crowd_data.csv`:

```csv
timestamp,people_count,alerts,max_occupancy,avg_occupancy
2025-12-14 13:00:00,8,0,3.2,1.8
2025-12-14 13:00:02,12,1,5.7,2.4
2025-12-14 13:00:04,15,2,6.3,3.1
```

---

### Customization 4: Add Custom Alert Rules

**Example: Alert if total people exceeds threshold**

**File to edit:** `monitor.py`

Add method after line 442:

```python
def _check_custom_alerts(self, tracks):
    """Check custom alert conditions"""
    total_people = len(tracks)

    # Alert if more than 50 people
    if total_people > 50 and not hasattr(self, '_total_alert_triggered'):
        logger.warning(f"TOTAL CAPACITY ALERT: {total_people} people detected!")
        self._total_alert_triggered = True
    elif total_people <= 50:
        self._total_alert_triggered = False
```

Call it in `_process_video_stream` after line 258:

```python
self._check_custom_alerts(tracks)
```

---

## 🌍 Real-World Use Cases

### Use Case 1: Marathon Finish Line

**Challenge:** Monitor finish line area for overcrowding as runners complete race.

**Setup:**

```bash
python main.py \
  --source finish_line_cam \
  --cell-width 2.0 \
  --cell-height 2.0 \
  --person-radius 0.8 \
  --hysteresis 3.0 \
  --detect-every 3
```

**Camera placement:**

- Mounted 8m above finish line
- Viewing area: 20m × 10m

**Expected patterns:**

- Sudden influx every few minutes (runners arriving)
- Gradual dispersal (runners leaving)
- Alerts when too many runners accumulate

**Actions based on alerts:**

- Direct runners to spread out
- Open additional exit paths
- Slow runner release from earlier corrals

---

### Use Case 2: Museum Gallery

**Challenge:** Ensure social distancing and prevent overcrowding in exhibit halls.

**Setup:**

```bash
python main.py \
  --source gallery_cam \
  --cell-width 3.0 \
  --cell-height 3.0 \
  --person-radius 1.5 \
  --hysteresis 5.0
```

**Layout:**

- Gallery: 15m × 12m
- Grid: 5×4 = 20 cells
- Capacity: ~2 people per cell = 40 total

**Integration:**

- Display at entrance: "Current capacity: 28/40"
- Staff tablet shows live grid view
- Alerts sent to staff when near capacity

**Benefits:**

- Maintain comfortable viewing experience
- Comply with capacity regulations
- Data for future exhibit planning

---

### Use Case 3: Train Station Platform

**Challenge:** Monitor platform occupancy to manage train boarding safely.

**Setup:**

```bash
python main.py \
  --source platform_cam \
  --cell-width 2.5 \
  --cell-height 2.5 \
  --person-radius 0.6 \
  --detect-every 2 \
  --hysteresis 2.0
```

**Physical setup:**

- Platform: 50m × 3m (long and narrow)
- Grid: 20×2 = 40 cells
- Critical zones near doors marked

**Smart features:**

1. Detect clustering near door positions
2. Alert if yellow line area exceeds capacity
3. Track longitudinal distribution

**Actions:**

- Digital signs: "Please move to center of platform"
- PA announcements when overcrowded
- Delay train entry if unsafe

---

### Use Case 4: Nightclub Compliance

**Challenge:** Ensure venue doesn't exceed legal capacity limit.

**Setup:**

```bash
python main.py \
  --source overhead_cam \
  --cell-width 2.0 \
  --cell-height 2.0 \
  --person-radius 0.7 \
  --conf 0.4
```

**Legal requirements:**

- Maximum capacity: 200 people
- Must monitor continuously
- Must log all readings

**System configuration:**

- Multiple cameras (entrance, main floor, VIP)
- Combined counts from all cameras
- Automatic logging to satisfy regulators

**Custom alert:**

```python
if total_people > 190:  # 95% capacity
    logger.warning("APPROACHING CAPACITY: 190/200")
    # Alert door staff to slow entry

if total_people >= 200:  # At capacity
    logger.error("CAPACITY REACHED: 200/200")
    # Stop all entry until people leave
```

---

### Use Case 5: Parking Garage Exit

**Challenge:** Detect pedestrian congestion at parking garage exits.

**Setup:**

```bash
python main.py \
  --source exit_cam \
  --cell-width 1.5 \
  --cell-height 1.5 \
  --person-radius 0.5 \
  --hysteresis 1.0 \
  --detect-every 1
```

**Critical safety:**

- Pedestrians and cars share space
- Fast detection needed (detect-every 1)
- Quick alerts (hysteresis 1.0s)

**Integration:**

- Trigger warning lights when pedestrians detected
- Alert drivers via LED sign
- Log incidents for safety review

**Data analysis:**

- Peak congestion times
- Near-miss incidents
- Effectiveness of warning system

---

## 📊 Performance Optimization Examples

### Optimization 1: Maximum Performance

**Goal:** Highest possible FPS for real-time monitoring.

**Configuration:**

```bash
python main.py \
  --detect-every 5 \
  --conf 0.5 \
  --min-bbox-area 2000
```

**Additional edits in code:**

**File: detector.py, line 123**

```python
results = self.model(
    frame,
    imgsz=416,  # Smaller than default 640
    conf=self.config.confidence_threshold,
    classes=[0],
    verbose=False,
    half=True  # ← Add this for GPU speedup
)
```

**Expected result:**

- 30+ FPS on modern hardware
- Quick response time
- Suitable for high-speed events

---

### Optimization 2: Maximum Accuracy

**Goal:** Catch every person, even at cost of speed.

**Configuration:**

```bash
python main.py \
  --detect-every 1 \
  --conf 0.25 \
  --min-bbox-area 1000 \
  --use-deepsort
```

**Installation needed:**

```bash
pip install deep-sort-realtime
```

**Expected result:**

- 10-15 FPS (slower)
- More accurate tracking
- Fewer missed people
- Suitable for analysis/review

---

## 🎓 Learning Exercise

**Challenge:** Monitor your own room!

1. **Set up camera** looking down at your floor
2. **Run system:**
   ```bash
   python main.py --cell-width 1.5 --cell-height 1.5
   ```
3. **Calibrate** using room corners
4. **Walk around** and watch yourself being tracked
5. **Experiment:**
    - Try different display modes (1-5)
    - Save screenshots (press 's')
    - Change grid size (press 'g')
    - Check the log file

**What you'll learn:**

- How calibration affects accuracy
- How tracking follows movement
- How grid size changes capacity
- How the system responds to real movement

---

## 🎉 Conclusion

You now have practical knowledge of:

✅ **Basic usage** - Running with different sources and settings
✅ **Configuration** - Adjusting for different scenarios
✅ **Troubleshooting** - Solving common problems
✅ **Customization** - Adding your own features
✅ **Real applications** - Solving actual problems

**Next steps:**

1. Try the examples that match your use case
2. Experiment with different settings
3. Customize colors and alerts
4. Deploy for actual monitoring

**Remember:** Start simple, then add complexity!

---

**Happy monitoring!** 🎥 📊 🚀
