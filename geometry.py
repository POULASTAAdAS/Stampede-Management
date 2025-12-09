"""
Geometry processing module for coordinate transformations.
Handles conversions between image and world coordinates.
"""

from typing import Optional, Tuple

import cv2
import numpy as np
from shapely.geometry import Polygon

from logger_config import get_logger

logger = get_logger(__name__)


class GeometryProcessor:
    """Handles geometric transformations and calculations"""

    def __init__(self, homography_matrix: np.ndarray, inverse_homography: np.ndarray):
        """
        Initialize geometry processor with transformation matrices.
        
        Args:
            homography_matrix: Matrix to transform from image to world coordinates
            inverse_homography: Matrix to transform from world to image coordinates
        """
        self.H_matrix = homography_matrix
        self.inv_H_matrix = inverse_homography

    def project_bbox_to_world(self, bbox: Tuple[int, int, int, int]) -> Tuple[Optional[Polygon], Optional[np.ndarray]]:
        """
        Project bounding box from image coordinates to world coordinates.
        
        Args:
            bbox: Bounding box as (x1, y1, x2, y2) in image coordinates
            
        Returns:
            Tuple of (Polygon in world coords, corner points in world coords)
        """
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
        """
        Convert world coordinates to image coordinates.
        
        Args:
            world_x: X coordinate in world space (meters)
            world_y: Y coordinate in world space (meters)
            
        Returns:
            Tuple of (x, y) in image coordinates (pixels)
        """
        try:
            point = np.array([[[float(world_x), float(world_y)]]], dtype=np.float32)
            image_point = cv2.perspectiveTransform(point, self.inv_H_matrix)[0, 0]
            return int(image_point[0]), int(image_point[1])
        except Exception as e:
            logger.warning(f"Failed to convert world to image point: {e}")
            return 0, 0
