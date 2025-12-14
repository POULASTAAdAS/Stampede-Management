# 🔍 Code Walkthrough: Understanding the Implementation

This document walks through the actual code, explaining what each important piece does. Perfect for understanding how
theory becomes practice!

---

## 📋 Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [File-by-File Deep Dive](#file-by-file-deep-dive)
3. [Important Code Patterns](#important-code-patterns)
4. [Data Flow Examples](#data-flow-examples)
5. [Common Code Snippets Explained](#common-code-snippets-explained)

---

## 🏗️ System Architecture Overview

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      main.py                            │
│              (Entry Point & Orchestrator)               │
└───────────────────────┬─────────────────────────────────┘
                        │ creates & configures
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    monitor.py                           │
│                (Main Control Loop)                      │
│  ┌──────────────────────────────────��─────────────┐   │
│  │ While running:                                 │   │
│  │  1. Capture frame                              │   │
│  │  2. Detect people                              │   │
│  │  3. Track people                               │   │
│  │  4. Update grid                                │   │
│  │  5. Visualize                                  │   │
│  │  6. Handle input                               │   │
│  └────────────────────────────────────────────────┘   │
└────┬──────┬──────┬──────┬──────┬──────┬──────┬────────┘
     │      │      │      │      │      │      │
     ↓      ↓      ↓      ↓      ↓      ↓      ↓
┌─────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│det- │ │cali- │ │track-│ │geom- │ │occu- │ │visu- │ │config│
│ector│ │bra-  │ │ers   │ │etry  │ │pancy │ │alizer│ │      │
│.py  │ │tion  │ │.py   │ │.py   │ │.py   │ │.py   │ │.py   │
└─────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
```

### Data Flow

```
Camera Frame (numpy array)
        ↓
PersonDetector.detect_persons()
        ↓
List of bounding boxes: [[x1,y1,x2,y2,conf], ...]
        ↓
Tracker.update_tracks()
        ↓
List of TrackData objects: [TrackData(id=1, bbox=...), ...]
        ↓
OccupancyGrid.update()
        ↓
Grid with counts: [[1.2, 3.4], [2.1, 0.8], ...]
        ↓
MonitorVisualizer.create_visualization()
        ↓
Annotated frame (numpy array) → Display on screen
```

---

## 📄 File-by-File Deep Dive

### 1. main.py - Entry Point

#### Key Function: `parse_arguments()`

**What it does:** Reads command-line arguments and creates a configuration object.

**Code breakdown:**

```python
def parse_arguments() -> MonitoringConfig:
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Enhanced Crowd Monitoring System with Interactive Features",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Define arguments
    parser.add_argument("--source", type=str, default="0",
                        help="Video source (camera index or video file path)")
    # ... more arguments ...

    # Parse them
    args = parser.parse_args()

    # Create config object
    config = MonitoringConfig(
        source=args.source,
        model_path=args.model,
        # ... more settings ...
    )

    return config
```

**What's happening:**

1. `argparse` library reads command-line arguments
2. Each argument has a default value (e.g., `source="0"` means use camera 0)
3. All settings are packaged into a `MonitoringConfig` object
4. This config is passed to all other components

**Example usage:**

```bash
# Use defaults
python main.py

# Custom settings
python main.py --source video.mp4 --cell-width 3.0 --conf 0.5
```

#### Key Function: `main()`

**Code breakdown:**

```python
def main():
    try:
        # 1. Get configuration
        config = parse_arguments()

        # 2. Log startup info
        logger.info("=== Enhanced Crowd Monitoring System ===")
        logger.info(f"Video source: {config.source}")
        # ... more logging ...

        # 3. Create and initialize monitor
        monitor = CrowdMonitor(config)
        success = monitor.initialize()

        if success:
            logger.info("Monitoring completed successfully")
        else:
            logger.error("Monitoring failed to initialize")
            return 1

    except KeyboardInterrupt:
        logger.info("System interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"System error: {e}")
        return 1
    finally:
        # Always cleanup
        cv2.destroyAllWindows()

    return 0
```

**What's happening:**

1. **try block:** Normal execution path
2. **except KeyboardInterrupt:** User pressed Ctrl+C (handle gracefully)
3. **except Exception:** Any other error (log it)
4. **finally:** Always runs, even if error (cleanup resources)
5. **return codes:** 0 = success, 1 = error (Unix convention)

---

### 2. detector.py - People Detection

#### Key Class: `PersonDetector`

**Initialization:**

```python
class PersonDetector:
    def __init__(self, config: MonitoringConfig):
        self.config = config  # Store configuration
        self.model = None  # Will hold YOLO model
```

**Loading the model:**

```python
def load_model(self) -> bool:
    logger.info(f"Loading YOLO model: {self.config.model_path}")

    # Ensure model file exists (download if needed)
    if not download_yolo_model(self.config.model_path):
        logger.error("Failed to download YOLO model")
        return False

    try:
        # Load YOLO model
        self.model = YOLO(self.config.model_path)
        logger.info("YOLO model loaded successfully")
        return True
    except Exception as e:
        # If loading fails, try re-downloading
        logger.error(f"Failed to load YOLO model: {e}")
        logger.info("Attempting to re-download model...")

        # Remove corrupted file
        model_path = Path(self.config.model_path)
        if model_path.exists():
            model_path.unlink()  # Delete file

        # Try again
        if not download_yolo_model(self.config.model_path):
            return False

        try:
            self.model = YOLO(self.config.model_path)
            logger.info("YOLO model loaded successfully after re-download")
            return True
        except Exception as e2:
            logger.error(f"Failed even after re-download: {e2}")
            return False
```

**What's happening:**

- **First attempt:** Try to load existing model
- **Error handling:** If it fails, assume the file is corrupted
- **Retry logic:** Delete and re-download, then try again
- **Robust:** Won't crash if model file is missing or corrupted

#### Key Function: `detect_persons()`

**Code breakdown:**

```python
def detect_persons(self, frame: np.ndarray) -> List[List[float]]:
    # Safety check
    if self.model is None:
        logger.error("Model not loaded")
        return []

    try:
        # Run YOLO detection
        results = self.model(
            frame,  # Input image
            imgsz=640,  # Resize to 640×640 for processing
            conf=self.config.confidence_threshold,  # Minimum confidence
            classes=[0],  # Class 0 = person in COCO dataset
            verbose=False  # Don't print progress
        )

        detections = []
        h_img, w_img = frame.shape[:2]  # Get image dimensions

        # Process each result
        for result in results:
            if hasattr(result, 'boxes') and result.boxes is not None:
                for box in result.boxes:
                    try:
                        # Extract box coordinates
                        xyxy = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                    except Exception:
                        continue  # Skip if extraction fails

                    x1, y1, x2, y2 = map(float, xyxy)

                    # Clamp to image boundaries
                    x1 = max(0, min(w_img - 1, x1))
                    x2 = max(0, min(w_img - 1, x2))
                    y1 = max(0, min(h_img - 1, y1))
                    y2 = max(0, min(h_img - 1, y2))

                    # Validate box
                    if x2 <= x1 or y2 <= y1:
                        continue  # Invalid box

                    # Check minimum area
                    area = (x2 - x1) * (y2 - y1)
                    if area < self.config.min_bbox_area:
                        continue  # Too small (likely false positive)

                    # Add to results
                    detections.append([x1, y1, x2, y2, conf])

        logger.debug(f"Detected {len(detections)} persons")
        return detections

    except Exception as e:
        logger.error(f"Detection error: {e}")
        return []  # Return empty list on error
```

**What's happening:**

1. **Input:** Frame (numpy array, shape: height × width × 3)
2. **YOLO processing:** AI analyzes image, finds people
3. **Result extraction:** Get bounding box coordinates
4. **Validation:**
    - Clamp coordinates to image boundaries (prevent out-of-bounds)
    - Check box is valid (x2 > x1, y2 > y1)
    - Check minimum area (filter out tiny false detections)
5. **Output:** List of `[x1, y1, x2, y2, confidence]`

**Example output:**

```python
[
    [120.5, 80.3, 250.7, 480.2, 0.92],  # Person 1: 92% confidence
    [350.1, 100.8, 480.3, 500.1, 0.87],  # Person 2: 87% confidence
    [600.2, 150.4, 720.8, 520.6, 0.78]  # Person 3: 78% confidence
]
```

---

### 3. calibration.py - Camera Calibration

#### Key Function: `calibrate()`

**Code breakdown:**

```python
def calibrate(self, frame: np.ndarray) -> bool:
    try:
        # Step 1: Get 4 calibration points from user
        pts_img = self._get_calibration_points(frame)
        if pts_img is None:
            return False  # User cancelled

        # Step 2: Get real-world dimensions
        world_width, world_height = self._get_world_dimensions()
        if world_width is None or world_height is None:
            return False  # User cancelled

        # Step 3: Create world coordinate points
        # These form a rectangle in world coordinates
        pts_world = np.array([
            [0, 0],  # Top-left
            [world_width, 0],  # Top-right
            [world_width, world_height],  # Bottom-right
            [0, world_height]  # Bottom-left
        ], dtype=np.float32)

        # Step 4: Calculate transformation matrices
        H_matrix = cv2.getPerspectiveTransform(pts_img, pts_world)
        inv_H_matrix = cv2.getPerspectiveTransform(pts_world, pts_img)

        # Step 5: Store results
        self.geometry_processor = GeometryProcessor(H_matrix, inv_H_matrix)
        self.world_width = world_width
        self.world_height = world_height

        logger.info(f"Calibration completed: {world_width}x{world_height}m")
        return True

    except Exception as e:
        logger.error(f"Calibration failed: {e}")
        return False
```

**What's happening:**

1. **User clicks 4 points** on the camera image (corners of a known area)
2. **User types dimensions** (e.g., "10 meters × 8 meters")
3. **Math magic:** OpenCV creates transformation matrices
    - `H_matrix`: Image → World (pixels to meters)
    - `inv_H_matrix`: World → Image (meters to pixels)
4. **Result:** System can now convert between pixel and real-world coordinates

**Visual example:**

```
User clicks:               System creates:
┌─────────────┐           
│ *       *   │           [0,0]────[10,0]
│             │    →       │         │
│ *       *   │           [0,8]────[10,8]
└─────────────┘           
(pixels)                  (meters)
```

#### Interactive Calibration: `_get_calibration_points()`

**Code breakdown:**

```python
def _get_calibration_points(self, frame: np.ndarray) -> Optional[np.ndarray]:
    clicked_points = []  # Store clicked points

    # Define mouse callback
    def click_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button
            clicked_points.append((x, y))
            logger.info(f"Clicked point {len(clicked_points)}: ({x}, {y})")

    try:
        # Create window and set callback
        window_name = "Calibration - Click 4 corners"
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(window_name, click_callback)

        logger.info("Click 4 ground reference points in clockwise order")
        logger.info("Press 'c' to continue after 4 points, or 'ESC' to cancel")

        # Main display loop
        while True:
            display_frame = frame.copy()

            # Draw clicked points
            for i, point in enumerate(clicked_points):
                cv2.circle(display_frame, point, 8, (0, 255, 0), -1)  # Green dot
                cv2.circle(display_frame, point, 10, (255, 255, 255), 2)  # White outline
                cv2.putText(display_frame, f"{i + 1}",
                            (point[0] + 12, point[1] - 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Draw connecting lines
            if len(clicked_points) > 1:
                for i in range(len(clicked_points)):
                    next_i = (i + 1) % len(clicked_points)
                    if next_i < len(clicked_points):
                        cv2.line(display_frame, clicked_points[i],
                                 clicked_points[next_i], (0, 255, 255), 2)

            # Show frame
            cv2.imshow(window_name, display_frame)
            key = cv2.waitKey(1) & 0xFF

            # Check for completion or cancellation
            if key == ord('c') and len(clicked_points) >= 4:
                break  # User finished
            elif key == 27:  # ESC key
                logger.info("Calibration cancelled")
                cv2.destroyWindow(window_name)
                return None

        cv2.destroyWindow(window_name)

        # Return first 4 points
        if len(clicked_points) >= 4:
            return np.array(clicked_points[:4], dtype=np.float32)

    except Exception as e:
        logger.warning(f"GUI calibration failed: {e}")
        return self._manual_calibration_entry(frame)  # Fallback
```

**What's happening:**

1. **Window creation:** Display calibration frame
2. **Mouse callback:** Function called when user clicks
3. **Visual feedback:** Draw dots and lines as user clicks
4. **Instructions:** Show on-screen guidance
5. **Completion:** Wait for 'c' key or 4 points
6. **Fallback:** If GUI fails, use manual entry

---

### 4. trackers.py - Person Tracking

#### SimpleCentroidTracker - How It Works

**Initialization:**

```python
class SimpleCentroidTracker:
    def __init__(self, max_age: int = 30, distance_threshold: float = 80.0):
        self.next_id = 1  # Next available ID
        self.tracks: Dict[int, TrackData] = {}  # Current tracks
        self.max_age = max_age  # Max frames without detection
        self.distance_threshold = distance_threshold  # Max distance for matching
```

**Main tracking logic:**

```python
def update_tracks(self, detections: List[List[float]],
                  frame: Optional[np.ndarray] = None) -> List[TrackData]:
    # Case 1: No detections
    if not detections:
        self._age_tracks()  # Increment age of all tracks
        return list(self.tracks.values())

    # Case 2: Calculate centroids
    centroids = [(det, (det[0] + det[2]) / 2, (det[1] + det[3]) / 2)
                 for det in detections if len(det) >= 4]

    # Case 3: First frame (no existing tracks)
    if not self.tracks:
        self._create_initial_tracks(centroids)
    else:
        # Case 4: Match detections to existing tracks
        self._match_tracks_to_detections(centroids)

    # Case 5: Remove old tracks
    self._remove_old_tracks()

    return list(self.tracks.values())
```

**Matching algorithm:**

```python
def _match_tracks_to_detections(self, centroids):
    used_detections = set()  # Track which detections are matched

    # For each existing track
    for track_id, track in list(self.tracks.items()):
        best_match = None
        best_distance = float('inf')

        # Find closest detection
        for i, (det, cx, cy) in enumerate(centroids):
            if i in used_detections:
                continue  # Already matched

            # Calculate distance
            distance = math.sqrt(
                (track.world_position[0] - cx) ** 2 +
                (track.world_position[1] - cy) ** 2
            )

            # Update best match
            if distance < best_distance and distance < self.distance_threshold:
                best_distance = distance
                best_match = (i, det, cx, cy)

        # Update track if match found
        if best_match:
            i, det, cx, cy = best_match
            used_detections.add(i)

            track.bbox = (int(det[0]), int(det[1]), int(det[2]), int(det[3]))
            track.world_position = (cx, cy)
            track.confidence = det[4] if len(det) > 4 else 1.0
            track.age = 0  # Reset age
        else:
            track.age += 1  # No match, age the track

    # Create new tracks for unmatched detections
    for i, (det, cx, cy) in enumerate(centroids):
        if i not in used_detections:
            self.tracks[self.next_id] = TrackData(
                track_id=self.next_id,
                bbox=(int(det[0]), int(det[1]), int(det[2]), int(det[3])),
                world_position=(cx, cy),
                confidence=det[4] if len(det) > 4 else 1.0
            )
            self.next_id += 1
```

**What's happening:**

1. **For each existing track:** Find the closest new detection
2. **Distance calculation:** Euclidean distance between centroids
3. **Threshold check:** Only match if distance < threshold (80 pixels)
4. **Update matched tracks:** New position, reset age
5. **Age unmatched tracks:** Increment age counter
6. **Create new tracks:** For detections without matches
7. **Remove old tracks:** Delete tracks with age > max_age

**Visual example:**

```
Frame N:                    Frame N+1:
Track #1 at (100, 200)      Detection at (105, 203)
Track #2 at (300, 150)      Detection at (298, 148)
Track #3 at (500, 400)      Detection at (450, 350)
                            Detection at (600, 100) [NEW]

Matching:
Track #1 → (105, 203): distance = 5.8 → Match! (update position)
Track #2 → (298, 148): distance = 2.8 → Match! (update position)
Track #3 → (450, 350): distance = 70.7 → Match! (update position)
           (600, 100): distance = too far → New track #4
```

---

### 5. occupancy.py - Grid Management

#### Key Function: `update()`

**Code breakdown:**

```python
def update(self, tracks: List[TrackData], dt: float):
    # Initialize counts for this frame
    current_counts = np.zeros_like(self.ema_counts)

    # For each tracked person
    for track in tracks:
        # Convert bounding box to world coordinates (polygon)
        polygon, _ = self.geometry_processor.project_bbox_to_world(track.bbox)
        if polygon is None or polygon.area <= 1e-6:
            continue  # Skip invalid polygons

        # Get bounding box of polygon in world coordinates
        minx, miny, maxx, maxy = polygon.bounds

        # Calculate which grid cells this polygon might overlap
        min_col = max(0, int(minx // self.config.cell_width))
        max_col = min(self.grid_cols - 1, int(maxx // self.config.cell_width))
        min_row = max(0, int(miny // self.config.cell_height))
        max_row = min(self.grid_rows - 1, int(maxy // self.config.cell_height))

        # Check each potentially overlapping cell
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                # Create cell polygon
                cell_polygon = shapely_box(
                    col * self.config.cell_width,
                    row * self.config.cell_height,
                    (col + 1) * self.config.cell_width,
                    (row + 1) * self.config.cell_height
                )

                try:
                    # Calculate intersection
                    intersection = polygon.intersection(cell_polygon)
                    if not intersection.is_empty:
                        # Calculate overlap fraction
                        overlap_fraction = intersection.area / polygon.area
                        # Add to cell count (clamped to [0, 1])
                        current_counts[row, col] += max(0.0, min(1.0, overlap_fraction))
                except Exception:
                    # Fallback: add small amount
                    current_counts[row, col] += 0.1

    # Apply exponential moving average
    self.ema_counts = (self.config.ema_alpha * current_counts +
                       (1.0 - self.config.ema_alpha) * self.ema_counts)

    # Update alerts
    self._update_alerts(dt)
```

**What's happening:**

1. **Initialize:** Create empty count array
2. **For each person:**
    - Convert bounding box to world coordinate polygon
    - Find which cells it might overlap
    - Calculate exact intersection with each cell
    - Add fractional count based on overlap
3. **Smoothing:** Apply EMA to prevent flickering
4. **Alerts:** Check for overcrowding

**Visual example:**

```
Person spans 2 cells:
┌────────┬────────┐
│ 30%    │ 70%    │  Person's area: 100%
│   ╔════╪════╗   │  Cell 1 overlap: 30%
│   ║XXXX│XXXX║   │  Cell 2 overlap: 70%
│   ╚════╪════╝   │
└────────┴────────┘
Count updates:
cell[0] += 0.3
cell[1] += 0.7
```

#### Alert Logic: `_update_alerts()`

**Code breakdown:**

```python
def _update_alerts(self, dt: float):
    for row in range(self.grid_rows):
        for col in range(self.grid_cols):
            # Check if overcapacity
            if self.ema_counts[row, col] > self.cell_capacity:
                self.timers[row, col] += dt  # Increment timer
            else:
                self.timers[row, col] = max(0.0, self.timers[row, col] - dt)  # Decrement

            # Trigger alert if overcrowded for long enough
            if (self.timers[row, col] >= self.config.hysteresis_time and
                    not self.notified[row, col]):
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                logger.warning(
                    f"OVERCAPACITY ALERT - Cell ({row},{col}) "
                    f"occupancy: {self.ema_counts[row, col]:.2f}/{self.cell_capacity} "
                    f"at {timestamp}"
                )
                self.notified[row, col] = True

            # Clear alert when occupancy drops
            if (self.notified[row, col] and
                    self.ema_counts[row, col] <= max(0, self.cell_capacity - 0.5)):
                logger.info(f"Alert cleared for cell ({row},{col})")
                self.notified[row, col] = False
```

**What's happening:**

1. **Timer logic:**
    - Overcrowded: timer increases
    - Normal: timer decreases
2. **Hysteresis:** Only alert if overcrowded for `hysteresis_time` seconds (default: 3s)
3. **Alert trigger:** Log warning message, set flag
4. **Alert clear:** When occupancy drops below threshold, clear flag

**Timeline example:**

```
Time:  0s   1s   2s   3s   4s   5s   6s
Count: 5 → 6 → 6 → 6 → 5 → 4 → 4
       │    │    │    │    │    └─ Alert cleared
       │    │    │    └─ ALERT!
       └─ Timer starts (capacity = 5)
```

---

### 6. monitor.py - Main Control Loop

#### The Main Loop: `_process_video_stream()`

**Code breakdown:**

```python
def _process_video_stream(self, cap: cv2.VideoCapture):
    logger.info("Starting interactive video processing loop")

    last_time = time.time()
    show_fps = False

    try:
        while True:
            # 1. Read frame
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to read frame, ending processing")
                break

            self.frame_count += 1
            current_time = time.time()
            dt = current_time - last_time  # Time delta
            last_time = current_time

            # 2. Update FPS tracking
            self.fps_counter.append(current_time)
            if len(self.fps_counter) > 30:
                self.fps_counter.pop(0)  # Keep only last 30

            # 3. Process frame (detect + track)
            tracks = self._process_frame(frame)

            # 4. Update occupancy (only in monitoring modes)
            if self.current_mode in ['4', '5']:
                self.occupancy_grid.update(tracks, dt)

            # 5. Generate visualization
            display_frame = self._create_visualization(frame, tracks, show_fps)

            # 6. Display
            window_title = f"Enhanced Crowd Monitor - {self.display_modes[self.current_mode]}"
            cv2.imshow(window_title, display_frame)

            # 7. Handle keyboard input
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                logger.info("User requested quit")
                break
            elif key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5')]:
                self._handle_mode_switch(chr(key))
            elif key == ord('s') and self.config.enable_screenshots:
                self._save_screenshot(display_frame)
            elif key == ord('g') and self.config.enable_grid_adjustment:
                self._toggle_grid_size()
            elif key == ord('r'):
                self._reset_grid_size()
            elif key == ord('f'):
                show_fps = not show_fps
                logger.info(f"FPS display: {'ON' if show_fps else 'OFF'}")

    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
    except Exception as e:
        logger.error(f"Error in video processing loop: {e}")
```

**What's happening:**

1. **Frame capture:** Read from camera
2. **Time tracking:** Calculate time delta (dt) for smooth updates
3. **Processing:** Detect → Track → Update grid
4. **Visualization:** Create display based on current mode
5. **Display:** Show on screen
6. **Input handling:** Check for key presses
7. **Loop control:** Continue until quit or error

---

## 🎯 Important Code Patterns

### Pattern 1: Error Handling with Try-Except

**Good example from the codebase:**

```python
try:
    # Try to do something
    result = risky_operation()
    return result
except SpecificException as e:
    # Handle specific error
    logger.error(f"Specific error: {e}")
    return fallback_value
except Exception as e:
    # Catch-all for unexpected errors
    logger.error(f"Unexpected error: {e}")
    return safe_default
finally:
    # Always runs (cleanup)
    cleanup_resources()
```

**Why this matters:**

- Prevents crashes from unexpected errors
- Provides fallback behavior
- Logs errors for debugging
- Ensures cleanup happens

### Pattern 2: Configuration Objects

**Instead of:**

```python
def initialize(cell_width, cell_height, person_radius, detect_every,
               confidence_threshold, min_bbox_area, ...):  # Too many parameters!
    pass
```

**Use:**

```python
@dataclass
class MonitoringConfig:
    cell_width: float = 1.0
    cell_height: float = 1.0
    person_radius: float = 2
    # ... all settings ...


def initialize(config: MonitoringConfig):  # One parameter!
    pass
```

**Benefits:**

- Fewer function parameters
- Easy to add new settings
- Clear default values
- Type checking

### Pattern 3: Type Hints

**Examples from the code:**

```python
def detect_persons(self, frame: np.ndarray) -> List[List[float]]:
    # Input type: numpy array
    # Output type: list of lists of floats
    pass


def world_to_image_point(self, world_x: float, world_y: float) -> Tuple[int, int]:
    # Inputs: two floats
    # Output: tuple of two ints
    pass
```

**Benefits:**

- IDE autocomplete works better
- Catches type errors early
- Self-documenting code
- Helps other developers

### Pattern 4: Defensive Programming

**Always validate inputs:**

```python
# Check for None
if self.model is None:
    logger.error("Model not loaded")
    return []

# Check bounds
x1 = max(0, min(w_img - 1, x1))  # Clamp to [0, w_img-1]

# Validate ranges
if x2 <= x1 or y2 <= y1:
    continue  # Skip invalid box

# Check for empty
if not detections:
    return []  # Early return
```

**Why:**

- Prevents crashes from bad data
- Makes code more robust
- Easier to debug

### Pattern 5: Logging Levels

**Usage in the code:**

```python
logger.debug(f"Detected {len(detections)} persons")  # Detailed info
logger.info("System started")  # Normal info
logger.warning("Model file appears corrupted")  # Something's wrong but not critical
logger.error("Failed to load model")  # Error occurred
```

**When to use each:**

- **DEBUG:** Detailed diagnostic info (usually disabled)
- **INFO:** Normal operational messages
- **WARNING:** Unexpected but handled situations
- **ERROR:** Errors that prevent functionality

---

## 📊 Data Flow Examples

### Example 1: Single Person Detection → Tracking → Grid Update

```python
# Step 1: Detection
frame = np.array([...])  # 1280×720×3 image
detections = detector.detect_persons(frame)
# Result: [[320, 180, 480, 650, 0.87]]
#          └─ x1  y1   x2   y2   confidence

# Step 2: Tracking
tracks = tracker.update_tracks(detections, frame)
# Result: [TrackData(
#     track_id=17,
#     bbox=(320, 180, 480, 650),
#     world_position=(400, 415),  # Centroid
#     confidence=0.87,
#     age=0
# )]

# Step 3: Geometry conversion
polygon, _ = geometry.project_bbox_to_world(tracks[0].bbox)
# Result: Polygon with coordinates in meters
#         [(2.5, 1.8), (3.5, 1.8), (3.5, 4.2), (2.5, 4.2)]

# Step 4: Grid update
occupancy_grid.update(tracks, dt=0.033)  # 30 FPS = 0.033s per frame
# Updates grid cells that overlap with polygon
# cell[1][2] += 0.7  (70% overlap)
# cell[1][3] += 0.3  (30% overlap)
```

### Example 2: Overcrowding Detection

```python
# Initial state
cell_capacity = 4
ema_counts[2][3] = 3.5  # Normal
timers[2][3] = 0.0
notified[2][3] = False

# Frame 1: More people enter
current_counts[2][3] = 5.2
ema_counts[2][3] = 0.4 * 5.2 + 0.6 * 3.5 = 4.18
timers[2][3] += 0.033  # 4.18 > 4, so timer increases

# Frame 2-90: Still crowded (3 seconds @ 30 FPS)
# ... timer increases to 3.0 ...

# Frame 91: Alert triggered!
if timers[2][3] >= 3.0 and not notified[2][3]:
    logger.warning("OVERCAPACITY ALERT - Cell (2,3)")
    notified[2][3] = True

# Frame 150: People leave
current_counts[2][3] = 2.1
ema_counts[2][3] = 0.4 * 2.1 + 0.6 * 4.18 = 3.35

# Frame 200: Alert cleared
if notified[2][3] and ema_counts[2][3] <= 3.5:
    logger.info("Alert cleared for cell (2,3)")
    notified[2][3] = False
```

---

## 🔧 Common Code Snippets Explained

### Snippet 1: OpenCV Key Handling

```python
key = cv2.waitKey(1) & 0xFF
```

**What's happening:**

- `cv2.waitKey(1)`: Wait 1 millisecond for key press
- Returns key code (or -1 if no key pressed)
- `& 0xFF`: Mask to get only last 8 bits (handles platform differences)

**Example:**

```python
key = cv2.waitKey(1) & 0xFF
if key == ord('q'):  # ord('q') = 113
    break
elif key == ord('s'):  # ord('s') = 115
    save_screenshot()
```

### Snippet 2: NumPy Array Indexing

```python
frame.shape[:2]  # Get (height, width)
```

**What's happening:**

- `frame.shape` returns `(height, width, channels)` e.g., `(720, 1280, 3)`
- `[:2]` takes first 2 elements: `(720, 1280)`

**Common patterns:**

```python
h, w = frame.shape[:2]  # Unpack height and width
h, w, c = frame.shape  # Unpack all three
frame[:, :, 0]  # Get blue channel (BGR format)
```

### Snippet 3: List Comprehension

```python
centroids = [(det, (det[0] + det[2]) / 2, (det[1] + det[3]) / 2)
             for det in detections if len(det) >= 4]
```

**Equivalent to:**

```python
centroids = []
for det in detections:
    if len(det) >= 4:
        cx = (det[0] + det[2]) / 2  # Center X
        cy = (det[1] + det[3]) / 2  # Center Y
        centroids.append((det, cx, cy))
```

**Benefits:**

- More concise
- Faster execution
- Pythonic style

### Snippet 4: Context Managers (with statement)

**Not used in this codebase, but good to know:**

```python
with open('file.txt', 'r') as f:
    content = f.read()
# File automatically closed, even if error occurs
```

**Video capture equivalent:**

```python
cap = cv2.VideoCapture(0)
try:
    # Use cap
    pass
finally:
    cap.release()  # Always release
```

---

## 🎓 Summary

Key takeaways from the code:

1. **Modular design:** Each file has a single responsibility
2. **Error handling:** Comprehensive try-except blocks prevent crashes
3. **Type hints:** Make code self-documenting and catch errors early
4. **Configuration objects:** Simplify function signatures
5. **Logging:** Track what's happening for debugging
6. **Defensive programming:** Validate inputs, check bounds
7. **Performance optimization:** Skip frames, use efficient algorithms

The codebase follows Python best practices and is designed to be:

- **Robust:** Handles errors gracefully
- **Maintainable:** Clear structure and documentation
- **Extensible:** Easy to add new features
- **Beginner-friendly:** Clear variable names and comments

---

**Happy coding!** 🚀
