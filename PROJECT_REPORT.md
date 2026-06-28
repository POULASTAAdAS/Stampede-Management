# Stampede Management System: Project Report

**Report level:** Master degree project report  
**Project:** Stampede Management  
**Basis of report:** Current source code inspection, not outdated documentation  
**Repository inspected:** `Stampede-Management`  
**Date:** 2026-06-28

This report describes the current implementation of the Stampede Management project as found in the source code. It does
not claim measured accuracy, latency, or production readiness beyond what is visible in the implementation. Sample
outputs are illustrative examples derived from the implemented payload schemas.

## 1. Introduction

Stampede Management is a crowd monitoring system designed to detect people from a live camera or video source, track
them over time, estimate crowd density over a calibrated area, and send live monitoring data to a dashboard. The project
combines a Python computer vision application, a Kotlin Spring Boot WebSocket backend, a React/Vite web dashboard, a
Kotlin Multiplatform Android/iOS dashboard client, and local configuration and licensing utilities.

The central purpose of the system is to support early identification of unsafe crowd concentration. Instead of only
counting people in a camera frame, the system maps detected people into a calibrated monitoring region and estimates
occupancy at grid-cell level. This allows the application to report whether specific zones are normal, close to
capacity, or over capacity.

The current system consists of these main parts:

| Layer             | Current implementation                                                                                               | Main source files                                                                                                                              |
|-------------------|----------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| Monitoring client | Python OpenCV/YOLO application for detection, tracking, calibration, occupancy, visualization, and WebSocket sending | `main.py`, `monitor.py`, `detector.py`, `trackers.py`, `calibration.py`, `geometry.py`, `occupancy.py`, `visualizer.py`, `websocket_sender.py` |
| Configuration UI  | Tkinter GUI and native macOS SwiftUI launcher                                                                        | `config_gui.py`, `swift-ui/`                                                                                                                   |
| Backend gateway   | Kotlin Spring Boot WebSocket service for raw monitoring ingestion and dashboard subscriptions                        | `backend/src/main/kotlin/com/poulastaa/backend/`                                                                                               |
| Web dashboard     | React/Vite interface for rooms, live occupancy, radar-style positioning, density grid, and alerts                    | `frontend/src/`                                                                                                                                |
| Mobile dashboards | Kotlin Multiplatform Android/iOS client for the same live room, occupancy, density, and tracked-person data          | `birdsEye/`                                                                                                                                    |
| Licensing         | Offline, machine-tied license validation and activation                                                              | `auth/license_manager.py`, `generate_dev_license.py`                                                                                           |

The report follows the requested root sections and focuses on the actual project implementation.

**Diagram Placeholder 1: High-Level System Overview**  
Aspect ratio: `16:9`  
Suggested replacement: A block diagram showing camera input, Python monitor, backend, and web/mobile dashboards.

Detailed ASCII version:

```text
+------------------+      +---------------------------------------------+      +-----------------------------+
| Camera / Video   | ---> | Python Monitoring Client                    | ---> | Spring Boot Backend         |
| Source           |      | - OpenCV capture                            |      | - /ws-raw ingestion         |
| - Webcam         |      | - YOLO person detection                    |      | - Room registry             |
| - Video file     |      | - Tracking                                 |      | - /ws-dashboard broadcast   |
| - Stream source  |      | - Calibration + occupancy grid             |      | - Latest payload per room   |
+------------------+      | - Local visualization + alerts              |      +--------------+--------------+
                          | - Debounced WebSocket payload sender        |                     |
                          +---------------------------------------------+                     v
                                                                      +-----------------------------+
                                                                      | Operator Dashboards         |
                                                                      | - React web dashboard        |
                                                                      | - birdsEye Android/iOS       |
                                                                      | - Room list + live metrics   |
                                                                      | - Radar + density grid       |
                                                                      | - Alert status               |
                                                                      +-----------------------------+
```

Normal graphical version:

![Dummy high-level system overview diagram, aspect ratio 16:9](https://placehold.co/1600x900?text=Dummy+Diagram:+High-Level+System+Overview+(16:9))

### 1.1 Project Motivation

Crowd monitoring is normally difficult because a human operator has to observe multiple visual signals at the same time.
A single camera feed can show where people are standing, but it does not automatically translate that visual scene into
structured measurements. The system developed in this project tries to close that gap by converting a camera frame into
live numerical and spatial indicators: current person count, active track list, per-cell occupancy, per-cell density,
and alert level.

The motivation is not only to detect the existence of people. The useful output for a crowd safety workflow is the
relation between people and space. For example, two people in a narrow cell can be more important than ten people spread
across a large area. The project therefore treats the monitored region as a calibrated grid. Each grid cell becomes a
local decision area, and each person track can contribute to one or more cells. This design connects computer vision
with operational decision support.

The current source code shows that the project is intended to run as a practical local monitoring application rather
than only as an offline experiment. It has a command-line entry point, a Tkinter configuration GUI, a SwiftUI
configuration launcher for macOS, license activation, OpenCV windows, live WebSocket sending, a backend service, a
browser dashboard, and Android/iOS dashboard clients. These parts indicate that the system is meant to move from raw
frame processing to live operator-facing monitoring.

### 1.2 Project Scope

The scope of the current project includes the following tasks:

| Scope item              | Included in current project                                              |
|-------------------------|--------------------------------------------------------------------------|
| Camera or video input   | Yes, through OpenCV `VideoCapture` in `monitor.py`                       |
| Person detection        | Yes, through YOLO in `detector.py`                                       |
| Person tracking         | Yes, through centroid tracking and optional DeepSort in `trackers.py`    |
| Camera calibration      | Yes, four-point calibration in `calibration.py`                          |
| Ground-plane mapping    | Yes, homography-based projection in `geometry.py`                        |
| Occupancy estimation    | Yes, grid cell counts and EMA smoothing in `occupancy.py`                |
| Alerting                | Yes, overcapacity timers, audio/log alerts, and alert flags              |
| Local visualization     | Yes, OpenCV-based visualizer in `visualizer.py`                          |
| Remote data transport   | Yes, WebSocket payloads in `websocket_sender.py`                         |
| Backend routing         | Yes, Spring Boot WebSocket handlers under `backend/`                     |
| Dashboard visualization | Yes, React components under `frontend/src/`                              |
| Mobile dashboard client | Yes, Kotlin Multiplatform Android/iOS client under `birdsEye/`           |
| Licensing               | Yes, local hardware-tied license validation in `auth/license_manager.py` |

The project scope does not currently include a database-backed analytics system, a complete production security model, a
multi-camera fusion algorithm, automatic camera calibration without user input, or a validated safety certification
process. These are suitable future improvements but are not implemented in the inspected source.

### 1.3 Report Methodology

This report was expanded using source-code inspection rather than relying on older documentation. The report uses the
implementation itself as the reference point. A statement is included only when it can be connected to the current
repository structure, source files, configuration files, or build manifests.

The main source areas inspected are:

| Source area                | Purpose of inspection                                                              |
|----------------------------|------------------------------------------------------------------------------------|
| Python root files          | Understand detection, tracking, calibration, occupancy, visualization, and startup |
| `auth/`                    | Understand license generation, validation, and activation behavior                 |
| `backend/src/main/kotlin/` | Understand WebSocket endpoints, room registry, and backend message flow            |
| `frontend/src/`            | Understand dashboard state, components, and rendering assumptions                  |
| `birdsEye/`                | Understand Android/iOS dashboard client, shared Compose UI, and Ktor WebSocket use |
| `swift-ui/`                | Understand native macOS configuration launcher behavior                            |
| Build and config files     | Understand dependencies, ports, runtime defaults, and packaging constraints        |

The report avoids claims that would require empirical measurement. For example, no specific detection accuracy, FPS
guarantee, maximum crowd size, or deployment capacity is claimed because the source code does not provide controlled
evaluation results. Where examples are shown, they are marked as illustrative samples based on implemented schemas.

### 1.4 Project Contributions

From the current implementation, the main contributions of the project can be stated as follows:

| Contribution               | Explanation                                                                                                             |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------|
| Integrated vision pipeline | The system links camera input, YOLO detection, tracking, calibration, occupancy estimation, alerting, and visualization |
| Localized density model    | The grid design produces cell-level occupancy instead of only full-frame counting                                       |
| Live monitoring transport  | Python payloads are sent to a backend through WebSocket and then distributed to dashboard clients                       |
| Multi-surface operation    | The project can be started from CLI, Tkinter GUI, or SwiftUI configuration launcher                                     |
| Room-based dashboard model | Backend creates logical rooms from device ID or MAC address and supports dashboard subscription                         |
| Cross-platform dashboard   | React web and birdsEye Android/iOS clients consume the same backend dashboard room protocol                             |
| Source-level extensibility | Detection, tracking, occupancy, transport, and visualization are in separate modules                                    |

These contributions are implementation contributions. They show how the project is built and what it currently supports.
They should not be confused with experimental claims such as improved accuracy over other systems, because no such
comparative experiment is present in the source.

### 1.5 Report Boundaries

To keep the report honest and technically useful, the following boundaries are maintained:

| Boundary                                                | Report handling                                                                                             |
|---------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| No unsupported accuracy claims                          | The report describes algorithms and expected behavior, not measured accuracy                                |
| No unsupported production claims                        | Security and persistence limitations are clearly identified                                                 |
| No hidden assumptions about deployment                  | Public and local endpoints are described only where present in code/config                                  |
| No claim of complete automation                         | Calibration still requires user-selected points                                                             |
| No claim of true world coordinates for dashboard tracks | Current tracker positions are image centroids, even though payload fields are named `world_x` and `world_y` |

### 1.6 Report Organization

The report is organized into the eleven root sections requested for the project report. The early sections introduce the
problem and implementation context. The middle sections explain the algorithms and implementation. The later sections
provide samples, conclusions, references, and appendix material. Diagram placeholders are placed where a final report
would normally contain architecture, flow, calibration, monitoring, and dashboard images.

## 2. Problem Analysis

### 2.1 Problem Statement

Crowded areas can become unsafe when local density rises faster than operators can observe manually. A camera view may
show many people, but the safety risk is often local: one gate, corridor, room section, or cell can become overfilled
while the total number of people still appears manageable.

The problem addressed by this project is:

> To monitor a camera-visible area in real time, detect and track people, estimate localized occupancy using a
> calibrated grid, generate alerts when occupancy crosses configured capacity rules, and stream live status to a remote
> dashboard.

### 2.2 Main Actors

| Actor                        | Role in the system                                                                               |
|------------------------------|--------------------------------------------------------------------------------------------------|
| Monitoring operator          | Starts/stops monitoring, selects camera/video source, views alerts and density visualizations    |
| Python monitoring device     | Captures frames, performs detection/tracking, computes occupancy, sends payloads                 |
| Backend gateway              | Receives monitoring payloads, groups them by device/room, distributes updates                    |
| Dashboard user               | Uses browser or mobile dashboards to observe rooms, population, density grid, tracks, and alerts |
| Administrator/license issuer | Generates or supplies machine-specific license data                                              |

### 2.3 Functional Requirements Identified From Source

| Requirement                                    | Current implementation evidence                                                                                                 |
|------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Accept webcam or video file input              | `main.py` parses `--source`; `monitor.py` converts numeric strings to camera indexes and keeps file paths as strings            |
| Detect people                                  | `detector.py` loads `ultralytics.YOLO` and filters class `0` people by confidence and bounding-box area                         |
| Track people                                   | `trackers.py` implements `SimpleCentroidTracker` and optional `DeepSortTracker`                                                 |
| Calibrate camera area                          | `calibration.py` collects four corner points and creates homography-based geometry                                              |
| Convert image detections to world/grid regions | `geometry.py` projects bounding boxes using perspective transform; `occupancy.py` intersects projected polygons with grid cells |
| Smooth occupancy values                        | `occupancy.py` applies exponential moving average with `ema_alpha`                                                              |
| Generate alerts                                | `occupancy.py` uses capacity, hysteresis timers, alert clear offset, and audio notification                                     |
| Display monitoring view                        | `visualizer.py` renders overlays, heatmaps, bird's-eye view, panels, and track annotations                                      |
| Send monitoring data                           | `websocket_sender.py` builds JSON payloads and sends them with debounce                                                         |
| Receive and distribute monitoring data         | Backend `/ws-raw` accepts raw payloads and `/ws-dashboard` serves dashboard subscriptions                                       |
| Visualize remote monitoring data               | `frontend/src/App.jsx` and components render room list, metrics, density grid, radar map, and tracked table                     |
| Visualize remote monitoring data on mobile     | `birdsEye/shared/src/commonMain/` renders the same room, metric, density, and tracked-person concepts                           |
| Validate license before use                    | `main.py`, `config_gui.py`, and Swift UI call `auth/license_manager.py` validation                                              |

### 2.4 Non-Functional Requirements Evident in Code

| Concern               | Current behavior                                                                       |
|-----------------------|----------------------------------------------------------------------------------------|
| Real-time processing  | Detection can run every `N` frames using `detect_every`; FPS counter is maintained     |
| Resilience            | DeepSort falls back to centroid tracking if unavailable; WebSocket sender reconnects   |
| Configurability       | CLI arguments, JSON config, Tkinter GUI, and SwiftUI launcher configure runtime values |
| Remote visibility     | WebSocket dashboard endpoint broadcasts room lists and room updates                    |
| Cross-platform access | Browser, Android, and iOS dashboard clients can consume the live dashboard endpoint    |
| Local operation       | License validation is local/offline; monitor can run from CLI or local UI              |

### 2.5 Constraints and Observed Gaps

The implementation has important constraints:

| Constraint                                                                    | Impact                                                                                                                                  |
|-------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| Calibration assumes a flat rectangular ground plane                           | Uneven floors, ramps, lens distortion, or non-rectangular scenes can reduce spatial accuracy                                            |
| `TrackData.world_position` is set to bounding-box centroid pixels in trackers | Dashboard `world_x/world_y` currently represent image-space centroids, not true calibrated metre coordinates                            |
| Backend room registry is in memory                                            | Room state disappears when backend restarts and cannot scale across instances without shared storage                                    |
| Backend WebSocket origins are unrestricted                                    | Production deployment needs authentication and origin restrictions                                                                      |
| Frontend density grid is fixed at 5x5                                         | Payloads with other grid sizes may not be fully represented in the current UI                                                           |
| Mobile dashboard clients lack separate authentication                         | The Android/iOS client uses the same dashboard WebSocket stream and needs production access control                                     |
| Mobile position map uses fixed coordinate normalization                       | `birdsEye` clamps positions to an 800x600 coordinate model and inherits the current `world_x/world_y` limitation                        |
| Automated tests are limited                                                   | No complete automated verification was found for detection accuracy, calibration correctness, frontend UI, or end-to-end WebSocket flow |

**Diagram Placeholder 2: Problem Domain and Data Movement**  
Aspect ratio: `4:3`  
Suggested replacement: A diagram showing crowd area, camera, monitoring client, backend, and operator dashboards.

Detailed ASCII version:

```text
        Physical Crowd Area
  +--------------------------------+
  | Grid Cell A | Grid Cell B      |
  | People move through monitored  |
  | area and occupy local zones.   |
  +---------------+----------------+
                  ^
                  | camera observes scene
                  |
          +-------+-------+
          | Camera Source |
          +-------+-------+
                  |
                  v
       +---------------------+        structured payload        +------------------+
       | Python Monitor      | -------------------------------> | Backend Gateway  |
       | detect-track-grid   |                                  | rooms + updates  |
       +----------+----------+                                  +--------+---------+
                  |                                                      |
                  | local overlay and siren                              | room_update
                  v                                                      v
       +---------------------+                                  +------------------+
       | Local Operator View |                                  | Dashboards       |
       +---------------------+                                  +------------------+
```

Normal graphical version:

![Dummy problem domain diagram, aspect ratio 4:3](https://placehold.co/1200x900?text=Dummy+Diagram:+Problem+Domain+and+Data+Movement+(4:3))

### 2.6 Detailed Operational Problem

The operational problem can be divided into four smaller problems. First, the system must identify people in a changing
scene. Second, it must maintain a useful representation of those people across time. Third, it must convert the visual
representation into a spatial crowd-density representation. Fourth, it must communicate the result to a user or
dashboard quickly enough to support monitoring decisions.

The first problem is handled by YOLO-based detection. The detector receives a frame and returns bounding boxes for the
configured person class. The second problem is handled by a tracker. The tracker creates persistent IDs and avoids
treating every detection in every frame as a new person. The third problem is handled by calibration, geometric
projection, grid intersection, and occupancy smoothing. The fourth problem is handled by local visualization and
WebSocket communication.

These problems are connected. If detection is weak, tracking becomes unstable. If calibration is wrong, occupancy cells
become inaccurate. If the grid configuration is unsuitable, alerts can be either too sensitive or too slow. If the
WebSocket connection is unavailable, the local monitor can still run, but remote dashboard visibility is affected. This
means the project is not just a single computer vision model; it is a pipeline where each stage affects later stages.

### 2.7 Input Analysis

The system accepts multiple categories of input:

| Input category       | Source in implementation                                                | Notes                                                   |
|----------------------|-------------------------------------------------------------------------|---------------------------------------------------------|
| Video source         | `source` in `MonitoringConfig`, CLI, or JSON                            | Can be a numeric camera index or file path              |
| Model path           | `model_path`                                                            | Used by YOLO loader; fallback download behavior exists  |
| Detection settings   | `confidence_threshold`, `min_bbox_area`, `yolo_imgsz`, `yolo_classes`   | Control sensitivity and runtime cost                    |
| Tracking settings    | `use_deepsort`, `max_age`, `n_init`, `centroid_distance_threshold`      | Control track persistence and matching                  |
| Spatial settings     | `cell_width`, `cell_height`, `person_radius`                            | Control grid size and cell capacity                     |
| Calibration settings | Four image points and real-world width/height                           | Define the transformation from image to monitored plane |
| Alert settings       | `ema_alpha`, `hysteresis_time`, `alert_clear_offset`, warning threshold | Control smoothing and alert behavior                    |
| WebSocket settings   | URL, device ID, device name, location, debounce interval                | Control remote payload delivery                         |
| License file         | `auth/license.dat` in application paths                                 | Required before main monitor execution                  |

The most sensitive inputs are calibration and spatial settings. If a camera watches a large hall but the configured
calibration width and height are too small, the grid cell capacity and density estimates will be misleading. Similarly,
if four calibration points do not match the actual ground region, the homography will map detections to the wrong cell
positions.

### 2.8 Output Analysis

The system produces several kinds of output:

| Output category        | Current implementation                                                                      |
|------------------------|---------------------------------------------------------------------------------------------|
| Local visual output    | OpenCV windows with raw view, grid overlay, detection view, monitoring view, and split view |
| Local logs             | `crowd_monitor.log` through the logging configuration                                       |
| Local alert signal     | Audio/log warning on overcapacity                                                           |
| Screenshot files       | Screenshot capture when enabled and triggered by key input                                  |
| Raw WebSocket payload  | Structured monitoring JSON sent by `websocket_sender.py`                                    |
| Backend response       | Accepted or rejected JSON response from `/ws-raw`                                           |
| Dashboard messages     | `room_list`, `subscribed`, `room_update`, and `error` messages                              |
| Frontend visual output | Room cards, metrics, radar map, density grid, alert banner, and tracked table               |
| Mobile visual output   | birdsEye Android/iOS rooms, summary metrics, position map, density grid, and tracked list   |

The most important output is the relationship between occupancy and alert state. The dashboard and local monitor both
use this information to communicate whether the monitored region is normal, approaching capacity, or critical.

### 2.9 Requirement Traceability

The following table connects major project requirements to source modules:

| Requirement                | Primary implementation                                                 | Secondary implementation                           |
|----------------------------|------------------------------------------------------------------------|----------------------------------------------------|
| Start the monitor          | `main.py`                                                              | `config_gui.py`, `swift-ui/`                       |
| Check license              | `auth/license_manager.py`                                              | `main.py`, `config_gui.py`, Swift services         |
| Load configuration         | `main.py`, `config.py`                                                 | `system_conf.json`, GUI save/load                  |
| Read video                 | `monitor.py`                                                           | OpenCV backend handling                            |
| Detect people              | `detector.py`                                                          | YOLO dependency in `requirements.txt`              |
| Track detections           | `trackers.py`                                                          | DeepSort optional dependency                       |
| Calibrate monitoring plane | `calibration.py`                                                       | `geometry.py`                                      |
| Compute occupancy          | `occupancy.py`                                                         | `geometry.py`, Shapely                             |
| Render local view          | `visualizer.py`                                                        | `window_utils.py`                                  |
| Send payload               | `websocket_sender.py`                                                  | Backend `/ws-raw`                                  |
| Register/update rooms      | `RoomRegistry.kt`                                                      | `RawMonitoringWebSocketHandler.kt`                 |
| Serve dashboard clients    | `DashboardWebSocketHandler.kt`                                         | React `App.jsx`                                    |
| Render dashboard           | `frontend/src/App.jsx`                                                 | Components under `frontend/src/components/`        |
| Render mobile dashboard    | `birdsEye/shared/src/commonMain/kotlin/org/poulastaa/birds_eye/App.kt` | Android `MainActivity.kt`, iOS `ContentView.swift` |

### 2.10 Failure Mode Analysis

The source code already handles some failure situations, while other situations remain open for future work.

| Failure mode               | Current handling                                | Remaining concern                                              |
|----------------------------|-------------------------------------------------|----------------------------------------------------------------|
| YOLO model missing         | Detector attempts download through YOLO         | Network failure or incompatible runtime can still fail startup |
| Camera unavailable         | Monitor logs failure and returns false          | User may need clearer UI recovery in all launchers             |
| Calibration frame unusable | Monitor tries warm-up frames for camera source  | Bad lighting can still produce poor calibration                |
| DeepSort unavailable       | Falls back to centroid tracker                  | Tracking quality may reduce in dense scenes                    |
| WebSocket package missing  | Sender logs disabled/unavailable behavior       | Dashboard will not receive live data from that client          |
| Backend unavailable        | Sender reconnects or skips while disconnected   | Local monitoring continues but remote visibility is lost       |
| Invalid raw JSON           | Backend rejects with `invalid_json`             | No schema-level validation beyond identity and JSON structure  |
| Missing device identity    | Backend rejects with `missing_device_id_or_mac` | Device provisioning workflow is not enforced by backend        |
| Backend restart            | In-memory rooms are lost                        | No persistence or replay exists                                |

### 2.11 Data and Privacy Considerations

The current payload does not send raw video frames to the backend. It sends structured monitoring data: device metadata,
current count, tracked persons, bounding boxes, cell occupancy, alert levels, frame number, and FPS. This is less
sensitive than streaming full video, but it is still operationally meaningful data. Device ID, device name, location,
MAC address, and IP address are included in the payload builder. In a production environment, those fields should be
treated as sensitive operational metadata.

The frontend displays tracked person IDs and coordinates but not faces or raw images. This reduces privacy exposure, but
it does not eliminate privacy responsibilities. A future production deployment should define retention rules, role-based
access, transport security, authentication, and clear policies for how long monitoring data is stored. The inspected
backend does not persist data, which reduces long-term retention risk, but it also limits auditability and historical
analysis.

### 2.12 Problem Complexity

The problem is complex because it combines several domains:

| Domain              | Complexity introduced                                                               |
|---------------------|-------------------------------------------------------------------------------------|
| Computer vision     | Detection depends on lighting, camera angle, occlusion, and model behavior          |
| Tracking            | Identity can change when people cross, disappear, or reappear                       |
| Geometry            | Homography accuracy depends on correct calibration points and flat-plane assumption |
| Real-time systems   | Processing must keep up with camera frames and user expectations                    |
| Distributed systems | WebSocket connections can drop and clients can reconnect                            |
| Human interface     | Operators need clear alerts without excessive false alarms                          |
| Licensing           | Application access is tied to machine-specific validation                           |

The current project addresses these domains in a pragmatic way. It provides a working chain from frame input to
dashboard output, while leaving advanced validation, production security, and long-term analytics for future work.

## 3. Review of Literature

This section is intentionally brief and directly related to the project implementation.

### 3.1 Object Detection for Crowd Monitoring

Modern crowd monitoring systems commonly use convolutional neural network based object detectors to identify people in
image frames. In this project, the detector is implemented with Ultralytics YOLO through `detector.py`. YOLO is suitable
for real-time applications because it performs object localization and classification in a single inference pass. The
implementation filters detections by confidence, target class, and bounding-box area.

### 3.2 Multi-Object Tracking

Tracking is required because frame-by-frame detection alone does not provide persistent identities. The project includes
two approaches:

| Tracking approach | Role in this project                                                                  |
|-------------------|---------------------------------------------------------------------------------------|
| Centroid tracking | Lightweight greedy matching based on Euclidean distance between old and new centroids |
| DeepSort          | Optional tracker using `deep-sort-realtime`, selected when enabled and importable     |

The centroid tracker is simpler and faster but can lose identity during occlusion or dense movement. DeepSort is more
advanced but depends on an additional package and runtime availability.

### 3.3 Perspective Transform and Ground Plane Mapping

A camera image does not directly represent real-world distance. The project uses a four-point perspective transform to
map image coordinates into a rectangular world plane. This is implemented in `calibration.py` and `geometry.py` using
OpenCV homography functions. The method is appropriate when the monitored region can be approximated as a flat plane.

### 3.4 Grid-Based Occupancy Estimation

Crowd safety depends on local density. The project divides the calibrated area into cells and estimates occupancy per
cell. `occupancy.py` projects each detected person bounding box into world coordinates and computes overlap with nearby
grid cells using Shapely polygons. This supports localized warnings instead of only total person count.

### 3.5 Temporal Smoothing and Alert Hysteresis

Raw detection and tracking can fluctuate between frames. The project smooths occupancy using exponential moving average
and avoids instant alert flicker by requiring overcapacity to persist for a configured hysteresis duration. This design
reduces noise in real-time alerts.

### 3.6 WebSocket-Based Live Dashboards

WebSockets are used because monitoring data changes continuously and should be pushed to dashboard clients without
repeated HTTP polling. The backend exposes `/ws-raw` for monitoring payload ingestion and `/ws-dashboard` for web and
mobile dashboard clients.

### 3.7 Relationship Between Literature Concepts and This Project

The concepts above are not used in isolation. The implementation combines them into one practical pipeline. Object
detection supplies bounding boxes. Tracking gives temporal continuity. Homography connects the image plane to an
approximate ground plane. Polygon-grid intersection estimates local occupancy. EMA and hysteresis reduce instability.
WebSockets publish the processed state to dashboard clients. This layered combination is common in applied real-time
monitoring because raw model predictions alone are not enough for an operator-facing system.

The important point for this project is that each technique is used in a restricted and understandable way. YOLO is used
only for the person class. The centroid tracker is a direct nearest-distance method. The homography maps four image
points to a rectangle. The occupancy grid divides the calibrated plane into equal cell sizes. The backend uses room IDs
derived from device ID or MAC address. A dashboard client subscribes to one selected room and renders the latest
payload.
These decisions make the system easier to inspect and explain in an academic report.

### 3.8 Object Detection in the Project Context

Object detection literature often discusses accuracy, precision, recall, and model architecture. The current project
does not include a formal benchmark, so this report cannot claim measured detector performance. The relevant
implementation detail is how detection is used inside the system.

`PersonDetector.detect_persons()` runs YOLO with a configured image size and confidence threshold. It passes a list of
class IDs, where class `0` is the person class. The method then filters invalid boxes and removes boxes smaller than a
configured minimum area. This post-processing is important because very small detections can create unstable tracks and
incorrect occupancy contributions. A small false positive in the background may not matter in a general object-detection
demo, but in this project it could create a grid contribution and eventually affect alert state.

The detector is not run necessarily on every frame. `CrowdMonitor` uses `detect_every` so detection can be performed
every N frames. This allows a tradeoff between computation and responsiveness. Running detection every frame gives
fresher detections but costs more processing time. Running detection less often can improve performance but depends more
heavily on tracker persistence.

### 3.9 Tracking in the Project Context

Multi-object tracking is used here to maintain identity and continuity. The centroid tracker is understandable and fast.
It calculates each detection's center and matches it against existing track positions. This approach can work in simple
scenes where people are separated and movement between frames is moderate.

However, the centroid tracker does not use appearance features, velocity prediction, or global assignment optimization.
It uses greedy matching, so the first suitable match can influence later matches. It can struggle when people cross
paths or are close together. The project includes optional DeepSort support to improve tracking when the external
dependency is installed, but the code still supports fallback operation if DeepSort is unavailable.

In the context of this project, tracking affects both the dashboard and occupancy. Track IDs appear in payloads and the
frontend table. Tracks also determine which bounding boxes are projected into the occupancy grid. A stale track can
continue contributing to occupancy until it ages out. This behavior is useful when detections briefly disappear, but it
can also temporarily overcount if a person leaves the scene and the track persists.

### 3.10 Calibration in the Project Context

Camera calibration in this project is not full intrinsic calibration. It does not estimate lens distortion, focal
length, or camera matrix. Instead, it uses planar perspective calibration with four selected points. This is a practical
approach when the monitored region is a flat floor or rectangular area visible in the camera frame.

The calibration procedure connects image-space detections to real-world cell dimensions. Without calibration, the system
could draw a grid over the image, but the grid would not represent real-world size. With the homography, the project can
define cells in metres and compute cell capacity from `cell_width`, `cell_height`, and `person_radius`.

The limitation is that a bounding box is not the same as a physical footprint. The implementation projects all four
bounding-box corners. For a standing person, the top of the box corresponds to upper body or head, not a point on the
ground. This can enlarge or distort the projected polygon, especially with tilted camera views. The implementation is
still useful for a prototype, but the report must identify this limitation clearly.

### 3.11 Occupancy Estimation in the Project Context

Occupancy estimation in this project is local and fractional. A person polygon can overlap more than one grid cell. The
algorithm adds a fraction of that person to each overlapped cell according to intersection area. This is more
informative than assigning each person only to one cell, because people near a cell boundary can contribute to
neighbouring cells.

The capacity formula uses area. The configured person radius gives an approximate person area. The cell area divided by
person area gives a cell capacity. This is a simplified physical model. It does not model body orientation, movement
direction, personal space standards, or crowd dynamics. Its benefit is that it is transparent, configurable, and easy to
connect to the grid visualization.

### 3.12 Alerting and Human Factors

An alerting system should avoid excessive flicker. If one frame briefly crosses a threshold and the next frame clears,
an immediate alert would be noisy. The project handles this with two techniques. First, EMA smooths occupancy values
over time. Second, hysteresis timers require overcapacity to persist before an alert is triggered and require a drop
below a clear threshold before the alert is cleared.

This behavior is important for a human operator. A monitoring dashboard should not constantly switch between normal and
critical because of detector jitter. At the same time, too much smoothing or too long a hysteresis interval can delay
alerts. The project exposes these values in configuration so the behavior can be tuned for the monitored environment.

### 3.13 Backend, Web Dashboard, and Mobile Clients in the Project Context

The backend follows a simple message gateway pattern. It does not interpret video or run computer vision. Its job is to
receive raw monitoring snapshots, normalize alert fields, store the latest payload per room, and broadcast updates to
dashboard subscribers. This separation keeps the expensive computer vision work on the monitoring client and keeps the
dashboard focused on visualization.

The React dashboard is designed around the idea of live telemetry. It maintains room state, selected room, connection
status, history for sparklines, selected track, and audio alert state. It renders the latest payload rather than
requesting static pages. This is consistent with WebSocket-based monitoring, where the important information is the
current state and recent changes.

The Android and iOS client under `birdsEye/` applies the same dashboard concept through Kotlin Multiplatform and Compose
Multiplatform. Its shared code parses the same backend room messages and presents rooms, summary metrics, a position
map,
a density grid, and tracked-person details. Platform-specific code is limited mainly to app entry points and Ktor
WebSocket engines.

### 3.14 Summary of Review

The literature-related concepts used by this project are well-established: object detection, multi-object tracking,
perspective transform, grid occupancy, smoothing, hysteresis, and WebSocket-based live dashboards. The contribution of
this project is not inventing a new detector or tracker. Its value is in integrating these concepts into a complete
monitoring workflow that moves from camera input to operator-facing alert visualization.

## 4. Formulation / Algorithm

### 4.1 Input Definitions

Let:

| Symbol   | Meaning                                                       |
|----------|---------------------------------------------------------------|
| `F_t`    | Video frame at time `t`                                       |
| `D_t`    | Set of detected person bounding boxes in frame `F_t`          |
| `T_t`    | Set of active tracks after tracker update                     |
| `H`      | Homography matrix from image coordinates to world coordinates |
| `G`      | Occupancy grid over the monitored world plane                 |
| `C[r,c]` | Smoothed occupancy count for grid cell `(r,c)`                |
| `K`      | Cell capacity calculated from cell area and person radius     |

### 4.2 Detection Algorithm

The detector in `detector.py` runs YOLO on a frame with configured image size, confidence threshold, and classes. The
implementation keeps class `0` for people.

For each YOLO box:

1. Clamp bounding box coordinates to the image boundary.
2. Reject invalid boxes where `x2 <= x1` or `y2 <= y1`.
3. Compute area `(x2 - x1) * (y2 - y1)`.
4. Reject boxes below `min_bbox_area`.
5. Return `[x1, y1, x2, y2, confidence]`.

### 4.3 Tracking Algorithm

The centroid tracker in `trackers.py` maintains a dictionary of active tracks. For each detection, the centroid is
calculated as:

```text
cx = (x1 + x2) / 2
cy = (y1 + y2) / 2
```

For each existing track, the tracker searches for the closest unused detection using Euclidean distance:

```text
distance = sqrt((old_cx - new_cx)^2 + (old_cy - new_cy)^2)
```

A match is accepted only if the distance is below `centroid_distance_threshold`. Unmatched detections become new tracks.
Tracks without detections age by one frame and are removed when their age exceeds `max_age`.

When DeepSort is enabled and available, detections are converted into `[left, top, width, height]` with confidence and
class label `person`.

### 4.4 Camera Calibration and Homography

The calibration process maps four clicked image points to a real-world rectangle:

```text
Image points: P1, P2, P3, P4
World points: (0,0), (W,0), (W,H), (0,H)
```

OpenCV computes the homography matrix `H`. For an image point `(x, y)`, world coordinates are computed in homogeneous
form:

```text
[X', Y', Z']^T = H * [x, y, 1]^T
X = X' / Z'
Y = Y' / Z'
```

The inverse homography maps world grid points back into image coordinates for overlay rendering.

### 4.5 Occupancy Grid Formulation

`occupancy.py` creates grid dimensions as:

```text
grid_cols = ceil(world_width / cell_width)
grid_rows = ceil(world_height / cell_height)
```

Cell capacity is calculated from configured cell size and person radius:

```text
person_area = pi * person_radius^2
cell_area = cell_width * cell_height
cell_capacity = max(1, int(cell_area / person_area))
```

Each tracked person's bounding box is projected into a world-space polygon. For every overlapping grid cell, the
contribution is:

```text
contribution = intersection_area(person_polygon, cell_polygon) / person_polygon_area
```

This means one person can contribute fractionally to multiple cells.

### 4.6 Exponential Moving Average

Raw occupancy can fluctuate because detection confidence, occlusion, and tracking state can change between frames. The
project smooths cell counts as:

```text
ema_counts = alpha * current_counts + (1 - alpha) * previous_ema_counts
```

where `alpha` is `config.ema_alpha`.

### 4.7 Alert Algorithm

For every cell:

```text
if ema_count > cell_capacity:
    timer += dt
else:
    timer = max(0, timer - dt)

if timer >= hysteresis_time and alert not already active:
    trigger overcapacity alert

if alert active and ema_count <= cell_capacity - alert_clear_offset:
    clear alert
```

The backend also normalizes incoming alert levels based on cell density. A stale `CRITICAL` cell with density below`1.0`
is downgraded to `WARNING` if density is at least `0.8`, otherwise to `NORMAL`.

### 4.8 End-to-End Runtime Algorithm

```text
Start application
Load configuration
Validate local license
Load YOLO model
Open camera or video source
Read calibration frame
Collect four calibration points
Create homography and occupancy grid
Initialize tracker
Start optional WebSocket sender

For each frame:
    Read frame
    If frame number matches detect_every:
        Run person detection
    Update tracks
    If display mode is Monitoring View or Split View:
        Update occupancy grid
    Build monitoring payload
    Schedule debounced WebSocket send
    Render selected visualization mode
    Process keyboard controls

Stop monitor and release resources
```

**Diagram Placeholder 3: Monitoring Algorithm Flowchart**  
Aspect ratio: `16:9`  
Suggested replacement: A flowchart from video frame to alert and WebSocket payload.

Detailed ASCII version:

```text
+-------+     +-------------+     +-------------+     +--------------+     +----------------+
| Start | --> | Load config | --> | Check       | --> | Load YOLO    | --> | Open video     |
|       |     | / JSON / UI |     | license     |     | model        |     | source         |
+-------+     +-------------+     +-------------+     +--------------+     +--------+-------+
                                                                                   |
                                                                                   v
                                                                        +--------------------+
                                                                        | Calibrate 4 points |
                                                                        | create homography  |
                                                                        +---------+----------+
                                                                                  |
                                                                                  v
 +--------------+     +-------------+     +--------------+     +----------------+     +----------------+
 | Render view  | <-- | Build/send  | <-- | Update       | <-- | Track persons | <-- | Detect persons |
 | handle keys  |     | WS payload  |     | occupancy    |     | across frames  |     | every N frames |
 +------+-------+     +-------------+     +------+-------+     +----------------+     +----------------+
        |                                      |
        | next frame                            v
        +-------------------------------- +----------------+
                                          | Alert decision |
                                          | EMA + timers   |
                                          +----------------+
```

Normal graphical version:

![Dummy monitoring algorithm flowchart, aspect ratio 16:9](https://placehold.co/1600x900?text=Dummy+Diagram:+Monitoring+Algorithm+Flowchart+(16:9))

### 4.9 State Variables Used by the Monitor

The runtime monitor maintains several state variables that control the processing loop. These are visible in
`CrowdMonitor.__init__()` and the processing loop in `monitor.py`.

| State variable                                | Purpose                                                                      |
|-----------------------------------------------|------------------------------------------------------------------------------|
| `frame_count`                                 | Counts processed frames                                                      |
| `last_detection_frame`                        | Stores the most recent frame index where detection was performed             |
| `fps_counter`                                 | Maintains timestamps for rolling FPS calculation                             |
| `fps_start_time`                              | Stores session start time for FPS-related payload information                |
| `display_modes`                               | Maps keyboard mode keys to view names                                        |
| `current_mode`                                | Controls whether raw, grid, detection, monitoring, or split view is rendered |
| `camera_width`, `camera_height`               | Store actual video source dimensions                                         |
| `original_cell_width`, `original_cell_height` | Preserve grid settings for reset behavior                                    |
| `should_stop`                                 | Allows GUI launchers to request monitor stop                                 |
| `ws_sender`                                   | Holds optional WebSocket sender instance                                     |

These state variables matter because the monitoring algorithm is not a stateless frame transformation. It uses time,
frame counts, mode selection, rolling FPS windows, tracker memory, occupancy timers, WebSocket debounce state, and UI
control state.

### 4.10 Detection Scheduling

The source code supports periodic detection through the `detect_every` setting. Conceptually, the frame index determines
whether the detector runs:

```text
if frame_count % detect_every == 0:
    detections = detector.detect_persons(frame)
else:
    detections = [] or previous tracker state is aged/maintained
```

This formulation separates the detection rate from the video frame rate. The practical reason is that YOLO inference is
normally more expensive than simple drawing or tracker updates. If the system detects every frame, the output may be
more responsive. If it detects every third or fifth frame, CPU/GPU load may reduce, but track persistence becomes more
important.

### 4.11 Tracker State Formulation

For centroid tracking, each track can be represented as:

```text
track = (track_id, bbox, position, confidence, age, confirmed)
```

The transition from frame `t` to `t+1` is based on nearest detection centroid. Let an existing track position be
`(cx_i, cy_i)` and a new detection centroid be `(cx_j, cy_j)`. A candidate match exists when:

```text
sqrt((cx_i - cx_j)^2 + (cy_i - cy_j)^2) < centroid_distance_threshold
```

The implementation uses a greedy process over tracks and detections. Once a detection is used, it cannot be assigned to
another track in the same update. This is computationally simple but not globally optimal. A future implementation could
use the Hungarian algorithm or motion prediction if denser crowd tracking becomes necessary.

### 4.12 Bounding Box to Polygon Formulation

Each bounding box is defined in image coordinates:

```text
bbox = (x1, y1, x2, y2)
```

The four corners are:

```text
[(x1,y1), (x2,y1), (x2,y2), (x1,y2)]
```

`GeometryProcessor.project_bbox_to_world()` applies the homography to these corners and creates a Shapely polygon. The
polygon is then used for occupancy. This formulation is direct and easy to implement, but it is also where a major
source of spatial error can enter because a person bounding box includes image height, not only floor contact area.

### 4.13 Cell Search Optimization

The occupancy algorithm does not test every cell for every person polygon. It first calculates polygon bounds:

```text
minx, miny, maxx, maxy = polygon.bounds
```

Then it converts those bounds into candidate grid row and column ranges:

```text
min_col = max(0, int(minx // cell_width))
max_col = min(grid_cols - 1, int(maxx // cell_width))
min_row = max(0, int(miny // cell_height))
max_row = min(grid_rows - 1, int(maxy // cell_height))
```

This reduces the number of intersection tests. Instead of checking all grid cells, the algorithm checks only the cells
within the polygon's bounding range. This is important when the grid becomes larger.

### 4.14 Alert State Machine

Each cell has three relevant pieces of state:

| State                 | Meaning                                                             |
|-----------------------|---------------------------------------------------------------------|
| `ema_counts[row,col]` | Smoothed occupancy estimate                                         |
| `timers[row,col]`     | How long the cell has been above capacity, adjusted down when clear |
| `notified[row,col]`   | Whether an alert has already been raised for the cell               |

The alert process can be described as a small state machine:

| Condition                                         | State transition                           |
|---------------------------------------------------|--------------------------------------------|
| Count below or equal to capacity and not notified | Remain normal, timer decreases toward zero |
| Count above capacity and not notified             | Timer increases                            |
| Timer reaches hysteresis and not notified         | Enter notified state and trigger alert     |
| Notified and count remains high                   | Stay notified                              |
| Notified and count drops below clear threshold    | Clear notification                         |

This logic avoids repeated alert triggers for the same cell while it remains crowded.

### 4.15 Payload Formulation

The monitoring payload can be considered a snapshot function:

```text
payload = f(device_info, tracks, occupancy_grid, frame_count, fps)
```

The payload includes current state, not a complete history. The backend stores only the latest payload for each room.
The frontend therefore displays the current state and locally builds short history arrays for sparklines from received
updates.

Payload-level alert level is computed from cell alert levels. If any cell is critical, the grid is critical. If no cell
is critical but at least one is warning, the grid is warning. Otherwise the grid is normal. The backend repeats a
normalization step to reduce stale critical states when density values do not support them.

### 4.16 Backend Room Identity Formulation

The backend needs a stable key to group messages. It extracts identity in this order:

```text
1. device_info.device_id
2. top-level device_id
3. device_info.mac_address
4. top-level mac_address
```

The resulting room ID is:

```text
device:<device_id>
```

or:

```text
mac:<normalized_mac_address>
```

The room registry increments `messageCount`, updates `lastSeenAt`, stores the latest payload, and notifies listeners.
This is enough for a live dashboard but not enough for historical analytics.

### 4.17 Dashboard Client Subscription Algorithm

The web and mobile dashboard client flow is:

```text
Open WebSocket connection
Send list request
Receive room_list
If no room selected, select first room
Send subscribe for selected room
Receive room_update messages
Update room payload and history
When user selects another room:
    Unsubscribe previous room
    Subscribe new room
```

The backend sends a fresh room list to all dashboard sessions whenever a raw room update arrives. It sends detailed
`room_update` messages only to sessions subscribed to that room.

### 4.18 Complexity Considerations

A simplified complexity view helps explain runtime behavior:

| Stage                | Approximate influencing factors                                           |
|----------------------|---------------------------------------------------------------------------|
| Detection            | YOLO model size, image size, hardware, frame resolution                   |
| Centroid tracking    | Number of active tracks times number of detections                        |
| Occupancy projection | Number of tracks and number of cells overlapped by each projected polygon |
| Visualization        | Frame size, number of tracks, grid size, display mode                     |
| WebSocket sending    | Debounce interval, payload size, backend connectivity                     |
| Dashboard rendering  | Number of rooms, grid cells, tracked persons, update rate                 |
| Mobile client render | Compose layout size, number of rooms, grid cells, and tracked persons     |

The implementation controls runtime cost through `detect_every`, model image size, grid size, display resizing, FPS
counter window, and WebSocket debounce interval.

### 4.19 Algorithmic Limitations

The formulation is intentionally simple and inspectable. It does not use advanced crowd-density estimation models,
optical flow, segmentation, pose estimation, or multi-camera fusion. These could improve some situations, but they would
also add complexity. For a master-level project report, the current formulation is valuable because each algorithmic
step can be explained and traced to source code.

## 5. Problem Discussion

### 5.1 Why the Implemented Approach Fits the Problem

The selected approach is practical for real-time crowd monitoring because it combines person detection, tracking,
spatial calibration, and grid-based alerting. Counting people alone would not identify which part of an area is risky.
The occupancy grid addresses this by dividing the calibrated area into smaller zones.

The use of WebSockets is also appropriate because the dashboard needs live updates. The backend's room model allows
multiple monitoring devices to appear as separate dashboard rooms using device ID or MAC address.

### 5.2 Strengths

| Strength                  | Explanation                                                                                  |
|---------------------------|----------------------------------------------------------------------------------------------|
| Modular source structure  | Detection, tracking, geometry, occupancy, visualization, backend, and frontend are separated |
| Configurable runtime      | CLI, JSON config, Tkinter GUI, and SwiftUI launcher support configuration                    |
| Multiple tracking options | Centroid tracking works as a fallback; DeepSort can be enabled when available                |
| Spatial alerting          | Alerts are based on grid cell capacity rather than only total people count                   |
| Debounced backend sending | `WebSocketSender` sends the latest staged payload at configured intervals                    |
| Remote dashboard support  | Backend, web frontend, and birdsEye client support live room updates over WebSockets         |
| Mobile dashboard support  | birdsEye reuses the dashboard protocol on Android and iOS through shared Compose code        |

### 5.3 Limitations

| Limitation                           | Discussion                                                                                                   |
|--------------------------------------|--------------------------------------------------------------------------------------------------------------|
| Spatial assumptions                  | Homography assumes the monitored area is a flat rectangular plane                                            |
| Bounding-box projection              | The implementation projects full bounding boxes, not only estimated footpoints or body footprints            |
| Current world coordinates in payload | Tracker `world_position` is image-centroid based, so `world_x/world_y` in payloads are not true world metres |
| Display-mode dependency              | Occupancy updates occur only in modes `4` and `5` in `monitor.py`                                            |
| No persistent backend storage        | Rooms and latest payloads are stored in memory only                                                          |
| Limited dashboard grid flexibility   | The frontend currently uses fixed `gridRows=5` and `gridCols=5`                                              |
| Security hardening needed            | Backend WebSocket endpoints allow all origins and do not authenticate clients                                |
| Mobile app hardening needed          | birdsEye has no separate login, notification policy, or production access-control layer                      |
| Limited automated testing            | Source inspection found no comprehensive end-to-end test suite for the full monitoring pipeline              |

### 5.4 Risk Discussion

Crowd safety systems should not depend solely on one camera or a single detection model. Lighting changes, occlusion,
camera angle, and calibration errors can affect the output. Therefore, this implementation should be treated as a
monitoring aid, not as a certified safety system without further validation.

### 5.5 Design Tradeoffs

The project contains several practical engineering tradeoffs.

| Tradeoff                 | Current choice                       | Benefit                                | Cost                                                         |
|--------------------------|--------------------------------------|----------------------------------------|--------------------------------------------------------------|
| YOLO detection frequency | Configurable `detect_every`          | Allows performance tuning              | Lower detection frequency can increase stale tracking        |
| Tracking method          | Centroid fallback, optional DeepSort | Runs even without optional dependency  | Centroid tracking can lose identity in dense scenes          |
| Occupancy model          | Projected bounding-box polygon       | Directly uses existing detector output | Bounding boxes are not exact physical footprints             |
| Backend storage          | In-memory registry                   | Simple and fast                        | No restart recovery or history                               |
| Dashboard grid           | Fixed 5x5 state in React             | Simple rendering                       | Does not fully adapt to arbitrary payload grid sizes         |
| WebSocket security       | Allowed origins set to `*`           | Easy development/testing               | Not production hardened                                      |
| License validation       | Local/offline HMAC license           | Works without server dependency        | Embedded secret and local validation limit security strength |

These tradeoffs are understandable for a prototype or academic implementation. They also define the most important
future engineering work if the system is moved closer to production.

### 5.6 Discussion of Detection Accuracy Risk

The detector uses a general person-detection model. Its output can be affected by camera placement, lighting, low
resolution, motion blur, occlusion, and crowd density. In a crowded environment, people may partially hide one another.
YOLO may merge people, miss people, or produce boxes that do not match full body extent. Because the occupancy algorithm
depends on bounding boxes, any detection error can influence grid counts.

The code partially mitigates noisy detections by filtering confidence and minimum area. However, these thresholds are
configuration values, not automatic guarantees. A high threshold may miss people. A low threshold may include false
positives. A small minimum area may accept distant false detections. A large minimum area may ignore far-away people.
This is why a real deployment would need scene-specific tuning and validation.

### 5.7 Discussion of Tracking Stability

Tracking improves temporal continuity, but it can also carry old errors forward. The centroid tracker ages tracks when
detections are missing and removes them only after `max_age`. This helps when a person is briefly missed by the
detector, but it also means a vanished person can remain active temporarily. The optional DeepSort tracker can improve
identity preservation by using a more advanced tracker, but it is still dependent on detections and runtime
availability.

For an operator, unstable tracking may appear as changing IDs, disappearing dots, or temporary overcount. For occupancy,
unstable tracking can affect cell counts. A future evaluation should measure how long stale tracks remain after a person
exits and how often track IDs switch when people cross.

### 5.8 Discussion of Calibration Sensitivity

Calibration is central to the project. The four clicked points define the transformation between image space and world
space. If the points are clicked inaccurately, every later projection is affected. If the chosen quadrilateral does not
represent the actual floor plane, occupancy estimates can be distorted.

The current implementation allows automatic calibration dimensions, but it still requires the four image points. This is
a reasonable balance between usability and control. Full automatic calibration would require additional assumptions or
scene markers. A future version could support saved calibration profiles, visual validation overlays, or calibration
error estimation.

### 5.9 Discussion of Grid Capacity

The capacity model is simple and transparent. It uses cell area divided by estimated person area. This makes the
configuration understandable: larger cells have higher capacity, and larger person radius reduces capacity. However,
real crowd safety standards can be more complex. They may consider movement direction, emergency exits, density per
square metre, bottlenecks, and local regulations.

In this implementation, `person_radius` is a model parameter rather than a measured physical property. Changing it
changes the capacity calculation and therefore the alert threshold. This makes it powerful but also sensitive. Operators
should not treat the default radius as universally valid without local calibration and policy input.

### 5.10 Discussion of Backend Simplicity

The backend is intentionally lightweight. It accepts raw JSON, identifies a room, stores latest payload, and pushes
updates. This design is sufficient for live display, but it does not validate the full schema, authenticate devices, or
store time series. It also broadcasts full room lists with latest payloads when rooms update. For a small number of
devices this is acceptable. For many rooms or large payloads, this could become inefficient.

The backend's simplicity is useful for the current project because it keeps the architecture understandable. It also
makes the limitations clear. A production backend would likely add a database, schema validation, device registration,
authentication, access control, payload size limits, and monitoring metrics.

### 5.11 Discussion of Dashboard Interpretation

The dashboard is a telemetry interface. It displays metrics and visualizations from the latest payload. The radar map
plots `world_x` and `world_y`, but the current Python trackers assign these values from image centroids. This means the
dashboard's coordinate display should be interpreted as a visual positioning aid, not as a true metre-based map, until
the payload builder or tracker is updated to send calibrated positions.

The density grid gives a useful overview of cell alert levels. The current React implementation uses fixed grid row and
column state, so it should be updated before using arbitrary grid sizes. This is a good example of a frontend-backend
contract issue: the payload contains rows and columns, but the UI currently does not fully derive its layout from them.

The birdsEye mobile dashboard already reads `rows` and `cols` when laying out its shared Compose density grid, but its
position map still normalizes coordinates against an 800x600 model. Therefore, it inherits the same coordinate
interpretation caution as the web radar map until calibrated positions are provided by the monitoring payload.

### 5.12 Ethical and Safety Discussion

Crowd monitoring software can support safety, but it also introduces responsibility. Even if the backend does not
receive video, it receives device metadata and population data. Any deployment should define who can view the dashboard,
how devices are identified, whether data is stored, and how alerts are acted upon.

The system should also avoid giving operators false confidence. A camera-based alert system can miss events outside the
camera view or in poor visibility. The correct operational role is decision support. Human operators and physical safety
procedures remain necessary.

### 5.13 Summary of Discussion

The project is technically coherent and useful as an integrated monitoring prototype. Its strongest part is the
end-to-end connection between computer vision and live dashboard delivery. Its most important weaknesses are spatial
accuracy limitations, simple backend state, limited frontend grid flexibility, mobile app hardening, and lack of full
production security. These weaknesses are not unusual for a project at this stage, but they must be documented honestly
in a master-level report.

## 6. Implementation Details

### 6.1 Python Monitoring Client

The Python application starts from `main.py`. It parses command-line arguments or loads a JSON config file through
`--config-file`. Before starting the monitor, it validates a license using `auth/license_manager.py`. If validation
succeeds, it creates `CrowdMonitor` from `monitor.py`.

Main runtime responsibilities of `CrowdMonitor`:

| Responsibility                       | Source                |
|--------------------------------------|-----------------------|
| Adjust display size for screen       | `monitor.py`          |
| Load YOLO detector                   | `detector.py`         |
| Initialize video capture             | `monitor.py`          |
| Read calibration frame               | `monitor.py`          |
| Run calibration                      | `calibration.py`      |
| Initialize occupancy grid            | `occupancy.py`        |
| Initialize tracker                   | `trackers.py`         |
| Initialize visualization             | `visualizer.py`       |
| Start WebSocket sender               | `websocket_sender.py` |
| Process frames and keyboard controls | `monitor.py`          |

### 6.2 Detection Module

`detector.py` uses `ultralytics.YOLO`. The model path is resolved for development mode and PyInstaller-style packaged
mode. If the model file is missing or too small, the code allows YOLO to download it.

Detection settings are controlled by `MonitoringConfig`, including:

| Field                  | Meaning                                     |
|------------------------|---------------------------------------------|
| `model_path`           | YOLO model path, default `model/yolov8n.pt` |
| `confidence_threshold` | Minimum YOLO confidence                     |
| `min_bbox_area`        | Minimum box area in pixels                  |
| `yolo_imgsz`           | YOLO inference image size                   |
| `yolo_classes`         | Target class IDs, default `(0,)` for person |

### 6.3 Tracking Module

`trackers.py` provides:

| Tracker                 | Behavior                                                                 |
|-------------------------|--------------------------------------------------------------------------|
| `SimpleCentroidTracker` | Greedy nearest-centroid matching with `max_age` and `distance_threshold` |
| `DeepSortTracker`       | Wrapper around `deep-sort-realtime`, used only if installed and enabled  |

The code falls back to centroid tracking if DeepSort cannot be imported or initialized.

### 6.4 Calibration and Geometry

Calibration is handled by `CameraCalibrator` in `calibration.py`. It collects four image points and maps them to a
configured real-world rectangle. `GeometryProcessor` in `geometry.py` stores both homography and inverse homography. It
can project bounding boxes to world-space polygons and map world points back into image coordinates.

### 6.5 Occupancy and Alerting

`OccupancyGrid` in `occupancy.py` calculates grid size, cell capacity, smoothed counts, timers, and alert flags. It uses
Shapely to compute polygon intersections between projected person polygons and grid cells.

Alerting uses:

| Parameter            | Purpose                                                            |
|----------------------|--------------------------------------------------------------------|
| `cell_capacity`      | Maximum expected people per cell based on configured person radius |
| `ema_alpha`          | Smoothing factor for occupancy                                     |
| `hysteresis_time`    | Time over capacity required before notification                    |
| `alert_clear_offset` | Amount below capacity needed to clear an active alert              |

On macOS, the audio alert uses a generated siren WAV and `say`; on other platforms it logs and prints a terminal bell.

### 6.6 WebSocket Payload Sender

`websocket_sender.py` defines dataclasses for outgoing payloads:

| Payload type         | Main contents                                                            |
|----------------------|--------------------------------------------------------------------------|
| `DeviceInfoPayload`  | Device ID, name, location, source, MAC, IP, timestamp                    |
| `PersonTrackPayload` | Track ID, bounding box, confidence, age, confirmation state, coordinates |
| `GridCellPayload`    | Row, column, occupant count, density, alert level                        |
| `PopulationPayload`  | Current count, tracked persons, occupancy grid, alert, frame, FPS        |
| `MonitoringPayload`  | Device info, population data, request ID, capture timestamp              |

The sender uses a debounce interval. During the interval, newer payloads replace older pending payloads; only the latest
payload is sent or logged when the timer fires.

### 6.7 Backend Implementation

The backend is a Kotlin Spring Boot application.

| Backend item                 | Current behavior                                                 |
|------------------------------|------------------------------------------------------------------|
| Runtime port                 | `9990`, from `backend/src/main/resources/application.properties` |
| Raw WebSocket endpoint       | `/ws-raw`, receives monitoring payload JSON                      |
| Dashboard WebSocket endpoint | `/ws-dashboard`, serves live room list and room updates          |
| HTTP endpoint                | `GET /api/rooms`, returns room metadata                          |
| Room storage                 | In-memory `ConcurrentHashMap` in `RoomRegistry.kt`               |
| Room identity                | `device:<device_id>` or `mac:<normalized_mac>`                   |
| Dashboard commands           | `list`, `subscribe`, `unsubscribe`                               |

The raw handler validates that a message is JSON and contains either a device ID or MAC address. It normalizes alert
levels, stores the latest payload, and sends an accepted/rejected response.

### 6.8 Frontend Dashboard

The frontend is a React/Vite dashboard.

| Frontend item               | Current behavior                                                                    |
|-----------------------------|-------------------------------------------------------------------------------------|
| Development port            | `9991`, from `frontend/vite.config.js`                                              |
| Default dashboard WebSocket | `wss://stamped.poulastaa.dev/ws-dashboard` unless `VITE_WS_URL` is set              |
| Room list                   | Stored from `room_list` WebSocket messages                                          |
| Room subscription           | Sends `subscribe` and `unsubscribe` messages                                        |
| Metrics                     | Total occupancy, average density, room risk, processing rate                        |
| Visuals                     | Radar-style positioning map, density grid, tracked-person table, sidebar room cards |
| Alerts                      | Critical siren/voice alert and selected-track overcrowding warning                  |

Main frontend components:

| Component      | Source                                     | Role                                          |
|----------------|--------------------------------------------|-----------------------------------------------|
| `Header`       | `frontend/src/components/Header.jsx`       | Gateway status, audio control, sidebar toggle |
| `Sidebar`      | `frontend/src/components/Sidebar.jsx`      | Room search and selection                     |
| `RoomCard`     | `frontend/src/components/RoomCard.jsx`     | Room summary and sparkline                    |
| `RadarScope`   | `frontend/src/components/RadarScope.jsx`   | Track visualization in an 800x600 SVG space   |
| `DensityGrid`  | `frontend/src/components/DensityGrid.jsx`  | Cell density visualization                    |
| `TrackedTable` | `frontend/src/components/TrackedTable.jsx` | Detailed tracked-person rows                  |

### 6.9 Android and iOS Dashboard Clients

The Android and iOS dashboard client lives under `birdsEye/`. It is a Kotlin Multiplatform project named `birdsEye` that
uses shared Compose Multiplatform code for the operator-facing dashboard UI and platform-specific entry points for
Android and iOS.

| Mobile item                 | Current behavior                                                                                             |
|-----------------------------|--------------------------------------------------------------------------------------------------------------|
| Shared UI                   | `birdsEye/shared/src/commonMain/kotlin/org/poulastaa/birds_eye/App.kt` renders the dashboard                 |
| Shared state and protocol   | `DashboardStore.kt` and `DashboardModels.kt` parse `room_list`, `room_update`, and `error` messages          |
| Default dashboard WebSocket | `wss://stamped.poulastaa.dev/ws-dashboard` from `DefaultDashboardWsUrl`                                      |
| Android entry point         | `androidApp/src/main/kotlin/org/poulastaa/birds_eye/MainActivity.kt` calls `App()`                           |
| Android permission          | `androidApp/src/main/AndroidManifest.xml` declares `android.permission.INTERNET`                             |
| iOS entry point             | `iosApp/iosApp/ContentView.swift` wraps the shared `MainViewController()` from the generated `Shared` module |
| Platform WebSocket engines  | Android uses Ktor OkHttp; iOS uses Ktor Darwin with cellular access allowed                                  |
| Reconnection behavior       | `DashboardStore` reconnects in a coroutine loop after a five-second delay                                    |

The shared mobile UI includes wide and compact layouts, room search, room cards, summary tiles, room details, metric
cards, a position map, a density grid, and tracked-person rows. This makes the mobile client a dashboard consumer rather
than a monitoring device: it does not capture video or run detection, but it subscribes to the same backend room stream
as the React web dashboard.

### 6.10 Licensing and Activation

`auth/license_manager.py` implements local license validation. The machine ID is derived from MAC address, hostname, and
username using SHA-256 and truncated to 32 characters. License data is signed with HMAC-SHA256 using an embedded secret
value. This report does not reproduce the secret.

Validation checks:

1. License file exists.
2. Signature is valid.
3. License machine ID matches the current machine.
4. License has not expired.
5. License `valid` flag is true.

The CLI uses `auth/license.dat`. The Tkinter GUI and SwiftUI launcher also validate license status before allowing
normal monitor use.

### 6.11 Technology Stack

| Area                            | Technology found in source                              |
|---------------------------------|---------------------------------------------------------|
| Computer vision                 | Python, OpenCV, Ultralytics YOLO                        |
| Numeric and geometry processing | NumPy, Shapely                                          |
| Optional tracker                | `deep-sort-realtime`                                    |
| Monitoring transport            | `websocket-client` in Python                            |
| Backend                         | Kotlin, Spring Boot, Java 17, WebSocket, Jackson Kotlin |
| Frontend                        | React 19, Vite, Stitches, Lucide icons                  |
| Mobile dashboard                | Kotlin Multiplatform, Compose Multiplatform, Ktor       |
| Native macOS config UI          | SwiftUI, macOS 13 target                                |

### 6.12 Configuration Model in Detail

The configuration model is centralized in `MonitoringConfig` in `config.py`. This dataclass acts as the contract between
the CLI, GUI launchers, monitor runtime, detector, tracker, occupancy module, visualizer, and WebSocket sender. The use
of one configuration dataclass reduces scattered constants and makes the project easier to control from a JSON file.

The configuration can be divided into several groups:

| Group                | Example fields                                                                                      | Used by                               |
|----------------------|-----------------------------------------------------------------------------------------------------|---------------------------------------|
| Video source         | `source`, `camera_width`, `camera_height`, `camera_fps`                                             | `main.py`, `monitor.py`               |
| Model and detection  | `model_path`, `detect_every`, `confidence_threshold`, `min_bbox_area`, `yolo_imgsz`, `yolo_classes` | `detector.py`, `monitor.py`           |
| Tracking             | `use_deepsort`, `max_age`, `n_init`, `centroid_distance_threshold`                                  | `trackers.py`, `monitor.py`           |
| Spatial grid         | `cell_width`, `cell_height`, `person_radius`                                                        | `occupancy.py`, `visualizer.py`       |
| Smoothing and alerts | `ema_alpha`, `hysteresis_time`, `alert_clear_offset`, `occupancy_warning_threshold`                 | `occupancy.py`, `websocket_sender.py` |
| Display              | `max_birdseye_pixels`, line thicknesses, color tuples, font sizes                                   | `visualizer.py`                       |
| Interactive controls | `enable_screenshots`, `enable_grid_adjustment`                                                      | `monitor.py`                          |
| WebSocket            | `websocket_enabled`, URL, device identity, debounce                                                 | `websocket_sender.py`, `main.py`      |
| Calibration          | point colors, line thickness, area width/height, `auto_calibration`                                 | `calibration.py`                      |

This model makes the system flexible. The same monitor can be tuned for a small room, a corridor, or a larger entrance
by changing source, cell size, detection threshold, and calibration area. However, the same flexibility also introduces
responsibility. Wrong configuration values can produce misleading output. For example, an unrealistic `person_radius`
changes cell capacity. A high `confidence_threshold` can miss people. A small `max_age` can drop tracks quickly, while a
large one can keep stale tracks.

The CLI parser in `main.py` supports both direct command-line options and a JSON file using `--config-file`. When a JSON
file is used, unknown keys are ignored with a warning. This behavior is useful when configuration files include fields
from older or newer versions, but it also means operators should verify that expected keys are actually applied.

### 6.13 Startup Lifecycle

The startup lifecycle is sequential and defensive. The monitor does not enter the processing loop until key requirements
are satisfied.

The sequence is:

1. Change working directory to the project directory so relative paths resolve correctly.
2. Add project and `auth/` directories to Python import path.
3. Parse configuration from CLI or JSON.
4. Validate the local license.
5. Load the detector model.
6. Open the video source.
7. Read a calibration frame.
8. Run camera calibration.
9. Create the occupancy grid.
10. Initialize the tracker.
11. Initialize the visualizer.
12. Start the WebSocket sender if enabled.
13. Enter the processing loop.

This order is important. For example, the occupancy grid cannot be created until calibration provides world width, world
height, and geometry processor. The tracker can be initialized before or after calibration, but in the current
implementation it is initialized after the grid. The visualizer needs camera dimensions from the opened video source.
The WebSocket sender is started only after the core monitoring components are ready.

### 6.14 Video Capture Implementation

The video capture logic is implemented in `monitor.py`. Numeric string sources are converted to integer camera indexes.
Non-numeric strings remain as paths or stream addresses. On macOS, the project attempts to use the native AVFoundation
capture backend when opening integer camera sources. This is a platform-specific detail that improves compatibility with
macOS camera handling.

When a camera source is opened, the code sets width, height, and FPS properties. It then verifies that a frame can be
read. For video files, it resets the frame position to the beginning after the initial read. This prevents the
verification read from skipping the first frame of a file-based run.

The monitor also reads a calibration frame separately. For camera sources, it may attempt up to thirty frames to allow
warm-up. It checks brightness and contrast before accepting a frame. This is a practical detail because many webcams
initially return black or unstable frames.

### 6.15 Detector Loading and Model Resolution

`detector.py` includes resource-path resolution for different runtime modes. In development, it uses the project root.
In a PyInstaller bundle, it checks `_MEIPASS`. It also checks a packaged Windows model layout under
`auth/CrowdMonitor_Package_Windows`. If none of these paths exists, it returns the original relative path and lets YOLO
handle loading or downloading.

The detector checks model file size before accepting an existing model. A file below a minimum size is treated as likely
corrupted. If loading fails, the code attempts to delete the corrupted model and download again. This behavior makes the
detector more robust than a simple one-line model load.

Detection returns plain lists rather than custom classes. Each detection is `[x1, y1, x2, y2, confidence]`. This simple
format is consumed by both tracker implementations. The advantage is low coupling. The disadvantage is that the code
relies on positional list indexes, so future extensions must be careful when adding fields.

### 6.16 Tracker Implementation Details

The centroid tracker stores active tracks in a dictionary keyed by track ID. The next available ID is stored in
`next_id`. Each track is a `TrackData` dataclass from `config.py`. It contains `track_id`, `bbox`, `world_position`,
`confidence`, `age`, and `confirmed`.

The current `world_position` name is somewhat misleading in the tracker context. The centroid tracker sets it to image
centroid coordinates. The DeepSort wrapper also sets it to image centroid coordinates after extracting the bounding box.
The WebSocket payload builder forwards these values as `world_x` and `world_y`. This is an implementation detail that
should be fixed in future work if the dashboard is expected to show calibrated metre positions.

The DeepSort wrapper formats detections in the structure expected by `deep-sort-realtime`: `[left, top, width, height]`,
confidence, and class label. It also filters out unconfirmed tracks when the track object exposes `is_confirmed()`. If
DeepSort raises an error during update, the wrapper logs the error and returns an empty list. This prevents one tracker
failure from crashing the whole monitor loop, but it may temporarily remove active tracks.

### 6.17 Calibration UI and Geometry Data

The calibration module allows the user to click four points. The points are expected to represent the corners of the
monitored area. The source includes visual feedback such as point circles, outlines, connecting lines, and instruction
text. The calibration process uses these points to create the homography matrix and inverse matrix.

The geometry processor is intentionally small. It provides two core operations:

| Operation                           | Method                    | Purpose                             |
|-------------------------------------|---------------------------|-------------------------------------|
| Image bounding box to world polygon | `project_bbox_to_world()` | Used by occupancy estimation        |
| World point to image point          | `world_to_image_point()`  | Used by visualization grid overlays |

The separation is useful because calibration creates the matrices, while geometry uses them. If future work adds saved
calibration profiles or alternative calibration techniques, the geometry processor could remain mostly unchanged.

### 6.18 Occupancy Grid Implementation Details

The occupancy grid stores three arrays with the same shape: smoothed counts, timers, and notification flags. The shape
is `(grid_rows, grid_cols)`. These arrays are initialized when the grid is created and reset when grid dimensions are
reinitialized.

The update method follows a clear process:

1. Create a zero array for current counts.
2. For each active track, project the track bounding box into the world plane.
3. Skip invalid or near-zero-area polygons.
4. Determine candidate cells from polygon bounds.
5. For each candidate cell, build a Shapely box polygon.
6. Compute intersection between person polygon and cell polygon.
7. Add a clipped overlap fraction to the current count.
8. Apply EMA smoothing.
9. Update alert timers and notifications.

The use of fractional contributions makes the occupancy output smoother than a hard single-cell assignment. It also
means cell counts can be decimal values. The dashboard rounds some values for display, but the payload can contain
fractional `occupant_count` values.

### 6.19 Audio Alert Implementation

The Python occupancy module includes platform-specific audio behavior. On macOS, it creates a temporary WAV file
containing a siren-like sweep and plays it with `afplay`. It then uses the `say` command to announce that crowd density
has been reached. On other platforms, it prints a terminal bell and logs a warning.

The code uses a flag `_audio_alert_running` so that multiple alert triggers do not start overlapping alert threads. The
alert sound runs in a daemon thread to avoid blocking the main video processing loop. This is important because audio
playback should not pause detection, tracking, or visualization.

### 6.20 Visualizer Implementation Details

The visualizer draws several kinds of information. It can draw the calibrated grid over the camera image, draw track
annotations, draw cell occupancy labels, create a bird's-eye view, generate an occupancy heatmap, and create an
information panel. The visualization is not only decorative; it helps the operator validate whether calibration, grid
sizing, and tracking are behaving plausibly.

The monitor supports multiple display modes because different debugging and operational situations require different
information. A raw camera view helps confirm input. A grid overlay helps confirm calibration. A detection view helps
inspect bounding boxes. A monitoring view combines tracks and occupancy. A split view provides a combined perspective.

The monitor also resizes display frames to fit screen limits. This avoids windows becoming too large for the user's
display. The screen-size detection includes macOS-specific AppKit and AppleScript attempts, then other fallbacks.

### 6.21 WebSocket Sender Implementation Details

The sender is built around a background connection loop and a debounce timer. When backend requests are enabled, it
starts a daemon thread with `WebSocketApp`. The loop reconnects after failures while `_running` is true. The connection
uses ping settings when running `run_forever()`.

Payload sending is decoupled from frame processing. The monitor calls `schedule(payload)` every frame when sending is
enabled. The sender stores the latest payload and starts a timer if one is not already active. When the timer fires,
`_flush()` serializes the latest payload and sends it if connected. This prevents sending every frame and reduces
backend load.

The sender can also operate in log-only mode when request sending is disabled. This is useful for development and
debugging. In that mode, payload flow can be logged without needing a backend connection.

### 6.22 Raw Backend Handler Details

The raw backend handler receives text messages at `/ws-raw`. It parses the message as JSON. If parsing fails, it sends a
rejected response with reason `invalid_json`. It then normalizes monitoring alert state, extracts room identity, and
rejects messages without device ID or MAC address.

The handler logs accepted requests with session ID, request ID, device ID, room ID, identifier type, people count, alert
level, and payload. It sends an accepted response containing the request ID and room ID. This makes it easier for a
monitoring client to confirm that the backend accepted a payload.

The handler also performs alert normalization. This is an implementation safeguard because the raw payload may contain
stale alert labels. The backend recalculates the grid-level alert from cell alert levels and cell densities. If a cell
says `CRITICAL` but density is below `1.0`, it is downgraded. This adds consistency before dashboard display.

### 6.23 Room Registry Details

`RoomRegistry` is a service with concurrent maps. It stores room metadata and latest payloads. When a payload arrives,
it either creates a new `Room` or updates an existing one. Existing rooms get a new `lastSeenAt` and incremented
`messageCount`. New rooms are initialized with the identifier type and value.

The registry also stores listeners. The dashboard handler registers as a listener after construction. When a room
receives a new payload, the registry calls each listener with the room and raw payload. This is the bridge between raw
ingestion and dashboard broadcasting.

The registry sorts rooms by `roomId` when listing them. This gives deterministic room order. However, the registry has
no expiration policy. If a device sends one payload and then disappears, the room remains until backend restart.

### 6.24 Dashboard Handler Details

The dashboard handler wraps sessions in `ConcurrentWebSocketSessionDecorator` with a five-second send timeout and a 256
KB buffer. This protects the server from some slow-client behavior. It stores sessions by ID and tracks subscriptions by
room ID.

When a dashboard connects, it immediately receives a room list. When it subscribes to a room, the server confirms the
subscription and sends the latest payload if one exists. On every room update, subscribed sessions receive a detailed
`room_update`, and all connected dashboard sessions receive a refreshed room list.

This design is convenient because a dashboard can always show current room metadata. It also means every raw update can
create broad room-list traffic. For a small number of rooms this is simple and acceptable. For a larger deployment, the
backend may need more selective updates.

### 6.25 Frontend State Management Details

The React application stores room list, selected room ID, search query, connection state, radar animation state, audio
mute state, selected track ID, sidebar state, loading state, and history. The WebSocket is stored in a ref so it can be
used by event handlers without being part of normal render state.

When the frontend receives a `room_list`, it stores the list. If no room is selected and at least one room exists, it
selects the first room and sends a subscribe message. When it receives a `room_update`, it replaces the latest payload
for that room and appends the current count to a local thirty-point history array.

The dashboard includes audio behavior for critical alerts. Browser audio requires user permission or interaction, so the
UI asks whether critical siren audio should be enabled. If enabled, the frontend can play a siren tone and use speech
synthesis for critical room alerts. It can also warn when a selected track is inside a warning or critical cell.

### 6.26 Frontend Rendering Details

The frontend renders several data views from the active room payload.

| View          | Data used                                                    |
|---------------|--------------------------------------------------------------|
| Header        | WebSocket connection state and audio mute state              |
| Sidebar       | Room list, search text, selected room ID, population history |
| Metrics row   | Current count, average density, alert level, FPS             |
| Radar scope   | `tracked_persons`, `world_x`, `world_y`, selected track ID   |
| Density grid  | `occupancy_grid.cells`, cell density, cell alert level       |
| Tracked table | Track ID, confidence, age, confirmation, coordinates         |

The dashboard has a strong visual identity, but there are technical assumptions. The radar scope uses an 800 by 600 SVG
coordinate space. The density grid uses fixed row and column state. These assumptions should be aligned with real
payload dimensions in future work.

### 6.27 Tkinter Configuration GUI

The Tkinter GUI in `config_gui.py` provides a local configuration surface. It checks license status before showing the
full configuration UI. It includes tabs for video source, grid/spatial settings, detection, tracking, smoothing/alerts,
visualization, interactive features, and calibration. It can load and save JSON configuration files.

On macOS, the GUI launches `main.py --config-file <temp.json>` as a child process so OpenCV and Cocoa run in the child
process. This is an implementation detail related to platform behavior. On non-macOS platforms, the existing threaded
monitor path is preserved. The GUI also detects cameras asynchronously, and macOS camera detection can be done in a
child Python process to avoid Tk/OpenCV conflicts.

The GUI currently preserves WebSocket metadata from the loaded config and forces WebSocket flow settings to enabled when
collecting config from the UI. This is important for report accuracy because the UI does not expose every WebSocket
field as a normal tab.

### 6.28 SwiftUI Configuration App

The SwiftUI app under `swift-ui/` is a native macOS replacement or companion for the Python configuration UI. It targets
macOS 13 and uses Swift tools 6. It locates the project directory by checking `STAMPEDE_APP_DIR` or climbing directories
until it finds `main.py` and `config.py`.

The Swift services resolve a Python interpreter through `STAMPEDE_PYTHON`, active virtual environment, common venv
directories, or system Python commands. It checks whether `cv2` can be imported. This is a practical requirement because
the monitor cannot run without OpenCV. If OpenCV is missing, the app provides an installation message showing how to
create a virtual environment and install requirements.

The Swift app uses Python snippets to interact with the existing license manager rather than reimplementing license
logic in Swift. It launches the monitor as an external Python process with a temporary JSON config file and cleans up
after exit.

### 6.29 Licensing Implementation Details

The licensing implementation is local and hardware-tied. It uses a machine ID generated from MAC address, hostname, and
username. A license contains machine ID, MAC address, username, customer name, creation time, expiry time, validity
flag, and HMAC signature. Validation loads the license file, verifies signature, compares machine ID, checks expiry, and
checks the valid flag.

This design allows offline validation without a licensing server. It also means license validity depends on local
machine identifiers and local clock. A change in username, hostname, or network identity can affect machine ID. The
embedded signing secret also means the scheme should not be treated as high-security licensing against a determined
attacker. It is sufficient for controlled local activation in the current project context, but production licensing
would require stronger key management.

### 6.30 Dependency and Runtime Requirements

The Python requirements include OpenCV, NumPy, Ultralytics, Shapely, WebSocket client, and optional DeepSort. NumPy
versions are constrained by Python version markers. This indicates the project is intended to work across different
Python versions without installing incompatible NumPy releases.

The backend uses Java 17 and Gradle with Kotlin and Spring Boot plugins. The frontend uses Vite and React. The birdsEye
mobile client uses Gradle, Kotlin Multiplatform, Compose Multiplatform, Ktor, Android tooling, and an Xcode iOS entry
project. The SwiftUI app has no external Swift package dependency in its package manifest. These choices make each
subsystem independently understandable, but they also mean development setup requires multiple toolchains.

| Subsystem        | Toolchain needed                                                |
|------------------|-----------------------------------------------------------------|
| Python monitor   | Python environment with OpenCV, YOLO, Shapely, WebSocket client |
| Backend          | Java 17 and Gradle wrapper                                      |
| Frontend         | Node/npm or compatible JavaScript package manager               |
| Mobile dashboard | Gradle wrapper, Android SDK for Android, Xcode for iOS          |
| SwiftUI launcher | Swift toolchain on macOS                                        |

### 6.31 Implementation Quality Observations

The project shows several good engineering practices:

| Practice               | Example                                                                                           |
|------------------------|---------------------------------------------------------------------------------------------------|
| Modular code           | Separate files for detection, tracking, geometry, occupancy, visualization, backend, and frontend |
| Runtime error handling | Detector load failures, camera failures, tracker fallback, WebSocket reconnect                    |
| Configurable behavior  | Many runtime values are exposed through `MonitoringConfig`                                        |
| Platform awareness     | macOS camera backend, SwiftUI launcher, display-size handling                                     |
| Structured payloads    | WebSocket payload dataclasses define clear output shape                                           |
| Cross-platform client  | birdsEye shares dashboard UI, protocol models, and state flow across Android and iOS              |
| Source-level comments  | Several modules explain purpose and parameters                                                    |

There are also areas for improvement:

| Improvement area         | Reason                                                                      |
|--------------------------|-----------------------------------------------------------------------------|
| Schema validation        | Backend accepts broad JSON and checks only limited fields                   |
| Automated testing        | Vision and UI behavior lack complete tests                                  |
| Security                 | Backend allows all origins and lacks authentication                         |
| Coordinate naming        | Payload `world_x/world_y` currently receive image centroid values           |
| Frontend layout contract | Dashboard should derive grid size from payload rows and cols                |
| Mobile app verification  | birdsEye needs more protocol, UI, and real-device testing                   |
| Persistence              | Backend should persist history if analytics or restart recovery is required |

### 6.32 Implementation Summary

The implementation is a multi-component system rather than a single script. The Python monitor performs the core
real-time analysis. The backend converts device payloads into dashboard rooms. The web and mobile dashboards provide
operator-facing visual telemetry. The configuration UIs make the monitor easier to run. Licensing controls local access.
Together, these pieces form a complete applied project suitable for a master-level report, provided that limitations and
future work are stated clearly.

**Diagram Placeholder 4: Implementation Architecture**  
Aspect ratio: `16:9`  
Suggested replacement: A layered architecture diagram showing Python monitor, backend, and dashboard modules.

Detailed ASCII version:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Presentation Layer                                                           │
│  config_gui.py     swift-ui/      visualizer.py      frontend/src   birdsEye/│
│  Tkinter UI       SwiftUI UI      OpenCV windows     Web + mobile dashboards │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────▼────────────────────────────────────────┐
│ Application Layer                                                            │
│  main.py                 monitor.py                  auth/license_manager.py  │
│  CLI/config parsing       orchestration              license validation       │
└─────────────────────────────────────┬────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────▼────────────────────────────────────────┐
│ Processing Layer                                                             │
│  detector.py             trackers.py             occupancy.py                │
│  YOLO detection          track IDs              grid counts + alerts         │
└─────────────────────────────────────┬────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────▼────────────────────────────────────────┐
│ Geometry and Transport Layer                                                 │
│  calibration.py       geometry.py        websocket_sender.py                 │
│  4-point setup        homography         payload + debounce                  │
└─────────────────────────────────────┬────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────▼────────────────────────────────────────┐
│ Backend Layer                                                                │
│  RawMonitoringWebSocketHandler   RoomRegistry   DashboardWebSocketHandler    │
│  /ws-raw ingestion               rooms          /ws-dashboard updates        │
└──────────────────────────────────────────────────────────────────────────────┘
```

Normal graphical version:

![Dummy implementation architecture diagram, aspect ratio 16:9](https://placehold.co/1600x900?text=Dummy+Diagram:+Implementation+Architecture+(16:9))

## 7. Implementation of Problem

This section explains how the original crowd safety problem is implemented as an operational system.

### 7.1 Step 1: Configure the Monitoring Source

The system accepts configuration from CLI arguments or a JSON config. The checked-in `system_conf.json` includes camera
source, model path, camera dimensions, grid size, detection parameters, tracking settings, calibration area, and
WebSocket settings.

The current config file enables WebSocket sending and points the raw monitoring client to the public raw endpoint.
Sensitive local identifiers in configuration should not be reproduced in a public report.

### 7.2 Step 2: Validate License

Before the monitor starts, `main.py` validates the license through `LicenseManager`. If validation fails, the CLI prints
a machine ID for support and exits. This prevents the main monitoring process from running without a valid local
license.

### 7.3 Step 3: Load Model and Video Source

`CrowdMonitor.initialize()` creates `PersonDetector`, loads the YOLO model, opens the configured camera or video file,
and reads a usable calibration frame. For camera sources, the code attempts warm-up frames before calibration.

### 7.4 Step 4: Calibrate the Scene

The user selects four corners of the monitored area. These image points are mapped to a real-world rectangle with
configured width and height. The homography matrix allows later conversion from image-space detections to grid-space
occupancy.

### 7.5 Step 5: Detect and Track People

During the processing loop, detections are generated periodically based on `detect_every`. The selected tracker then
produces active `TrackData` values. Each track contains a track ID, bounding box, confidence, age, and position.

### 7.6 Step 6: Estimate Occupancy

For each active track, the bounding box is projected into world coordinates as a polygon. The polygon is intersected
with grid cells. Fractional contributions are accumulated, smoothed with EMA, and compared to cell capacity.

### 7.7 Step 7: Generate Alerts

When smoothed occupancy remains above capacity for the hysteresis interval, the system marks the cell as notified and
triggers an audio/log alert. Alerts clear only after occupancy drops enough below capacity.

### 7.8 Step 8: Visualize Locally

The OpenCV interface supports modes:

| Mode key | View            |
|----------|-----------------|
| `1`      | Raw Camera      |
| `2`      | Grid Overlay    |
| `3`      | Detection View  |
| `4`      | Monitoring View |
| `5`      | Split View      |

The monitor also supports screenshot capture, grid-size toggle, reset to original grid, FPS information, and quit
controls.

### 7.9 Step 9: Stream to Backend

The monitoring client builds a structured payload. The sender stages it and sends/logs the latest payload once per
debounce interval. The backend receives this at `/ws-raw`, identifies the room, stores the latest payload, and notifies
dashboard subscribers.

### 7.10 Step 10: Display on Dashboard

The browser dashboard or birdsEye mobile client connects to `/ws-dashboard`, requests room list, subscribes to a
selected
room, receives `room_update` events, and updates live metrics and visualizations.

### 7.11 End-to-End Scenario: Normal Monitoring Session

A normal monitoring session begins with a valid license and a configured camera source. The operator starts the monitor
from the CLI, Tkinter GUI, or SwiftUI launcher. The monitor loads the model and opens the camera. The user performs
calibration by selecting the four corners of the monitored region. After calibration, the monitor enters the live loop.

During a normal session, the local OpenCV window displays the selected view mode. The backend sender prepares payloads
at the configured debounce interval. The backend creates or updates the room corresponding to the device identity. Web
or mobile dashboard clients receive the room list, subscribe to the room, and display live metrics.

The expected operator-facing state in a normal low-density scene is:

| Output              | Expected state                                     |
|---------------------|----------------------------------------------------|
| Local monitor       | Tracks and grid visible if in monitoring mode      |
| Occupancy cells     | Mostly `NORMAL`                                    |
| Audio alerts        | No alert sound                                     |
| Backend response    | `accepted` for valid payloads                      |
| Dashboard room risk | `NORMAL`                                           |
| Dashboard metrics   | Current count and average density update over time |

### 7.12 End-to-End Scenario: Warning or Critical Cell

When people concentrate in a small area, projected person polygons contribute to one or more grid cells. If the smoothed
count approaches configured capacity, the cell can become a warning in the payload. If the count exceeds capacity and
remains high beyond the hysteresis time, the Python occupancy module marks the cell as notified and triggers an alert.

The sequence is:

1. More tracks overlap the same grid cell or nearby cells.
2. `current_counts` increases for those cells.
3. `ema_counts` rises according to `ema_alpha`.
4. If `ema_counts` exceeds capacity, the cell timer increases.
5. If the timer reaches `hysteresis_time`, the alert becomes active.
6. The payload reports cell alert state and room alert state.
7. The backend normalizes alert levels and broadcasts the update.
8. Dashboard clients show the alert message; the web dashboard can trigger audio if enabled.

This sequence demonstrates why smoothing and timers exist. A single noisy frame should not immediately trigger a
critical alert. Persistent density should.

### 7.13 End-to-End Scenario: Backend Not Available

If the backend is not available, the Python monitor can still perform local monitoring. The WebSocket sender tries to
connect and reconnect when request sending is enabled. If a payload is ready while the backend is not connected, the
sender logs a skip message rather than stopping the monitor.

This design separates local safety monitoring from remote dashboard availability. A local operator can still view the
OpenCV monitor. Remote dashboard clients, however, will not receive updates until the backend connection is restored.
This behavior is appropriate for resilience, but a production deployment should show clear backend connection status to
the operator.

### 7.14 End-to-End Scenario: Invalid Backend Payload

The backend rejects invalid raw messages. If a client sends text that is not valid JSON, the response is:

```json
{
  "status": "rejected",
  "reason": "invalid_json"
}
```

If the JSON does not contain a device ID or MAC address, the response is:

```json
{
  "status": "rejected",
  "reason": "missing_device_id_or_mac"
}
```

This validation is minimal but important. The backend must have an identity in order to create a room. Without identity,
the dashboard cannot group updates.

### 7.15 End-to-End Scenario: Dashboard Reconnection

The React frontend marks the gateway offline when the WebSocket closes and schedules a reconnect after five seconds.
This behavior is implemented in the main WebSocket effect in `frontend/src/App.jsx`. When the connection opens again,
the dashboard sends a list request and can resubscribe based on its room-selection behavior.

The birdsEye mobile client follows the same operational idea in `DashboardStore.kt`. It runs a coroutine connection
loop,
marks the state disconnected when the session ends, delays for five seconds, and then attempts to connect again. If a
room is already selected, it sends a subscribe action after reconnecting.

This is important because WebSocket connections can close due to network changes, backend restarts, browser or device
sleep, or deployment reloads. A live dashboard should attempt recovery without requiring a page refresh.

### 7.16 Implementation Mapping to Original Problem

The original problem was to support crowd safety monitoring. The implementation maps each part of that problem to a
concrete module:

| Problem need              | Implementation response                                              |
|---------------------------|----------------------------------------------------------------------|
| Observe a physical area   | OpenCV video capture from camera/video source                        |
| Detect people             | YOLO person detection                                                |
| Avoid frame-only counting | Trackers maintain IDs and state                                      |
| Understand location       | Calibration and homography map image detections to a monitored plane |
| Estimate local crowding   | Occupancy grid and polygon intersections                             |
| Reduce noisy alerts       | EMA smoothing and hysteresis timers                                  |
| Inform local operator     | OpenCV visualization and audio alert                                 |
| Inform remote operator    | WebSocket backend, React dashboard, and birdsEye Android/iOS clients |
| Control usage             | Local license validation                                             |

### 7.17 Data Flow Across Modules

The data flow can be described in terms of transformations:

```text
Frame
  -> Detections
  -> Tracks
  -> Projected polygons
  -> Cell occupancy counts
  -> Smoothed occupancy state
  -> Alert state
  -> Local visualization
  -> Monitoring payload
  -> Backend room update
  -> Web/mobile dashboard visual state
```

Each transformation reduces or restructures information. The raw frame contains visual data. Detections reduce it to
boxes. Tracks add identity. Projected polygons connect boxes to the floor plane. Grid counts convert geometry to
density. Alerts convert density to operator-priority state.

### 7.18 Control Flow Across Components

The control flow is different from data flow. The Python monitor controls frame processing. The WebSocket sender
controls connection and debounce timing. The backend controls room registry and dashboard broadcasting. The frontend
and mobile `DashboardStore` control room selection and UI rendering. These control loops operate independently but
communicate through payloads.

This distributed control structure is useful because a slow dashboard does not directly stop local frame processing.
Similarly, the Python monitor does not need to know how many dashboard clients are connected. The backend mediates that
relationship.

### 7.19 Configuration Workflow

A practical operator workflow is:

1. Open configuration UI.
2. Validate or activate license if needed.
3. Choose camera or video source.
4. Configure grid cell size and person radius.
5. Configure detection threshold and model settings.
6. Configure tracking options.
7. Configure smoothing and alert values.
8. Save configuration to JSON.
9. Start monitoring.
10. Perform calibration.
11. Observe local monitor and dashboard.

This workflow is supported by the Tkinter GUI and partially by the SwiftUI launcher. The CLI supports direct
command-line configuration for users who prefer scripts or automation.

### 7.20 Operational Parameters and Their Effect

The following parameters have strong operational impact:

| Parameter                    | If increased                                     | If decreased                                   |
|------------------------------|--------------------------------------------------|------------------------------------------------|
| `confidence_threshold`       | Fewer detections, possibly fewer false positives | More detections, possibly more false positives |
| `min_bbox_area`              | Ignores small/far boxes                          | Accepts smaller detections                     |
| `detect_every`               | Reduces detection frequency and processing cost  | Increases responsiveness and processing cost   |
| `max_age`                    | Tracks persist longer during missed detections   | Tracks disappear faster                        |
| `cell_width`/`cell_height`   | Fewer, larger cells                              | More, smaller cells                            |
| `person_radius`              | Lower calculated capacity                        | Higher calculated capacity                     |
| `ema_alpha`                  | More responsive smoothing                        | More stable but slower smoothing               |
| `hysteresis_time`            | Alerts require longer sustained crowding         | Alerts trigger faster                          |
| `websocket_debounce_seconds` | Fewer backend updates                            | More frequent backend updates                  |

These parameters should be adjusted carefully. They define the practical behavior of the monitoring system more than the
source code structure alone.

### 7.21 Manual Calibration Procedure

A careful manual calibration procedure should include:

1. Select a camera angle that clearly sees the monitored floor region.
2. Avoid selecting points on walls, railings, or objects above the ground plane.
3. Click the four corners consistently in the expected order.
4. Enter realistic real-world width and height.
5. Confirm that the overlay grid aligns visually with the physical area.
6. Observe a test person walking through the region and verify that grid cell changes look plausible.

The source code supports the calibration mechanism, but it does not automatically verify calibration accuracy. Human
validation is therefore part of the implementation workflow.

### 7.22 Backend Deployment Workflow

The backend is configured to listen on port `9990`. A local deployment workflow is:

1. Start the Spring Boot backend.
2. Confirm `/ws-raw` and `/ws-dashboard` are available.
3. Configure the Python client WebSocket URL to the backend raw endpoint.
4. Configure web or mobile dashboard clients to use the dashboard endpoint.
5. Start a Python monitor and send payloads.
6. Open the React dashboard or birdsEye mobile client and verify that a room appears.

For the public deployment reflected in configuration, the raw endpoint is `wss://stamped.poulastaa.dev/ws-raw` and the
dashboard endpoint is `wss://stamped.poulastaa.dev/ws-dashboard`. Local development may instead use
`ws://localhost:9990/ws-raw` and `ws://localhost:9990/ws-dashboard`.

### 7.23 Dashboard Client Operation Workflow

The dashboard client workflow is:

1. Open the React frontend application or birdsEye Android/iOS app.
2. If using the web dashboard, allow or keep muted the critical siren audio prompt.
3. Wait for WebSocket gateway connection.
4. Select a room from the sidebar or mobile room list.
5. Observe total occupancy, average density, room risk, and processing rate.
6. Inspect the radar scope and density grid.
7. Select a tracked person if detailed track information is needed.
8. Respond to warning or critical alerts according to operational policy.

The dashboard does not currently define the operational policy. It only presents telemetry. The policy for what to do
when a cell becomes warning or critical must be defined by the organization using the system. The birdsEye mobile client
is especially useful for portable viewing, but it should still be treated as a telemetry display rather than an
emergency
procedure system.

### 7.24 Validation Workflow Proposed for Project Evaluation

Although the source includes limited automated testing, a master-level project should describe how the system could be
validated. A practical validation workflow would include:

| Validation target   | Suggested method                                                         |
|---------------------|--------------------------------------------------------------------------|
| Camera capture      | Verify camera opens and produces non-black frames                        |
| Calibration         | Place markers at known floor points and compare projected positions      |
| Detection           | Use labeled video frames to calculate precision and recall               |
| Tracking            | Count ID switches and lost tracks in short test videos                   |
| Occupancy           | Compare cell counts against manually annotated occupancy                 |
| Alert timing        | Simulate sustained overcapacity and measure trigger delay                |
| WebSocket delivery  | Send sample payloads and verify backend acceptance and dashboard update  |
| Dashboard rendering | Test rooms with different payload states: normal, warning, critical      |
| Mobile dashboard    | Build Android/iOS clients and verify room list, subscription, and render |
| License behavior    | Test valid, expired, wrong-machine, and corrupted license files          |

This validation workflow is proposed because the current source does not provide full empirical results.

### 7.25 Implementation Summary of the Problem Solution

The implemented solution transforms an unstructured visual scene into structured operational telemetry. It does this by
chaining detection, tracking, calibration, occupancy, alerting, and WebSocket messaging. The project therefore solves
the practical integration problem: how to move from camera frames to web and mobile dashboards that can display live
crowd-risk state.

**Diagram Placeholder 5: Backend and Dashboard Sequence Diagram**  
Aspect ratio: `21:9`  
Suggested replacement: A sequence diagram showing Python client, `/ws-raw`, room registry, `/ws-dashboard`, and a
dashboard client.

Detailed ASCII version:

```text
Python Monitor          /ws-raw Handler          RoomRegistry          /ws-dashboard Handler        Dashboard Client
     |                        |                       |                         |                         |
     | monitoring payload     |                       |                         |                         |
     |----------------------->| parse JSON            |                         |                         |
     |                        | extract identity      |                         |                         |
     |                        | normalize alert       |                         |                         |
     |                        |---------------------->| create/touch room       |                         |
     |                        |                       | store latest payload    |                         |
     |                        |                       | notify listeners        |                         |
     |                        |                       |------------------------>| onRoomUpdate            |
     | accepted + room_id     |                       |                         | room_update             |
     |<-----------------------|                       |                         |------------------------>|
     |                        |                       |                         | refreshed room_list     |
     |                        |                       |                         |------------------------>|
     |                        |                       |                         |                         |
```

Normal graphical version:

![Dummy backend dashboard sequence diagram, aspect ratio 21:9](https://placehold.co/2100x900?text=Dummy+Diagram:+Backend+and+Dashboard+Sequence+(21:9))

## 8. Sample Output

The following samples are illustrative examples based on implemented payload structures. They are not measured output
from a live camera run.

### 8.1 Sample Monitoring Payload Sent by Python Client

```json
{
  "device_info": {
    "device_id": "camera-01",
    "device_name": "Gate A Camera (camera-01)",
    "location": "Gate A",
    "camera_source": "0",
    "mac_address": "aa:bb:cc:dd:ee:ff",
    "ip_address": "192.168.1.10",
    "timestamp": "2026-06-28T12:00:00Z"
  },
  "population_data": {
    "current_count": 2,
    "tracked_persons": [
      {
        "track_id": 1,
        "bounding_box": {
          "x": 120,
          "y": 80,
          "width": 44,
          "height": 120
        },
        "confidence": 0.91,
        "age": 0,
        "confirmed": true,
        "world_x": 142.0,
        "world_y": 140.0
      }
    ],
    "occupancy_grid": {
      "rows": 5,
      "cols": 5,
      "cells": [
        {
          "row": 1,
          "col": 2,
          "occupant_count": 0.82,
          "density": 0.82,
          "alert_level": "WARNING"
        }
      ],
      "total_occupants": 2,
      "average_density": 0.08
    },
    "alert_level": "WARNING",
    "alert_message": "WARNING: Crowd density approaching capacity in one or more grid cells.",
    "frame_number": 120,
    "fps": 15.2
  },
  "request_id": "00000000-0000-0000-0000-000000000000",
  "captured_at": "2026-06-28T12:00:00Z"
}
```

### 8.2 Sample Backend Acceptance Response

```json
{
  "status": "accepted",
  "request_id": "00000000-0000-0000-0000-000000000000",
  "room_id": "device:camera-01"
}
```

### 8.3 Sample Dashboard Room List Message

```json
{
  "type": "room_list",
  "rooms": [
    {
      "roomId": "device:camera-01",
      "identifierType": "DEVICE_ID",
      "identifierValue": "camera-01",
      "createdAt": "2026-06-28T12:00:00Z",
      "lastSeenAt": "2026-06-28T12:00:03Z",
      "messageCount": 2,
      "latestPayload": {
        "device_info": {
          "device_id": "camera-01"
        },
        "population_data": {
          "current_count": 2,
          "alert_level": "WARNING"
        }
      }
    }
  ]
}
```

### 8.4 Sample Dashboard Room Update Message

```json
{
  "type": "room_update",
  "roomId": "device:camera-01",
  "data": {
    "population_data": {
      "current_count": 2,
      "alert_level": "WARNING",
      "alert_message": "WARNING: Crowd density approaching capacity in one or more grid cells."
    }
  }
}
```

### 8.5 Sample Invalid JSON Response

If the raw backend endpoint receives a text message that cannot be parsed as JSON, the implemented handler returns:

```json
{
  "status": "rejected",
  "reason": "invalid_json"
}
```

This output is important because it confirms that the backend does not silently accept malformed messages. It also gives
the sending client a simple reason string for logging or debugging.

### 8.6 Sample Missing Identity Response

If the backend receives valid JSON but cannot find a device ID or MAC address, it returns:

```json
{
  "status": "rejected",
  "reason": "missing_device_id_or_mac"
}
```

This behavior follows from the room registry design. Without a device or MAC identity, the backend cannot create a
stable `roomId`.

### 8.7 Sample Dashboard Subscribe Command

A dashboard client subscribes to a room using:

```json
{
  "action": "subscribe",
  "roomId": "device:camera-01"
}
```

The server confirms with:

```json
{
  "type": "subscribed",
  "roomId": "device:camera-01"
}
```

If a latest payload is already stored for that room, the backend sends it immediately as a `room_update` message after
confirming the subscription.

### 8.8 Sample Dashboard Error Message

If a dashboard client sends an unknown action, the backend can reply with:

```json
{
  "type": "error",
  "message": "unknown_action"
}
```

If the dashboard command is malformed JSON, the backend can reply with:

```json
{
  "type": "error",
  "message": "invalid_json"
}
```

### 8.9 Sample Occupancy Cell States

The occupancy grid cells can represent different local states. The following table is an illustrative interpretation of
payload fields.

| Cell state | Example payload fields                                          | Meaning                                |
|------------|-----------------------------------------------------------------|----------------------------------------|
| Normal     | `occupant_count: 0.2`, `density: 0.2`, `alert_level: NORMAL`    | Cell is below warning/critical level   |
| Warning    | `occupant_count: 0.85`, `density: 0.85`, `alert_level: WARNING` | Cell is approaching capacity           |
| Critical   | `occupant_count: 1.2`, `density: 1.0`, `alert_level: CRITICAL`  | Cell is at or above capacity condition |

In the Python sender, density is capped to `1.0` when serialized. Therefore, overload magnitude is more visible through
`occupant_count` and `alert_level` than through density alone.

### 8.10 Sample Local Log Flow

The exact log formatting depends on the logger configuration, but the following messages represent the kinds of events
implemented by the source code:

```text
Initializing Enhanced Crowd Monitoring System...
Loading YOLO model: model/yolov8n.pt
Successfully connected to video source: 0
Camera resolution: 1280x720
Starting camera calibration...
Grid initialized: 2x2 cells, capacity: 1 per cell
Using simple centroid tracker
WebSocket sender started -> wss://stamped.poulastaa.dev/ws-raw
Starting interactive video processing loop
[WS READY] reason=debounce request_enabled=True device=camera-01 people=2 alert=WARNING frame=120 request_id=...
[WS SENT] device=camera-01 people=2 alert=WARNING frame=120 request_id=...
```

This sample is illustrative. It is based on implemented logger calls, but it is not copied from a measured run.

### 8.11 Sample CLI Usage

The monitor can be started with a camera source:

```bash
python main.py --source 0
```

It can also be started with a JSON configuration file:

```bash
python main.py --config-file system_conf.json
```

To use local backend endpoints during development, a user could configure a raw WebSocket URL such as:

```bash
python main.py --source 0 --websocket-url ws://localhost:9990/ws-raw
```

These examples are based on the current CLI parser. They assume dependencies and license are already valid.

### 8.12 Sample Frontend Environment Configuration

The frontend defaults to the public dashboard WebSocket endpoint. For local development, the dashboard WebSocket URL can
be set with `VITE_WS_URL` before running Vite. An example environment value is:

```text
VITE_WS_URL=ws://localhost:9990/ws-dashboard
```

This value is consumed by `frontend/src/App.jsx`. If it is not set, the frontend uses the configured public WSS
endpoint.

### 8.13 Sample Mobile Dashboard Commands

The birdsEye client is built from the `birdsEye/` Gradle project. From `birdsEye/`, the Android debug application can be
assembled with:

```bash
./gradlew :androidApp:assembleDebug
```

The shared Android host tests and iOS simulator tests are exposed as Gradle tasks:

```bash
./gradlew :shared:testAndroidHostTest
./gradlew :shared:iosSimulatorArm64Test
```

The iOS application entry point is under `birdsEye/iosApp/`; it is intended to be opened and run from Xcode. These
commands and locations are based on the current birdsEye README and Gradle project structure.

### 8.14 Sample Test Case Table

The following table describes sample tests that should be included in a final evaluation. They are not all present as
automated tests in the current source.

| Test case             | Input                                                   | Expected output                                      |
|-----------------------|---------------------------------------------------------|------------------------------------------------------|
| Valid monitor payload | JSON with `device_info.device_id` and `population_data` | Backend returns `accepted` with `room_id`            |
| Missing identity      | JSON without device ID or MAC                           | Backend returns `missing_device_id_or_mac`           |
| Invalid JSON          | Non-JSON text                                           | Backend returns `invalid_json`                       |
| Dashboard list        | `{"action":"list"}`                                     | Backend returns `room_list`                          |
| Dashboard subscribe   | Existing or future `roomId`                             | Backend returns `subscribed`                         |
| Overcapacity cell     | Payload with critical cell density                      | Dashboard receives `room_update` with critical state |
| Mobile room list      | birdsEye connected to `/ws-dashboard`                   | Android/iOS client displays rooms from `room_list`   |
| Camera unavailable    | Invalid camera index                                    | Monitor fails initialization and logs error          |
| License missing       | No license file                                         | CLI prints license error and machine ID              |

### 8.15 Sample Evaluation Record Template

A master report can include an evaluation table like this after running real tests:

| Experiment ID | Scene                   | Camera            | Config file        | Expected result                     | Observed result | Notes                        |
|---------------|-------------------------|-------------------|--------------------|-------------------------------------|-----------------|------------------------------|
| EXP-01        | Empty room              | Webcam 0          | `system_conf.json` | Count near zero                     | To be measured  | Validate false positives     |
| EXP-02        | One person walking      | Webcam 0          | `system_conf.json` | One active track                    | To be measured  | Validate tracking continuity |
| EXP-03        | Two people in same cell | Webcam 0          | `system_conf.json` | Warning/critical depending capacity | To be measured  | Validate occupancy alert     |
| EXP-04        | Backend disconnected    | Webcam 0          | local config       | Local monitor continues             | To be measured  | Validate resilience          |
| EXP-05        | Dashboard reconnect     | Browser dashboard | local backend      | Reconnect after close               | To be measured  | Validate UI recovery         |
| EXP-06        | Mobile dashboard        | Android/iOS app   | local backend      | Room list and updates render        | To be measured  | Validate birdsEye client     |

### 8.16 Sample Acceptance Criteria

The following acceptance criteria are reasonable for the current prototype stage:

| Area        | Acceptance criterion                                                        |
|-------------|-----------------------------------------------------------------------------|
| Startup     | Application should not enter monitoring loop without valid license          |
| Detection   | Person detections should produce bounding boxes above configured threshold  |
| Tracking    | Active tracks should persist through short detector gaps within `max_age`   |
| Calibration | Grid overlay should visually align with selected monitored area             |
| Occupancy   | Cell counts should increase when tracked people occupy that area            |
| Alerting    | Alert should trigger only after hysteresis time when over capacity          |
| WebSocket   | Valid payload should create or update backend room                          |
| Dashboard   | Subscribed room should update metrics when backend receives new payload     |
| Mobile app  | Android/iOS client should display room updates through shared protocol code |

These criteria are descriptive. They should be converted into automated and manual test procedures for a final evaluated
deployment.

### 8.17 Local Visual Output Placeholders

**Diagram Placeholder 6: Calibration Screen**  
Aspect ratio: `4:3`  
Suggested replacement: Screenshot showing four clicked calibration points on the camera frame.

Detailed ASCII version:

```text
+--------------------------------------------------+
| Calibration Window                               |
|                                                  |
|   P1 ●--------------------------------● P2       |
|      |                                |           |
|      |        monitored floor         |           |
|      |        rectangle / area        |           |
|      |                                |           |
|   P4 ●--------------------------------● P3       |
|                                                  |
| Instructions: click four corners clockwise.      |
| Press c to confirm, ESC to cancel.               |
+--------------------------------------------------+
```

Normal graphical version:

![Dummy calibration screenshot placeholder, aspect ratio 4:3](https://placehold.co/1200x900?text=Dummy+Screenshot:+Calibration+Screen+(4:3))

**Diagram Placeholder 7: Monitoring View**  
Aspect ratio: `16:9`  
Suggested replacement: Screenshot showing camera feed, bounding boxes, grid overlay, occupancy values, and alert panel.

Detailed ASCII version:

```text
+--------------------------------------------------------------------------------+
| Enhanced Crowd Monitor - Monitoring View                                       |
|                                                                                |
|  Camera frame with calibrated grid overlay                                      |
|  +-------------------+-------------------+-------------------+                 |
|  | Cell 0,0          | Cell 0,1          | Cell 0,2          |                 |
|  | 0.0 / cap NORMAL  | 1.0 / cap WARNING | 0.0 / cap NORMAL  |                 |
|  +-------------------+-------------------+-------------------+                 |
|  | Cell 1,0          | Cell 1,1          | Cell 1,2          |                 |
|  | 0.0 / cap NORMAL  | [Track #3 bbox]   | 1.2 / cap CRIT   |                 |
|  +-------------------+-------------------+-------------------+                 |
|                                                                                |
|  Bottom panel: People=3 | Alerts=1 | FPS=15.2 | Mode=Monitoring              |
+--------------------------------------------------------------------------------+
```

Normal graphical version:

![Dummy monitoring view screenshot placeholder, aspect ratio 16:9](https://placehold.co/1600x900?text=Dummy+Screenshot:+Monitoring+View+(16:9))

**Diagram Placeholder 8: Web Dashboard**  
Aspect ratio: `16:9`  
Suggested replacement: Screenshot showing room list, occupancy metrics, radar map, density grid, and tracked table.

Detailed ASCII version:

```text
+--------------------------------------------------------------------------------+
| STAMPEDE SYSTEM DASHBOARD                         Gateway: ONLINE              |
+----------------------+---------------------------------------------------------+
| Rooms Sidebar        | Active Room: DEVICE:CAMERA-01                            |
| - camera-01          | +-----------+ +-------------+ +----------+ +-----------+ |
| - entrance-west      | | Occupancy | | Avg Density | | Risk     | | FPS       | |
| - gate-b             | | 12        | | 48%         | | WARNING  | | 15.2 Hz   | |
| Search rooms...      | +-----------+ +-------------+ +----------+ +-----------+ |
|                      |                                                         |
|                      | +-----------------------+ +---------------------------+ |
|                      | | Live Positioning Map  | | Occupancy Density Grid    | |
|                      | | dots = tracked people | | cells = normal/warn/crit  | |
|                      | +-----------------------+ +---------------------------+ |
|                      |                                                         |
|                      | +-----------------------------------------------------+ |
|                      | | Tracked Persons Table: ID, confidence, age, coords | |
|                      | +-----------------------------------------------------+ |
+----------------------+---------------------------------------------------------+
```

Normal graphical version:

![Dummy web dashboard screenshot placeholder, aspect ratio 16:9](https://placehold.co/1600x900?text=Dummy+Screenshot:+Web+Dashboard+(16:9))

**Diagram Placeholder 9: Mobile Dashboard**
Aspect ratio: `9:16`
Suggested replacement: Screenshot of the birdsEye Android or iOS app showing room list, room metrics, density grid, and
tracked people.

Detailed ASCII version:

```text
+------------------------------+
| birdsEye              Online |
| Live crowd dashboard         |
+------------------------------+
| Gateway: Live | Rooms: 2     |
+------------------------------+
| Rooms                        |
| Search rooms, cameras...     |
| - Entrance Camera  WARNING   |
| - North Exit       NORMAL    |
+------------------------------+
| Entrance Camera              |
| Occupancy 12 | Density 48%   |
| Risk WARNING | Rate 15 Hz    |
+------------------------------+
| Position map                 |
| Density grid                 |
| Tracked people               |
+------------------------------+
```

Normal graphical version:

![Dummy mobile dashboard screenshot placeholder, aspect ratio 9:16](https://placehold.co/900x1600?text=Dummy+Screenshot:+Mobile+Dashboard+(9:16))

## 9. Conclusion / Future Scope of Work

### 9.1 Conclusion

The Stampede Management project implements a complete prototype-level crowd monitoring pipeline. It captures video,
detects and tracks people, calibrates image coordinates to a monitored area, estimates grid-based occupancy, produces
alerts, streams structured payloads to a backend, and presents live data in web and mobile dashboards.

The source code shows a modular design that separates vision processing, tracking, geometry, occupancy, visualization,
backend transport, dashboard rendering, configuration, and licensing. This makes the project suitable as a master-level
applied software engineering and computer vision project.

The most important technical achievement is localized crowd risk estimation. Rather than only reporting total population
count, the system computes cell-level occupancy and alert state, which is closer to the actual safety problem.

### 9.2 Future Scope of Work

| Future work                                              | Reason                                                                                                                |
|----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| Use calibrated footpoint positions for `world_x/world_y` | Dashboard coordinates should represent real-world position, not image centroids                                       |
| Make frontend density grid dynamic                       | UI should render payload `rows` and `cols` instead of fixed 5x5 values                                                |
| Add persistent backend storage                           | Room history, replay, analytics, and restart recovery require a database                                              |
| Add backend authentication                               | Raw monitoring clients and dashboard users should be authenticated                                                    |
| Restrict WebSocket origins                               | Production deployment should not allow all origins                                                                    |
| Harden mobile dashboards                                 | Android/iOS clients need authentication, notification policy, and real-device validation before production use        |
| Add end-to-end tests                                     | Detection pipeline, WebSocket delivery, dashboard rendering, and alert logic need automated validation                |
| Add camera/lens calibration                              | Distortion correction can improve spatial accuracy                                                                    |
| Add multi-camera support                                 | Larger areas may require multiple cameras and identity fusion                                                         |
| Add privacy controls                                     | Crowd systems should minimize personally identifiable data and support retention policies                             |
| Measure accuracy and performance                         | A formal report should include FPS, false positive/negative behavior, calibration error, and alert delay measurements |

### 9.3 Technical Conclusion

Technically, the project demonstrates the integration of multiple software layers into one working monitoring concept.
The Python application performs the computationally heavy work and produces structured snapshots. The backend acts as a
lightweight real-time gateway. The web frontend and birdsEye mobile client turn snapshots into dashboard views. The
configuration and licensing tools make the application usable outside a pure development script.

The strongest technical part is the traceable data pipeline. A frame becomes detections, detections become tracks,
tracks become projected polygons, polygons become grid contributions, grid contributions become smoothed occupancy
counts, and counts become alert states. This chain is easy to explain, debug, and improve because each stage is
implemented in a separate source module.

The largest technical weakness is that several values are named or displayed as world-space values even though the
tracker stores image centroids. This does not break the basic pipeline, but it matters for the dashboard positioning map
and any future claim about real-world coordinates. Correcting this should be a high-priority improvement.

### 9.4 Academic Conclusion

From an academic perspective, the project is a useful applied system because it combines computer vision, geometry,
real-time communication, frontend visualization, and software engineering. It is not only an algorithm demonstration; it
is a full-stack implementation that connects local sensing to remote monitoring.

The project also provides several discussion points suitable for a master degree report: calibration assumptions,
density estimation, alert stability, distributed telemetry, privacy implications, and production-readiness gaps. These
topics show that the project requires engineering judgement, not only programming ability.

### 9.5 Practical Conclusion

Practically, the current system can be used as a prototype for monitoring a camera-visible area and presenting live
status. It can help operators observe occupancy patterns and test alert behavior. However, before it is used for real
safety-critical decisions, it needs structured validation, better security, calibration accuracy checks, and operational
procedures.

The system should be introduced as a decision-support tool. It should not replace human supervision, emergency planning,
physical crowd-control measures, or certified safety systems.

### 9.6 Short-Term Future Work

Short-term improvements are changes that can be made within the current architecture.

| Improvement                         | Description                                                            | Expected benefit                          |
|-------------------------------------|------------------------------------------------------------------------|-------------------------------------------|
| Correct dashboard coordinate source | Send calibrated positions or rename fields to image coordinates        | Prevents misleading map interpretation    |
| Dynamic frontend grid               | Use payload `rows` and `cols` in `DensityGrid`                         | Supports arbitrary grid sizes             |
| Add JSON schema validation          | Validate raw payload structure at backend                              | Reduces invalid or partial payload issues |
| Add frontend error states           | Show missing payload, stale room, and backend reconnect status clearly | Improves operator understanding           |
| Add mobile dashboard tests          | Cover birdsEye protocol parsing, room selection, and rendering states  | Improves Android/iOS reliability          |
| Add unit tests for occupancy        | Test capacity, smoothing, and alert timer behavior                     | Increases confidence in core logic        |
| Add backend handler tests           | Test accepted/rejected payload cases and room updates                  | Improves gateway reliability              |

### 9.7 Medium-Term Future Work

Medium-term improvements require more design but can still build on the current system.

| Improvement                      | Description                                                  | Expected benefit                                 |
|----------------------------------|--------------------------------------------------------------|--------------------------------------------------|
| Persistent storage               | Store rooms, payload history, and alert events in a database | Enables history, analytics, and restart recovery |
| Authentication and authorization | Require device tokens and dashboard user login               | Makes deployment safer                           |
| Calibration profiles             | Save and reload calibration points per camera                | Reduces repeated manual setup                    |
| Better position estimation       | Use bottom-center footpoint projection or segmentation       | Improves spatial accuracy                        |
| Alert policy configuration       | Define warning/critical thresholds per room or cell          | Supports different venue layouts                 |
| Dashboard playback               | Replay past room state over time                             | Supports analysis after incidents                |

### 9.8 Long-Term Future Work

Long-term improvements move the project toward a more advanced crowd intelligence platform.

| Improvement               | Description                                                 | Expected benefit                   |
|---------------------------|-------------------------------------------------------------|------------------------------------|
| Multi-camera fusion       | Combine multiple camera views into one occupancy model      | Covers larger or complex venues    |
| Edge deployment packaging | Package monitor as a managed edge device service            | Improves deployment reliability    |
| Advanced density models   | Use segmentation or crowd-density estimation networks       | Better performance in dense crowds |
| Predictive alerts         | Predict near-future overcrowding from movement trends       | Allows earlier intervention        |
| Role-based dashboards     | Different views for operators, administrators, and analysts | Improves usability and security    |
| Formal safety validation  | Validate against venue-specific safety standards            | Required for critical use cases    |

### 9.9 Recommended Evaluation Metrics

Future evaluation should measure both computer vision performance and system behavior.

| Metric                       | Meaning                                                            |
|------------------------------|--------------------------------------------------------------------|
| Detection precision          | Fraction of detected people that are true people                   |
| Detection recall             | Fraction of actual people that are detected                        |
| Tracking ID switches         | Number of times identities change incorrectly                      |
| Track persistence error      | Time stale tracks remain after a person leaves                     |
| Calibration projection error | Difference between known floor points and projected points         |
| Cell count error             | Difference between estimated and manually annotated cell occupancy |
| Alert trigger delay          | Time between true overcapacity and system alert                    |
| Alert false positive rate    | Alerts generated when cell is not truly over capacity              |
| End-to-end latency           | Time from frame capture to dashboard update                        |
| Backend update throughput    | Number of room updates handled per second                          |
| Dashboard recovery time      | Time to reconnect after WebSocket close                            |
| Mobile dashboard recovery    | Time for birdsEye to reconnect and resubscribe after network loss  |

### 9.10 Final Statement

The Stampede Management project is a strong base for a master-level applied project because it demonstrates a complete
pipeline and exposes meaningful future research and engineering directions. The current implementation is not perfect,
but it is sufficiently structured to be analyzed, extended, tested, and improved. Its main value is the integration of
vision-based sensing with spatial occupancy reasoning and live operational visualization.

## 10. Reference

### 10.1 Source Code References

| Area                      | Source files inspected                                                                                                                 |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| CLI and startup           | `main.py`                                                                                                                              |
| Runtime orchestration     | `monitor.py`                                                                                                                           |
| Configuration data        | `config.py`, `system_conf.json`                                                                                                        |
| Detection                 | `detector.py`                                                                                                                          |
| Tracking                  | `trackers.py`                                                                                                                          |
| Calibration               | `calibration.py`                                                                                                                       |
| Geometry                  | `geometry.py`                                                                                                                          |
| Occupancy and alerting    | `occupancy.py`                                                                                                                         |
| Visualization             | `visualizer.py`                                                                                                                        |
| WebSocket payload sending | `websocket_sender.py`                                                                                                                  |
| Licensing                 | `auth/license_manager.py`, `generate_dev_license.py`                                                                                   |
| Python dependencies       | `requirements.txt`                                                                                                                     |
| Backend WebSockets        | `backend/src/main/kotlin/com/poulastaa/backend/WebSocketConfig.kt`, `RawMonitoringWebSocketHandler.kt`, `DashboardWebSocketHandler.kt` |
| Backend room registry     | `backend/src/main/kotlin/com/poulastaa/backend/RoomRegistry.kt`, `Room.kt`, `RoomController.kt`                                        |
| Backend build/runtime     | `backend/build.gradle.kts`, `backend/src/main/resources/application.properties`                                                        |
| Frontend dashboard        | `frontend/src/App.jsx`, `frontend/src/components/`                                                                                     |
| Frontend build/runtime    | `frontend/package.json`, `frontend/vite.config.js`                                                                                     |
| Mobile dashboard clients  | `birdsEye/shared/src/commonMain/kotlin/org/poulastaa/birds_eye/`, `birdsEye/androidApp/`, `birdsEye/iosApp/`                           |
| Mobile build/runtime      | `birdsEye/build.gradle.kts`, `birdsEye/shared/build.gradle.kts`, `birdsEye/gradle/libs.versions.toml`, `birdsEye/settings.gradle.kts`  |
| macOS native UI           | `swift-ui/Package.swift`, `swift-ui/Sources/StampedeConfigSwift/`                                                                      |

### 10.2 Conceptual and Technology References

| Topic                         | Reference type                                             |
|-------------------------------|------------------------------------------------------------|
| YOLO object detection         | Ultralytics YOLO framework and object-detection literature |
| Multi-object tracking         | Centroid tracking and Deep SORT tracking concepts          |
| Perspective transform         | OpenCV homography and perspective transform documentation  |
| Polygon intersection          | Shapely geometric operations documentation                 |
| Real-time dashboard transport | WebSocket protocol concepts                                |
| Backend implementation        | Spring Boot WebSocket and Kotlin/JVM concepts              |
| Frontend implementation       | React and Vite application concepts                        |
| Mobile client implementation  | Kotlin Multiplatform, Compose Multiplatform, and Ktor      |

## 11. Appendix (Program Code)

This appendix includes the most important code-level structures and pseudocode extracted from the current
implementation. The complete program code remains in the repository files listed in the references.

### 11.1 Core Runtime Entry Point

Source: `main.py`

```python
config = parse_arguments()
license_manager = LicenseManager(license_file=str(AUTH_DIR / 'license.dat'))
is_valid, message = license_manager.validate_license()

if not is_valid:
    print(f"License Error: {message}")
    return 1

monitor = CrowdMonitor(config)
success = monitor.initialize()
```

### 11.2 Detection Output Shape

Source: `detector.py`

```python
detections.append([x1, y1, x2, y2, conf])
```

This output is consumed by `trackers.py`.

### 11.3 Centroid Tracking Logic

Source: `trackers.py`

```text
For each existing track:
    Find closest unused detection centroid
    If distance is below threshold:
        Update bbox, centroid, confidence, age=0
    Else:
        Increase track age

For each unmatched detection:
    Create new track ID

Remove tracks where age > max_age
```

### 11.4 Occupancy Update Logic

Source: `occupancy.py`

```python
current_counts = np.zeros_like(self.ema_counts)

for track in tracks:
    polygon, _ = self.geometry_processor.project_bbox_to_world(track.bbox)
    if polygon is None or polygon.area <= 1e-6:
        continue

    for row, col in overlapping_cells:
        intersection = polygon.intersection(cell_polygon)
        if not intersection.is_empty:
            overlap_fraction = intersection.area / polygon.area
            current_counts[row, col] += max(0.0, min(1.0, overlap_fraction))

self.ema_counts = (
    self.config.ema_alpha * current_counts
    + (1.0 - self.config.ema_alpha) * self.ema_counts
)
```

### 11.5 Alert Logic

Source: `occupancy.py`

```text
If smoothed cell occupancy is greater than capacity:
    Increase timer
Else:
    Decrease timer down to zero

If timer reaches hysteresis time and cell is not already notified:
    Mark notified and play/log alert

If notified cell drops below capacity minus clear offset:
    Clear alert
```

### 11.6 WebSocket Payload Builder

Source: `websocket_sender.py`

```python
population = PopulationPayload(
    current_count=len(tracks),
    tracked_persons=tracked_persons,
    occupancy_grid=occ_grid_payload,
    alert_level=grid_alert,
    alert_message=alert_message,
    frame_number=frame_count,
    fps=round(fps, 2),
)

return MonitoringPayload(device_info=device_info, population_data=population)
```

### 11.7 Backend Room Creation

Source: `backend/src/main/kotlin/com/poulastaa/backend/RoomRegistry.kt`

```kotlin
val room = rooms.compute(identifier.roomId) { _, existing ->
    existing?.apply {
        lastSeenAt = Instant.now()
        messageCount += 1
    } ?: Room(
        roomId = identifier.roomId,
        identifierType = identifier.type,
        identifierValue = identifier.value,
        messageCount = 1,
    )
}!!
```

### 11.8 Dashboard WebSocket Commands

Source: `DashboardWebSocketHandler.kt`, `frontend/src/App.jsx`, and
`birdsEye/shared/src/commonMain/kotlin/.../DashboardStore.kt`

```json
{
  "action": "list"
}
{
  "action": "subscribe",
  "roomId": "device:camera-01"
}
{
  "action": "unsubscribe",
  "roomId": "device:camera-01"
}
```

### 11.9 Program File Map

```text
Stampede-Management/
  main.py                         CLI entry point
  monitor.py                      Runtime orchestrator
  detector.py                     YOLO person detector
  trackers.py                     Centroid and DeepSort tracking
  calibration.py                  Four-point camera calibration
  geometry.py                     Homography projection helpers
  occupancy.py                    Grid occupancy and alert logic
  visualizer.py                   OpenCV rendering
  websocket_sender.py             Monitoring payload builder/sender
  config.py                       Runtime dataclasses and defaults
  config_gui.py                   Tkinter configuration UI
  auth/license_manager.py         Local license validation and activation
  backend/src/main/kotlin/...     Kotlin Spring Boot backend
  frontend/src/...                React dashboard
  birdsEye/androidApp/...         Android dashboard app entry point
  birdsEye/iosApp/...             iOS SwiftUI app entry point
  birdsEye/shared/src/...         Shared Compose dashboard client
  swift-ui/...                    Native macOS SwiftUI configuration app
```

### 11.10 MonitoringConfig Field Dictionary

The following dictionary summarizes important configuration fields and how they affect the application. It is based on
`config.py` and current runtime usage.

| Field                         | Category    | Purpose                                                   |
|-------------------------------|-------------|-----------------------------------------------------------|
| `source`                      | Video       | Camera index or video file path                           |
| `model_path`                  | Detection   | YOLO model file path                                      |
| `camera_width`                | Video       | Requested camera capture width                            |
| `camera_height`               | Video       | Requested camera capture height                           |
| `camera_fps`                  | Video       | Requested camera frame rate                               |
| `cell_width`                  | Occupancy   | Width of one grid cell in metres                          |
| `cell_height`                 | Occupancy   | Height of one grid cell in metres                         |
| `person_radius`               | Occupancy   | Radius used for person area and cell capacity calculation |
| `detect_every`                | Detection   | Number of frames between detection runs                   |
| `confidence_threshold`        | Detection   | Minimum confidence for YOLO detections                    |
| `min_bbox_area`               | Detection   | Minimum bounding-box area accepted as a person            |
| `yolo_imgsz`                  | Detection   | YOLO inference image size                                 |
| `yolo_classes`                | Detection   | Target YOLO classes; person is class `0`                  |
| `use_deepsort`                | Tracking    | Selects DeepSort when available                           |
| `max_age`                     | Tracking    | Maximum frames to keep unmatched tracks                   |
| `n_init`                      | Tracking    | Confirmation setting for DeepSort                         |
| `centroid_distance_threshold` | Tracking    | Maximum centroid match distance                           |
| `ema_alpha`                   | Occupancy   | Smoothing factor for cell counts                          |
| `fps`                         | Timing      | Expected FPS for timing calculations                      |
| `hysteresis_time`             | Alert       | Time over capacity required before alert                  |
| `alert_clear_offset`          | Alert       | Drop below capacity required to clear alert               |
| `occupancy_warning_threshold` | Alert       | Warning threshold as capacity fraction                    |
| `enable_screenshots`          | Interaction | Enables screenshot key behavior                           |
| `enable_grid_adjustment`      | Interaction | Enables runtime grid toggle                               |
| `websocket_enabled`           | Transport   | Enables payload building/sender path                      |
| `websocket_request_enabled`   | Transport   | Enables actual backend WebSocket sending                  |
| `websocket_url`               | Transport   | Raw backend WebSocket endpoint                            |
| `websocket_device_id`         | Transport   | Device identity used for backend rooms                    |
| `websocket_device_name`       | Transport   | Human-readable device name                                |
| `websocket_location`          | Transport   | Location label in payload                                 |
| `websocket_debounce_seconds`  | Transport   | Interval between sent/logged snapshots                    |
| `calibration_area_width`      | Calibration | Real-world width mapped from selected region              |
| `calibration_area_height`     | Calibration | Real-world height mapped from selected region             |
| `auto_calibration`            | Calibration | Skips dimension prompt but not four-point selection       |

### 11.11 TrackData Structure

`TrackData` represents one active tracked person.

| Field            | Meaning                             | Current source behavior                                              |
|------------------|-------------------------------------|----------------------------------------------------------------------|
| `track_id`       | Unique track identifier             | Incremented by centroid tracker or provided by DeepSort              |
| `bbox`           | Bounding box `(x1, y1, x2, y2)`     | Used for projection and visualization                                |
| `world_position` | Position tuple                      | Currently image centroid from trackers                               |
| `confidence`     | Detection confidence                | From detector for centroid tracker; set to `1.0` in DeepSort wrapper |
| `age`            | Frames since last matched detection | Used by centroid tracker for expiry                                  |
| `confirmed`      | Confirmation flag                   | Default true in dataclass; DeepSort wrapper skips unconfirmed tracks |

### 11.12 Monitoring Payload Field Dictionary

The monitoring payload is the contract between the Python monitor and backend.

| Field path                                       | Meaning                               |
|--------------------------------------------------|---------------------------------------|
| `device_info.device_id`                          | Stable device identifier              |
| `device_info.device_name`                        | Human-readable device name            |
| `device_info.location`                           | Operator-defined location             |
| `device_info.camera_source`                      | Camera or video source value          |
| `device_info.mac_address`                        | Local MAC address or configured value |
| `device_info.ip_address`                         | Local IP address when available       |
| `device_info.timestamp`                          | Device info timestamp                 |
| `population_data.current_count`                  | Number of active tracks               |
| `population_data.tracked_persons`                | List of active track payloads         |
| `population_data.occupancy_grid.rows`            | Grid row count                        |
| `population_data.occupancy_grid.cols`            | Grid column count                     |
| `population_data.occupancy_grid.cells`           | Per-cell occupancy data               |
| `population_data.occupancy_grid.total_occupants` | Rounded total smoothed occupants      |
| `population_data.occupancy_grid.average_density` | Average density across cells          |
| `population_data.alert_level`                    | Overall room/grid alert level         |
| `population_data.alert_message`                  | Human-readable alert message or null  |
| `population_data.frame_number`                   | Frame count at capture                |
| `population_data.fps`                            | Rolling FPS estimate                  |
| `request_id`                                     | Unique payload/request ID             |
| `captured_at`                                    | Payload capture timestamp             |

### 11.13 Backend Message Dictionary

| Message                | Direction                           | Purpose                                  |
|------------------------|-------------------------------------|------------------------------------------|
| Raw monitoring payload | Python client to `/ws-raw`          | Send latest monitoring snapshot          |
| `accepted` response    | `/ws-raw` to Python client          | Confirm payload was accepted             |
| `rejected` response    | `/ws-raw` to Python client          | Reject invalid JSON or missing identity  |
| `list` action          | Dashboard client to `/ws-dashboard` | Request current room list                |
| `subscribe` action     | Dashboard client to `/ws-dashboard` | Subscribe to one room                    |
| `unsubscribe` action   | Dashboard client to `/ws-dashboard` | Stop receiving one room's updates        |
| `room_list`            | `/ws-dashboard` to dashboard client | Send available rooms and latest payloads |
| `subscribed`           | `/ws-dashboard` to dashboard client | Confirm room subscription                |
| `room_update`          | `/ws-dashboard` to dashboard client | Send latest data for subscribed room     |
| `error`                | `/ws-dashboard` to dashboard client | Report invalid command or JSON           |

### 11.14 Extended Pseudocode: Main Processing Loop

```text
last_time = current_time()
while monitor is running:
    if external stop requested:
        break

    ret, frame = video_capture.read()
    if frame not available:
        break

    frame_count += 1
    now = current_time()
    dt = now - last_time
    last_time = now

    append now to fps_counter
    trim fps_counter to configured window

    tracks = process_frame(frame)

    if current display mode is Monitoring View or Split View:
        occupancy_grid.update(tracks, dt)

    if websocket sender exists:
        payload = build_payload(tracks, occupancy_grid, frame_count, fps_counter, config)
        websocket_sender.schedule(payload)

    display_frame = create_visualization(frame, tracks)
    resize display_frame if needed
    show display_frame in OpenCV window

    key = wait for keyboard input
    handle mode changes, screenshot, grid toggle, reset, FPS, or quit
```

### 11.15 Extended Pseudocode: Backend Raw Handler

```text
on raw websocket text message:
    try parse text as JSON
    if parse fails:
        send rejected invalid_json
        return

    normalize monitoring payload alert fields

    identifier = device_id from device_info or top-level field
    if no device_id:
        identifier = mac_address from device_info or top-level field

    if no identifier:
        send rejected missing_device_id_or_mac
        return

    room = roomRegistry.createOrTouchRoom(identifier, normalizedPayload)
    send accepted response with request_id and room_id
```

### 11.16 Extended Pseudocode: Dashboard Handler

```text
on dashboard websocket connect:
    wrap session in concurrent session decorator
    store session
    send room_list

on message:
    parse JSON
    if action == list:
        send room_list
    if action == subscribe:
        add session ID to room subscription set
        send subscribed confirmation
        if latest room payload exists:
            send room_update
    if action == unsubscribe:
        remove session ID from room subscription set
    else:
        send error

on room update from registry:
    send room_update to sessions subscribed to that room
    send refreshed room_list to all dashboard sessions
```

### 11.17 Extended Pseudocode: Frontend WebSocket Flow

```text
on component mount:
    choose wsUrl from VITE_WS_URL or default public endpoint
    open WebSocket

on open:
    set connected true
    send list action

on room_list:
    update rooms state
    if no selected room and list is not empty:
        select first room
        send subscribe action

on room_update:
    update matching room's latest payload
    append current_count to local history for that room

on close:
    set connected false
    reconnect after delay while component is active

on room selection:
    unsubscribe previous room
    subscribe selected room
    reset selected track
```

### 11.18 Extended Pseudocode: Mobile Dashboard Store Flow

Source: `birdsEye/shared/src/commonMain/kotlin/org/poulastaa/birds_eye/DashboardStore.kt`

```text
create DashboardStore with default dashboard WebSocket URL

start:
    if connection job is already active:
        return

    launch coroutine loop:
        while active:
            connect to dashboard WebSocket
            mark connected
            send list action
            if a room is already selected:
                send subscribe action for that room

            for each incoming text frame:
                if type is room_list:
                    parse rooms
                    if no room is selected and list is not empty:
                        select first room
                        send subscribe action
                if type is room_update:
                    update or add room snapshot
                    append current_count to 30-point room history
                if type is error:
                    store error message

            mark disconnected when session ends
            wait five seconds before reconnecting

select room:
    store selected room ID and clear selected track
    if connected:
        unsubscribe previous room
        subscribe selected room
```

### 11.19 Proposed Database Schema for Future Work

The current backend does not use a database. If persistence is added later, a possible schema could be:

| Table             | Fields                                                              | Purpose                                |
|-------------------|---------------------------------------------------------------------|----------------------------------------|
| `devices`         | `id`, `device_id`, `mac_address`, `name`, `location`, `created_at`  | Store registered devices               |
| `rooms`           | `id`, `room_id`, `device_id`, `created_at`, `last_seen_at`          | Store logical monitoring rooms         |
| `payloads`        | `id`, `room_id`, `request_id`, `captured_at`, `payload_json`        | Store raw monitoring snapshots         |
| `alerts`          | `id`, `room_id`, `level`, `message`, `started_at`, `cleared_at`     | Store alert events                     |
| `cell_snapshots`  | `id`, `payload_id`, `row`, `col`, `count`, `density`, `alert_level` | Query occupancy at cell level          |
| `dashboard_users` | `id`, `username`, `role`, `created_at`                              | Support authenticated dashboard access |

This schema is not implemented. It is included as future design material for a complete report.

### 11.20 Proposed API Contract Improvements

The current backend uses WebSocket JSON messages without a formal schema file. Future work can define JSON schemas for:

| Schema                    | Purpose                                                   |
|---------------------------|-----------------------------------------------------------|
| Monitoring payload schema | Validate Python client payloads                           |
| Dashboard command schema  | Validate list/subscribe/unsubscribe messages              |
| Room list schema          | Document dashboard room response shape                    |
| Room update schema        | Document live update response shape                       |
| Error schema              | Standardize backend error messages                        |
| Mobile dashboard schemas  | Keep birdsEye shared models aligned with backend messages |

Formal schemas would make frontend, backend, and Python client development safer. They would also support automated
contract tests.

### 11.21 Proposed Unit Test List

| Test file area            | Proposed tests                                                                         |
|---------------------------|----------------------------------------------------------------------------------------|
| `detector.py`             | Filter invalid boxes, filter small boxes, handle model-not-loaded state                |
| `trackers.py`             | Create tracks, match by distance, age unmatched tracks, remove expired tracks          |
| `geometry.py`             | Project known points with test homography, handle invalid boxes                        |
| `occupancy.py`            | Grid dimension calculation, capacity calculation, EMA update, alert timer, alert clear |
| `websocket_sender.py`     | Build payload fields, debounce behavior, log-only mode                                 |
| Backend raw handler       | Invalid JSON, missing identity, accepted payload, alert normalization                  |
| Backend dashboard handler | List, subscribe, unsubscribe, room update broadcast                                    |
| Frontend components       | Render normal/warning/critical cells, room selection, empty dashboard state            |
| birdsEye shared client    | Parse room messages, filter rooms, update selected room, maintain history              |
| License manager           | Valid license, invalid signature, expired license, wrong machine ID                    |

### 11.22 Proposed Manual Test Checklist

| Step                 | Check                                                                     |
|----------------------|---------------------------------------------------------------------------|
| Start backend        | Confirm port `9990` is listening                                          |
| Start frontend       | Confirm dashboard opens on port `9991` in development                     |
| Start monitor        | Confirm license passes and camera opens                                   |
| Calibrate            | Confirm four points are accepted and grid appears                         |
| Walk through scene   | Confirm track appears and moves                                           |
| Enter dense cell     | Confirm occupancy count rises                                             |
| Sustain overcapacity | Confirm alert triggers after hysteresis                                   |
| Stop backend         | Confirm Python monitor continues locally and sender logs connection issue |
| Restart backend      | Confirm sender reconnects and dashboard receives updates                  |
| Change selected room | Confirm dashboard unsubscribe/subscribe behavior                          |
| Run birdsEye client  | Confirm Android/iOS app receives room list and room updates               |

### 11.23 Known Limitations Checklist

| Limitation                                  | Where visible                       |
|---------------------------------------------|-------------------------------------|
| Backend state is in memory                  | `RoomRegistry.kt`                   |
| WebSocket origins allow all                 | `WebSocketConfig.kt`                |
| Raw payload validation is minimal           | `RawMonitoringWebSocketHandler.kt`  |
| Frontend grid rows/cols are fixed           | `frontend/src/App.jsx`              |
| Radar coordinate space is fixed             | `RadarScope.jsx`                    |
| Mobile position map uses 800x600 model      | `birdsEye/shared/.../App.kt`        |
| Mobile dashboard lacks authentication       | `birdsEye/` dashboard WebSocket use |
| Tracker world positions are image centroids | `trackers.py`                       |
| Calibration assumes flat rectangle          | `calibration.py`, `geometry.py`     |
| Full bounding box is projected              | `geometry.py`, `occupancy.py`       |
| License signing secret is embedded          | `auth/license_manager.py`           |
| Algorithmic tests are limited               | Source tree inspection              |

### 11.24 Glossary

| Term           | Meaning in this project                                          |
|----------------|------------------------------------------------------------------|
| Bounding box   | Rectangle around a detected person in image coordinates          |
| birdsEye       | Kotlin Multiplatform Android/iOS dashboard client                |
| Calibration    | Mapping between selected image points and real-world rectangle   |
| Cell capacity  | Approximate maximum occupants per grid cell                      |
| Crowd density  | Occupancy relation between people and cell capacity              |
| DeepSort       | Optional multi-object tracking algorithm used through dependency |
| EMA            | Exponential moving average used to smooth occupancy counts       |
| Homography     | Perspective transform matrix between image and world plane       |
| KMP            | Kotlin Multiplatform shared-code approach used by birdsEye       |
| Occupancy grid | Grid over calibrated monitored area                              |
| Room           | Backend logical grouping for one device or MAC identity          |
| Track          | Persistent representation of a detected person across frames     |
| WebSocket      | Bidirectional communication channel used for live updates        |

### 11.25 Final Appendix Note

The appendix intentionally includes both implemented code behavior and proposed evaluation artifacts. Implemented
behavior is tied to source files. Proposed artifacts are marked as proposed or future work. This distinction is
important because a master-level report should explain the current system while also showing how it can be validated and
extended.
