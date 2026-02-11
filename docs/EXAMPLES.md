# Code Examples and Use Cases

Practical examples for using the Stampede Management System.

## Table of Contents

- [Basic Examples](#basic-examples)
- [Advanced Usage](#advanced-usage)
- [Integration Examples](#integration-examples)
- [Custom Implementations](#custom-implementations)
- [Real-World Scenarios](#real-world-scenarios)

---

## Basic Examples

### Example 1: Simple Webcam Monitoring

**Scenario**: Monitor a single webcam with default settings

```python
from config import MonitoringConfig
from monitor import CrowdMonitor

# Create configuration with defaults
config = MonitoringConfig(source=0)

# Initialize and run monitor
monitor = CrowdMonitor(config)
success = monitor.initialize()

if success:
    print("Monitoring completed successfully")
else:
    print("Monitoring failed")
```

**Run from command line:**

```bash
python main.py --source 0
```

---

### Example 2: Video File Analysis

**Scenario**: Analyze a recorded video file for crowd density

```python
from config import MonitoringConfig
from monitor import CrowdMonitor

# Configure for video file
config = MonitoringConfig(
    source="events/concert_2024.mp4",
    enable_screenshots=True,
    auto_calibration=True,
    calibration_area_width=50.0,  # 50m wide area
    calibration_area_height=30.0   # 30m deep area
)

monitor = CrowdMonitor(config)
monitor.initialize()
```

**Run from command line:**

```bash
python main.py \
  --source events/concert_2024.mp4 \
  --auto-calibration \
  --calibration-width 50 \
  --calibration-height 30
```

---

### Example 3: Custom Detection Parameters

**Scenario**: Adjust detection sensitivity for specific conditions

```python
from config import MonitoringConfig
from monitor import CrowdMonitor

# High-precision configuration
config = MonitoringConfig(
    source=0,
    confidence_threshold=0.45,     # Higher confidence = fewer false positives
    min_bbox_area=2000,            # Larger minimum size
    detect_every=1,                # Detect every frame
    cell_width=1.5,                # Smaller cells for detail
    cell_height=1.5
)

monitor = CrowdMonitor(config)
monitor.initialize()
```

**Run from command line:**

```bash
python main.py \
  --source 0 \
  --conf 0.45 \
  --min-bbox-area 2000 \
  --detect-every 1 \
  --cell-width 1.5 \
  --cell-height 1.5
```

---

### Example 4: Performance-Optimized Settings

**Scenario**: Run on low-end hardware or for high frame rates

```python
from config import MonitoringConfig
from monitor import CrowdMonitor

# Fast configuration
config = MonitoringConfig(
    source=0,
    detect_every=10,               # Detect every 10 frames
    confidence_threshold=0.3,      # Lower threshold
    yolo_imgsz=320,                # Smaller input size
    camera_width=640,              # Lower resolution
    camera_height=480,
    use_deepsort=False,            # Use faster centroid tracker
    cell_width=3.0,                # Larger cells = less processing
    cell_height=3.0
)

monitor = CrowdMonitor(config)
monitor.initialize()
```

---

## Advanced Usage

### Example 5: Multiple Camera Monitoring

**Scenario**: Monitor multiple cameras simultaneously

```python
import threading
from config import MonitoringConfig
from monitor import CrowdMonitor

def monitor_camera(camera_id, area_name):
    """Monitor a single camera"""
    print(f"Starting monitoring for {area_name} (Camera {camera_id})")
    
    config = MonitoringConfig(
        source=camera_id,
        cell_width=2.0,
        cell_height=2.0,
        auto_calibration=True,
        calibration_area_width=10.0,
        calibration_area_height=10.0
    )
    
    monitor = CrowdMonitor(config)
    monitor.initialize()

# Monitor entrance and exit areas
cameras = [
    (0, "Main Entrance"),
    (1, "Emergency Exit"),
    (2, "Stage Area")
]

threads = []
for camera_id, area_name in cameras:
    thread = threading.Thread(
        target=monitor_camera,
        args=(camera_id, area_name)
    )
    thread.start()
    threads.append(thread)

# Wait for all threads
for thread in threads:
    thread.join()
```

---

### Example 6: Custom Detection Loop

**Scenario**: Implement your own processing logic

```python
import cv2
import time
from detector import PersonDetector
from trackers import SimpleCentroidTracker
from config import MonitoringConfig

# Initialize components
config = MonitoringConfig(
    confidence_threshold=0.35,
    min_bbox_area=1500
)

detector = PersonDetector(config)
detector.load_model()

tracker = SimpleCentroidTracker(
    max_age=30,
    distance_threshold=80.0
)

# Open video capture
cap = cv2.VideoCapture(0)
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    
    # Detect people every 3 frames
    if frame_count % 3 == 0:
        detections = detector.detect_persons(frame)
        print(f"Frame {frame_count}: Detected {len(detections)} people")
    else:
        detections = []
    
    # Update tracks
    tracks = tracker.update_tracks(detections, frame)
    
    # Draw results
    for track in tracks:
        x1, y1, x2, y2 = track.bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        label = f"ID:{track.track_id}"
        cv2.putText(frame, label, (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Add info text
    info = f"People: {len(tracks)} | Frame: {frame_count}"
    cv2.putText(frame, info, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # Display
    cv2.imshow("Custom Detection", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

### Example 7: Occupancy Analysis Only

**Scenario**: Extract occupancy data without visualization

```python
import cv2
import numpy as np
from config import MonitoringConfig
from detector import PersonDetector
from trackers import SimpleCentroidTracker
from calibration import CameraCalibrator
from occupancy import OccupancyGrid

# Setup
config = MonitoringConfig(
    source=0,
    cell_width=2.0,
    cell_height=2.0,
    person_radius=0.5,
    auto_calibration=True,
    calibration_area_width=20.0,
    calibration_area_height=15.0
)

# Initialize components
detector = PersonDetector(config)
detector.load_model()

tracker = SimpleCentroidTracker()

cap = cv2.VideoCapture(0)
ret, frame = cap.read()

# Calibration (simplified)
calibrator = CameraCalibrator(config)
calibrator.calibrate(frame)

# Create occupancy grid
grid = OccupancyGrid(
    config,
    calibrator.geometry_processor,
    calibrator.world_width,
    calibrator.world_height
)

print(f"Grid: {grid.grid_rows}x{grid.grid_cols} cells")
print(f"Cell capacity: {grid.cell_capacity} people per cell")
print()

# Process frames
frame_count = 0
import time

while frame_count < 300:  # Process 300 frames
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    
    # Detection and tracking
    if frame_count % 3 == 0:
        detections = detector.detect_persons(frame)
    else:
        detections = []
    
    tracks = tracker.update_tracks(detections, frame)
    
    # Update occupancy
    grid.update(tracks, dt=0.033)  # 30 FPS
    
    # Print occupancy report every 30 frames
    if frame_count % 30 == 0:
        print(f"Frame {frame_count}:")
        print(f"  Total people: {len(tracks)}")
        
        overcapacity_cells = []
        for row in range(grid.grid_rows):
            for col in range(grid.grid_cols):
                if grid.ema_counts[row, col] > grid.cell_capacity:
                    overcapacity_cells.append((
                        row, col, 
                        grid.ema_counts[row, col],
                        grid.cell_capacity
                    ))
        
        if overcapacity_cells:
            print(f"  ALERTS: {len(overcapacity_cells)} overcapacity cells")
            for row, col, count, capacity in overcapacity_cells:
                print(f"    Cell ({row},{col}): {count:.1f}/{capacity}")
        else:
            print("  All cells within capacity")
        print()

cap.release()
```

---

### Example 8: Data Export to CSV

**Scenario**: Export occupancy data for analysis

```python
import cv2
import csv
import time
from datetime import datetime
from config import MonitoringConfig
from monitor import CrowdMonitor

class DataExportMonitor(CrowdMonitor):
    def __init__(self, config, csv_filename):
        super().__init__(config)
        self.csv_filename = csv_filename
        self.csv_file = None
        self.csv_writer = None
    
    def initialize(self):
        # Open CSV file
        self.csv_file = open(self.csv_filename, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        
        # Write header
        self.csv_writer.writerow([
            'timestamp', 'frame', 'total_people', 
            'alerts', 'overcapacity_cells'
        ])
        
        # Call parent initialization
        return super().initialize()
    
    def _process_frame(self, frame):
        # Call parent processing
        tracks = super()._process_frame(frame)
        
        # Export data every 30 frames
        if self.frame_count % 30 == 0:
            self._export_data(tracks)
        
        return tracks
    
    def _export_data(self, tracks):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Count overcapacity cells
        overcapacity = 0
        for row in range(self.occupancy_grid.grid_rows):
            for col in range(self.occupancy_grid.grid_cols):
                if self.occupancy_grid.ema_counts[row, col] > \
                   self.occupancy_grid.cell_capacity:
                    overcapacity += 1
        
        # Count alerts
        alerts = self.occupancy_grid.notified.sum()
        
        # Write to CSV
        self.csv_writer.writerow([
            timestamp,
            self.frame_count,
            len(tracks),
            int(alerts),
            overcapacity
        ])
        self.csv_file.flush()
    
    def __del__(self):
        if self.csv_file:
            self.csv_file.close()

# Usage
config = MonitoringConfig(source=0)
monitor = DataExportMonitor(config, "occupancy_data.csv")
monitor.initialize()
```

---

## Integration Examples

### Example 9: Webhook Alerts

**Scenario**: Send HTTP webhook when overcapacity detected

```python
import requests
from occupancy import OccupancyGrid

class WebhookOccupancyGrid(OccupancyGrid):
    def __init__(self, config, geometry_processor, world_width, world_height, 
                 webhook_url):
        super().__init__(config, geometry_processor, world_width, world_height)
        self.webhook_url = webhook_url
        self.last_alert_time = {}
    
    def _update_alerts(self, dt):
        super()._update_alerts(dt)
        
        import time
        current_time = time.time()
        
        # Check for new alerts
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                cell_key = (row, col)
                
                if self.notified[row, col]:
                    # Only send webhook if not sent recently (avoid spam)
                    last_sent = self.last_alert_time.get(cell_key, 0)
                    if current_time - last_sent > 60:  # 60 second cooldown
                        self._send_webhook_alert(row, col)
                        self.last_alert_time[cell_key] = current_time
    
    def _send_webhook_alert(self, row, col):
        """Send webhook notification"""
        import time
        
        payload = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'alert_type': 'overcapacity',
            'cell_row': row,
            'cell_col': col,
            'occupancy': float(self.ema_counts[row, col]),
            'capacity': self.cell_capacity,
            'severity': 'high' if self.ema_counts[row, col] > \
                       self.cell_capacity * 1.2 else 'medium'
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f"Webhook sent for cell ({row},{col})")
            else:
                print(f"Webhook failed: {response.status_code}")
        except Exception as e:
            print(f"Webhook error: {e}")

# Usage
from config import MonitoringConfig
from monitor import CrowdMonitor

config = MonitoringConfig(source=0)
monitor = CrowdMonitor(config)

# Replace occupancy grid with webhook version
webhook_url = "https://your-server.com/alerts"
monitor.occupancy_grid = WebhookOccupancyGrid(
    config,
    monitor.calibrator.geometry_processor,
    monitor.calibrator.world_width,
    monitor.calibrator.world_height,
    webhook_url
)

monitor.initialize()
```

---

### Example 10: Email Alerts

**Scenario**: Send email notifications for critical alerts

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from occupancy import OccupancyGrid

class EmailAlertGrid(OccupancyGrid):
    def __init__(self, config, geometry_processor, world_width, world_height,
                 smtp_server, smtp_port, sender_email, sender_password,
                 recipient_emails):
        super().__init__(config, geometry_processor, world_width, world_height)
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_emails = recipient_emails
        self.alert_sent = {}
    
    def _update_alerts(self, dt):
        super()._update_alerts(dt)
        
        # Send emails for new alerts
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                cell_key = (row, col)
                
                if self.notified[row, col] and not self.alert_sent.get(cell_key):
                    self._send_email_alert(row, col)
                    self.alert_sent[cell_key] = True
                elif not self.notified[row, col] and self.alert_sent.get(cell_key):
                    self.alert_sent[cell_key] = False
    
    def _send_email_alert(self, row, col):
        """Send email notification"""
        import time
        
        subject = f"OVERCAPACITY ALERT - Cell ({row},{col})"
        
        body = f"""
        CROWD MONITORING ALERT
        
        Time: {time.strftime("%Y-%m-%d %H:%M:%S")}
        Location: Grid Cell ({row}, {col})
        
        Current Occupancy: {self.ema_counts[row, col]:.1f} people
        Maximum Capacity: {self.cell_capacity} people
        Overflow: {self.ema_counts[row, col] - self.cell_capacity:.1f} people
        
        Immediate action required to prevent safety hazard.
        
        -- Automated Crowd Monitoring System
        """
        
        try:
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = ', '.join(self.recipient_emails)
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print(f"Email alert sent for cell ({row},{col})")
        except Exception as e:
            print(f"Failed to send email: {e}")

# Usage
config = MonitoringConfig(source=0)
monitor = CrowdMonitor(config)

monitor.occupancy_grid = EmailAlertGrid(
    config,
    monitor.calibrator.geometry_processor,
    monitor.calibrator.world_width,
    monitor.calibrator.world_height,
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    sender_email="alerts@your-domain.com",
    sender_password="your-password",
    recipient_emails=["security@your-domain.com", "manager@your-domain.com"]
)
```

---

### Example 11: Database Logging

**Scenario**: Log all data to SQLite database

```python
import sqlite3
import time
from datetime import datetime
from monitor import CrowdMonitor
from config import MonitoringConfig

class DatabaseMonitor(CrowdMonitor):
    def __init__(self, config, db_path='monitoring.db'):
        super().__init__(config)
        self.db_path = db_path
        self.conn = None
        self.setup_database()
    
    def setup_database(self):
        """Create database tables"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                frame_number INTEGER,
                people_count INTEGER,
                fps REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cell_occupancy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                frame_number INTEGER,
                row INTEGER,
                col INTEGER,
                occupancy REAL,
                capacity INTEGER,
                is_overcapacity BOOLEAN
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                row INTEGER,
                col INTEGER,
                occupancy REAL,
                capacity INTEGER,
                alert_type TEXT
            )
        ''')
        
        self.conn.commit()
    
    def _process_frame(self, frame):
        tracks = super()._process_frame(frame)
        
        # Log every 30 frames
        if self.frame_count % 30 == 0:
            self._log_to_database(tracks)
        
        return tracks
    
    def _log_to_database(self, tracks):
        """Log current state to database"""
        cursor = self.conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log monitoring data
        fps = len(self.fps_counter) / (time.time() - self.fps_start_time) \
              if len(self.fps_counter) > 0 else 0
        
        cursor.execute('''
            INSERT INTO monitoring_data (timestamp, frame_number, people_count, fps)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, self.frame_count, len(tracks), fps))
        
        # Log cell occupancy
        for row in range(self.occupancy_grid.grid_rows):
            for col in range(self.occupancy_grid.grid_cols):
                occupancy = self.occupancy_grid.ema_counts[row, col]
                capacity = self.occupancy_grid.cell_capacity
                is_overcapacity = occupancy > capacity
                
                cursor.execute('''
                    INSERT INTO cell_occupancy 
                    (timestamp, frame_number, row, col, occupancy, capacity, is_overcapacity)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (timestamp, self.frame_count, row, col, occupancy, 
                      capacity, is_overcapacity))
                
                # Log alert if overcapacity
                if is_overcapacity and self.occupancy_grid.notified[row, col]:
                    cursor.execute('''
                        INSERT INTO alerts (timestamp, row, col, occupancy, capacity, alert_type)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (timestamp, row, col, occupancy, capacity, 'overcapacity'))
        
        self.conn.commit()
    
    def __del__(self):
        if self.conn:
            self.conn.close()

# Usage
config = MonitoringConfig(source=0)
monitor = DatabaseMonitor(config, 'crowd_monitoring.db')
monitor.initialize()

# Query database later
conn = sqlite3.connect('crowd_monitoring.db')
cursor = conn.cursor()

# Get average occupancy
cursor.execute('''
    SELECT AVG(people_count), AVG(fps)
    FROM monitoring_data
''')
avg_people, avg_fps = cursor.fetchone()
print(f"Average people: {avg_people:.1f}")
print(f"Average FPS: {avg_fps:.1f}")

# Get alert history
cursor.execute('''
    SELECT timestamp, row, col, occupancy, capacity
    FROM alerts
    ORDER BY timestamp DESC
    LIMIT 10
''')
print("\nRecent alerts:")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
```

---

## Real-World Scenarios

### Example 12: Stadium Section Monitoring

**Scenario**: Monitor different sections of a stadium

```python
from config import MonitoringConfig
from monitor import CrowdMonitor

# Configuration for stadium section
config = MonitoringConfig(
    source=0,
    
    # Large area coverage
    calibration_area_width=40.0,    # 40m wide section
    calibration_area_height=30.0,   # 30m deep
    auto_calibration=True,
    
    # Grid for seating sections
    cell_width=5.0,                  # 5m x 5m cells (section size)
    cell_height=5.0,
    
    # Capacity based on seating density
    person_radius=0.6,               # Seated people need less space
    
    # Detection settings for distance
    confidence_threshold=0.3,        # Lower for distant people
    min_bbox_area=800,               # Smaller boxes at distance
    
    # Alert settings
    hysteresis_time=5.0,             # 5 second delay
    ema_alpha=0.3,                   # More smoothing for crowd
    
    # Performance
    detect_every=5,                  # Don't need every frame
    use_deepsort=False
)

monitor = CrowdMonitor(config)
monitor.initialize()
```

---

### Example 13: Concert Pit Monitoring

**Scenario**: High-density, high-movement area

```python
from config import MonitoringConfig
from monitor import CrowdMonitor

# Configuration for concert pit
config = MonitoringConfig(
    source=0,
    
    # Close-up area
    calibration_area_width=15.0,    # 15m wide pit
    calibration_area_height=10.0,   # 10m deep
    auto_calibration=True,
    
    # Fine-grained grid
    cell_width=1.5,                  # Small cells for detail
    cell_height=1.5,
    
    # Tight packing capacity
    person_radius=0.4,               # Standing, close together
    
    # High-quality detection
    confidence_threshold=0.4,        # Reduce false positives
    min_bbox_area=1500,
    detect_every=2,                  # Frequent detection
    
    # Responsive tracking
    use_deepsort=True,               # Better for movement
    max_age=20,                      # Short age (fast movement)
    
    # Quick alerts
    hysteresis_time=2.0,             # Fast alert (2 seconds)
    ema_alpha=0.5,                   # Responsive
    
    # Alert earlier
    occupancy_warning_threshold=0.7  # Warn at 70%
)

monitor = CrowdMonitor(config)
monitor.initialize()
```

---

### Example 14: Mall Corridor Monitoring

**Scenario**: Linear space with passing traffic

```python
from config import MonitoringConfig
from monitor import CrowdMonitor

# Configuration for mall corridor
config = MonitoringConfig(
    source=0,
    
    # Long narrow area
    calibration_area_width=30.0,    # 30m long corridor
    calibration_area_height=5.0,    # 5m wide
    auto_calibration=True,
    
    # Rectangular cells matching corridor
    cell_width=5.0,                  # 5m segments
    cell_height=2.5,                 # 2.5m width sections
    
    # Walking people
    person_radius=0.5,
    
    # Standard detection
    confidence_threshold=0.35,
    detect_every=3,
    use_deepsort=False,
    
    # Relaxed alerts (people passing through)
    hysteresis_time=10.0,            # Long delay
    ema_alpha=0.2,                   # Heavy smoothing
    
    # Higher threshold (transient occupancy)
    alert_clear_offset=1.0
)

monitor = CrowdMonitor(config)
monitor.initialize()
```

---

### Example 15: Emergency Exit Monitoring

**Scenario**: Critical safety monitoring

```python
from config import MonitoringConfig
from monitor import CrowdMonitor
from occupancy import OccupancyGrid

class EmergencyExitGrid(OccupancyGrid):
    """Custom grid with immediate emergency alerts"""
    
    def _update_alerts(self, dt):
        super()._update_alerts(dt)
        
        # Check for dangerous conditions
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                occupancy = self.ema_counts[row, col]
                capacity = self.cell_capacity
                
                # Emergency threshold (150% capacity)
                if occupancy > capacity * 1.5:
                    self._trigger_emergency_protocol(row, col, occupancy)
    
    def _trigger_emergency_protocol(self, row, col, occupancy):
        """Trigger emergency response"""
        import time
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        print("=" * 60)
        print("🚨 EMERGENCY ALERT 🚨")
        print(f"Time: {timestamp}")
        print(f"Location: Cell ({row},{col})")
        print(f"Occupancy: {occupancy:.1f} (CRITICAL)")
        print(f"Capacity: {self.cell_capacity}")
        print("IMMEDIATE EVACUATION REQUIRED")
        print("=" * 60)
        
        # Here you would:
        # - Trigger alarm system
        # - Open emergency exits
        # - Alert security personnel
        # - Send emergency services notification

# Configuration
config = MonitoringConfig(
    source=0,
    cell_width=2.0,
    cell_height=2.0,
    person_radius=0.45,              # Tight packing expected
    confidence_threshold=0.4,
    detect_every=1,                  # Every frame for safety
    use_deepsort=True,
    hysteresis_time=1.0,             # Quick alert (1 second)
    ema_alpha=0.6                    # Very responsive
)

monitor = CrowdMonitor(config)

# Replace with emergency exit grid
monitor.occupancy_grid = EmergencyExitGrid(
    config,
    monitor.calibrator.geometry_processor,
    monitor.calibrator.world_width,
    monitor.calibrator.world_height
)

monitor.initialize()
```

---

## Custom Implementations

### Example 16: Heatmap Visualization

**Scenario**: Create occupancy heatmap

```python
import cv2
import numpy as np
from visualizer import MonitorVisualizer

class HeatmapVisualizer(MonitorVisualizer):
    """Custom visualizer with heatmap"""
    
    def create_occupancy_heatmap(self, frame, geometry_processor, occupancy_grid):
        """Draw heatmap overlay"""
        overlay = frame.copy()
        
        for row in range(occupancy_grid.grid_rows):
            for col in range(occupancy_grid.grid_cols):
                # Get cell coordinates
                x1 = col * occupancy_grid.config.cell_width
                y1 = row * occupancy_grid.config.cell_height
                x2 = (col + 1) * occupancy_grid.config.cell_width
                y2 = (row + 1) * occupancy_grid.config.cell_height
                
                # Convert to image coordinates
                corners = [
                    geometry_processor.world_to_image_point(x1, y1),
                    geometry_processor.world_to_image_point(x2, y1),
                    geometry_processor.world_to_image_point(x2, y2),
                    geometry_processor.world_to_image_point(x1, y2)
                ]
                
                # Calculate heatmap color
                occupancy = occupancy_grid.ema_counts[row, col]
                capacity = occupancy_grid.cell_capacity
                ratio = min(occupancy / capacity, 1.5)  # Cap at 150%
                
                # Color gradient: Blue → Green → Yellow → Red
                if ratio < 0.5:
                    # Blue to green
                    color = (255, int(ratio * 510), 0)
                elif ratio < 1.0:
                    # Green to yellow
                    color = (255 - int((ratio - 0.5) * 510), 255, 0)
                else:
                    # Yellow to red
                    color = (0, 255 - int((ratio - 1.0) * 510), 0)
                
                # Draw filled polygon
                pts = np.array(corners, np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.fillPoly(overlay, [pts], color)
        
        # Blend overlay with original
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
        
        return frame

# Usage
from config import MonitoringConfig
from monitor import CrowdMonitor

config = MonitoringConfig(source=0)
monitor = CrowdMonitor(config)
monitor.visualizer = HeatmapVisualizer(config, 1280, 720)
monitor.initialize()
```

---

### Example 17: Track History Trails

**Scenario**: Show movement paths

```python
from collections import deque
from trackers import SimpleCentroidTracker

class TrailTracker(SimpleCentroidTracker):
    """Tracker that maintains position history"""
    
    def __init__(self, max_age=30, distance_threshold=80.0, trail_length=30):
        super().__init__(max_age, distance_threshold)
        self.trails = {}  # track_id -> deque of positions
        self.trail_length = trail_length
    
    def update_tracks(self, detections, frame=None):
        tracks = super().update_tracks(detections, frame)
        
        # Update trails
        active_ids = set()
        for track in tracks:
            active_ids.add(track.track_id)
            
            if track.track_id not in self.trails:
                self.trails[track.track_id] = deque(maxlen=self.trail_length)
            
            # Add current position
            cx, cy = track.world_position
            self.trails[track.track_id].append((cx, cy))
        
        # Remove trails for dead tracks
        dead_ids = set(self.trails.keys()) - active_ids
        for track_id in dead_ids:
            del self.trails[track_id]
        
        return tracks

# Custom visualization
def draw_trails(frame, tracker, geometry_processor):
    """Draw movement trails"""
    for track_id, trail in tracker.trails.items():
        if len(trail) < 2:
            continue
        
        # Convert trail to image coordinates
        points = []
        for world_x, world_y in trail:
            img_x, img_y = geometry_processor.world_to_image_point(world_x, world_y)
            points.append((img_x, img_y))
        
        # Draw trail
        for i in range(len(points) - 1):
            # Fade from old to new
            alpha = i / len(points)
            thickness = max(1, int(3 * alpha))
            color = (0, int(255 * alpha), 0)
            
            cv2.line(frame, points[i], points[i + 1], color, thickness)

# Usage
tracker = TrailTracker(trail_length=30)
# Use tracker in your monitoring loop
# Call draw_trails(frame, tracker, geometry_processor) in visualization
```

---

## Performance Benchmarks

### Example 18: FPS Benchmarking

**Scenario**: Test different configurations

```python
import time
import cv2
from config import MonitoringConfig
from detector import PersonDetector
from trackers import SimpleCentroidTracker

def benchmark_configuration(config_name, config, num_frames=300):
    """Benchmark a configuration"""
    print(f"\nBenchmarking: {config_name}")
    print("-" * 60)
    
    # Initialize
    detector = PersonDetector(config)
    detector.load_model()
    tracker = SimpleCentroidTracker()
    
    cap = cv2.VideoCapture(config.source)
    
    # Warm-up
    for _ in range(10):
        ret, frame = cap.read()
        if not ret:
            break
        detections = detector.detect_persons(frame)
        tracker.update_tracks(detections, frame)
    
    # Benchmark
    start_time = time.time()
    frames_processed = 0
    detections_run = 0
    
    for i in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            break
        
        if i % config.detect_every == 0:
            detections = detector.detect_persons(frame)
            detections_run += 1
        else:
            detections = []
        
        tracker.update_tracks(detections, frame)
        frames_processed += 1
    
    elapsed = time.time() - start_time
    fps = frames_processed / elapsed
    
    print(f"Frames processed: {frames_processed}")
    print(f"Detections run: {detections_run}")
    print(f"Time elapsed: {elapsed:.2f} seconds")
    print(f"Average FPS: {fps:.2f}")
    print(f"Time per frame: {1000/fps:.2f} ms")
    
    cap.release()
    return fps

# Test configurations
configs = {
    "High Quality": MonitoringConfig(
        source=0,
        detect_every=1,
        yolo_imgsz=640,
        confidence_threshold=0.4
    ),
    "Balanced": MonitoringConfig(
        source=0,
        detect_every=3,
        yolo_imgsz=640,
        confidence_threshold=0.35
    ),
    "Fast": MonitoringConfig(
        source=0,
        detect_every=5,
        yolo_imgsz=320,
        confidence_threshold=0.3
    ),
    "Ultra Fast": MonitoringConfig(
        source=0,
        detect_every=10,
        yolo_imgsz=320,
        confidence_threshold=0.3
    )
}

results = {}
for name, config in configs.items():
    fps = benchmark_configuration(name, config, num_frames=300)
    results[name] = fps

print("\n" + "=" * 60)
print("BENCHMARK RESULTS")
print("=" * 60)
for name, fps in sorted(results.items(), key=lambda x: x[1], reverse=True):
    print(f"{name:20s}: {fps:6.2f} FPS")
```

---

**These examples cover a wide range of use cases from basic monitoring to advanced integrations and custom
implementations. Adapt them to your specific needs!**
