# System Architecture

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                           main.py                                │
│                    (Entry Point & CLI)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         monitor.py                               │
│                   (System Orchestrator)                          │
│  • Initializes all components                                    │
│  • Manages video processing loop                                 │
│  • Handles user interactions                                     │
└───┬────────────┬─────────────┬────────────┬──────────────┬──────┘
    │            │             │            │              │
    ▼            ▼             ▼            ▼              ▼
┌────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐
│detector│  │trackers  │  │occupancy│  │visualizer│  │calibration│
│  .py   │  │  .py     │  │  .py    │  │   .py    │  │   .py    │
└────────┘  └──────────┘  └─────────┘  └──────────┘  └──────────┘
    │            │             │            │              │
    │            │             ▼            │              ▼
    │            │         ┌─────────┐      │          ┌─────────┐
    │            │         │geometry │◄─────┴──────────│geometry │
    │            │         │  .py    │                 │  .py    │
    │            │         └─────────┘                 └─────────┘
    │            │             ▲
    │            │             │
    ▼            ▼             │
┌────────────────────────────────────────┐
│           config.py                    │
│  • MonitoringConfig                    │
│  • TrackData                           │
└────────────────────────────────────────┘
```

## Data Flow

```
Camera Feed ──────────────────────────────────────────────┐
                                                           │
                                                           ▼
                                                    ┌──────────────┐
                                                    │  monitor.py  │
                                                    └──────┬───────┘
                                                           │
                        ┌──────────────────────────────────┼────────────────────────┐
                        │                                  │                        │
                        ▼                                  ▼                        ▼
              ┌─────────────────┐              ┌──────────────────┐     ┌──────────────────┐
              │  detector.py    │              │   trackers.py    │     │ calibration.py   │
              │  (YOLO Model)   │              │  (Centroid/DS)   │     │  (Perspective)   │
              └────────┬────────┘              └────────┬─────────┘     └────────┬─────────┘
                       │                                │                        │
                       │ Detections                     │ Tracks                 │ Transform
                       │ [x1,y1,x2,y2,conf]            │ TrackData[]            │ Matrices
                       │                                │                        │
                       └────────────────┬───────────────┘                        │
                                        │                                        │
                                        ▼                                        │
                              ┌──────────────────┐                               │
                              │  occupancy.py    │◄──────────────────────────────┘
                              │  (Grid Manager)  │
                              └────────┬─────────┘
                                       │
                                       │ Occupancy Data
                                       │ Alert Status
                                       │
                                       ▼
                              ┌──────────────────┐
                              │  visualizer.py   │
                              │  (Rendering)     │
                              └────────┬─────────┘
                                       │
                                       │ Display Frames
                                       │
                                       ▼
                                   User Display
```

## Module Responsibilities

### 1. Configuration Layer (`config.py`)

**Purpose**: Centralized configuration and data structures

**Components**:

- `MonitoringConfig`: System-wide settings
- `TrackData`: Track information container

**Dependencies**: None (base layer)

---

### 2. Logging Layer (`logger_config.py`)

**Purpose**: Centralized logging configuration

**Features**:

- Console output
- File logging
- Configurable log levels

**Dependencies**: None (base layer)

---

### 3. Geometry Layer (`geometry.py`)

**Purpose**: Coordinate transformations

**Key Class**: `GeometryProcessor`

**Methods**:

- `project_bbox_to_world()`: Image → World coordinates
- `world_to_image_point()`: World → Image coordinates

**Dependencies**:

- OpenCV (perspective transforms)
- Shapely (polygon operations)

---

### 4. Detection Layer (`detector.py`)

**Purpose**: Person detection using YOLO

**Key Class**: `PersonDetector`

**Methods**:

- `load_model()`: Initialize YOLO model
- `detect_persons()`: Detect people in frame

**Output**: List of `[x1, y1, x2, y2, confidence]`

**Dependencies**:

- Ultralytics YOLO
- Config

---

### 5. Tracking Layer (`trackers.py`)

**Purpose**: Multi-object tracking

**Classes**:

- `SimpleCentroidTracker`: Fast centroid matching
- `DeepSortTracker`: Appearance-based tracking

**Input**: Detections `[x1, y1, x2, y2, conf]`

**Output**: List of `TrackData` objects

**Algorithm** (Centroid):

1. Calculate centroids of detections
2. Match to existing tracks by distance
3. Create new tracks for unmatched
4. Age out old tracks

---

### 6. Calibration Layer (`calibration.py`)

**Purpose**: Camera perspective calibration

**Key Class**: `CameraCalibrator`

**Workflow**:

1. User clicks 4 ground points
2. User enters real-world dimensions
3. Calculate homography matrix
4. Create `GeometryProcessor`

**Dependencies**:

- OpenCV (GUI, homography)
- Geometry

---

### 7. Occupancy Layer (`occupancy.py`)

**Purpose**: Grid-based crowd density monitoring

**Key Class**: `OccupancyGrid`

**Features**:

- Dynamic grid sizing
- Polygon intersection for accurate counting
- Exponential Moving Average (EMA) smoothing
- Alert system with hysteresis

**Algorithm**:

1. Project track bboxes to world coords
2. Calculate intersection with each grid cell
3. Update counts with EMA smoothing
4. Check capacity thresholds
5. Trigger/clear alerts

**Dependencies**:

- Geometry (coordinate transforms)
- Shapely (polygon intersection)
- Config

---

### 8. Visualization Layer (`visualizer.py`)

**Purpose**: All rendering operations

**Key Class**: `MonitorVisualizer`

**Display Modes**:

1. **Raw Camera**: Unprocessed feed
2. **Grid Overlay**: Camera + grid lines
3. **Detection View**: Bounding boxes + IDs
4. **Monitoring View**: Full system (grid + occupancy + alerts)
5. **Split View**: Quad-split with bird's eye

**Methods**:

- `draw_grid_overlay()`: Grid lines on camera view
- `draw_track_annotation()`: Bounding boxes + info
- `draw_cell_occupancy_overlay()`: Occupancy numbers
- `create_birdseye_view()`: Top-down heatmap
- `create_info_panel()`: Statistics panel

**Dependencies**:

- OpenCV (drawing)
- Geometry, Occupancy (data)

---

### 9. Monitor Layer (`monitor.py`)

**Purpose**: System orchestration

**Key Class**: `CrowdMonitor`

**Responsibilities**:

- Initialize all components
- Manage video capture
- Processing loop coordination
- User interaction handling
- Mode switching

**Processing Loop**:

```python
while True:
    frame = capture_frame()
    detections = detector.detect(frame)
    tracks = tracker.update(detections)
    occupancy.update(tracks)
    display = visualizer.render(frame, tracks)
    handle_user_input()
