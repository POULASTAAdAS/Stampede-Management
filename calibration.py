"""
Camera calibration module.
Handles perspective transformation setup and user interaction.
"""

from typing import Optional, Tuple

import cv2
import numpy as np

from config import MonitoringConfig
from geometry import GeometryProcessor
from logger_config import get_logger

logger = get_logger(__name__)


class CameraCalibrator:
    """Handles camera calibration for perspective transformation"""

    def __init__(self, config: Optional[MonitoringConfig] = None):
        """Initialize camera calibrator
        
        Args:
            config: Optional monitoring configuration for visual settings
        """
        self.config = config if config is not None else MonitoringConfig()
        self.geometry_processor: Optional[GeometryProcessor] = None
        self.world_width = 0.0
        self.world_height = 0.0

    def calibrate(self, frame: np.ndarray) -> bool:
        """
        Perform camera calibration with user interaction.
        
        Args:
            frame: Calibration frame
            
        Returns:
            True if successful, False otherwise
        """
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
            self.world_width = world_width
            self.world_height = world_height

            logger.info(f"Calibration completed: {world_width}x{world_height}m")
            return True

        except Exception as e:
            logger.error(f"Calibration failed: {e}")
            return False

    def _get_calibration_points(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Get calibration points from user with GUI.
        
        Args:
            frame: Frame to display for calibration
            
        Returns:
            Array of 4 calibration points or None
        """
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
                    cv2.circle(display_frame, point, self.config.calibration_point_radius,
                               self.config.calibration_point_color, -1)
                    cv2.circle(display_frame, point, self.config.calibration_point_radius + 2,
                               self.config.calibration_point_outline_color, 2)
                    cv2.putText(display_frame, f"{i + 1}", (point[0] + 12, point[1] - 12),
                                cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_large,
                                self.config.calibration_point_color, 2)

                # Draw lines connecting points
                if len(clicked_points) > 1:
                    for i in range(len(clicked_points)):
                        next_i = (i + 1) % len(clicked_points)
                        if next_i < len(clicked_points):
                            cv2.line(display_frame, clicked_points[i], clicked_points[next_i],
                                     self.config.calibration_line_color, self.config.calibration_line_thickness)

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
                                cv2.FONT_HERSHEY_SIMPLEX, self.config.font_size_medium, (0, 255, 0), 2)
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
        """
        Fallback manual calibration point entry.
        
        Args:
            frame: Frame to save for reference
            
        Returns:
            Array of 4 calibration points or None
        """
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
        """
        Get real-world dimensions from user or config.
        
        Returns:
            Tuple of (width, height) in meters or (None, None)
        """
        try:
            # Check if auto-calibration is enabled (use preset dimensions)
            if self.config.auto_calibration:
                width = self.config.calibration_area_width
                height = self.config.calibration_area_height
                logger.info(f"Using preset calibration dimensions: {width}m x {height}m")
                print(f"\nUsing preset calibration dimensions: {width}m x {height}m")
                return width, height

            # Manual input
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
