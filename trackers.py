"""
Tracking module for person tracking across frames.
Supports both simple centroid tracking and DeepSort.
"""

import math
from typing import Dict, List, Optional, Tuple

import numpy as np

from config import TrackData
from logger_config import get_logger

logger = get_logger(__name__)

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


class SimpleCentroidTracker:
    """Optimized centroid-based tracker with better performance"""

    def __init__(self, max_age: int = 30, distance_threshold: float = 80.0):
        """
        Initialize simple centroid tracker.
        
        Args:
            max_age: Maximum frames to keep track without detection
            distance_threshold: Maximum distance for track-detection matching
        """
        self.next_id = 1
        self.tracks: Dict[int, TrackData] = {}
        self.max_age = max_age
        self.distance_threshold = distance_threshold

    def update_tracks(self, detections: List[List[float]], frame: Optional[np.ndarray] = None) -> List[TrackData]:
        """
        Update tracks with new detections using optimized algorithm.
        
        Args:
            detections: List of detections as [x1, y1, x2, y2, confidence]
            frame: Optional frame for appearance-based tracking (unused in centroid)
            
        Returns:
            List of current TrackData objects
        """
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
        """Match existing tracks to new detections using greedy algorithm"""
        used_detections = set()

        # Simple greedy matching - could be improved with Hungarian algorithm
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
        """
        Initialize DeepSort tracker.
        
        Args:
            max_age: Maximum frames to keep track without detection
            n_init: Number of consecutive detections to confirm track
        """
        if not DEEPSORT_AVAILABLE:
            raise ImportError("DeepSort is not available")

        try:
            self.tracker = DeepSort(max_age=max_age, n_init=n_init)
            logger.info("DeepSort tracker initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DeepSort: {e}")
            raise

    def update_tracks(self, detections: List[List[float]], frame: Optional[np.ndarray] = None) -> List[TrackData]:
        """
        Update tracks using DeepSort.
        
        Args:
            detections: List of detections as [x1, y1, x2, y2, confidence]
            frame: Frame image for appearance feature extraction
            
        Returns:
            List of current TrackData objects
        """
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
