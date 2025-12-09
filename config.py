"""
Configuration module for the crowd monitoring system.
Contains all configuration classes and data structures.
"""

from dataclasses import dataclass
from typing import Tuple, Union


@dataclass
class MonitoringConfig:
    """Configuration class for crowd monitoring system"""
    # Video source settings
    source: Union[str, int] = "0"
    model_path: str = "model/yolov8n.pt"

    # Grid and spatial settings
    cell_width: float = 1.0
    cell_height: float = 1.0
    person_radius: float = 2

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
