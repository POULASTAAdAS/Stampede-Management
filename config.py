"""
Configuration module for the crowd monitoring system.
Contains all configuration classes and data structures.
"""

from dataclasses import dataclass
from typing import Tuple, Union


@dataclass
class MonitoringConfig:
    """Comprehensive configuration class for crowd monitoring system"""

    # ==================== Video Source Settings ====================
    source: Union[str, int] = "0"
    model_path: str = "model/yolov8n.pt"

    # Camera resolution settings
    camera_width: int = 1280
    camera_height: int = 720
    camera_fps: int = 30

    # ==================== Grid and Spatial Settings ====================
    cell_width: float = 1.0
    cell_height: float = 1.0
    person_radius: float = 2

    # ==================== Detection Settings ====================
    detect_every: int = 5
    confidence_threshold: float = 0.35
    min_bbox_area: int = 1500

    # YOLO model settings
    yolo_imgsz: int = 640
    yolo_classes: Tuple[int, ...] = (0,)  # 0 = person class
    min_model_size_bytes: int = 1000000  # 1MB minimum for valid model

    # ==================== Tracking Settings ====================
    use_deepsort: bool = False
    max_age: int = 80
    n_init: int = 1

    # Centroid tracker settings
    centroid_distance_threshold: float = 80.0

    # ==================== Smoothing and Alert Settings ====================
    ema_alpha: float = 0.4
    fps: float = 15.0
    hysteresis_time: float = 3.0

    # Alert thresholds
    alert_clear_offset: float = 0.5  # Clear alert when occupancy drops this much below capacity

    # ==================== Visualization Settings ====================
    max_birdseye_pixels: int = 900
    grid_line_thickness: int = 2
    bbox_thickness: int = 3

    # Color scheme (BGR format for OpenCV)
    grid_color: Tuple[int, int, int] = (100, 255, 100)
    bbox_color: Tuple[int, int, int] = (0, 255, 0)
    track_id_bg_color: Tuple[int, int, int] = (0, 255, 0)
    track_id_text_color: Tuple[int, int, int] = (0, 0, 0)
    cell_label_bg_color: Tuple[int, int, int] = (255, 255, 0)
    cell_label_text_color: Tuple[int, int, int] = (0, 0, 0)

    # Occupancy level colors
    occupancy_normal_color: Tuple[int, int, int] = (0, 255, 0)  # Green
    occupancy_warning_color: Tuple[int, int, int] = (0, 165, 255)  # Orange
    occupancy_critical_color: Tuple[int, int, int] = (0, 0, 255)  # Red
    occupancy_normal_text_color: Tuple[int, int, int] = (0, 0, 0)
    occupancy_critical_text_color: Tuple[int, int, int] = (255, 255, 255)

    # Occupancy warning threshold (fraction of capacity)
    occupancy_warning_threshold: float = 0.8  # Warning at 80% capacity

    # Bird's eye view settings
    birdseye_background_value: int = 40
    birdseye_max_scale_fallback: float = 200.0
    birdseye_person_radius: int = 6
    birdseye_person_color: Tuple[int, int, int] = (0, 255, 0)
    birdseye_person_outline_color: Tuple[int, int, int] = (255, 255, 255)
    birdseye_grid_color: Tuple[int, int, int] = (120, 120, 120)
    birdseye_alert_box_color: Tuple[int, int, int] = (0, 0, 255)
    birdseye_overlay_alpha: float = 0.6

    # ==================== UI Panel Settings ====================
    info_panel_height: int = 120
    info_panel_background_color: Tuple[int, int, int] = (0, 0, 0)

    # Text overlay settings
    info_overlay_alpha: float = 0.2
    info_overlay_bg_color: Tuple[int, int, int] = (0, 0, 0)

    # Font sizes
    font_size_large: float = 0.8
    font_size_medium: float = 0.6
    font_size_small: float = 0.5
    font_size_tiny: float = 0.4
    font_size_birdseye: float = 0.35

    # ==================== Interactive Features ====================
    enable_screenshots: bool = True
    enable_grid_adjustment: bool = True

    # Grid adjustment multipliers
    grid_toggle_multipliers: Tuple[float, ...] = (1.0, 0.67, 0.5)
    grid_toggle_cell_thresholds: Tuple[int, ...] = (24, 48)  # Cell count thresholds for toggling

    # FPS counter settings
    fps_counter_window: int = 30  # Number of frames to average

    # Split view layout
    split_view_divisor: int = 2  # Divide camera dimensions by this for split view

    # ==================== Calibration Settings ====================
    calibration_point_radius: int = 8
    calibration_point_color: Tuple[int, int, int] = (0, 255, 0)
    calibration_point_outline_color: Tuple[int, int, int] = (255, 255, 255)
    calibration_line_color: Tuple[int, int, int] = (0, 255, 255)
    calibration_line_thickness: int = 2

    # Real-world dimensions of calibration area
    calibration_area_width: float = 10.0  # meters
    calibration_area_height: float = 10.0  # meters
    auto_calibration: bool = False  # Use preset dimensions instead of prompting


@dataclass
class VisualizationColorScheme:
    """Alternative color schemes for visualization (optional advanced feature)"""

    # Heatmap colors for different occupancy levels
    empty_color: Tuple[int, int, int] = (100, 60, 40)
    low_occupancy_color: Tuple[int, int, int] = (0, 155, 0)
    medium_occupancy_color: Tuple[int, int, int] = (100, 255, 100)
    high_occupancy_color: Tuple[int, int, int] = (0, 200, 255)
    over_capacity_color: Tuple[int, int, int] = (0, 0, 255)

    # Thresholds for color transitions (as fraction of capacity)
    low_threshold: float = 0.1
    medium_threshold: float = 0.5
    high_threshold: float = 0.8


@dataclass
class TrackData:
    """Data structure for tracking information"""
    track_id: int
    bbox: Tuple[int, int, int, int]
    world_position: Tuple[float, float]
    confidence: float = 1.0
    age: int = 0
    confirmed: bool = True