```

**Dependencies**: All other modules

---

### 10. Entry Point (`main.py`)

**Purpose**: Application startup

**Responsibilities**:

- Parse CLI arguments
- Create configuration
- Initialize monitor
- Handle cleanup

---

## Interaction Patterns

### Initialization Sequence

```
main.py
  └─> parse_arguments()
  └─> create MonitoringConfig
  └─> create CrowdMonitor(config)
       └─> create PersonDetector
       └─> load YOLO model
       └─> initialize video capture
       └─> create CameraCalibrator
       └─> perform calibration
            └─> create GeometryProcessor
       └─> create OccupancyGrid
       └─> create tracker (Centroid/DeepSort)
       └─> create MonitorVisualizer
       └─> start processing loop
```

### Frame Processing Sequence

```
1. Capture frame from camera
2. detector.detect_persons(frame) → detections
3. tracker.update_tracks(detections) → tracks
4. occupancy.update(tracks) → grid state + alerts
5. visualizer.render() → display frame
6. cv2.imshow() → show to user
7. handle_user_input() → mode switching, screenshots, etc.
```

### Coordinate Transform Flow

```
Camera Image (pixels)
    │
    ▼ (calibration)
Homography Matrix
    │
    ▼ (geometry.project_bbox_to_world)
World Coordinates (meters)
    │
    ▼ (occupancy.update)
Grid Cell Assignment
    │
    ▼ (geometry.world_to_image_point)
Back to Image for Display
```

## Extension Points

### Adding New Trackers

1. Create class in `trackers.py`
2. Implement `update_tracks()` method
3. Return `List[TrackData]`
4. Register in `monitor._initialize_tracker()`

### Adding New Display Modes

1. Add mode to `monitor.display_modes` dict
2. Implement `_create_[mode]_view()` method
3. Add visualization logic in `visualizer.py`

### Adding New Alert Types

1. Extend `occupancy.OccupancyGrid`
2. Add alert logic in `_update_alerts()`
3. Update visualization in `visualizer.py`

### Adding New Detectors

1. Create class in `detector.py`
2. Implement `detect_persons()` method
3. Return detections in standard format
4. Update `monitor.py` initialization

## Performance Considerations

### Bottlenecks

1. **YOLO Detection**: Most expensive operation
    - Mitigate: Adjust `detect_every` parameter

2. **Polygon Intersection**: CPU-intensive for many cells
    - Mitigate: Reduce grid resolution

3. **Video Rendering**: Multiple overlays
    - Mitigate: Use simpler display modes

### Optimization Strategies

- Detection frequency control (`detect_every`)
- Grid size tuning
- Simple vs DeepSort tracking
- Lightweight YOLO models (yolov8n vs yolov8x)

## Testing Strategy

### Unit Tests

- `geometry.py`: Coordinate transformations
- `trackers.py`: Track matching logic
- `occupancy.py`: Grid calculations
- `detector.py`: Detection filtering

### Integration Tests

- Full pipeline with sample video
- Calibration workflow
- Mode switching
- Alert triggering

### Performance Tests

- FPS benchmarking
- Memory usage profiling
- Long-running stability
