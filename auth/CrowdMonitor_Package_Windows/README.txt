# CrowdMonitor Installation Guide (Windows)

## Installation

1. Extract all files from this folder to a location on your computer
2. The folder should contain:
   - CrowdMonitor.exe
   - model/yolov8n.pt (YOLO model file)
3. Run CrowdMonitor.exe

## First Run

On first run, you will be prompted to activate with a license key.

1. Click "Request License" to see your Machine ID
2. Send your Machine ID to support@yourcompany.com
3. Paste the license key you receive
4. Click "Activate"

## License Information

- Your license is tied to this computer
- If you upgrade your hardware, contact support for a new license
- Check license status: Click "License Info" button in the application

## System Requirements

- Windows 10 or later
- Webcam or video file for monitoring
- YOLO model file included (model/yolov8n.pt)

## Model File

The application includes a pre-trained YOLOv8n model for person detection.
Default location: model/yolov8n.pt

If you need to use a different model:
1. Open the application
2. Go to "Video Source" tab
3. Click "Browse" next to "Model Path"
4. Select your custom .pt model file

## Support

Email: support@yourcompany.com
Website: www.yourcompany.com

## Troubleshooting

**License activation fails:**
- Verify you copied the entire license key
- Check your internet connection (if using online validation)
- Contact support with your Machine ID

**Application won't start:**
- Ensure the model folder with yolov8n.pt exists
- Check that your video source (camera/file) is accessible
- Run as Administrator if necessary

**"Model not found" error:**
- Verify model/yolov8n.pt exists in the same folder as the executable
- Browse for the model file manually in the Video Source tab
