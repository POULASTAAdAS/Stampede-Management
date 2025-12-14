"""
Main crowd monitoring system.
Orchestrates all components for real-time monitoring.
"""

import time
from typing import List, Optional, Union

import cv2
import numpy as np

from calibration import CameraCalibrator
from config import MonitoringConfig, TrackData
from detector import PersonDetector
from logger_config import get_logger
from occupancy import OccupancyGrid
from trackers import DeepSortTracker, SimpleCentroidTracker
from visualizer import MonitorVisualizer

logger = get_logger(__name__)


class CrowdMonitor:
    """Enhanced crowd monitoring system with interactive features"""

    def __init__(self, config: MonitoringConfig):
        """
        Initialize crowd monitor.
        
        Args:
            config: Monitoring configuration
        """
        self.config = config

        # Components
        self.detector: Optional[PersonDetector] = None
        self.calibrator: Optional[CameraCalibrator] = None
        self.tracker: Union[SimpleCentroidTracker, DeepSortTracker, None] = None
        self.occupancy_grid: Optional[OccupancyGrid] = None
        self.visualizer: Optional[MonitorVisualizer] = None

        # Runtime state
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

        # Grid settings
        self.original_cell_width = config.cell_width
        self.original_cell_height = config.cell_height

    def initialize(self) -> bool:
        """
        Initialize all components of the monitoring system.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Initializing Enhanced Crowd Monitoring System...")

            # Initialize detector
            self.detector = PersonDetector(self.config)
            if not self.detector.load_model():
                return False

            # Initialize video capture
            cap = self._initialize_video_capture()
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

            self.calibrator = CameraCalibrator(self.config)
            if not self.calibrator.calibrate(frame):
                cap.release()
                return False

            # Initialize occupancy grid
            self.occupancy_grid = OccupancyGrid(
                self.config,
                self.calibrator.geometry_processor,
                self.calibrator.world_width,
                self.calibrator.world_height
            )

            # Initialize tracker
            self._initialize_tracker()

            # Initialize visualizer
            self.visualizer = MonitorVisualizer(self.config, self.camera_width, self.camera_height)

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

    def _initialize_video_capture(self) -> Optional[cv2.VideoCapture]:
        """
        Initialize video capture with fallback support.
        
        Returns:
            Video capture object or None
        """
        try:
            source = self.config.source
            if isinstance(source, str) and source.isdigit():
                source = int(source)

            logger.info(f"Trying primary camera source: {source}")
            cap = cv2.VideoCapture(source)

            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera_width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera_height)
                cap.set(cv2.CAP_PROP_FPS, self.config.camera_fps)
                logger.info(f"Connected to camera source: {source}")
                return cap

            cap.release()

            # Try fallback sources
            if isinstance(source, int):
                fallback_sources = [i for i in range(3) if i != source]
                for fallback_source in fallback_sources:
                    logger.info(f"Trying fallback camera source: {fallback_source}")
                    cap = cv2.VideoCapture(fallback_source)

                    if cap.isOpened():
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera_width)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera_height)
                        cap.set(cv2.CAP_PROP_FPS, self.config.camera_fps)
                        logger.info(f"Connected to fallback camera: {fallback_source}")
                        return cap

                    cap.release()

            logger.error("No camera sources available")
            return None

        except Exception as e:
            logger.error(f"Failed to initialize video capture: {e}")
            return None

    def _initialize_tracker(self):
        """Initialize the tracking system"""
        try:
            # Try DeepSort if enabled
            if self.config.use_deepsort:
                try:
                    from trackers import DEEPSORT_AVAILABLE
                    if DEEPSORT_AVAILABLE:
                        logger.info("Initializing DeepSort tracker")
                        self.tracker = DeepSortTracker(
                            max_age=self.config.max_age,
                            n_init=self.config.n_init
                        )
                        return
                    else:
                        logger.warning("DeepSort not available, using simple tracker")
                except Exception as e:
                    logger.warning(f"Failed to initialize DeepSort: {e}, using simple tracker")

            # Use simple tracker
            logger.info("Using simple centroid tracker")
            self.tracker = SimpleCentroidTracker(
                max_age=self.config.max_age,
                distance_threshold=self.config.centroid_distance_threshold
            )

        except Exception as e:
            logger.error(f"Failed to initialize tracker: {e}")
            self.tracker = SimpleCentroidTracker(max_age=self.config.max_age)

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

    def _process_video_stream(self, cap: cv2.VideoCapture):
        """
        Main video processing loop with interactive controls.
        
        Args:
            cap: Video capture object
        """
        logger.info("Starting interactive video processing loop")

        last_time = time.time()
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
                if len(self.fps_counter) > self.config.fps_counter_window:
                    self.fps_counter.pop(0)

                # Process frame
                tracks = self._process_frame(frame)

                # Update occupancy grid (only for monitoring modes)
                if self.current_mode in ['4', '5']:
                    self.occupancy_grid.update(tracks, dt)

                # Generate visualization
                display_frame = self._create_visualization(frame, tracks, show_fps)

                # Display the frame
                window_title = f"Enhanced Crowd Monitor - {self.display_modes[self.current_mode]}"
                cv2.imshow(window_title, display_frame)

                # Handle user input
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

    def _process_frame(self, frame: np.ndarray) -> List[TrackData]:
        """
        Process a single frame for detections and tracking.
        
        Args:
            frame: Input frame
            
        Returns:
            List of current tracks
        """
        detections = []
        if self.frame_count % self.config.detect_every == 0:
            detections = self.detector.detect_persons(frame)
            self.last_detection_frame = self.frame_count

        if self.tracker is not None:
            tracks = self.tracker.update_tracks(detections, frame)
            return tracks
        return []

    def _create_visualization(self, frame: np.ndarray, tracks: List[TrackData],
                              show_fps: bool) -> np.ndarray:
        """
        Create visualization based on current display mode.
        
        Args:
            frame: Input frame
            tracks: Current tracks
            show_fps: Whether to show FPS
            
        Returns:
            Visualization frame
        """
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
        """Create raw camera view"""
        view = frame.copy()
        self.visualizer.add_basic_info_overlay(view, "Raw Camera", self.fps_counter,
                                               self.fps_start_time, show_fps)
        return view

    def _create_grid_overlay_view(self, frame: np.ndarray, show_fps: bool) -> np.ndarray:
        """Create camera view with grid overlay"""
        view = frame.copy()
        self.visualizer.draw_grid_overlay(view, self.calibrator.geometry_processor, self.occupancy_grid)
        self.visualizer.add_basic_info_overlay(view, "Grid Overlay", self.fps_counter,
                                               self.fps_start_time, show_fps)
        return view

    def _create_detection_view(self, frame: np.ndarray, tracks: List[TrackData],
                               show_fps: bool) -> np.ndarray:
        """Create detection view with bounding boxes"""
        view = frame.copy()
        for track in tracks:
            self.visualizer.draw_simple_track_annotation(view, track)
        info_text = f"People detected: {len(tracks)}"
        cv2.putText(view, info_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        self.visualizer.add_basic_info_overlay(view, "Detection View", self.fps_counter,
                                               self.fps_start_time, show_fps)
        return view

    def _create_monitoring_view(self, frame: np.ndarray, tracks: List[TrackData],
                                show_fps: bool) -> np.ndarray:
        """Create full monitoring view with all features"""
        view = frame.copy()
        self.visualizer.draw_grid_overlay(view, self.calibrator.geometry_processor, self.occupancy_grid)
        for track in tracks:
            self.visualizer.draw_track_annotation(view, track, self.occupancy_grid)
        self.visualizer.draw_cell_occupancy_overlay(view, self.calibrator.geometry_processor,
                                                    self.occupancy_grid)
        info_panel = self.visualizer.create_info_panel(
            view.shape[1], tracks, self.occupancy_grid, self.frame_count,
            self.display_modes[self.current_mode], self.tracker, self.fps_counter,
            self.fps_start_time, show_fps
        )
        view = np.vstack([view, info_panel])
        return view

    def _create_split_view(self, frame: np.ndarray, tracks: List[TrackData],
                           show_fps: bool) -> np.ndarray:
        """Create split view showing multiple perspectives"""
        small_height = self.camera_height // self.config.split_view_divisor
        small_width = self.camera_width // self.config.split_view_divisor

        raw_small = cv2.resize(self._create_raw_camera_view(frame, False), (small_width, small_height))
        grid_small = cv2.resize(self._create_grid_overlay_view(frame, False), (small_width, small_height))
        detection_small = cv2.resize(self._create_detection_view(frame, tracks, False),
                                     (small_width, small_height))
        birdseye_view = self.visualizer.create_birdseye_view(tracks, self.calibrator.geometry_processor,
                                                             self.occupancy_grid)
        birdseye_small = cv2.resize(birdseye_view, (small_width, small_height))

        cv2.putText(raw_small, "RAW CAMERA", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(grid_small, "WITH GRID", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(detection_small, "DETECTION", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(birdseye_small, "BIRD'S EYE", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

        top_row = np.hstack([raw_small, grid_small])
        bottom_row = np.hstack([detection_small, birdseye_small])
        split_frame = np.vstack([top_row, bottom_row])

        return split_frame

    def _handle_mode_switch(self, new_mode: str):
        """Handle display mode switch"""
        old_mode = self.current_mode
        self.current_mode = new_mode
        mode_name = self.display_modes[self.current_mode]
        logger.info(f"Display mode switched from {self.display_modes[old_mode]} to {mode_name}")

    def _save_screenshot(self, frame: np.ndarray):
        """Save screenshot to file"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"crowd_monitor_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        logger.info(f"Screenshot saved: {filename}")

    def _toggle_grid_size(self):
        """Toggle between different grid sizes"""
        current_cells = self.occupancy_grid.grid_rows * self.occupancy_grid.grid_cols

        # Determine which multiplier to use based on thresholds
        multiplier_index = 0
        for threshold in self.config.grid_toggle_cell_thresholds:
            if current_cells <= threshold:
                multiplier_index += 1
                break

        if multiplier_index >= len(self.config.grid_toggle_multipliers):
            multiplier_index = 0

        multiplier = self.config.grid_toggle_multipliers[multiplier_index]
        new_width = self.original_cell_width * multiplier
        new_height = self.original_cell_height * multiplier

        self.config.cell_width = new_width
        self.config.cell_height = new_height
        self.occupancy_grid.reinitialize(self.calibrator.world_width, self.calibrator.world_height)

    def _reset_grid_size(self):
        """Reset grid to original size"""
        self.config.cell_width = self.original_cell_width
        self.config.cell_height = self.original_cell_height
        self.occupancy_grid.reinitialize(self.calibrator.world_width, self.calibrator.world_height)
        logger.info("Grid reset to original size")
