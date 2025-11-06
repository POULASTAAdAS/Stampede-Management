import argparse
import logging
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
from shapely.geometry import Polygon, box as shapely_box
from ultralytics import YOLO

# Configure logging with ASCII-safe formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('crowd_monitor.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Import DeepSort with comprehensive error handling
try:
    from deep_sort_realtime.deepsort_tracker import DeepSort

    DEEPSORT_AVAILABLE = True
    logger.info("DeepSort successfully imported")
except ImportError as e:
    logger.warning(f"DeepSort not available: {e}")
    logger.info("Install with: pip install deep-sort-realtime")
    DEEPSORT_AVAILABLE = False
    DeepSort = None


@dataclass
class MonitoringConfig:
    """Configuration class for crowd monitoring system"""
    # Video source settings
    source: Union[str, int] = "0"
    model_path: str = "yolov8n.pt"

    # Grid and spatial settings
    cell_width: float = 10.0
    cell_height: float = 10.0
    person_radius: float = 0.06  # TODO manage number of people
    person_threshold: int = -1

    # Detection settings
    detect_every: int = 5
    confidence_threshold: float = 0.35
    min_bbox_area: int = 1500

    # Tracking settings
    use_deepsort: bool = False
    max_age: int = 80
    n_init: int = 1

    # Smoothing and alert settings
    ema_alpha: float = 0.4
    fps: float = 15.0
    hysteresis_time: float = 3.0

    # Visualization settings
    max_birdseye_pixels: int = 900
    grid_line_thickness: int = 2
    bbox_thickness: int = 3

    # Interactive features
    enable_screenshots: bool = True
    enable_grid_adjustment: bool = True


@dataclass
class TrackData:
    """Data structure for tracking information"""
    track_id: int
    bbox: Tuple[int, int, int, int]
    world_position: Tuple[float, float]
    confidence: float = 1.0
    age: int = 0
    confirmed: bool = True


def download_yolo_model(model_name: str) -> bool:
    """Download YOLO model if it doesn't exist or is corrupted"""
    model_path = Path(model_name)

    # Check if model exists and is valid
    if model_path.exists():
        try:
            # Quick validation - check file size
            if model_path.stat().st_size > 1000000:  # At least 1MB
                logger.info(f"Using existing model: {model_name}")
                return True
            else:
                logger.warning(f"Model file {model_name} appears corrupted (too small)")
        except Exception as e:
            logger.warning(f"Error checking model file: {e}")

    logger.info(f"Downloading YOLO model: {model_name}")

    try:
        # Let YOLO handle the download automatically
        YOLO(model_name)
        logger.info(f"Model {model_name} downloaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to download model {model_name}: {e}")
        return False


