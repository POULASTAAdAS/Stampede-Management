"""
Example usage of the modular crowd monitoring system.
Demonstrates how to use individual components.
"""


# Example 1: Basic usage with default configuration
def example_basic():
    """Run monitoring system with default settings"""
    from config import MonitoringConfig
    from monitor import CrowdMonitor

    config = MonitoringConfig(
        source="0",  # Use default camera
        cell_width=2.0,
        cell_height=2.0
    )

    monitor = CrowdMonitor(config)
    monitor.initialize()


# Example 2: Custom configuration
def example_custom_config():
    """Run with custom configuration"""
    from config import MonitoringConfig
    from monitor import CrowdMonitor

    config = MonitoringConfig(
        source="video.mp4",  # Use video file
        model_path="yolov8n.pt",
        cell_width=1.5,
        cell_height=1.5,
        person_radius=0.5,
        detect_every=3,
        confidence_threshold=0.4,
        use_deepsort=False,
        enable_screenshots=True
    )

    monitor = CrowdMonitor(config)
    monitor.initialize()


# Example 3: Using individual components
def example_individual_components():
    """Use components independently"""
    from config import MonitoringConfig
    from detector import PersonDetector
    import cv2

    config = MonitoringConfig(model_path="yolov8n.pt")
    detector = PersonDetector(config)

    if detector.load_model():
        # Detect in a single frame
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            detections = detector.detect_persons(frame)
            print(f"Found {len(detections)} persons")
            for i, det in enumerate(detections):
                x1, y1, x2, y2, conf = det
                print(f"Person {i + 1}: bbox=({x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}), conf={conf:.2f}")
        cap.release()


# Example 4: Custom tracker
def example_custom_tracker():
    """Create and use a custom tracker"""
    from config import TrackData
    from typing import List, Optional
    import numpy as np

    class MyCustomTracker:
        """Example custom tracker"""

        def __init__(self):
            self.next_id = 1
            self.tracks = {}

        def update_tracks(self, detections: List[List[float]],
                          frame: Optional[np.ndarray] = None) -> List[TrackData]:
            """Update tracks with custom logic"""
            tracks = []
            for det in detections:
                if len(det) >= 4:
                    x1, y1, x2, y2 = det[:4]
                    conf = det[4] if len(det) > 4 else 1.0

                    track = TrackData(
                        track_id=self.next_id,
                        bbox=(int(x1), int(y1), int(x2), int(y2)),
                        world_position=((x1 + x2) / 2, (y1 + y2) / 2),
                        confidence=conf
                    )
                    tracks.append(track)
                    self.next_id += 1

            return tracks

    # Use custom tracker
    tracker = MyCustomTracker()
    detections = [[100, 100, 200, 300, 0.9], [300, 150, 400, 350, 0.85]]
    tracks = tracker.update_tracks(detections)
    print(f"Created {len(tracks)} tracks")


# Example 5: Geometry transformations
def example_geometry():
    """Demonstrate coordinate transformations"""
    import numpy as np
    from geometry import GeometryProcessor
    import cv2

    # Define calibration points (image coordinates)
    pts_img = np.array([
        [100, 100],  # Top-left
        [500, 100],  # Top-right
        [500, 400],  # Bottom-right
        [100, 400]  # Bottom-left
    ], dtype=np.float32)

    # Define world coordinates (meters)
    pts_world = np.array([
        [0, 0],  # Top-left
        [4, 0],  # Top-right (4 meters wide)
        [4, 3],  # Bottom-right (3 meters tall)
        [0, 3]  # Bottom-left
    ], dtype=np.float32)

    # Calculate homography
    H_matrix = cv2.getPerspectiveTransform(pts_img, pts_world)
    inv_H_matrix = cv2.getPerspectiveTransform(pts_world, pts_img)

    # Create geometry processor
    geo = GeometryProcessor(H_matrix, inv_H_matrix)

    # Transform a bounding box
    bbox = (200, 200, 300, 350)  # Image coordinates
    polygon, world_points = geo.project_bbox_to_world(bbox)

    if polygon:
        print(f"Bbox area in image: {(300 - 200) * (350 - 200)} pixels²")
        print(f"Bbox area in world: {polygon.area:.2f} m²")
        print(f"Centroid: ({polygon.centroid.x:.2f}, {polygon.centroid.y:.2f}) meters")

    # Transform back to image
    world_x, world_y = 2.0, 1.5  # 2m right, 1.5m down
    img_x, img_y = geo.world_to_image_point(world_x, world_y)
    print(f"World point ({world_x}, {world_y})m → Image point ({img_x}, {img_y})px")


