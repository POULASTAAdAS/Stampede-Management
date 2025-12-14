"""
Detection module for person detection using YOLO.
"""

from pathlib import Path
from typing import List

import numpy as np
from ultralytics import YOLO

from config import MonitoringConfig
from logger_config import get_logger

logger = get_logger(__name__)


def download_yolo_model(model_name: str) -> bool:
    """
    Download YOLO model if it doesn't exist or is corrupted.
    
    Args:
        model_name: Name/path of the YOLO model
        
    Returns:
        True if model is available, False otherwise
    """
    model_path = Path(model_name)

    # Check if model exists and is valid
    if model_path.exists():
        try:
            # Quick validation - check file size
            # Note: min_model_size_bytes is imported from config if needed, default 1MB
            min_size = 1000000  # Default 1MB if not in config
            if model_path.stat().st_size > min_size:
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


class PersonDetector:
    """YOLO-based person detector"""

    def __init__(self, config: MonitoringConfig):
        """
        Initialize person detector.
        
        Args:
            config: Monitoring configuration
        """
        self.config = config
        self.model = None

    def load_model(self) -> bool:
        """
        Load YOLO model with error handling.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Loading YOLO model: {self.config.model_path}")

        # Ensure model is available
        if not download_yolo_model(self.config.model_path):
            logger.error("Failed to download YOLO model")
            return False

        # Load the model with error handling
        try:
            self.model = YOLO(self.config.model_path)
            logger.info("YOLO model loaded successfully")
            return True
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
                return True
            except Exception as e2:
                logger.error(f"Failed to load YOLO model even after re-download: {e2}")
                return False

    def detect_persons(self, frame: np.ndarray) -> List[List[float]]:
        """
        Detect persons in the frame using YOLO.
        
        Args:
            frame: Input frame
            
        Returns:
            List of detections as [x1, y1, x2, y2, confidence]
        """
        if self.model is None:
            logger.error("Model not loaded")
            return []

        try:
            results = self.model(
                frame,
                imgsz=self.config.yolo_imgsz,
                conf=self.config.confidence_threshold,
                classes=list(self.config.yolo_classes),
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
