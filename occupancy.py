"""
Occupancy grid management module.
Handles grid-based crowd density monitoring and alerts.
"""

import math
import time
from typing import List, Optional

import numpy as np
from shapely.geometry import box as shapely_box

from config import MonitoringConfig, TrackData
from geometry import GeometryProcessor
from logger_config import get_logger

logger = get_logger(__name__)


class OccupancyGrid:
    """Manages occupancy grid for crowd density monitoring"""

    def __init__(self, config: MonitoringConfig, geometry_processor: GeometryProcessor,
                 world_width: float, world_height: float):
        """
        Initialize occupancy grid.
        
        Args:
            config: Monitoring configuration
            geometry_processor: Geometry processor for coordinate transforms
            world_width: Width of monitored area in meters
            world_height: Height of monitored area in meters
        """
        self.config = config
        self.geometry_processor = geometry_processor
        self.world_width = world_width
        self.world_height = world_height

        # Calculate grid dimensions
        self.grid_cols = int(math.ceil(world_width / config.cell_width))
        self.grid_rows = int(math.ceil(world_height / config.cell_height))

        # Calculate cell capacity based on person radius
        person_area = math.pi * config.person_radius ** 2
        cell_area = config.cell_width * config.cell_height
        self.cell_capacity = max(1, int(cell_area / person_area))

        # Initialize runtime state arrays
        self.ema_counts = np.zeros((self.grid_rows, self.grid_cols), dtype=np.float32)
        self.timers = np.zeros((self.grid_rows, self.grid_cols), dtype=np.float32)
        self.notified = np.zeros((self.grid_rows, self.grid_cols), dtype=bool)

        logger.info(f"Grid initialized: {self.grid_rows}x{self.grid_cols} cells, "
                    f"capacity: {self.cell_capacity} per cell")

    def update(self, tracks: List[TrackData], dt: float):
        """
        Update the occupancy grid with current tracks.
        
        Args:
            tracks: List of current tracks
            dt: Time delta since last update
        """
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

        # Apply exponential moving average
        self.ema_counts = (self.config.ema_alpha * current_counts +
                           (1.0 - self.config.ema_alpha) * self.ema_counts)

        # Update alerts
        self._update_alerts(dt)

    def _update_alerts(self, dt: float):
        """
        Update alert timers and trigger notifications.
        
        Args:
            dt: Time delta since last update
        """
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

    def get_cell_for_track(self, track: TrackData) -> Optional[tuple]:
        """
        Get grid cell coordinates for a track.
        
        Args:
            track: Track to locate
            
        Returns:
            Tuple of (row, col) or None
        """
        polygon, _ = self.geometry_processor.project_bbox_to_world(track.bbox)
        if polygon is None:
            return None

        centroid = polygon.centroid
        col = int(centroid.x // self.config.cell_width)
        row = int(centroid.y // self.config.cell_height)

        if 0 <= row < self.grid_rows and 0 <= col < self.grid_cols:
            return (row, col)
        return None

    def reinitialize(self, world_width: float, world_height: float):
        """
        Reinitialize grid with new dimensions.
        
        Args:
            world_width: New world width in meters
            world_height: New world height in meters
        """
        self.world_width = world_width
        self.world_height = world_height

        # Recalculate grid dimensions
        self.grid_cols = int(math.ceil(world_width / self.config.cell_width))
        self.grid_rows = int(math.ceil(world_height / self.config.cell_height))

        # Recalculate cell capacity
        person_area = math.pi * self.config.person_radius ** 2
        cell_area = self.config.cell_width * self.config.cell_height
        self.cell_capacity = max(1, int(cell_area / person_area))

        # Reinitialize runtime state arrays
        self.ema_counts = np.zeros((self.grid_rows, self.grid_cols), dtype=np.float32)
        self.timers = np.zeros((self.grid_rows, self.grid_cols), dtype=np.float32)
        self.notified = np.zeros((self.grid_rows, self.grid_cols), dtype=bool)

        logger.info(f"Grid reinitialized: {self.grid_rows}x{self.grid_cols} cells")
