# API Reference

Complete API documentation for the Stampede Management System.

## Table of Contents

- [Configuration](#configuration)
- [Core Classes](#core-classes)
- [Detection](#detection)
- [Tracking](#tracking)
- [Geometry](#geometry)
- [Occupancy](#occupancy)
- [Visualization](#visualization)
- [Utilities](#utilities)

---

## Configuration

### MonitoringConfig

**Module**: `config.py`

Complete configuration class for the crowd monitoring system.

```python
from config import MonitoringConfig

config = MonitoringConfig(
    source="0",
    model_path="model/yolov8n.pt",
    # ... other parameters
)
```

#### Parameters

**Video Source Settings**

- **`source`** (`Union[str, int]`, default: `"0"`)  
  Video source - camera index (int) or file path (str)
  ```python
  source=0          # First webcam
  source="video.mp4"  # Video file
  source="rtsp://192.168.1.100/stream"  # IP camera
  ```

- **`model_path`** (`str`, default: `"model/yolov8n.pt"`)  
  Path to YOLO model file

- **`camera_width`** (`int`, default: `1280`)  
  Desired camera frame width in pixels

- **`camera_height`** (`int`, default: `720`)  
  Desired camera frame height in pixels

- **`camera_fps`** (`int`, default: `30`)  
  Desired camera frames per second

**Grid and Spatial Settings**

- **`cell_width`** (`float`, default: `1.0`)  
  Grid cell width in meters

- **`cell_height`** (`float`, default: `1.0`)  
  Grid cell height in meters

- **`person_radius`** (`float`, default: `2.0`)  
  Person radius for capacity calculation in meters

**Detection Settings**

- **`detect_every`** (`int`, default: `5`)  
  Run detection every N frames (1 = every frame)

- **`confidence_threshold`** (`float`, default: `0.35`)  
  YOLO detection confidence threshold (0.0 to 1.0)

- **`min_bbox_area`** (`int`, default: `1500`)  
  Minimum bounding box area in pixels²

- **`yolo_imgsz`** (`int`, default: `640`)  
  YOLO input image size (320, 640, or 1280)

- **`yolo_classes`** (`Tuple[int, ...]`, default: `(0,)`)  
  YOLO class IDs to detect (0 = person)

- **`min_model_size_bytes`** (`int`, default: `1000000`)  
  Minimum valid model file size in bytes

**Tracking Settings**

- **`use_deepsort`** (`bool`, default: `False`)  
  Use DeepSort tracker (True) or Centroid tracker (False)

- **`max_age`** (`int`, default: `80`)  
  Maximum frames to keep track without detection

- **`n_init`** (`int`, default: `1`)  
  Frames needed to confirm track (DeepSort only)

- **`centroid_distance_threshold`** (`float`, default: `80.0`)  
  Maximum distance for centroid tracker matching (pixels)

**Smoothing and Alert Settings**

- **`ema_alpha`** (`float`, default: `0.4`)  
  Exponential moving average smoothing factor (0.0 to 1.0)
    - Higher = more responsive to changes
    - Lower = more smoothing

- **`fps`** (`float`, default: `15.0`)  
  Expected FPS for timing calculations

- **`hysteresis_time`** (`float`, default: `3.0`)  
  Alert delay time in seconds

- **`alert_clear_offset`** (`float`, default: `0.5`)  
  Occupancy drop needed to clear alert

**Visualization Settings**

- **`max_birdseye_pixels`** (`int`, default: `900`)  
  Maximum bird's eye view dimension

- **`grid_line_thickness`** (`int`, default: `2`)  
  Grid line thickness in pixels

- **`bbox_thickness`** (`int`, default: `3`)  
  Bounding box line thickness

**Colors (BGR format)**

- **`grid_color`** (`Tuple[int, int, int]`, default: `(100, 255, 100)`)
- **`bbox_color`** (`Tuple[int, int, int]`, default: `(0, 255, 0)`)
- **`occupancy_normal_color`** (`Tuple[int, int, int]`, default: `(0, 255, 0)`)
- **`occupancy_warning_color`** (`Tuple[int, int, int]`, default: `(0, 165, 255)`)
- **`occupancy_critical_color`** (`Tuple[int, int, int]`, default: `(0, 0, 255)`)

**Interactive Features**

- **`enable_screenshots`** (`bool`, default: `True`)  
  Allow screenshot capture with 's' key

- **`enable_grid_adjustment`** (`bool`, default: `True`)  
  Allow runtime grid size changes

**Calibration Settings**

- **`calibration_area_width`** (`float`, default: `10.0`)  
  Calibration area width in meters

- **`calibration_area_height`** (`float`, default: `10.0`)  
  Calibration area height in meters

- **`auto_calibration`** (`bool`, default: `False`)  
  Use preset dimensions (skip manual input)

---

### TrackData

**Module**: `config.py`

Data structure for track information.

```python
from config import TrackData

track = TrackData(
    track_id=1,
    bbox=(100, 150, 200, 300),
    world_position=(5.2, 3.7),
    confidence=0.87,
    age=0,
    confirmed=True
)
```

#### Attributes

- **`track_id`** (`int`)  
  Unique track identifier

- **`bbox`** (`Tuple[int, int, int, int]`)  
  Bounding box as (x1, y1, x2, y2) in pixels

- **`world_position`** (`Tuple[float, float]`)  
  Position as (x, y) in meters

- **`confidence`** (`float`)  
  Detection confidence (0.0 to 1.0)

- **`age`** (`int`, default: `0`)  
  Frames since last detection

- **`confirmed`** (`bool`, default: `True`)  
  Whether track is confirmed

---

## Core Classes

### CrowdMonitor

**Module**: `monitor.py`

Main orchestrator for the crowd monitoring system.

```python
from monitor import CrowdMonitor
from config import MonitoringConfig

config = MonitoringConfig(source=0)
monitor = CrowdMonitor(config)
success = monitor.initialize()
```

#### Constructor

```python
CrowdMonitor(config: MonitoringConfig)
```

**Parameters:**

- `config`: MonitoringConfig object

#### Methods

##### `initialize() -> bool`

Initialize and start the monitoring system (blocking call).

**Returns:**

- `True` if successful, `False` otherwise

**Example:**

```python
monitor = CrowdMonitor(config)
if monitor.initialize():
    print("Monitoring completed")
else:
    print("Monitoring failed")
```

##### `@staticmethod detect_available_cameras(max_cameras: int = 10, timeout: float = 1.0) -> List[dict]`

Detect all available camera sources.

**Parameters:**

- `max_cameras`: Maximum camera indices to check
- `timeout`: Timeout per camera in seconds

**Returns:**

- List of dictionaries with camera info:
  ```python
  [
      {'index': 0, 'name': 'Camera 0 (1280x720)', 'width': 1280, 'height': 720},
      {'index': 1, 'name': 'Camera 1 (640x480)', 'width': 640, 'height': 480}
  ]
  ```

**Example:**

```python
cameras = CrowdMonitor.detect_available_cameras()
for cam in cameras:
    print(f"Found: {cam['name']}")
```

#### Attributes

- **`config`** (`MonitoringConfig`)  
  Configuration object

- **`detector`** (`PersonDetector`)  
  Person detector instance

- **`calibrator`** (`CameraCalibrator`)  
  Camera calibrator instance

- **`tracker`** (`Union[SimpleCentroidTracker, DeepSortTracker]`)  
  Person tracker instance

- **`occupancy_grid`** (`OccupancyGrid`)  
  Occupancy grid instance

- **`visualizer`** (`MonitorVisualizer`)  
  Visualizer instance

- **`frame_count`** (`int`)  
  Current frame number

- **`current_mode`** (`str`)  
  Current display mode ('1'-'5')

- **`should_stop`** (`callable`)  
  Function that returns True to stop monitoring

---

## Detection

### PersonDetector

**Module**: `detector.py`

YOLO-based person detector.

```python
from detector import PersonDetector
from config import MonitoringConfig

config = MonitoringConfig()
detector = PersonDetector(config)
detector.load_model()
```

#### Constructor

```python
PersonDetector(config: MonitoringConfig)
```

#### Methods

##### `load_model() -> bool`

Load YOLO model with auto-download and error handling.

**Returns:**

- `True` if successful, `False` otherwise

**Example:**

```python
detector = PersonDetector(config)
if detector.load_model():
    print("Model loaded successfully")
```

##### `detect_persons(frame: np.ndarray) -> List[List[float]]`

Detect persons in frame.

**Parameters:**

- `frame`: Input frame as numpy array (H×W×3)

**Returns:**

- List of detections: `[[x1, y1, x2, y2, confidence], ...]`

**Example:**

```python
import cv2

frame = cv2.imread("image.jpg")
detections = detector.detect_persons(frame)

for det in detections:
    x1, y1, x2, y2, conf = det
    print(f"Person at ({x1:.0f},{y1:.0f}) conf={conf:.2f}")
```

---

## Tracking

### SimpleCentroidTracker

**Module**: `trackers.py`

Fast centroid-based tracker.

```python
from trackers import SimpleCentroidTracker

tracker = SimpleCentroidTracker(
    max_age=30,
    distance_threshold=80.0
)
```

#### Constructor

```python
SimpleCentroidTracker(
    max_age: int = 30,
    distance_threshold: float = 80.0
)
```

**Parameters:**

- `max_age`: Maximum frames to keep track without detection
- `distance_threshold`: Maximum pixel distance for matching

#### Methods

##### `update_tracks(detections: List[List[float]], frame: Optional[np.ndarray] = None) -> List[TrackData]`

Update tracks with new detections.

**Parameters:**

- `detections`: List of `[x1, y1, x2, y2, confidence]`
- `frame`: Optional frame (unused in centroid tracker)

**Returns:**

- List of `TrackData` objects

**Example:**

```python
detections = detector.detect_persons(frame)
tracks = tracker.update_tracks(detections, frame)

for track in tracks:
    print(f"Track {track.track_id}: bbox={track.bbox}")
```

---

### DeepSortTracker

**Module**: `trackers.py`

Advanced DeepSort tracker with appearance features.

```python
from trackers import DeepSortTracker, DEEPSORT_AVAILABLE

if DEEPSORT_AVAILABLE:
    tracker = DeepSortTracker(
        max_age=30,
        n_init=1
    )
```

#### Constructor

```python
DeepSortTracker(
    max_age: int = 30,
    n_init: int = 1
)
```

**Parameters:**

- `max_age`: Maximum frames to keep track without detection
- `n_init`: Frames needed to confirm track

**Raises:**

- `ImportError`: If DeepSort is not installed

#### Methods

##### `update_tracks(detections: List[List[float]], frame: Optional[np.ndarray] = None) -> List[TrackData]`

Update tracks using DeepSort algorithm.

**Parameters:**

- `detections`: List of `[x1, y1, x2, y2, confidence]`
- `frame`: Frame image for appearance extraction (required for DeepSort)

**Returns:**

- List of `TrackData` objects

---

## Geometry

### GeometryProcessor

**Module**: `geometry.py`

Handles coordinate transformations.

```python
from geometry import GeometryProcessor
import numpy as np

# After calibration
geom = GeometryProcessor(H_matrix, inv_H_matrix)
```

#### Constructor

```python
GeometryProcessor(
    homography_matrix: np.ndarray,
    inverse_homography: np.ndarray
)
```

**Parameters:**

- `homography_matrix`: 3×3 matrix for image → world transform
- `inverse_homography`: 3×3 matrix for world → image transform

#### Methods

##### `project_bbox_to_world(bbox: Tuple[int, int, int, int]) -> Tuple[Optional[Polygon], Optional[np.ndarray]]`

Transform bounding box to world coordinates.

**Parameters:**

- `bbox`: Bounding box as `(x1, y1, x2, y2)` in pixels

**Returns:**

- Tuple of:
    - `Polygon`: Shapely polygon in world coordinates (meters)
    - `np.ndarray`: Corner points in world coordinates
    - Returns `(None, None)` on error

**Example:**

```python
bbox = (100, 150, 200, 300)
polygon, corners = geom.project_bbox_to_world(bbox)

if polygon:
    print(f"Area: {polygon.area:.2f} m²")
    print(f"Centroid: ({polygon.centroid.x:.2f}, {polygon.centroid.y:.2f})")
```

##### `world_to_image_point(world_x: float, world_y: float) -> Tuple[int, int]`

Convert world coordinates to image coordinates.

**Parameters:**

- `world_x`: X coordinate in meters
- `world_y`: Y coordinate in meters

**Returns:**

- Tuple of `(x, y)` in pixels

**Example:**

```python
world_x, world_y = 5.0, 7.5  # meters
img_x, img_y = geom.world_to_image_point(world_x, world_y)
print(f"Image coordinates: ({img_x}, {img_y}) pixels")
```

---

### CameraCalibrator

**Module**: `calibration.py`

Handles camera calibration.

```python
from calibration import CameraCalibrator
from config import MonitoringConfig

config = MonitoringConfig(
    calibration_area_width=10.0,
    calibration_area_height=10.0,
    auto_calibration=True
)

calibrator = CameraCalibrator(config)
```

#### Constructor

```python
CameraCalibrator(config: Optional[MonitoringConfig] = None)
```

**Parameters:**

- `config`: Optional configuration (uses defaults if None)

#### Methods

##### `calibrate(frame: np.ndarray) -> bool`

Perform camera calibration.

**Parameters:**

- `frame`: Calibration frame

**Returns:**

- `True` if successful, `False` otherwise

**Example:**

```python
import cv2

cap = cv2.VideoCapture(0)
ret, frame = cap.read()

calibrator = CameraCalibrator(config)
if calibrator.calibrate(frame):
    print(f"Calibrated: {calibrator.world_width}m × {calibrator.world_height}m")
    geom = calibrator.geometry_processor
```

#### Attributes

- **`geometry_processor`** (`GeometryProcessor`)  
  Initialized after calibration

- **`world_width`** (`float`)  
  Calibrated area width in meters

- **`world_height`** (`float`)  
  Calibrated area height in meters

---

## Occupancy

### OccupancyGrid

**Module**: `occupancy.py`

Grid-based occupancy monitoring.

```python
from occupancy import OccupancyGrid
from config import MonitoringConfig

config = MonitoringConfig(
    cell_width=2.0,
    cell_height=2.0,
    person_radius=0.5
)

grid = OccupancyGrid(
    config,
    geometry_processor,
    world_width=10.0,
    world_height=10.0
)
```

#### Constructor

```python
OccupancyGrid(
    config: MonitoringConfig,
    geometry_processor: GeometryProcessor,
    world_width: float,
    world_height: float
)
```

**Parameters:**

- `config`: Monitoring configuration
- `geometry_processor`: Geometry processor for transforms
- `world_width`: Width of monitored area in meters
- `world_height`: Height of monitored area in meters

#### Methods

##### `update(tracks: List[TrackData], dt: float) -> None`

Update grid with current tracks.

**Parameters:**

- `tracks`: List of current tracks
- `dt`: Time delta since last update in seconds

**Example:**

```python
tracks = tracker.update_tracks(detections, frame)
grid.update(tracks, dt=0.033)  # 30 FPS

# Check for alerts
for row in range(grid.grid_rows):
    for col in range(grid.grid_cols):
        if grid.notified[row, col]:
            occupancy = grid.ema_counts[row, col]
            print(f"ALERT: Cell ({row},{col}) = {occupancy:.1f}/{grid.cell_capacity}")
```

##### `get_cell_for_track(track: TrackData) -> Optional[Tuple[int, int]]`

Get grid cell for a track.

**Parameters:**

- `track`: Track to locate

**Returns:**

- Tuple of `(row, col)` or `None` if outside grid

**Example:**

```python
cell = grid.get_cell_for_track(track)
if cell:
    row, col = cell
    occupancy = grid.ema_counts[row, col]
    print(f"Track {track.track_id} in cell ({row},{col}): {occupancy:.1f}")
```

##### `reinitialize(world_width: float, world_height: float) -> None`

Reinitialize grid with new dimensions.

**Parameters:**

- `world_width`: New world width in meters
- `world_height`: New world height in meters

**Example:**

```python
# Change grid size at runtime
config.cell_width = 3.0
config.cell_height = 3.0
grid.reinitialize(world_width, world_height)
```

#### Attributes

- **`grid_rows`** (`int`)  
  Number of grid rows

- **`grid_cols`** (`int`)  
  Number of grid columns

- **`cell_capacity`** (`int`)  
  Maximum people per cell

- **`ema_counts`** (`np.ndarray`)  
  Current occupancy (smoothed), shape: `(rows, cols)`

- **`timers`** (`np.ndarray`)  
  Alert timers per cell, shape: `(rows, cols)`

- **`notified`** (`np.ndarray`)  
  Alert status per cell, shape: `(rows, cols)`, dtype: bool

**Example:**

```python
print(f"Grid: {grid.grid_rows}×{grid.grid_cols}")
print(f"Total cells: {grid.grid_rows * grid.grid_cols}")
print(f"Cell capacity: {grid.cell_capacity} people")

# Access occupancy data
total_occupancy = grid.ema_counts.sum()
print(f"Total people: {total_occupancy:.1f}")

max_occupancy = grid.ema_counts.max()
print(f"Peak cell occupancy: {max_occupancy:.1f}")

alert_count = grid.notified.sum()
print(f"Active alerts: {alert_count}")
```

---

## Visualization

### MonitorVisualizer

**Module**: `visualizer.py`

Handles all visualization rendering.

```python
from visualizer import MonitorVisualizer
from config import MonitoringConfig

config = MonitoringConfig()
visualizer = MonitorVisualizer(
    config,
    camera_width=1280,
    camera_height=720
)
```

#### Constructor

```python
MonitorVisualizer(
    config: MonitoringConfig,
    camera_width: int,
    camera_height: int
)
```

**Parameters:**

- `config`: Monitoring configuration
- `camera_width`: Camera frame width
- `camera_height`: Camera frame height

#### Methods

#####
`draw_grid_overlay(frame: np.ndarray, geometry_processor: GeometryProcessor, occupancy_grid: OccupancyGrid) -> None`

Draw grid lines on frame (modifies in-place).

**Parameters:**

- `frame`: Frame to draw on
- `geometry_processor`: Geometry processor
- `occupancy_grid`: Occupancy grid

**Example:**

```python
frame = cap.read()
visualizer.draw_grid_overlay(frame, geom, grid)
cv2.imshow("Grid", frame)
```

##### `draw_track_annotation(frame: np.ndarray, track: TrackData, occupancy_grid: OccupancyGrid) -> None`

Draw bounding box and info for track (modifies in-place).

**Parameters:**

- `frame`: Frame to draw on
- `track`: Track to draw
- `occupancy_grid`: Occupancy grid for color coding

**Example:**

```python
for track in tracks:
    visualizer.draw_track_annotation(frame, track, grid)
```

##### `draw_simple_track_annotation(frame: np.ndarray, track: TrackData) -> None`

Draw simple bounding box without occupancy info.

**Parameters:**

- `frame`: Frame to draw on
- `track`: Track to draw

#####
`draw_cell_occupancy_overlay(frame: np.ndarray, geometry_processor: GeometryProcessor, occupancy_grid: OccupancyGrid) -> None`

Draw occupancy labels on grid cells.

**Parameters:**

- `frame`: Frame to draw on
- `geometry_processor`: Geometry processor
- `occupancy_grid`: Occupancy grid

#####
`create_birdseye_view(tracks: List[TrackData], geometry_processor: GeometryProcessor, occupancy_grid: OccupancyGrid) -> np.ndarray`

Create bird's eye (top-down) view.

**Parameters:**

- `tracks`: Current tracks
- `geometry_processor`: Geometry processor
- `occupancy_grid`: Occupancy grid

**Returns:**

- Bird's eye view frame

**Example:**

```python
birdseye = visualizer.create_birdseye_view(tracks, geom, grid)
cv2.imshow("Bird's Eye", birdseye)
```

#####
`create_info_panel(width: int, tracks: List[TrackData], occupancy_grid: OccupancyGrid, frame_count: int, mode_name: str, tracker, fps_counter: List[float], fps_start_time: float, show_fps: bool) -> np.ndarray`

Create information panel.

**Parameters:**

- `width`: Panel width
- `tracks`: Current tracks
- `occupancy_grid`: Occupancy grid
- `frame_count`: Current frame number
- `mode_name`: Display mode name
- `tracker`: Tracker instance
- `fps_counter`: FPS counter data
- `fps_start_time`: FPS tracking start time
- `show_fps`: Whether to show FPS

**Returns:**

- Info panel frame

#####
`add_basic_info_overlay(frame: np.ndarray, mode_name: str, fps_counter: List[float], fps_start_time: float, show_fps: bool) -> None`

Add basic info overlay (modifies in-place).

**Parameters:**

- `frame`: Frame to draw on
- `mode_name`: Mode name to display
- `fps_counter`: FPS counter data
- `fps_start_time`: FPS tracking start time
- `show_fps`: Whether to show FPS

---

## Utilities

### Logger Configuration

**Module**: `logger_config.py`

```python
from logger_config import get_logger

logger = get_logger(__name__)
logger.info("This is an info message")
logger.warning("This is a warning")
logger.error("This is an error")
```

#### Functions

##### `get_logger(name: str) -> logging.Logger`

Get configured logger instance.

**Parameters:**

- `name`: Logger name (typically `__name__`)

**Returns:**

- Configured logger

**Log Levels:**

- `DEBUG`: Detailed information for debugging
- `INFO`: General information messages
- `WARNING`: Warning messages
- `ERROR`: Error messages

**Log Output:**

- Console (INFO and above)
- File `crowd_monitor.log` (all levels)

---

### Resource Path Resolution

**Module**: `detector.py`

```python
from detector import get_resource_path

# Get path to resource (works in dev and PyInstaller)
model_path = get_resource_path("model/yolov8n.pt")
```

#### Functions

##### `get_resource_path(relative_path: str) -> str`

Get absolute path to resource (PyInstaller-compatible).

**Parameters:**

- `relative_path`: Relative path to resource

**Returns:**

- Absolute path to resource

---

## Data Types Reference

### Type Aliases

```python
# Detection format
Detection = List[float]  # [x1, y1, x2, y2, confidence]

# Multiple detections
Detections = List[Detection]

# Track list
Tracks = List[TrackData]

# Bounding box
BBox = Tuple[int, int, int, int]  # (x1, y1, x2, y2)

# World position
WorldPos = Tuple[float, float]  # (x_meters, y_meters)

# Image point
ImagePoint = Tuple[int, int]  # (x_pixels, y_pixels)

# Color (BGR)
Color = Tuple[int, int, int]  # (blue, green, red)
```

---

## Constants

### YOLO Classes

```python
YOLO_PERSON_CLASS = 0  # COCO class ID for person
```

### Display Modes

```python
MODE_RAW_CAMERA = '1'
MODE_GRID_OVERLAY = '2'
MODE_DETECTION_VIEW = '3'
MODE_MONITORING_VIEW = '4'
MODE_SPLIT_VIEW = '5'
```

### Key Codes

```python
KEY_QUIT = ord('q')
KEY_SCREENSHOT = ord('s')
KEY_GRID_TOGGLE = ord('g')
KEY_RESET = ord('r')
KEY_FPS = ord('f')
KEY_ESC = 27
```

---

## Error Handling

### Common Exceptions

```python
# Import errors
try:
    from deep_sort_realtime import DeepSort
except ImportError:
    print("DeepSort not available")

# Model loading errors
try:
    detector.load_model()
except Exception as e:
    print(f"Failed to load model: {e}")

# Video capture errors
try:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")
except Exception as e:
    print(f"Video capture error: {e}")

# Calibration errors
try:
    calibrator.calibrate(frame)
except KeyboardInterrupt:
    print("Calibration cancelled")
except Exception as e:
    print(f"Calibration failed: {e}")
```

---

## Complete Usage Example

```python
import cv2
from config import MonitoringConfig, TrackData
from monitor import CrowdMonitor
from detector import PersonDetector
from trackers import SimpleCentroidTracker
from calibration import CameraCalibrator
from geometry import GeometryProcessor
from occupancy import OccupancyGrid
from visualizer import MonitorVisualizer
from logger_config import get_logger

# Setup logging
logger = get_logger(__name__)

# Create configuration
config = MonitoringConfig(
    source=0,
    cell_width=2.0,
    cell_height=2.0,
    person_radius=0.5,
    confidence_threshold=0.35,
    detect_every=3,
    use_deepsort=False,
    auto_calibration=True,
    calibration_area_width=10.0,
    calibration_area_height=10.0
)

# Method 1: Simple usage with CrowdMonitor
logger.info("Starting crowd monitoring system")
monitor = CrowdMonitor(config)
success = monitor.initialize()

# Method 2: Manual component initialization
detector = PersonDetector(config)
detector.load_model()

tracker = SimpleCentroidTracker(
    max_age=config.max_age,
    distance_threshold=config.centroid_distance_threshold
)

cap = cv2.VideoCapture(config.source)
ret, frame = cap.read()

calibrator = CameraCalibrator(config)
calibrator.calibrate(frame)

grid = OccupancyGrid(
    config,
    calibrator.geometry_processor,
    calibrator.world_width,
    calibrator.world_height
)

visualizer = MonitorVisualizer(
    config,
    frame.shape[1],
    frame.shape[0]
)

# Processing loop
frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    
    # Detection
    if frame_count % config.detect_every == 0:
        detections = detector.detect_persons(frame)
    else:
        detections = []
    
    # Tracking
    tracks = tracker.update_tracks(detections, frame)
    
    # Occupancy
    grid.update(tracks, dt=0.033)
    
    # Visualization
    visualizer.draw_grid_overlay(frame, calibrator.geometry_processor, grid)
    for track in tracks:
        visualizer.draw_track_annotation(frame, track, grid)
    visualizer.draw_cell_occupancy_overlay(frame, calibrator.geometry_processor, grid)
    
    # Display
    cv2.imshow("Monitoring", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## Version Information

- **API Version**: 1.0
- **Python**: 3.8+
- **OpenCV**: 4.8.0+
- **Ultralytics**: 8.0.0+
- **NumPy**: 2.3.0+
- **Shapely**: 2.0.0+

---

**For more information, see:**

- [README.md](README.md) - Complete documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [EXAMPLES.md](EXAMPLES.md) - Code examples
- [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) - Getting started
