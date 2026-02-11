# System Architecture Documentation

## Table of Contents

- [Overview](#overview)
- [System Design Principles](#system-design-principles)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Processing Pipeline](#processing-pipeline)
- [Key Algorithms](#key-algorithms)
- [Performance Considerations](#performance-considerations)

---

## Overview

The Stampede Management System follows a **modular, layered architecture** designed for:

- **Scalability**: Easy to extend with new features
- **Maintainability**: Clear separation of concerns
- **Performance**: Optimized processing pipeline
- **Reliability**: Robust error handling and recovery

### Architectural Layers

```
┌───────────────────────────────────────────────────┐
│           Presentation Layer                       │
│  - GUI (config_gui.py)                            │
│  - CLI (main.py)                                  │
│  - Visualization (visualizer.py)                  │
└───────────────────────────────────────────────────┘
                       │
┌───────────────────────────────────────────────────┐
│         Application Layer                          │
│  - Monitor Orchestrator (monitor.py)              │
│  - Configuration Management (config.py)           │
│  - License Management (auth/license_manager.py)   │
└───────────────────────────────────────────────────┘
                       │
┌───────────────────────────────────────────────────┐
│          Processing Layer                          │
│  - Detection (detector.py)                        │
│  - Tracking (trackers.py)                         │
│  - Occupancy Analysis (occupancy.py)              │
└───────────────────────────────────────────────────┘
                       │
┌───────────────────────────────────────────────────┐
│          Infrastructure Layer                      │
│  - Geometry Transforms (geometry.py)              │
│  - Camera Calibration (calibration.py)            │
│  - Logging (logger_config.py)                     │
└───────────────────────────────────────────────────┘
```

---

## System Design Principles

### 1. Single Responsibility Principle

Each module has one clear purpose:

```python
# detector.py - ONLY handles person detection
class PersonDetector:
    def load_model(self) -> bool: ...
    def detect_persons(self, frame) -> List: ...

# trackers.py - ONLY handles person tracking
class SimpleCentroidTracker:
    def update_tracks(self, detections, frame) -> List[TrackData]: ...

# occupancy.py - ONLY handles grid occupancy
class OccupancyGrid:
    def update(self, tracks, dt) -> None: ...
```

### 2. Dependency Injection

Configuration and dependencies are injected, not hardcoded:

```python
# Good: Dependencies injected via config
class CrowdMonitor:
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.detector = PersonDetector(config)
        self.tracker = self._initialize_tracker()

# Configuration is centralized
config = MonitoringConfig(
    source=0,
    cell_width=2.0,
    confidence_threshold=0.35
)
monitor = CrowdMonitor(config)
```

### 3. Separation of Concerns

- **Detection**: YOLO neural network processing
- **Tracking**: Maintaining object identity across frames
- **Geometry**: Coordinate transformations
- **Occupancy**: Grid-based crowd analysis
- **Visualization**: Rendering and display

### 4. Error Handling

Defensive programming with graceful degradation:

```python
try:
    # Try advanced feature
    tracker = DeepSortTracker()
except ImportError:
    # Fallback to simpler implementation
    logger.warning("DeepSort not available, using simple tracker")
    tracker = SimpleCentroidTracker()
```

---

## Component Architecture

### 1. Monitor (monitor.py)

**Role**: Main orchestrator that coordinates all components

**Responsibilities:**

- Initialize all subsystems
- Manage video capture
- Coordinate processing pipeline
- Handle user interactions
- Manage display modes

**Key Methods:**

```python
class CrowdMonitor:
    def initialize(self) -> bool:
        """Initialize all components and start processing"""
        # 1. Load detection model
        # 2. Initialize video capture
        # 3. Perform camera calibration
        # 4. Create occupancy grid
        # 5. Initialize tracker
        # 6. Start processing loop
        
    def _process_video_stream(self, cap):
        """Main processing loop"""
        while True:
            frame = cap.read()
            tracks = self._process_frame(frame)
            self.occupancy_grid.update(tracks, dt)
            display_frame = self._create_visualization(frame, tracks)
            cv2.imshow(window_title, display_frame)
```

**State Management:**

```python
# Runtime state
self.frame_count = 0
self.last_detection_frame = -1
self.fps_counter = []
self.current_mode = '4'  # Display mode
self.should_stop = lambda: False  # Stop flag for GUI
```

---

### 2. Detector (detector.py)

**Role**: Person detection using YOLOv8 neural network

**Architecture:**

```python
class PersonDetector:
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.model = None  # YOLO model loaded later
    
    def load_model(self) -> bool:
        """Load YOLO model with error handling"""
        # 1. Resolve model path (handle PyInstaller)
        # 2. Download if not present
        # 3. Load into memory
        # 4. Validate
        
    def detect_persons(self, frame) -> List[List[float]]:
        """Run detection on frame"""
        # 1. Preprocess frame
        # 2. Run YOLO inference
        # 3. Filter by confidence threshold
        # 4. Filter by minimum area
        # 5. Return [x1, y1, x2, y2, conf] list
```

**YOLO Processing Pipeline:**

```
Input Frame (H×W×3)
    ↓
Resize to 640×640 (YOLO input size)
    ↓
Normalize pixel values
    ↓
YOLO Neural Network
    ↓
Output: Bounding boxes + confidence scores
    ↓
Non-maximum Suppression (NMS)
    ↓
Filter by confidence threshold
    ↓
Filter by minimum bounding box area
    ↓
Return detections
```

**Performance Optimization:**

```python
# Detection every N frames (not every frame)
if self.frame_count % self.config.detect_every == 0:
    detections = self.detector.detect_persons(frame)
```

---

### 3. Tracker (trackers.py)

**Role**: Maintain consistent IDs for detected people across frames

**Two Implementations:**

#### Simple Centroid Tracker

**Algorithm:**

```python
class SimpleCentroidTracker:
    """
    Fast, simple tracking based on centroid distance
    
    Algorithm:
    1. Calculate centroid of each detection
    2. For each existing track:
       - Find closest detection within threshold
       - Update track if match found
       - Increment age if no match
    3. Create new tracks for unmatched detections
    4. Remove tracks older than max_age
    """
    
    def update_tracks(self, detections, frame):
        centroids = [(det, (det[0]+det[2])/2, (det[1]+det[3])/2) 
                     for det in detections]
        
        # Match tracks to detections
        for track_id, track in self.tracks.items():
            best_match = None
            best_distance = float('inf')
            
            for i, (det, cx, cy) in enumerate(centroids):
                distance = euclidean_distance(track.position, (cx, cy))
                if distance < best_distance and distance < threshold:
                    best_match = (i, det, cx, cy)
                    best_distance = distance
            
            if best_match:
                # Update track
                track.update(best_match)
            else:
                track.age += 1
```

**Time Complexity**: O(N×M) where N=tracks, M=detections

#### DeepSort Tracker

**Algorithm:**

```python
class DeepSortTracker:
    """
    Advanced tracking using appearance features
    
    Algorithm:
    1. Extract appearance features from detection patches
    2. Predict track positions using Kalman filter
    3. Match detections to tracks using:
       - Motion model (Kalman filter)
       - Appearance model (ReID features)
    4. Update tracks with Hungarian algorithm
    5. Manage track lifecycle (tentative → confirmed → deleted)
    """
```

**Advantages over Centroid:**

- Better handling of occlusions
- More robust to rapid movement
- Appearance-based re-identification

**Disadvantages:**

- Slower (requires deep learning features)
- More memory intensive
- Requires `deep-sort-realtime` library

---

### 4. Calibration (calibration.py)

**Role**: Map camera perspective to real-world coordinates

**Process Flow:**

```
User selects 4 corners → Calculate homography matrix → Create geometry processor
```

**Implementation:**

```python
class CameraCalibrator:
    def calibrate(self, frame) -> bool:
        # 1. Get 4 corner points from user
        pts_img = self._get_calibration_points(frame)
        
        # 2. Get real-world dimensions
        world_width, world_height = self._get_world_dimensions()
        
        # 3. Create world coordinate rectangle
        pts_world = np.array([
            [0, 0],
            [world_width, 0],
            [world_width, world_height],
            [0, world_height]
        ])
        
        # 4. Calculate homography
        H = cv2.getPerspectiveTransform(pts_img, pts_world)
        inv_H = cv2.getPerspectiveTransform(pts_world, pts_img)
        
        # 5. Create geometry processor
        self.geometry_processor = GeometryProcessor(H, inv_H)
```

**Homography Mathematics:**

The homography matrix **H** transforms image coordinates to world coordinates:

```
┌   ┐     ┌         ┐ ┌   ┐
│ x'│     │ h11 h12 h13│ │ x │
│ y'│  =  │ h21 h22 h23│ │ y │
│ w'│     │ h31 h32 h33│ │ 1 │
└   ┘     └         ┘ └   ┘

x_world = x' / w'
y_world = y' / w'
```

**Example:**

```python
# Image point (pixel coordinates)
img_point = (320, 240)

# After transformation (world coordinates in meters)
world_point = (5.2, 3.7)
```

---

### 5. Geometry Processor (geometry.py)

**Role**: Coordinate transformations between image and world space

**Core Operations:**

```python
class GeometryProcessor:
    def __init__(self, H_matrix, inv_H_matrix):
        self.H_matrix = H_matrix          # Image → World
        self.inv_H_matrix = inv_H_matrix  # World → Image
    
    def project_bbox_to_world(self, bbox):
        """Transform bounding box to world coordinates"""
        # 1. Extract 4 corners from bbox
        corners = [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]
        
        # 2. Apply perspective transform
        world_corners = cv2.perspectiveTransform(corners, H_matrix)
        
        # 3. Create polygon
        polygon = Polygon(world_corners)
        
        return polygon, world_corners
    
    def world_to_image_point(self, world_x, world_y):
        """Transform world point to image coordinates"""
        point = np.array([[[world_x, world_y]]])
        img_point = cv2.perspectiveTransform(point, inv_H_matrix)
        return int(img_point[0,0,0]), int(img_point[0,0,1])
```

**Use Cases:**

1. **Detection → World**: Map detected person bbox to real-world position
2. **Grid → Image**: Draw grid lines on camera view
3. **Occupancy → World**: Calculate which grid cell person occupies

---

### 6. Occupancy Grid (occupancy.py)

**Role**: Grid-based crowd density monitoring with alerts

**Grid Structure:**

```
World space divided into cells:

0,0  0,1  0,2  0,3  0,4
1,0  1,1  1,2  1,3  1,4
2,0  2,1  2,2  2,3  2,4
3,0  3,1  3,2  3,3  3,4

Each cell: width × height meters
Capacity: cell_area / person_area
```

**Data Structures:**

```python
class OccupancyGrid:
    # Grid dimensions
    self.grid_rows: int      # Number of rows
    self.grid_cols: int      # Number of columns
    self.cell_capacity: int  # Max people per cell
    
    # Runtime state (all numpy arrays: rows × cols)
    self.ema_counts: np.ndarray   # Current occupancy (smoothed)
    self.timers: np.ndarray       # Alert timer per cell
    self.notified: np.ndarray     # Alert status per cell
```

**Update Algorithm:**

```python
def update(self, tracks, dt):
    # 1. Create fresh counts array
    current_counts = zeros(rows, cols)
    
    # 2. For each tracked person:
    for track in tracks:
        # 2a. Project bbox to world coordinates
        polygon = project_to_world(track.bbox)
        
        # 2b. Find overlapping cells
        for cell in overlapping_cells(polygon):
            # 2c. Calculate intersection area
            overlap = intersection(polygon, cell)
            fraction = overlap.area / polygon.area
            
            # 2d. Add fractional count
            current_counts[cell] += fraction
    
    # 3. Apply exponential moving average (smoothing)
    ema_counts = α × current_counts + (1-α) × ema_counts
    
    # 4. Update alerts
    for each cell:
        if ema_counts[cell] > capacity:
            timer[cell] += dt
            if timer[cell] >= hysteresis_time:
                trigger_alert(cell)
        else:
            timer[cell] = max(0, timer[cell] - dt)
```

**Capacity Calculation:**

```python
# Person footprint area
person_area = π × radius²

# Cell area
cell_area = width × height

# Maximum people per cell
capacity = floor(cell_area / person_area)

# Example:
# Cell: 2m × 2m = 4 m²
# Person radius: 0.5m → area = π × 0.25 = 0.785 m²
# Capacity: 4 / 0.785 = 5.09 ≈ 5 people
```

**Exponential Moving Average (EMA):**

Smooths occupancy counts to reduce noise from detection jitter:

```python
EMA[t] = α × Current[t] + (1 - α) × EMA[t-1]

Where:
- α = smoothing factor (0.4 default)
- Higher α = more responsive
- Lower α = more smoothing
```

**Alert Hysteresis:**

Prevents rapid alert on/off toggling:

```
Occupancy > Capacity
    ↓
Timer starts incrementing
    ↓
Timer >= hysteresis_time (e.g., 3 seconds)
    ↓
ALERT TRIGGERED
    ↓
Occupancy drops below (Capacity - offset)
    ↓
Timer decrements
    ↓
Timer reaches 0
    ↓
Alert cleared
```

---

### 7. Visualizer (visualizer.py)

**Role**: Render all visual outputs

**Visualization Pipeline:**

```
Base Frame
    ↓
Add Grid Overlay → draw_grid_overlay()
    ↓
Add Track Annotations → draw_track_annotation()
    ↓
Add Cell Occupancy Labels → draw_cell_occupancy_overlay()
    ↓
Add Info Panel → create_info_panel()
    ↓
Display Frame
```

**Key Rendering Functions:**

```python
class MonitorVisualizer:
    def draw_grid_overlay(self, frame, geom, grid):
        """Draw grid lines on frame"""
        for row in range(grid.grid_rows + 1):
            y = row * grid.cell_height
            # Convert world coordinate line to image coordinates
            for col in range(grid.grid_cols):
                x1, x2 = col * grid.cell_width, (col+1) * grid.cell_width
                pt1 = geom.world_to_image_point(x1, y)
                pt2 = geom.world_to_image_point(x2, y)
                cv2.line(frame, pt1, pt2, color, thickness)
    
    def draw_track_annotation(self, frame, track, grid):
        """Draw bounding box and info for track"""
        x1, y1, x2, y2 = track.bbox
        
        # Get occupancy info
        cell = grid.get_cell_for_track(track)
        if cell:
            occupancy = grid.ema_counts[cell]
            capacity = grid.cell_capacity
            color = self._get_occupancy_color(occupancy, capacity)
        
        # Draw bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        
        # Draw ID label
        cv2.putText(frame, f"ID:{track.track_id}", (x1, y1-10), ...)
    
    def create_birdseye_view(self, tracks, geom, grid):
        """Create top-down view of monitored area"""
        # 1. Create blank canvas
        # 2. Draw grid
        # 3. Draw person positions as circles
        # 4. Color-code by occupancy
        # 5. Return bird's eye frame
```

**Color Coding:**

```python
def _get_occupancy_color(occupancy, capacity):
    ratio = occupancy / capacity
    
    if ratio >= 1.0:
        return RED      # Over capacity
    elif ratio >= 0.8:
        return ORANGE   # Warning (80%+)
    else:
        return GREEN    # Normal
```

---

## Data Flow

### Frame Processing Flow

```
┌─────────────┐
│ Video Frame │
└─────────────┘
       │
       ↓
┌─────────────────────────┐
│  Person Detection       │
│  (Every N frames)       │
│  Input: frame           │
│  Output: [bbox, conf]   │
└─────────────────────────┘
       │
       ↓
┌─────────────────────────┐
│  Person Tracking        │
│  Input: detections      │
│  Output: [TrackData]    │
└─────────────────────────┘
       │
       ↓
┌─────────────────────────┐
│  Coordinate Transform   │
│  Input: track.bbox      │
│  Output: world_polygon  │
└─────────────────────────┘
       │
       ↓
┌─────────────────────────┐
│  Occupancy Grid Update  │
│  Input: tracks          │
│  Output: cell_counts    │
└─────────────────────────┘
       │
       ↓
┌─────────────────────────┐
│  Alert Processing       │
│  Input: cell_counts     │
│  Output: alerts         │
└─────────────────────────┘
       │
       ↓
┌─────────────────────────┐
│  Visualization          │
│  Input: all of above    │
│  Output: display_frame  │
└─────────────────────────┘
       │
       ↓
┌─────────────┐
│   Display   │
└─────────────┘
```

### Data Structures Flow

```python
# 1. Detection
detections: List[List[float]]
# [[x1, y1, x2, y2, conf], [x1, y1, x2, y2, conf], ...]

# 2. Tracking
tracks: List[TrackData]
# [TrackData(id=1, bbox=(x1,y1,x2,y2), pos=(cx,cy), conf=0.9), ...]

# 3. Geometry
polygon: Polygon
# Polygon([(x1,y1), (x2,y2), (x3,y3), (x4,y4)])

# 4. Occupancy
ema_counts: np.ndarray  # shape: (rows, cols)
# [[0.5, 1.2, 0.0],
#  [2.1, 3.5, 1.8],
#  [0.0, 0.7, 0.0]]

# 5. Visualization
display_frame: np.ndarray  # shape: (H, W, 3)
# RGB image with all overlays
```

---

## Processing Pipeline

### Initialization Phase

```
1. License Validation
   ├─ Load license.dat
   ├─ Verify machine ID
   └─ Check expiration
   
2. Model Loading
   ├─ Check if model exists
   ├─ Download if missing
   └─ Load into memory
   
3. Video Capture
   ├─ Open video source
   ├─ Set camera properties
   └─ Verify frame capture
   
4. Camera Calibration
   ├─ Display calibration frame
   ├─ User clicks 4 corners
   ├─ User enters dimensions
   └─ Calculate homography
   
5. Component Initialization
   ├─ Create occupancy grid
   ├─ Initialize tracker
   ├─ Initialize visualizer
   └─ Setup display windows
```

### Runtime Phase

```
Loop (for each frame):
   │
   ├─ 1. Capture Frame
   │     └─ Read from video source
   │
   ├─ 2. Detection (every N frames)
   │     ├─ Preprocess frame
   │     ├─ Run YOLO
   │     └─ Filter results
   │
   ├─ 3. Tracking
   │     ├─ Match detections to tracks
   │     ├─ Update existing tracks
   │     ├─ Create new tracks
   │     └─ Remove old tracks
   │
   ├─ 4. Occupancy Update
   │     ├─ Project tracks to world
   │     ├─ Calculate cell occupancy
   │     ├─ Apply EMA smoothing
   │     └─ Update alert timers
   │
   ├─ 5. Visualization
   │     ├─ Render based on mode
   │     ├─ Add overlays
   │     └─ Create display frame
   │
   ├─ 6. Display
   │     └─ Show frame in window
   │
   └─ 7. User Input
         ├─ Check keyboard
         └─ Handle commands
```

---

## Key Algorithms

### 1. Centroid Tracking Algorithm

**Purpose**: Track people across frames using position similarity

**Algorithm:**

```python
def update_tracks(detections, existing_tracks):
    # Step 1: Extract centroids
    detection_centroids = []
    for det in detections:
        cx = (det[0] + det[2]) / 2
        cy = (det[1] + det[3]) / 2
        detection_centroids.append((det, cx, cy))
    
    # Step 2: Match existing tracks
    used_detections = set()
    
    for track_id, track in existing_tracks.items():
        best_distance = infinity
        best_match = None
        
        # Find closest detection
        for i, (det, cx, cy) in enumerate(detection_centroids):
            if i in used_detections:
                continue
            
            # Euclidean distance
            dist = sqrt((track.cx - cx)² + (track.cy - cy)²)
            
            if dist < best_distance and dist < threshold:
                best_distance = dist
                best_match = (i, det, cx, cy)
        
        # Update or age track
        if best_match:
            i, det, cx, cy = best_match
            track.update(det, cx, cy)
            used_detections.add(i)
        else:
            track.age += 1
    
    # Step 3: Create new tracks for unmatched
    for i, (det, cx, cy) in enumerate(detection_centroids):
        if i not in used_detections:
            create_new_track(det, cx, cy)
    
    # Step 4: Remove old tracks
    remove_tracks_where(age > max_age)
```

**Complexity**: O(N×M) where N=tracks, M=detections

**Pros**: Fast, simple, low memory
**Cons**: Struggles with occlusions, identity switches

---

### 2. Grid Occupancy Algorithm

**Purpose**: Calculate how many people occupy each grid cell

**Algorithm:**

```python
def update_occupancy(tracks, dt):
    # Step 1: Initialize count array
    current_counts = zeros(rows, cols)
    
    # Step 2: Calculate occupancy
    for track in tracks:
        # 2a: Project to world space
        polygon = project_bbox_to_world(track.bbox)
        bounds = polygon.bounds  # (minx, miny, maxx, maxy)
        
        # 2b: Find candidate cells
        min_col = floor(bounds.minx / cell_width)
        max_col = floor(bounds.maxx / cell_width)
        min_row = floor(bounds.miny / cell_height)
        max_row = floor(bounds.maxy / cell_height)
        
        # 2c: Check each candidate cell
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                # Create cell polygon
                cell = box(
                    col * cell_width,
                    row * cell_height,
                    (col+1) * cell_width,
                    (row+1) * cell_height
                )
                
                # Calculate intersection
                intersection = polygon.intersection(cell)
                if not intersection.is_empty:
                    # Add fractional count based on overlap
                    fraction = intersection.area / polygon.area
                    current_counts[row, col] += fraction
    
    # Step 3: Apply EMA smoothing
    for row in range(rows):
        for col in range(cols):
            ema_counts[row, col] = (
                alpha * current_counts[row, col] +
                (1 - alpha) * ema_counts[row, col]
            )
    
    # Step 4: Update alerts
    for row in range(rows):
        for col in range(cols):
            if ema_counts[row, col] > capacity:
                timers[row, col] += dt
                if timers[row, col] >= hysteresis_time:
                    if not notified[row, col]:
                        trigger_alert(row, col)
                        notified[row, col] = True
            else:
                timers[row, col] = max(0, timers[row, col] - dt)
                if notified[row, col] and ema_counts[row, col] < threshold:
                    clear_alert(row, col)
                    notified[row, col] = False
```

**Complexity**: O(T×C) where T=tracks, C=cells per track footprint

---

### 3. Perspective Transform Algorithm

**Purpose**: Convert between image pixels and real-world meters

**Mathematics:**

Homography transformation using 3×3 matrix:

```
┌   ┐     ┌           ┐ ┌ ┐
│ x'│     │ h11 h12 h13│ │x│
│ y'│  =  │ h21 h22 h23│ │y│
│ w'│     │ h31 h32 h33│ │1│
└   ┘     └           ┘ └ ┘

x_out = x' / w'
y_out = y' / w'
```

**Implementation:**

```python
def perspective_transform(points, H_matrix):
    # Convert points to homogeneous coordinates
    pts = np.array([[[x, y]] for x, y in points], dtype=np.float32)
    
    # Apply transformation
    transformed = cv2.perspectiveTransform(pts, H_matrix)
    
    # Extract results
    result = [(pt[0][0], pt[0][1]) for pt in transformed]
    
    return result
```

**Computing Homography:**

Given 4 point correspondences:

```python
# Image points (pixels)
pts_img = [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]

# World points (meters)
pts_world = [(0,0), (w,0), (w,h), (0,h)]

# Compute homography
H = cv2.getPerspectiveTransform(
    np.array(pts_img, dtype=np.float32),
    np.array(pts_world, dtype=np.float32)
)
```

---

## Performance Considerations

### Bottlenecks

1. **YOLO Detection** (~80% of compute time)
   - Most expensive operation
   - Run on GPU if available
   - Reduce frequency with `detect_every` parameter

2. **Frame Capture** (~10% of time)
   - Can be slow on some cameras
   - Use lower resolution if needed

3. **Tracking** (~5% of time)
   - DeepSort much slower than Centroid
   - Consider centroid for real-time needs

4. **Rendering** (~5% of time)
   - Complex overlays can slow down
   - Minimize text rendering

### Optimization Strategies

**1. Reduce Detection Frequency:**

```python
config = MonitoringConfig(
    detect_every=5  # Detect every 5 frames instead of every frame
)
```

**2. Lower YOLO Input Size:**

```python
config = MonitoringConfig(
    yolo_imgsz=320  # Default is 640
)
```

**3. Use Simpler Tracker:**

```python
config = MonitoringConfig(
    use_deepsort=False  # Use centroid tracker
)
```

**4. Reduce Camera Resolution:**

```python
config = MonitoringConfig(
    camera_width=640,
    camera_height=480
)
```

**5. GPU Acceleration:**

Ensure PyTorch uses CUDA:

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```

### Performance Metrics

**Target Performance:**

- **FPS**: 15-30 fps for real-time monitoring
- **Latency**: <100ms frame-to-display
- **Memory**: <2GB RAM usage

**Typical Performance:**

| Configuration                                   | FPS   | CPU Usage | RAM   |
|-------------------------------------------------|-------|-----------|-------|
| High Quality (YOLOv8m, DeepSort, every frame)   | 8-10  | 70%       | 1.5GB |
| Balanced (YOLOv8n, Centroid, every 3 frames)    | 20-25 | 50%       | 800MB |
| Fast (YOLOv8n, Centroid, every 5 frames, 320px) | 30-35 | 30%       | 600MB |

---

## Scalability Considerations

### Horizontal Scaling

**Multi-Camera Support:**

```python
# Create separate monitor for each camera
monitors = []
for camera_index in range(num_cameras):
    config = MonitoringConfig(source=camera_index)
    monitor = CrowdMonitor(config)
    monitors.append(monitor)

# Run in separate threads/processes
```

### Vertical Scaling

**Larger Areas:**

```python
# Increase grid resolution for larger areas
config = MonitoringConfig(
    cell_width=1.0,  # Smaller cells
    cell_height=1.0
)
```

**More Complex Scenes:**

```python
# Use more sophisticated tracker
config = MonitoringConfig(
    use_deepsort=True,
    n_init=3  # More frames to confirm
)
```

---

## Extension Points

### Adding New Trackers

```python
class MyCustomTracker:
    def update_tracks(self, detections, frame) -> List[TrackData]:
        # Your tracking algorithm
        pass

# Use in monitor
monitor.tracker = MyCustomTracker()
```

### Adding New Visualization Modes

```python
def _create_heatmap_view(self, frame, tracks):
    # Your visualization logic
    pass

# Register in display_modes
self.display_modes['6'] = 'Heatmap View'
```

### Custom Alert Logic

```python
class MyOccupancyGrid(OccupancyGrid):
    def _update_alerts(self, dt):
        # Your custom alert logic
        pass
```

---

**This architecture provides a robust foundation for crowd monitoring with clear separation of concerns and multiple
extension points for future enhancements.**