# Example 6: Occupancy grid
def example_occupancy():
    """Demonstrate occupancy grid usage"""
    from config import MonitoringConfig, TrackData
    from occupancy import OccupancyGrid
    from geometry import GeometryProcessor
    import numpy as np
    import cv2

    # Setup
    config = MonitoringConfig(cell_width=2.0, cell_height=2.0, person_radius=0.5)

    # Create geometry processor (simplified)
    pts_img = np.array([[0, 0], [640, 0], [640, 480], [0, 480]], dtype=np.float32)
    pts_world = np.array([[0, 0], [10, 0], [10, 8], [0, 8]], dtype=np.float32)
    H_matrix = cv2.getPerspectiveTransform(pts_img, pts_world)
    inv_H_matrix = cv2.getPerspectiveTransform(pts_world, pts_img)
    geo = GeometryProcessor(H_matrix, inv_H_matrix)

    # Create occupancy grid
    grid = OccupancyGrid(config, geo, world_width=10.0, world_height=8.0)

    print(f"Grid size: {grid.grid_rows} x {grid.grid_cols}")
    print(f"Cell capacity: {grid.cell_capacity} persons per cell")

    # Simulate some tracks
    tracks = [
        TrackData(1, (100, 100, 150, 200), (125, 150), 0.9),
        TrackData(2, (300, 150, 350, 250), (325, 200), 0.85),
    ]

    # Update grid
    grid.update(tracks, dt=0.1)

    # Check occupancy
    print(f"\nOccupancy state:")
    for row in range(min(3, grid.grid_rows)):  # Show first 3 rows
        for col in range(min(5, grid.grid_cols)):  # Show first 5 cols
            count = grid.ema_counts[row, col]
            print(f"  Cell({row},{col}): {count:.1f}/{grid.cell_capacity}", end="")
        print()


# Example 7: Visualization
def example_visualization():
    """Demonstrate visualization components"""
    from config import MonitoringConfig, TrackData
    from visualizer import MonitorVisualizer
    import numpy as np

    config = MonitoringConfig()
    viz = MonitorVisualizer(config, camera_width=640, camera_height=480)

    # Create a sample frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Create sample tracks
    tracks = [
        TrackData(1, (100, 100, 200, 300), (150, 200), 0.9),
        TrackData(2, (300, 150, 400, 350), (350, 250), 0.85),
    ]

    # Draw annotations
    for track in tracks:
        viz.draw_simple_track_annotation(frame, track)

    print("Visualization created (frame with 2 tracks)")
    # In real usage, you would: cv2.imshow("Result", frame)


if __name__ == "__main__":
    import sys

    examples = {
        "1": ("Basic usage", example_basic),
        "2": ("Custom config", example_custom_config),
        "3": ("Individual components", example_individual_components),
        "4": ("Custom tracker", example_custom_tracker),
        "5": ("Geometry transforms", example_geometry),
        "6": ("Occupancy grid", example_occupancy),
        "7": ("Visualization", example_visualization),
    }

    print("=" * 60)
    print("Crowd Monitoring System - Example Usage")
    print("=" * 60)
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print()

    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("Select example (1-7): ").strip()

    if choice in examples:
        name, func = examples[choice]
        print(f"\n{'=' * 60}")
        print(f"Running: {name}")
        print(f"{'=' * 60}\n")
        try:
            func()
        except Exception as e:
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()
    else:
        print(f"Invalid choice: {choice}")
        sys.exit(1)