class GeometryProcessor:
    """Handles geometric transformations and calculations"""

    def __init__(self, homography_matrix: np.ndarray, inverse_homography: np.ndarray):
        self.H_matrix = homography_matrix
        self.inv_H_matrix = inverse_homography

    def project_bbox_to_world(self, bbox: Tuple[int, int, int, int]) -> Tuple[Optional[Polygon], Optional[np.ndarray]]:
        """Project bbox from image coordinates to world coordinates"""
        try:
            x1, y1, x2, y2 = bbox
            corners = np.array([[[x1, y1], [x2, y1], [x2, y2], [x1, y2]]], dtype=np.float32)
            world_points = cv2.perspectiveTransform(corners, self.H_matrix)[0]

            polygon = Polygon([(float(p[0]), float(p[1])) for p in world_points])
            return polygon, world_points
        except Exception as e:
            logger.warning(f"Failed to project bbox to world: {e}")
            return None, None

    def world_to_image_point(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to image coordinates"""
        try:
            point = np.array([[[float(world_x), float(world_y)]]], dtype=np.float32)
            image_point = cv2.perspectiveTransform(point, self.inv_H_matrix)[0, 0]
            return int(image_point[0]), int(image_point[1])
        except Exception as e:
            logger.warning(f"Failed to convert world to image point: {e}")
            return 0, 0


class SimpleCentroidTracker:
    """Optimized centroid-based tracker with better performance"""

    def __init__(self, max_age: int = 30, distance_threshold: float = 80.0):
        self.next_id = 1
        self.tracks: Dict[int, TrackData] = {}
        self.max_age = max_age
        self.distance_threshold = distance_threshold

    def update_tracks(self, detections: List[List[float]], frame: Optional[np.ndarray] = None) -> List[TrackData]:
        """Update tracks with new detections using optimized algorithm"""
        if not detections:
            self._age_tracks()
            return list(self.tracks.values())

        # Extract centroids efficiently
        centroids = [(det, (det[0] + det[2]) / 2, (det[1] + det[3]) / 2)
                     for det in detections if len(det) >= 4]

        if not self.tracks:
            # Initialize tracks for first frame
            self._create_initial_tracks(centroids)
        else:
            # Match existing tracks to detections
            self._match_tracks_to_detections(centroids)

        self._remove_old_tracks()
        return list(self.tracks.values())

    def _create_initial_tracks(self, centroids: List[Tuple[List[float], float, float]]):
        """Create initial tracks for first frame"""
        for det, cx, cy in centroids:
            self.tracks[self.next_id] = TrackData(
                track_id=self.next_id,
                bbox=(int(det[0]), int(det[1]), int(det[2]), int(det[3])),
                world_position=(cx, cy),
                confidence=det[4] if len(det) > 4 else 1.0
            )
            self.next_id += 1

    def _match_tracks_to_detections(self, centroids: List[Tuple[List[float], float, float]]):
        """Match existing tracks to new detections using Hungarian algorithm approximation"""
        used_detections = set()

        # Simple greedy matching - could be improved with Hungarian algorithm for better performance
        for track_id, track in list(self.tracks.items()):
            best_match = None
            best_distance = float('inf')

            for i, (det, cx, cy) in enumerate(centroids):
                if i in used_detections:
                    continue

                # Calculate Euclidean distance
                distance = math.sqrt(
                    (track.world_position[0] - cx) ** 2 +
                    (track.world_position[1] - cy) ** 2
                )

                if distance < best_distance and distance < self.distance_threshold:
                    best_distance = distance
                    best_match = (i, det, cx, cy)

            if best_match:
                i, det, cx, cy = best_match
                used_detections.add(i)

                # Update track
                track.bbox = (int(det[0]), int(det[1]), int(det[2]), int(det[3]))
                track.world_position = (cx, cy)
                track.confidence = det[4] if len(det) > 4 else 1.0
                track.age = 0
            else:
                track.age += 1

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

    def _age_tracks(self):
        """Age all tracks when no detections are available"""
        for track in self.tracks.values():
            track.age += 1

    def _remove_old_tracks(self):
        """Remove tracks that are too old"""
        expired_tracks = [track_id for track_id, track in self.tracks.items()
                          if track.age > self.max_age]
        for track_id in expired_tracks:
            del self.tracks[track_id]


class DeepSortTracker:
    """Wrapper for DeepSort tracker with error handling"""

    def __init__(self, max_age: int = 30, n_init: int = 1):
        if not DEEPSORT_AVAILABLE:
            raise ImportError("DeepSort is not available")

        try:
            self.tracker = DeepSort(max_age=max_age, n_init=n_init)
            logger.info("DeepSort tracker initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DeepSort: {e}")
            raise

    def update_tracks(self, detections: List[List[float]], frame: Optional[np.ndarray] = None) -> List[TrackData]:
        """Update tracks using DeepSort"""
        try:
            if not detections:
                tracks = self.tracker.update_tracks([], frame=frame)
            else:
                # Format detections for DeepSort (x, y, w, h, confidence)
                formatted_detections = []
                for det in detections:
                    if len(det) >= 4:
                        x1, y1, x2, y2 = det[:4]
                        w, h = x2 - x1, y2 - y1
                        conf = det[4] if len(det) > 4 else 0.9
                        if w > 0 and h > 0:
                            formatted_detections.append([float(x1), float(y1), float(w), float(h), float(conf)])

                tracks = self.tracker.update_tracks(formatted_detections, frame=frame)

            # Convert to TrackData format
            track_data_list = []
            for track in tracks:
                if hasattr(track, 'is_confirmed') and not track.is_confirmed():
                    continue

                track_id = getattr(track, 'track_id', None)
                if track_id is None:
                    continue

                # Get bounding box
                bbox = self._extract_bbox(track)
                if bbox is None:
                    continue

                x1, y1, x2, y2 = bbox
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

                track_data_list.append(TrackData(
                    track_id=track_id,
                    bbox=bbox,
                    world_position=(cx, cy),
                    confidence=1.0
                ))

            return track_data_list

        except Exception as e:
            logger.error(f"DeepSort tracking error: {e}")
            return []

    def _extract_bbox(self, track) -> Optional[Tuple[int, int, int, int]]:
        """Extract bounding box from track object"""
        try:
            if hasattr(track, 'to_tlbr'):
                tlbr = track.to_tlbr()
                return int(tlbr[0]), int(tlbr[1]), int(tlbr[2]), int(tlbr[3])
            elif hasattr(track, 'to_ltrb'):
                ltrb = track.to_ltrb()
                return int(ltrb[0]), int(ltrb[1]), int(ltrb[2]), int(ltrb[3])
            elif hasattr(track, 'to_ltwh'):
                ltwh = track.to_ltwh()
                x1, y1, w, h = ltwh
                return int(x1), int(y1), int(x1 + w), int(y1 + h)
            elif hasattr(track, 'bbox'):
                bbox = track.bbox
                if len(bbox) == 4:
                    return tuple(map(int, bbox))
        except Exception as e:
            logger.warning(f"Failed to extract bbox: {e}")

        return None


class EnhancedCrowdMonitor:
    """Enhanced crowd monitoring system with interactive features"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.geometry_processor: Optional[GeometryProcessor] = None
        self.tracker: Union[SimpleCentroidTracker, DeepSortTracker, None] = None
        self.model: Optional[YOLO] = None

        # Grid and capacity settings
        self.grid_rows = 0
        self.grid_cols = 0
        self.cell_capacity = 0
        self.world_width = 0.0
        self.world_height = 0.0
        self.original_cell_width = config.cell_width
        self.original_cell_height = config.cell_height

        # Runtime state
        self.ema_counts: Optional[np.ndarray] = None
        self.timers: Optional[np.ndarray] = None
        self.notified: Optional[np.ndarray] = None

        # Performance tracking
        self.frame_count = 0
        self.last_detection_frame = -1
        self.fps_counter = []
        self.fps_start_time = time.time()

        # Interactive display modes
        self.display_modes = {
            '1': 'Raw Camera',
            '2': 'Grid Overlay',
            '3': 'Detection View',
            '4': 'Monitoring View',
            '5': 'Split View'
        }
        self.current_mode = '4'  # Start with monitoring view

        # Camera dimensions
        self.camera_width = 0
        self.camera_height = 0

    def initialize(self) -> bool:
        """Initialize all components of the monitoring system"""
        try:
            logger.info("Initializing Enhanced Crowd Monitoring System...")

            # Download and load YOLO model
            logger.info(f"Loading YOLO model: {self.config.model_path}")

            # Ensure model is available
            if not download_yolo_model(self.config.model_path):
                logger.error("Failed to download YOLO model")
                return False

            # Load the model with error handling
            try:
                self.model = YOLO(self.config.model_path)
                logger.info("YOLO model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}")
                logger.info("Attempting to re-download model...")

                # Remove corrupted model file
                model_path = Path(self.config.model_path)
                if model_path.exists():
                    model_path.unlink()

                # Force re-download
                if not download_yolo_model(self.config.model_path):
                    return False

                try:
                    self.model = YOLO(self.config.model_path)
                    logger.info("YOLO model loaded successfully after re-download")
                except Exception as e2:
                    logger.error(f"Failed to load YOLO model even after re-download: {e2}")
                    return False

            # Initialize video capture with fallback
            cap = self._initialize_video_capture_with_fallback()
            if cap is None:
                return False

            # Get camera properties
            self.camera_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.camera_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            logger.info(f"Camera resolution: {self.camera_width}x{self.camera_height}")

            # Perform calibration
            ret, frame = cap.read()
            if not ret:
                logger.error("Cannot read from video source")
                cap.release()
                return False

            success = self._perform_calibration(frame)
            if not success:
                cap.release()
                return False

            # Initialize tracker
            self._initialize_tracker()

            # Show controls
            self._show_controls()

            # Start main processing loop
            self._process_video_stream(cap)

            cap.release()
            cv2.destroyAllWindows()
            return True

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False

    def _initialize_video_capture_with_fallback(self) -> Optional[cv2.VideoCapture]:
        """Initialize video capture with multiple camera source fallback"""
        try:
            # Try primary source first
            source = self.config.source
            if isinstance(source, str) and source.isdigit():
                source = int(source)

            logger.info(f"Trying primary camera source: {source}")
            cap = cv2.VideoCapture(source)

            if cap.isOpened():
                # Set camera properties for better quality
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                cap.set(cv2.CAP_PROP_FPS, 30)
                logger.info(f"Connected to camera source: {source}")
                return cap

            cap.release()

            # Try fallback camera sources if primary fails
            if isinstance(source, int):
                fallback_sources = [i for i in range(3) if i != source]
                for fallback_source in fallback_sources:
                    logger.info(f"Trying fallback camera source: {fallback_source}")
                    cap = cv2.VideoCapture(fallback_source)

                    if cap.isOpened():
                        # Set camera properties
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                        cap.set(cv2.CAP_PROP_FPS, 30)
                        logger.info(f"Connected to fallback camera: {fallback_source}")
                        return cap

                    cap.release()

            logger.error("No camera sources available. Please check:")
            logger.error("   1. Camera is connected and not used by other apps")
            logger.error("   2. Camera drivers are installed")
            logger.error("   3. Camera permissions are granted")
            return None

        except Exception as e:
            logger.error(f"Failed to initialize video capture: {e}")
            return None

    def _show_controls(self):
        """Display control instructions"""
        logger.info("\n" + "=" * 60)
        logger.info("INTERACTIVE CONTROLS:")
        logger.info("=" * 60)
        for key, mode in self.display_modes.items():
            logger.info(f"   '{key}' - {mode}")
        logger.info("   'q' - Quit")
        if self.config.enable_screenshots:
            logger.info("   's' - Save screenshot")
        if self.config.enable_grid_adjustment:
            logger.info("   'g' - Toggle grid size")
        logger.info("   'r' - Reset to original grid")
        logger.info("   'f' - Show FPS info")
        logger.info("=" * 60 + "\n")

    def _perform_calibration(self, frame: np.ndarray) -> bool:
        """Perform camera calibration with user interaction"""
        try:
            logger.info("Starting camera calibration...")

            # Get calibration points from user
            pts_img = self._get_calibration_points(frame)
            if pts_img is None:
                return False

            # Get real-world dimensions
            world_width, world_height = self._get_world_dimensions()
            if world_width is None or world_height is None:
                return False

            # Calculate homography matrices
            pts_world = np.array([[0, 0], [world_width, 0], [world_width, world_height], [0, world_height]],
                                 dtype=np.float32)

            H_matrix = cv2.getPerspectiveTransform(pts_img, pts_world)
            inv_H_matrix = cv2.getPerspectiveTransform(pts_world, pts_img)

            self.geometry_processor = GeometryProcessor(H_matrix, inv_H_matrix)

            # Initialize grid parameters
            self._initialize_grid_parameters(world_width, world_height)

            logger.info(
                f"Calibration completed: {world_width}x{world_height}m, grid {self.grid_rows}x{self.grid_cols}")
            return True

        except Exception as e:
            logger.error(f"Calibration failed: {e}")
            return False

    def _get_calibration_points(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Get calibration points from user with GUI fallback"""
        clicked_points = []

        def click_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                clicked_points.append((x, y))
                logger.info(f"Clicked point {len(clicked_points)}: ({x}, {y})")

        try:
            # Try GUI-based calibration
            window_name = "Calibration - Click 4 corners"
            cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
            cv2.setMouseCallback(window_name, click_callback)

            logger.info("Click 4 ground reference points in clockwise order")
            logger.info("Press 'c' to continue after 4 points, or 'ESC' to cancel")

            while True:
                display_frame = frame.copy()

                # Draw clicked points
                for i, point in enumerate(clicked_points):
                    cv2.circle(display_frame, point, 8, (0, 255, 0), -1)
                    cv2.circle(display_frame, point, 10, (255, 255, 255), 2)
                    cv2.putText(display_frame, f"{i + 1}", (point[0] + 12, point[1] - 12),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                # Draw lines connecting points
                if len(clicked_points) > 1:
                    for i in range(len(clicked_points)):
                        next_i = (i + 1) % len(clicked_points)
                        if next_i < len(clicked_points):
                            cv2.line(display_frame, clicked_points[i], clicked_points[next_i], (0, 255, 255), 2)

                # Add instructions
                instructions = [
                    f"Points: {len(clicked_points)}/4",
                    "Click corners clockwise",
                    "'c' to continue, ESC to cancel"
                ]

                y_pos = 30
                for instruction in instructions:
                    cv2.rectangle(display_frame, (10, y_pos - 25), (400, y_pos + 5), (0, 0, 0), -1)
                    cv2.putText(display_frame, instruction, (15, y_pos),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    y_pos += 35

                cv2.imshow(window_name, display_frame)
                key = cv2.waitKey(1) & 0xFF

                if key == ord('c') and len(clicked_points) >= 4:
                    break
                elif key == 27:  # ESC key
                    logger.info("Calibration cancelled")
                    cv2.destroyWindow(window_name)
                    return None

            cv2.destroyWindow(window_name)

            if len(clicked_points) >= 4:
                return np.array(clicked_points[:4], dtype=np.float32)

        except Exception as e:
            logger.warning(f"GUI calibration failed: {e}")

        # Fallback to manual entry
        return self._manual_calibration_entry(frame)

    def _manual_calibration_entry(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Fallback manual calibration point entry"""
        try:
            # Save frame for reference
            calibration_image = "calibration_frame.jpg"
            cv2.imwrite(calibration_image, frame)
            logger.info(f"Saved calibration frame to: {calibration_image}")

            print("\nManual calibration mode:")
            print("1. Open the saved calibration frame")
            print("2. Note 4 corner points in clockwise order")
            print("3. Enter the pixel coordinates below")

            points = []
            for i in range(4):
                while True:
                    try:
                        coord_input = input(f"Enter point {i + 1} as 'x,y' (e.g., 123,456): ").strip()
                        if not coord_input:
                            continue

                        x_str, y_str = coord_input.split(',')
                        x, y = int(x_str.strip()), int(y_str.strip())
                        points.append((x, y))
                        break

                    except (ValueError, IndexError):
                        print("Invalid format. Please use 'x,y' format.")
                    except KeyboardInterrupt:
                        logger.info("Manual calibration cancelled")
                        return None

            return np.array(points, dtype=np.float32)

        except Exception as e:
            logger.error(f"Manual calibration failed: {e}")
            return None

    def _get_world_dimensions(self) -> Tuple[Optional[float], Optional[float]]:
        """Get real-world dimensions from user"""
        try:
            print("\nEnter the real-world dimensions of the calibrated area:")

            while True:
                try:
                    width_str = input("Width (meters): ").strip()
                    width = float(width_str.replace(',', '.'))
                    if width > 0:
                        break
                    print("Width must be positive")
                except (ValueError, KeyboardInterrupt):
                    logger.info("Dimension input cancelled")
                    return None, None

            while True:
                try:
                    height_str = input("Height (meters): ").strip()
                    height = float(height_str.replace(',', '.'))
                    if height > 0:
                        break
                    print("Height must be positive")
                except (ValueError, KeyboardInterrupt):
                    logger.info("Dimension input cancelled")
                    return None, None

            return width, height

        except Exception as e:
            logger.error(f"Failed to get world dimensions: {e}")
            return None, None

    def _initialize_grid_parameters(self, world_width: float, world_height: float):
        """Initialize grid and capacity parameters"""
        self.world_width = world_width
        self.world_height = world_height

        # Calculate grid dimensions
        self.grid_cols = int(math.ceil(world_width / self.config.cell_width))
        self.grid_rows = int(math.ceil(world_height / self.config.cell_height))

        # Calculate cell capacity based on person radius OR use threshold
        if self.config.person_threshold > 0:  # ADD THIS BLOCK
            self.cell_capacity = self.config.person_threshold
        else:
            person_area = math.pi * self.config.person_radius ** 2
            cell_area = self.config.cell_width * self.config.cell_height
            self.cell_capacity = max(1, int(cell_area / person_area))

        # Initialize runtime state arrays
        self.ema_counts = np.zeros((self.grid_rows, self.grid_cols), dtype=np.float32)
        self.timers = np.zeros((self.grid_rows, self.grid_cols), dtype=np.float32)
        self.notified = np.zeros((self.grid_rows, self.grid_cols), dtype=bool)

        logger.info(
            f"Grid initialized: {self.grid_rows}x{self.grid_cols} cells, capacity: {self.cell_capacity} per cell")

    def _initialize_tracker(self):
        """Initialize the tracking system"""
        try:
            if self.config.use_deepsort and DEEPSORT_AVAILABLE:
                logger.info("Initializing DeepSort tracker")
                self.tracker = DeepSortTracker(
                    max_age=self.config.max_age,
                    n_init=self.config.n_init
                )
            else:
                if self.config.use_deepsort:
                    logger.warning("DeepSort requested but not available, using simple tracker")
                else:
                    logger.info("Using simple centroid tracker")

                self.tracker = SimpleCentroidTracker(
                    max_age=self.config.max_age,
                    distance_threshold=80.0
                )

        except Exception as e:
            logger.error(f"Failed to initialize tracker: {e}")
            # Fallback to simple tracker
            self.tracker = SimpleCentroidTracker(max_age=self.config.max_age)

    def _process_video_stream(self, cap: cv2.VideoCapture):
        """Main video processing loop with interactive controls"""
        logger.info("Starting interactive video processing loop")

        last_time = time.time()
        fps_display_counter = 0
        show_fps = False

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to read frame, ending processing")
                    break

                self.frame_count += 1
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time

                # Update FPS tracking
                self.fps_counter.append(current_time)
                if len(self.fps_counter) > 30:  # Keep last 30 measurements
                    self.fps_counter.pop(0)

                # Process frame
                tracks = self._process_frame(frame)

                # Update occupancy grid (only for monitoring modes)
                if self.current_mode in ['4', '5']:  # Monitoring or Split view
                    self._update_occupancy_grid(tracks, dt)

                # Generate appropriate visualization based on current mode
                display_frame = self._create_mode_specific_visualization(frame, tracks, show_fps)

                # Display the frame
                window_title = f"Enhanced Crowd Monitor - {self.display_modes[self.current_mode]}"
                cv2.imshow(window_title, display_frame)

                # Handle user input
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    logger.info("User requested quit")
                    break
                elif key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5')]:
                    old_mode = self.current_mode
                    self.current_mode = chr(key)
                    mode_name = self.display_modes[self.current_mode]
                    logger.info(f"Display mode switched from {self.display_modes[old_mode]} to {mode_name}")

                elif key == ord('s') and self.config.enable_screenshots:
                    # Save screenshot
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"crowd_monitor_{timestamp}.jpg"
                    cv2.imwrite(filename, display_frame)
                    logger.info(f"Screenshot saved: {filename}")

                elif key == ord('g') and self.config.enable_grid_adjustment:
                    # Toggle grid size
                    self._toggle_grid_size()

                elif key == ord('r'):
                    # Reset to original grid
                    self._reset_grid_size()

                elif key == ord('f'):
                    # Toggle FPS display
                    show_fps = not show_fps
                    status = "ON" if show_fps else "OFF"
                    logger.info(f"FPS display: {status}")

                # Display FPS info every 60 frames if requested
                fps_display_counter += 1
                if fps_display_counter % 60 == 0 and show_fps:
                    elapsed = current_time - self.fps_start_time
                    fps = len(self.fps_counter) / max(elapsed, 1)
                    logger.info(f"Current FPS: {fps:.1f}")

        except KeyboardInterrupt:
            logger.info("Processing interrupted by user")
        except Exception as e:
            logger.error(f"Error in video processing loop: {e}")

    def _toggle_grid_size(self):
        """Toggle between different grid sizes"""
        current_cells = self.grid_rows * self.grid_cols

        # Cycle through different grid configurations
        if current_cells <= 24:  # Small grid (e.g., 4x6 or 6x4)
            new_width = self.original_cell_width * 0.67
            new_height = self.original_cell_height * 0.67
        elif current_cells <= 48:  # Medium grid
            new_width = self.original_cell_width * 0.5
            new_height = self.original_cell_height * 0.5
        else:  # Large grid, reset to original
            new_width = self.original_cell_width
            new_height = self.original_cell_height

        self.config.cell_width = new_width
        self.config.cell_height = new_height
        self._reinitialize_grid()

    def _reset_grid_size(self):
        """Reset grid to original size"""
        self.config.cell_width = self.original_cell_width
        self.config.cell_height = self.original_cell_height
        self._reinitialize_grid()
        logger.info("Grid reset to original size")

    def _reinitialize_grid(self):
        """Reinitialize grid with new cell dimensions"""
        self._initialize_grid_parameters(self.world_width, self.world_height)
        logger.info(f"Grid size changed to: {self.grid_rows}x{self.grid_cols} cells")

    def _create_mode_specific_visualization(self, frame: np.ndarray, tracks: List[TrackData],
                                            show_fps: bool) -> np.ndarray:
        """Create visualization based on current display mode"""
        if self.current_mode == '1':  # Raw Camera
            return self._create_raw_camera_view(frame, show_fps)
        elif self.current_mode == '2':  # Grid Overlay
            return self._create_grid_overlay_view(frame, show_fps)
        elif self.current_mode == '3':  # Detection View
            return self._create_detection_view(frame, tracks, show_fps)
        elif self.current_mode == '4':  # Monitoring View
            return self._create_monitoring_view(frame, tracks, show_fps)
        elif self.current_mode == '5':  # Split View
            return self._create_split_view(frame, tracks, show_fps)
        else:
            return frame

    def _create_raw_camera_view(self, frame: np.ndarray, show_fps: bool) -> np.ndarray:
        """Create raw camera view with minimal overlay"""
        view = frame.copy()
        self._add_basic_info_overlay(view, "Raw Camera", show_fps)
        return view

    def _create_grid_overlay_view(self, frame: np.ndarray, show_fps: bool) -> np.ndarray:
        """Create camera view with grid overlay"""
        view = frame.copy()
        if self.geometry_processor is not None:
            self._draw_grid_overlay(view)
        self._add_basic_info_overlay(view, "Grid Overlay", show_fps)
        return view

    def _create_detection_view(self, frame: np.ndarray, tracks: List[TrackData], show_fps: bool) -> np.ndarray:
        """Create detection view with bounding boxes"""
        view = frame.copy()
        for track in tracks:
            self._draw_simple_track_annotation(view, track)
        info_text = f"People detected: {len(tracks)}"
        cv2.putText(view, info_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        self._add_basic_info_overlay(view, "Detection View", show_fps)
        return view

    def _create_monitoring_view(self, frame: np.ndarray, tracks: List[TrackData], show_fps: bool) -> np.ndarray:
        """Create full monitoring view with all features"""
        view = frame.copy()
        if self.geometry_processor is not None:
            self._draw_grid_overlay(view)
            for track in tracks:
                self._draw_track_annotation(view, track)
            self._draw_cell_occupancy_overlay(view)
        info_panel = self._create_info_panel(view.shape[1], tracks, show_fps)
        view = np.vstack([view, info_panel])
        return view

    def _create_split_view(self, frame: np.ndarray, tracks: List[TrackData], show_fps: bool) -> np.ndarray:
        """Create split view showing multiple perspectives"""
        small_height = self.camera_height // 2
        small_width = self.camera_width // 2

        raw_small = cv2.resize(self._create_raw_camera_view(frame, False), (small_width, small_height))
        grid_small = cv2.resize(self._create_grid_overlay_view(frame, False), (small_width, small_height))
        detection_small = cv2.resize(self._create_detection_view(frame, tracks, False), (small_width, small_height))
        birdseye_view = self._create_birdseye_view(tracks)
        birdseye_small = cv2.resize(birdseye_view, (small_width, small_height))

        cv2.putText(raw_small, "RAW CAMERA", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(grid_small, "WITH GRID", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(detection_small, "DETECTION", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(birdseye_small, "BIRD'S EYE", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

        top_row = np.hstack([raw_small, grid_small])
        bottom_row = np.hstack([detection_small, birdseye_small])
        split_frame = np.vstack([top_row, bottom_row])

        if show_fps:
            info_panel = self._create_split_info_panel(split_frame.shape[1], tracks, show_fps)
            split_frame = np.vstack([split_frame, info_panel])

        return split_frame

    def _process_frame(self, frame: np.ndarray) -> List[TrackData]:
        """Process a single frame for detections and tracking"""
        detections = []
        if self.frame_count % self.config.detect_every == 0:
            detections = self._detect_persons(frame)
            self.last_detection_frame = self.frame_count

        if self.tracker is not None:
            tracks = self.tracker.update_tracks(detections, frame)
            return tracks
        return []

    def _detect_persons(self, frame: np.ndarray) -> List[List[float]]:
        """Detect persons in the frame using YOLO"""
        try:
            results = self.model(
                frame,
                imgsz=640,
                conf=self.config.confidence_threshold,
                classes=[0],  # Person class
                verbose=False
            )

            detections = []
            h_img, w_img = frame.shape[:2]

            for result in results:
                if hasattr(result, 'boxes') and result.boxes is not None:
                    for box in result.boxes:
                        try:
                            xyxy = box.xyxy[0].cpu().numpy() if hasattr(box.xyxy[0], 'cpu') else np.array(box.xyxy[0])
                            conf = float(box.conf[0].cpu().numpy()) if hasattr(box.conf[0], 'cpu') else float(
                                box.conf[0])
                        except Exception:
                            continue

                        x1, y1, x2, y2 = map(float, xyxy)
                        x1 = max(0, min(w_img - 1, x1))
                        x2 = max(0, min(w_img - 1, x2))
                        y1 = max(0, min(h_img - 1, y1))
                        y2 = max(0, min(h_img - 1, y2))

                        if x2 <= x1 or y2 <= y1:
                            continue

                        area = (x2 - x1) * (y2 - y1)
                        if area < self.config.min_bbox_area:
                            continue

                        detections.append([x1, y1, x2, y2, conf])

            logger.debug(f"Detected {len(detections)} persons")
            return detections

        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []

    def _update_occupancy_grid(self, tracks: List[TrackData], dt: float):
        """Update the occupancy grid with current tracks"""
        if self.geometry_processor is None or self.ema_counts is None:
            return

        current_counts = np.zeros_like(self.ema_counts)

        for track in tracks:
            polygon, _ = self.geometry_processor.project_bbox_to_world(track.bbox)
            if polygon is None or polygon.area <= 1e-6:
                continue

            minx, miny, maxx, maxy = polygon.bounds
            min_col = max(0, int(minx // self.config.cell_width))
            max_col = min(self.grid_cols - 1, int(maxx // self.config.cell_width))
            min_row = max(0, int(miny // self.config.cell_height))
            max_row = min(self.grid_rows - 1, int(maxy // self.config.cell_height))

            for row in range(min_row, max_row + 1):
                for col in range(min_col, max_col + 1):
                    cell_polygon = shapely_box(
                        col * self.config.cell_width,
                        row * self.config.cell_height,
                        (col + 1) * self.config.cell_width,
                        (row + 1) * self.config.cell_height
                    )

                    try:
                        intersection = polygon.intersection(cell_polygon)
                        if not intersection.is_empty:
                            overlap_fraction = intersection.area / polygon.area
                            current_counts[row, col] += max(0.0, min(1.0, overlap_fraction))
                    except Exception:
                        current_counts[row, col] += 0.1

        self.ema_counts = (self.config.ema_alpha * current_counts +
                           (1.0 - self.config.ema_alpha) * self.ema_counts)
        self._update_alerts(dt)

    def _update_alerts(self, dt: float):
        """Update alert timers and trigger notifications"""
        if self.timers is None or self.notified is None:
            return

        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if self.ema_counts[row, col] > self.cell_capacity:
                    self.timers[row, col] += dt
                else:
                    self.timers[row, col] = max(0.0, self.timers[row, col] - dt)

                if (self.timers[row, col] >= self.config.hysteresis_time and
                        not self.notified[row, col]):
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    logger.warning(
                        f"OVERCAPACITY ALERT - Cell ({row},{col}) "
                        f"occupancy: {self.ema_counts[row, col]:.2f}/{self.cell_capacity} "
                        f"at {timestamp}"
                    )
                    self.notified[row, col] = True

                if (self.notified[row, col] and
                        self.ema_counts[row, col] <= max(0, self.cell_capacity - 0.5)):
                    logger.info(f"Alert cleared for cell ({row},{col})")
                    self.notified[row, col] = False

    def _draw_grid_overlay(self, view: np.ndarray):
        """Draw grid lines on camera view"""
        if self.geometry_processor is None:
            return

        grid_color = (100, 255, 100)
        thickness = self.config.grid_line_thickness

        for i in range(self.grid_rows + 1):
            y_world = i * self.config.cell_height
            try:
                x1, y1 = self.geometry_processor.world_to_image_point(0.0, y_world)
                x2, y2 = self.geometry_processor.world_to_image_point(self.world_width, y_world)
                cv2.line(view, (x1, y1), (x2, y2), grid_color, thickness)
            except Exception:
                pass

        for j in range(self.grid_cols + 1):
            x_world = j * self.config.cell_width
            try:
                x1, y1 = self.geometry_processor.world_to_image_point(x_world, 0.0)
                x2, y2 = self.geometry_processor.world_to_image_point(x_world, self.world_height)
                cv2.line(view, (x1, y1), (x2, y2), grid_color, thickness)
            except Exception:
                pass

    def _draw_simple_track_annotation(self, view: np.ndarray, track: TrackData):
        """Draw simple track bounding box and ID"""
        x1, y1, x2, y2 = track.bbox
        cv2.rectangle(view, (x1, y1), (x2, y2), (0, 255, 0), self.config.bbox_thickness)
        id_text = f"ID:{track.track_id}"
        text_size = cv2.getTextSize(id_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        cv2.rectangle(view, (x1, y1 - 30), (x1 + text_size[0] + 10, y1), (0, 255, 0), -1)
        cv2.putText(view, id_text, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    def _draw_track_annotation(self, view: np.ndarray, track: TrackData):
        """Draw track bounding box and ID with full information"""
        x1, y1, x2, y2 = track.bbox
        cv2.rectangle(view, (x1, y1), (x2, y2), (0, 255, 0), self.config.bbox_thickness)
        id_text = f"ID:{track.track_id}"
        text_size = cv2.getTextSize(id_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        cv2.rectangle(view, (x1, y1 - 30), (x1 + text_size[0] + 10, y1), (0, 255, 0), -1)
        cv2.putText(view, id_text, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        if self.geometry_processor is not None:
            polygon, _ = self.geometry_processor.project_bbox_to_world(track.bbox)
            if polygon is not None:
                centroid = polygon.centroid
                col = int(centroid.x // self.config.cell_width)
                row = int(centroid.y // self.config.cell_height)

                if 0 <= row < self.grid_rows and 0 <= col < self.grid_cols:
                    cell_text = f"Cell({row},{col})"
                    cell_size = cv2.getTextSize(cell_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                    cv2.rectangle(view, (x1, y2 + 5), (x1 + cell_size[0] + 10, y2 + 25), (255, 255, 0), -1)
                    cv2.putText(view, cell_text, (x1 + 5, y2 + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    def _draw_cell_occupancy_overlay(self, view: np.ndarray):
        """Draw cell occupancy numbers on camera view"""
        if self.geometry_processor is None or self.ema_counts is None:
            return

        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                cx_world = (col + 0.5) * self.config.cell_width
                cy_world = (row + 0.5) * self.config.cell_height
                cx_img, cy_img = self.geometry_processor.world_to_image_point(cx_world, cy_world)

                count_val = self.ema_counts[row, col]
                occupancy_text = f"{count_val:.1f}/{self.cell_capacity}"

                if count_val > self.cell_capacity:
                    bg_color = (0, 0, 255)  # Red for overcapacity
                    text_color = (255, 255, 255)
                elif count_val > self.cell_capacity * 0.8:
                    bg_color = (0, 165, 255)  # Orange for warning
                    text_color = (0, 0, 0)
                else:
                    bg_color = (0, 255, 0)  # Green for normal
                    text_color = (0, 0, 0)

                text_size = cv2.getTextSize(occupancy_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                padding = 5

                cv2.rectangle(view,
                              (cx_img - text_size[0] // 2 - padding, cy_img - text_size[1] // 2 - padding),
                              (cx_img + text_size[0] // 2 + padding, cy_img + text_size[1] // 2 + padding + 3),
                              bg_color, -1)

                cv2.putText(view, occupancy_text,
                            (cx_img - text_size[0] // 2, cy_img + text_size[1] // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)

    def _add_basic_info_overlay(self, view: np.ndarray, mode_name: str, show_fps: bool):
        """Add basic information overlay to view"""
        overlay = view.copy()
        cv2.rectangle(overlay, (10, 10), (350, 80), (0, 0, 0), -1)
        cv2.putText(overlay, f"Mode: {mode_name}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(overlay, f"Resolution: {self.camera_width}x{self.camera_height}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        if show_fps and len(self.fps_counter) > 5:
            elapsed = time.time() - self.fps_start_time
            fps = len(self.fps_counter) / max(elapsed, 1)
            cv2.putText(overlay, f"FPS: {fps:.1f}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(overlay, timestamp, (10, view.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.addWeighted(view, 0.8, overlay, 0.2, 0, view)

    def _create_info_panel(self, width: int, tracks: List[TrackData], show_fps: bool = False) -> np.ndarray:
        """Create comprehensive information panel for monitoring view"""
        panel_height = 120
        panel = np.zeros((panel_height, width, 3), dtype=np.uint8)

        total_people = len(tracks)
        total_capacity = self.grid_rows * self.grid_cols * self.cell_capacity if hasattr(self, 'grid_rows') else 0
        alert_count = int(np.sum(self.notified)) if self.notified is not None else 0

        info_text = (f"People: {total_people} | Capacity: {total_capacity} | "
                     f"Grid: {self.grid_rows}x{self.grid_cols} | "
                     f"Cell: {self.config.cell_width:.1f}x{self.config.cell_height:.1f}m")
        cv2.putText(panel, info_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        if alert_count > 0:
            alert_text = f"ALERTS: {alert_count} cells over capacity!"
            cv2.putText(panel, alert_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        else:
            status_text = "All cells within capacity"
            cv2.putText(panel, status_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

        perf_text = f"Frame: {self.frame_count} | Mode: {self.display_modes[self.current_mode]}"
        if show_fps and len(self.fps_counter) > 5:
            elapsed = time.time() - self.fps_start_time
            fps = len(self.fps_counter) / max(elapsed, 1)
            perf_text += f" | FPS: {fps:.1f}"
        cv2.putText(panel, perf_text, (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

        controls_text = "Controls: 1-5 (modes) | s (screenshot) | g (grid) | r (reset) | f (fps) | q (quit)"
        cv2.putText(panel, controls_text, (10, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (120, 120, 120), 1)

        tracker_type = "DeepSort" if isinstance(self.tracker, DeepSortTracker) else "Centroid"
        tracker_text = f"Tracker: {tracker_type}"
        cv2.putText(panel, tracker_text, (10, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

        return panel

    def _create_split_info_panel(self, width: int, tracks: List[TrackData], show_fps: bool) -> np.ndarray:
        """Create information panel for split view"""
        panel_height = 60
        panel = np.zeros((panel_height, width, 3), dtype=np.uint8)

        total_people = len(tracks)
        info_text = f"People: {total_people} | Frame: {self.frame_count}"
        cv2.putText(panel, info_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        controls_text = "Controls: 1-5 (modes) | s (screenshot) | g (grid) | f (fps) | q (quit)"
        cv2.putText(panel, controls_text, (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

        if show_fps and len(self.fps_counter) > 5:
            elapsed = time.time() - self.fps_start_time
            fps = len(self.fps_counter) / max(elapsed, 1)
            fps_text = f"FPS: {fps:.1f}"
            cv2.putText(panel, fps_text, (width - 100, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        return panel

    def _create_birdseye_view(self, tracks: List[TrackData]) -> np.ndarray:
        """Create bird's eye view visualization"""
        if self.ema_counts is None:
            return np.zeros((400, 400, 3), dtype=np.uint8)

        scale = min(self.config.max_birdseye_pixels / max(self.world_width, self.world_height), 200.0)
        view_width = int(self.world_width * scale)
        view_height = int(self.world_height * scale)

        view = np.zeros((view_height, view_width, 3), dtype=np.uint8) + 40

        self._draw_occupancy_heatmap(view, scale)
        self._draw_birdseye_grid(view, scale)
        self._draw_birdseye_tracks(view, tracks, scale)

        legend_panel = self._create_birdseye_legend(view_width)
        view = np.vstack([legend_panel, view])

        return view

    def _draw_occupancy_heatmap(self, view: np.ndarray, scale: float):
        """Draw occupancy heat map on bird's eye view"""
        overlay = np.zeros_like(view)

        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                x1 = int(col * self.config.cell_width * scale)
                y1 = int(row * self.config.cell_height * scale)
                x2 = int((col + 1) * self.config.cell_width * scale)
                y2 = int((row + 1) * self.config.cell_height * scale)

                x1 = max(0, min(view.shape[1] - 1, x1))
                x2 = max(0, min(view.shape[1], x2))
                y1 = max(0, min(view.shape[0] - 1, y1))
                y2 = max(0, min(view.shape[0], y2))

                if x2 <= x1 or y2 <= y1:
                    continue

                count = self.ema_counts[row, col]
                color = self._get_occupancy_color(count)
                cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)

        cv2.addWeighted(overlay, 0.6, view, 0.4, 0, view)

    def _get_occupancy_color(self, occupancy: float) -> Tuple[int, int, int]:
        """Get color for occupancy level"""
        if occupancy > self.cell_capacity:
            intensity = min(255, int(150 + 105 * min(1.0, (occupancy / self.cell_capacity - 1))))
            return (0, 0, intensity)

        fraction = occupancy / max(1.0, self.cell_capacity)

        if fraction > 0.8:
            t = (fraction - 0.8) / 0.2
            return (0, int(165 + 90 * t), int(255 - 100 * t))
        elif fraction > 0.5:
            t = (fraction - 0.5) / 0.3
            return (int(100 * t), 255, int(100 * t))
        elif fraction > 0.1:
            t = (fraction - 0.1) / 0.4
            return (0, int(80 + 175 * t), 0)
        else:
            return (100, 60, 40)

    def _draw_birdseye_grid(self, view: np.ndarray, scale: float):
        """Draw grid lines on bird's eye view"""
        grid_color = (120, 120, 120)

        for col in range(self.grid_cols + 1):
            x = int(col * self.config.cell_width * scale)
            if 0 <= x < view.shape[1]:
                cv2.line(view, (x, 0), (x, view.shape[0] - 1), grid_color, 1)

        for row in range(self.grid_rows + 1):
            y = int(row * self.config.cell_height * scale)
            if 0 <= y < view.shape[0]:
                cv2.line(view, (0, y), (view.shape[1] - 1, y), grid_color, 1)

        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                center_x = int((col + 0.5) * self.config.cell_width * scale)
                center_y = int((row + 0.5) * self.config.cell_height * scale)

                coord_text = f"({row},{col})"
                cv2.putText(view, coord_text, (center_x - 25, center_y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)

                count_text = f"{self.ema_counts[row, col]:.1f}"
                cv2.putText(view, count_text, (center_x - 15, center_y + 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

                if self.notified[row, col]:
                    cv2.rectangle(view, (center_x - 20, center_y - 15), (center_x + 20, center_y + 15),
                                  (0, 0, 255), 2)

    def _draw_birdseye_tracks(self, view: np.ndarray, tracks: List[TrackData], scale: float):
        """Draw person positions on bird's eye view"""
        if self.geometry_processor is None:
            return

        for track in tracks:
            polygon, _ = self.geometry_processor.project_bbox_to_world(track.bbox)
            if polygon is None:
                continue

            centroid = polygon.centroid
            px = int(centroid.x * scale)
            py = int(centroid.y * scale)

            if 0 <= px < view.shape[1] and 0 <= py < view.shape[0]:
                cv2.circle(view, (px, py), 6, (0, 255, 0), -1)
                cv2.circle(view, (px, py), 6, (255, 255, 255), 1)
                cv2.putText(view, f"{track.track_id}", (px + 8, py + 3),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

    def _create_birdseye_legend(self, width: int) -> np.ndarray:
        """Create legend for bird's eye view"""
        legend_height = 60
        legend = np.zeros((legend_height, width, 3), dtype=np.uint8) + 30

        legend_items = [
            ("Empty", (100, 60, 40)),
            ("Low", (0, 155, 0)),
            ("Med", (100, 255, 100)),
            ("High", (0, 200, 255)),
            ("Over", (0, 0, 255))
        ]

        x_pos = 10
        for label, color in legend_items:
            cv2.rectangle(legend, (x_pos, 15), (x_pos + 15, 30), color, -1)
            cv2.rectangle(legend, (x_pos, 15), (x_pos + 15, 30), (255, 255, 255), 1)
            cv2.putText(legend, label, (x_pos, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
            x_pos += 60

        if self.ema_counts is not None:
            total_occupancy = float(np.sum(self.ema_counts))
            avg_occupancy = total_occupancy / (self.grid_rows * self.grid_cols)
            alert_cells = int(np.sum(self.notified)) if self.notified is not None else 0

            stats_text = f"Total: {total_occupancy:.1f} | Avg: {avg_occupancy:.1f} | Alerts: {alert_cells}"
            cv2.putText(legend, stats_text, (x_pos + 20, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        return legend


def parse_arguments() -> MonitoringConfig:
    """Parse command line arguments and create configuration"""
    parser = argparse.ArgumentParser(
        description="Enhanced Crowd Monitoring System with Interactive Features",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Video source and model
    parser.add_argument("--source", type=str, default="0",
                        help="Video source (camera index or video file path)")
    parser.add_argument("--model", type=str, default="yolov8n.pt",
                        help="YOLO model path")

    # Spatial parameters
    parser.add_argument("--cell-width", type=float, default=2.0,
                        help="Grid cell width in meters")
    parser.add_argument("--cell-height", type=float, default=2.0,
                        help="Grid cell height in meters")
    parser.add_argument("--person-radius", type=float, default=0.6,
                        help="Person radius for capacity calculation (meters)")
    parser.add_argument("--person-threshold", type=int, default=1,
                        help="Override capacity calculation, alert when more than N people per cell")

    # Detection parameters
    parser.add_argument("--detect-every", type=int, default=3,
                        help="Run detection every N frames")
    parser.add_argument("--conf", type=float, default=0.35,
                        help="Detection confidence threshold")
    parser.add_argument("--min-bbox-area", type=int, default=1500,
                        help="Minimum bounding box area")

    # Tracking parameters
    parser.add_argument("--use-deepsort", action="store_true",
                        help="Use DeepSort tracker (requires installation)")
    parser.add_argument("--max-age", type=int, default=30,
                        help="Maximum age for tracks")
    parser.add_argument("--n-init", type=int, default=1,
                        help="Number of frames to confirm track")

    # Smoothing and alert settings
    parser.add_argument("--ema-alpha", type=float, default=0.4,
                        help="EMA smoothing factor")
    parser.add_argument("--fps", type=float, default=15.0,
                        help="Expected FPS for timing calculations")
    parser.add_argument("--hysteresis", type=float, default=3.0,
                        help="Alert hysteresis time in seconds")

    # Interactive features
    parser.add_argument("--disable-screenshots", action="store_true",
                        help="Disable screenshot functionality")
    parser.add_argument("--disable-grid-adjustment", action="store_true",
                        help="Disable runtime grid adjustment")

    args = parser.parse_args()

    # Create configuration object
    config = MonitoringConfig(
        source=args.source,
        model_path=args.model,
        cell_width=args.cell_width,
        cell_height=args.cell_height,
        person_radius=args.person_radius,
        person_threshold=args.person_threshold,
        detect_every=args.detect_every,
        confidence_threshold=args.conf,
        min_bbox_area=args.min_bbox_area,
        use_deepsort=args.use_deepsort,
        max_age=args.max_age,
        n_init=args.n_init,
        ema_alpha=args.ema_alpha,
        fps=args.fps,
        hysteresis_time=args.hysteresis,
        enable_screenshots=not args.disable_screenshots,
        enable_grid_adjustment=not args.disable_grid_adjustment
    )

    return config


def main():
    """Main entry point"""
    try:
        # Parse configuration
        config = parse_arguments()

        logger.info("=== Enhanced Crowd Monitoring System ===")
        logger.info(f"Video source: {config.source}")
        logger.info(f"YOLO model: {config.model_path}")
        logger.info(f"Grid cell size: {config.cell_width}x{config.cell_height}m")
        logger.info(f"Person radius: {config.person_radius}m")
        logger.info(f"Using tracker: {'DeepSort' if config.use_deepsort else 'Centroid'}")
        logger.info(
            f"Interactive features enabled: Screenshots={config.enable_screenshots}, Grid adjustment={config.enable_grid_adjustment}")

        # Initialize and run monitoring system
        monitor = EnhancedCrowdMonitor(config)
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
        # Cleanup
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
