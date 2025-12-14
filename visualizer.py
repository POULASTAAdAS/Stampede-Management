"""
Visualization module for rendering monitoring views.
Handles all drawing and display operations.
"""

import time
from typing import List, Tuple

import cv2
import numpy as np

from config import MonitoringConfig, TrackData
from geometry import GeometryProcessor
from logger_config import get_logger
from occupancy import OccupancyGrid
from trackers import DeepSortTracker

logger = get_logger(__name__)


class MonitorVisualizer:
    """Handles all visualization and rendering operations"""

    def __init__(self, config: MonitoringConfig, camera_width: int, camera_height: int):
        """
        Initialize visualizer.
        
        Args:
            config: Monitoring configuration
            camera_width: Camera frame width
            camera_height: Camera frame height
        """
        self.config = config
        self.camera_width = camera_width
        self.camera_height = camera_height

    def draw_grid_overlay(self, view: np.ndarray, geometry_processor: GeometryProcessor,
                          occupancy_grid: OccupancyGrid):
        """
        Draw grid lines on camera view.
        
        Args:
            view: Image to draw on
            geometry_processor: Geometry processor for coordinate conversion
            occupancy_grid: Occupancy grid for dimensions
        """
        grid_color = self.config.grid_color
        thickness = self.config.grid_line_thickness

        for i in range(occupancy_grid.grid_rows + 1):
            y_world = i * self.config.cell_height
            try:
                x1, y1 = geometry_processor.world_to_image_point(0.0, y_world)
                x2, y2 = geometry_processor.world_to_image_point(occupancy_grid.world_width, y_world)
                cv2.line(view, (x1, y1), (x2, y2), grid_color, thickness)
            except Exception:
                pass

        for j in range(occupancy_grid.grid_cols + 1):
            x_world = j * self.config.cell_width
            try:
                x1, y1 = geometry_processor.world_to_image_point(x_world, 0.0)
                x2, y2 = geometry_processor.world_to_image_point(x_world, occupancy_grid.world_height)
                cv2.line(view, (x1, y1), (x2, y2), grid_color, thickness)
            except Exception:
                pass

    def draw_simple_track_annotation(self, view: np.ndarray, track: TrackData):
        """
        Draw simple track bounding box and ID.
        
        Args:
            view: Image to draw on
            track: Track to visualize
        """
        x1, y1, x2, y2 = track.bbox
        cv2.rectangle(view, (x1, y1), (x2, y2), self.config.bbox_color, self.config.bbox_thickness)
        id_text = f"ID:{track.track_id}"
        text_size = cv2.getTextSize(id_text, cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_medium, 2)[0]
        cv2.rectangle(view, (x1, y1 - 30), (x1 + text_size[0] + 10, y1), self.config.track_id_bg_color, -1)
        cv2.putText(view, id_text, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_medium,
                    self.config.track_id_text_color, 2)

    def draw_track_annotation(self, view: np.ndarray, track: TrackData, occupancy_grid: OccupancyGrid):
        """
        Draw track bounding box and ID with cell information.
        
        Args:
            view: Image to draw on
            track: Track to visualize
            occupancy_grid: Occupancy grid for cell lookup
        """
        x1, y1, x2, y2 = track.bbox
        cv2.rectangle(view, (x1, y1), (x2, y2), self.config.bbox_color, self.config.bbox_thickness)
        id_text = f"ID:{track.track_id}"
        text_size = cv2.getTextSize(id_text, cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_medium, 2)[0]
        cv2.rectangle(view, (x1, y1 - 30), (x1 + text_size[0] + 10, y1), self.config.track_id_bg_color, -1)
        cv2.putText(view, id_text, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_medium,
                    self.config.track_id_text_color, 2)

        # Draw cell information
        cell = occupancy_grid.get_cell_for_track(track)
        if cell is not None:
            row, col = cell
            cell_text = f"Cell({row},{col})"
            cell_size = cv2.getTextSize(cell_text, cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_small, 1)[0]
            cv2.rectangle(view, (x1, y2 + 5), (x1 + cell_size[0] + 10, y2 + 25), self.config.cell_label_bg_color, -1)
            cv2.putText(view, cell_text, (x1 + 5, y2 + 18), cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_small,
                        self.config.cell_label_text_color, 1)

    def draw_cell_occupancy_overlay(self, view: np.ndarray, geometry_processor: GeometryProcessor,
                                    occupancy_grid: OccupancyGrid):
        """
        Draw cell occupancy numbers on camera view.
        
        Args:
            view: Image to draw on
            geometry_processor: Geometry processor for coordinate conversion
            occupancy_grid: Occupancy grid with counts
        """
        for row in range(occupancy_grid.grid_rows):
            for col in range(occupancy_grid.grid_cols):
                cx_world = (col + 0.5) * self.config.cell_width
                cy_world = (row + 0.5) * self.config.cell_height
                cx_img, cy_img = geometry_processor.world_to_image_point(cx_world, cy_world)

                count_val = occupancy_grid.ema_counts[row, col]
                occupancy_text = f"{count_val:.1f}/{occupancy_grid.cell_capacity}"

                if count_val > occupancy_grid.cell_capacity:
                    bg_color = self.config.occupancy_critical_color
                    text_color = self.config.occupancy_critical_text_color
                elif count_val > occupancy_grid.cell_capacity * self.config.occupancy_warning_threshold:
                    bg_color = self.config.occupancy_warning_color
                    text_color = self.config.occupancy_normal_text_color
                else:
                    bg_color = self.config.occupancy_normal_color
                    text_color = self.config.occupancy_normal_text_color

                text_size = cv2.getTextSize(occupancy_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                padding = 5

                cv2.rectangle(view,
                              (cx_img - text_size[0] // 2 - padding, cy_img - text_size[1] // 2 - padding),
                              (cx_img + text_size[0] // 2 + padding, cy_img + text_size[1] // 2 + padding + 3),
                              bg_color, -1)

                cv2.putText(view, occupancy_text,
                            (cx_img - text_size[0] // 2, cy_img + text_size[1] // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)

    def add_basic_info_overlay(self, view: np.ndarray, mode_name: str, fps_counter: list,
                               fps_start_time: float, show_fps: bool):
        """
        Add basic information overlay to view.
        
        Args:
            view: Image to draw on
            mode_name: Current display mode name
            fps_counter: FPS counter list
            fps_start_time: FPS measurement start time
            show_fps: Whether to show FPS
        """
        overlay = view.copy()
        cv2.rectangle(overlay, (10, 10), (350, 80), self.config.info_overlay_bg_color, -1)
        cv2.putText(overlay, f"Mode: {mode_name}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    self.config.font_size_medium, (255, 255, 255), 2)
        cv2.putText(overlay, f"Resolution: {self.camera_width}x{self.camera_height}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_tiny, (255, 255, 255), 1)

        if show_fps and len(fps_counter) > 5:
            elapsed = time.time() - fps_start_time
            fps = len(fps_counter) / max(elapsed, 1)
            cv2.putText(overlay, f"FPS: {fps:.1f}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX,
                        self.config.font_size_tiny, (0, 255, 255), 1)

        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(overlay, timestamp, (10, view.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    self.config.font_size_small, (255, 255, 255), 1)
        cv2.addWeighted(view, 1.0 - self.config.info_overlay_alpha, overlay, self.config.info_overlay_alpha, 0, view)

    def create_info_panel(self, width: int, tracks: List[TrackData], occupancy_grid: OccupancyGrid,
                          frame_count: int, display_mode: str, tracker, fps_counter: list,
                          fps_start_time: float, show_fps: bool) -> np.ndarray:
        """
        Create comprehensive information panel for monitoring view.
        
        Args:
            width: Panel width
            tracks: Current tracks
            occupancy_grid: Occupancy grid
            frame_count: Current frame count
            display_mode: Current display mode
            tracker: Tracker instance
            fps_counter: FPS counter list
            fps_start_time: FPS measurement start time
            show_fps: Whether to show FPS
            
        Returns:
            Information panel image
        """
        panel_height = self.config.info_panel_height
        panel = np.zeros((panel_height, width, 3), dtype=np.uint8)
        panel[:] = self.config.info_panel_background_color

        total_people = len(tracks)
        total_capacity = occupancy_grid.grid_rows * occupancy_grid.grid_cols * occupancy_grid.cell_capacity
        alert_count = int(np.sum(occupancy_grid.notified))

        info_text = (f"People: {total_people} | Capacity: {total_capacity} | "
                     f"Grid: {occupancy_grid.grid_rows}x{occupancy_grid.grid_cols} | "
                     f"Cell: {self.config.cell_width:.1f}x{self.config.cell_height:.1f}m")
        cv2.putText(panel, info_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_medium,
                    (255, 255, 255), 1)

        if alert_count > 0:
            alert_text = f"ALERTS: {alert_count} cells over capacity!"
            cv2.putText(panel, alert_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_medium,
                        (0, 0, 255), 2)
        else:
            status_text = "All cells within capacity"
            cv2.putText(panel, status_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_medium,
                        (0, 255, 0), 1)

        perf_text = f"Frame: {frame_count} | Mode: {display_mode}"
        if show_fps and len(fps_counter) > 5:
            elapsed = time.time() - fps_start_time
            fps = len(fps_counter) / max(elapsed, 1)
            perf_text += f" | FPS: {fps:.1f}"
        cv2.putText(panel, perf_text, (10, 75), cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_small,
                    (180, 180, 180), 1)

        controls_text = "Controls: 1-5 (modes) | s (screenshot) | g (grid) | r (reset) | f (fps) | q (quit)"
        cv2.putText(panel, controls_text, (10, 95), cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_tiny,
                    (120, 120, 120), 1)

        tracker_type = "DeepSort" if isinstance(tracker, DeepSortTracker) else "Centroid"
        tracker_text = f"Tracker: {tracker_type}"
        cv2.putText(panel, tracker_text, (10, 115), cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_tiny,
                    (180, 180, 180), 1)

        return panel

    def create_birdseye_view(self, tracks: List[TrackData], geometry_processor: GeometryProcessor,
                             occupancy_grid: OccupancyGrid) -> np.ndarray:
        """
        Create bird's eye view visualization.
        
        Args:
            tracks: Current tracks
            geometry_processor: Geometry processor
            occupancy_grid: Occupancy grid
            
        Returns:
            Bird's eye view image
        """
        scale = min(self.config.max_birdseye_pixels / max(occupancy_grid.world_width,
                                                          occupancy_grid.world_height),
                    self.config.birdseye_max_scale_fallback)
        view_width = int(occupancy_grid.world_width * scale)
        view_height = int(occupancy_grid.world_height * scale)

        view = np.zeros((view_height, view_width, 3), dtype=np.uint8) + self.config.birdseye_background_value

        self._draw_occupancy_heatmap(view, scale, occupancy_grid)
        self._draw_birdseye_grid(view, scale, occupancy_grid)
        self._draw_birdseye_tracks(view, tracks, scale, geometry_processor)

        legend_panel = self._create_birdseye_legend(view_width, occupancy_grid)
        view = np.vstack([legend_panel, view])

        return view

    def _draw_occupancy_heatmap(self, view: np.ndarray, scale: float, occupancy_grid: OccupancyGrid):
        """Draw occupancy heat map on bird's eye view"""
        overlay = np.zeros_like(view)

        for row in range(occupancy_grid.grid_rows):
            for col in range(occupancy_grid.grid_cols):
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

                count = occupancy_grid.ema_counts[row, col]
                color = self._get_occupancy_color(count, occupancy_grid.cell_capacity)
                cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)

        cv2.addWeighted(overlay, self.config.birdseye_overlay_alpha, view,
                        1.0 - self.config.birdseye_overlay_alpha, 0, view)

    def _get_occupancy_color(self, occupancy: float, cell_capacity: int) -> Tuple[int, int, int]:
        """Get color for occupancy level"""
        if occupancy > cell_capacity:
            intensity = min(255, int(150 + 105 * min(1.0, (occupancy / cell_capacity - 1))))
            return (0, 0, intensity)

        fraction = occupancy / max(1.0, cell_capacity)

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

    def _draw_birdseye_grid(self, view: np.ndarray, scale: float, occupancy_grid: OccupancyGrid):
        """Draw grid lines on bird's eye view"""
        grid_color = self.config.birdseye_grid_color

        for col in range(occupancy_grid.grid_cols + 1):
            x = int(col * self.config.cell_width * scale)
            if 0 <= x < view.shape[1]:
                cv2.line(view, (x, 0), (x, view.shape[0] - 1), grid_color, 1)

        for row in range(occupancy_grid.grid_rows + 1):
            y = int(row * self.config.cell_height * scale)
            if 0 <= y < view.shape[0]:
                cv2.line(view, (0, y), (view.shape[1] - 1, y), grid_color, 1)

        for row in range(occupancy_grid.grid_rows):
            for col in range(occupancy_grid.grid_cols):
                center_x = int((col + 0.5) * self.config.cell_width * scale)
                center_y = int((row + 0.5) * self.config.cell_height * scale)

                coord_text = f"({row},{col})"
                cv2.putText(view, coord_text, (center_x - 25, center_y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_birdseye, (200, 200, 200), 1)

                count_text = f"{occupancy_grid.ema_counts[row, col]:.1f}"
                cv2.putText(view, count_text, (center_x - 15, center_y + 5),
                            cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_tiny, (255, 255, 255), 1)

                if occupancy_grid.notified[row, col]:
                    cv2.rectangle(view, (center_x - 20, center_y - 15), (center_x + 20, center_y + 15),
                                  self.config.birdseye_alert_box_color, 2)

    def _draw_birdseye_tracks(self, view: np.ndarray, tracks: List[TrackData], scale: float,
                              geometry_processor: GeometryProcessor):
        """Draw person positions on bird's eye view"""
        for track in tracks:
            polygon, _ = geometry_processor.project_bbox_to_world(track.bbox)
            if polygon is None:
                continue

            centroid = polygon.centroid
            px = int(centroid.x * scale)
            py = int(centroid.y * scale)

            if 0 <= px < view.shape[1] and 0 <= py < view.shape[0]:
                cv2.circle(view, (px, py), self.config.birdseye_person_radius,
                           self.config.birdseye_person_color, -1)
                cv2.circle(view, (px, py), self.config.birdseye_person_radius,
                           self.config.birdseye_person_outline_color, 1)
                cv2.putText(view, f"{track.track_id}", (px + 8, py + 3),
                            cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_birdseye, (255, 255, 255), 1)

    def _create_birdseye_legend(self, width: int, occupancy_grid: OccupancyGrid) -> np.ndarray:
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
            cv2.putText(legend, label, (x_pos, 45), cv2.FONT_HERSHEY_SIMPLEX,
                        self.config.font_size_birdseye, (255, 255, 255), 1)
            x_pos += 60

        total_occupancy = float(np.sum(occupancy_grid.ema_counts))
        avg_occupancy = total_occupancy / (occupancy_grid.grid_rows * occupancy_grid.grid_cols)
        alert_cells = int(np.sum(occupancy_grid.notified))

        stats_text = f"Total: {total_occupancy:.1f} | Avg: {avg_occupancy:.1f} | Alerts: {alert_cells}"
        cv2.putText(legend, stats_text, (x_pos + 20, 25), cv2.FONT_HERSHEY_SIMPLEX,
                    self.config.font_size_tiny, (255, 255, 255), 1)

        return legend
