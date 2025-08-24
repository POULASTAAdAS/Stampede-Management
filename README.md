# <h1 align='center'>Stampede Management</h1>

## <h2 align='center'>Project Description</h2>

> Stampede Management is a crowd-monitoring and safety system that uses computer vision to detect, track, and analyze
> people in real-time to prevent overcrowding and potential stampede incidents. It combines YOLO object detection with
> DeepSORT tracking and provides live visualization, density analysis, and alerting.

---

## <h2 align='center'>🚀 Features</h2>

* **Real-time person detection** (YOLOv8)
* **Multi-object tracking** (DeepSORT)
* **Crowd density & heatmaps** for zone analysis
* **Threshold-based alerts** (console, logs, or custom hooks)
* **Calibration tool** to map frame coordinates to ground plane
* **Video input and output** (file, webcam, RTSP)

---

## <h2 align='center'>🏗️ Tech Stack</h2>

* **Language:** Python 3.8+
* **Detection:** YOLOv8 (Ultralytics)
* **Tracking:** DeepSORT
* **Core libs:** OpenCV, NumPy, Pillow

---

## <h2 align='center'>⚙️ Quick Start (Windows PowerShell)</h2>

1. Clone & enter the repo:

    ```powershell
    git clone https://github.com/<your-username>/<repo>.git
    cd "Stampede Management"
    ```

2. Create and activate a virtual environment:

    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```

3. Run the main script:

    ```powershell
    python PromisingTest.py
    ```

---

## <h2 align='center'>🖱️ Usage Notes</h2>

* On first run the script will ask you to **click 4 ground points** on the frame (clockwise or counter-clockwise). These
  are used to compute homography for distance/density calculations.
* Press `q` (or the configured key) when calibration is complete.
* Use configuration variables at the top of the script (or a config file) to change thresholds, model paths, input
  sources, and output behavior.

---

## <h2 align='center'>📸 Screenshots & Demo</h2>

---

<img src="/docs/test%20sample%201.jpg" alt="sample 1">
<div style="height:10px"></div>
<img src="/docs/test%20sample%202.jpg" alt="sample 2">

---

## <h2  align='center'>📜 Developers</h2>

Designed and developed by:

1. [Poulastaa Das](https://www.linkedin.com/in/poulastaa-das-7a5332235/?originalSubdomain=in)
2. [Shreya Chakraborty](https://www.linkedin.com/in/rohan-wadadar-98439934a/)
3. [Rohan Waddader](https://www.linkedin.com/in/rohan-wadadar-98439934a/)
4. Payal Ghosh

Under Supervision of:  [**Subhasis Choudhury**](https://www.linkedin.com/in/subhasis-chowdhury-026418177/?originalSubdomain=in)

---

## <h2  align='center'>📜 License</h2>

    ```xml
        Licensed under the Apache License, Version 2.0 (the "License");
        you may not use this file except in compliance with the License.
        You may obtain a copy of the License at
        
        http://www.apache.org/licenses/LICENSE-2.0
        
        Unless required by applicable law or agreed to in writing, software
        distributed under the License is distributed on an "AS IS" BASIS,
        WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
        See the License for the specific language governing permissions and
        limitations under the License.
    ```

---


*This README was generated to give a comprehensive starting point. Edit the sections and placeholders to match your
exact setup and preferences.*
