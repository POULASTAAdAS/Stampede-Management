# Display Size Fix - Webcam Detection

## Problem

When using webcam for detection, the display window would exceed the screen boundaries, making parts of the interface
inaccessible or causing the window to appear "out of size."

## Solution

Implemented automatic display resizing that:

- Detects when the display frame (including info panels) exceeds screen boundaries
- Automatically scales the display down while maintaining aspect ratio
- Keeps the entire interface visible and accessible

## Configuration

### Default Settings (Conservative for Maximum Compatibility)

- **Max Display Width**: 1280 pixels (safe for most screens)
- **Max Display Height**: 720 pixels (safe for most screens)

These conservative defaults ensure the window fits on most displays, including smaller laptop screens.

### For Larger Screens

If you have a larger screen and want bigger display:

```bash
# For 1920x1080 Full HD screen
python main.py --max-display-width 1700 --max-display-height 900

# For 2560x1440 2K screen
python main.py --max-display-width 2300 --max-display-height 1250

# For smaller laptop (1366x768)
python main.py --max-display-width 1200 --max-display-height 650
```

### Customization via Code

Edit `config.py` to change the default values permanently:

```python
max_display_width: int = 1280  # Your desired width
max_display_height: int = 720   # Your desired height
```

## Recommended Settings by Screen Resolution

| Screen Resolution       | max_display_width | max_display_height | Notes             |
|-------------------------|-------------------|--------------------|-------------------|
| 1366x768 (Small Laptop) | 1200              | 650                | Conservative      |
| 1600x900 (Laptop)       | 1450              | 800                | Standard          |
| 1920x1080 (Full HD)     | 1700              | 900                | Most common       |
| 2560x1440 (2K)          | 2300              | 1250               | High-end displays |
| 3840x2160 (4K)          | 3600              | 2000               | 4K monitors       |

**Important**: Always leave 150-200 pixels margin for window borders, taskbar, and system UI elements.

## Quick Screen Size Check

To find your screen resolution:

- **Windows**: Right-click desktop → Display settings → Look for "Resolution"
- **Task Manager**: Performance tab → GPU section shows display resolution

## Features

- **Automatic Scaling**: Frames are only resized if they exceed the maximum bounds
- **Aspect Ratio Maintained**: No distortion of the video feed
- **High-Quality Interpolation**: Uses cv2.INTER_AREA for downscaling
- **Applies to All Modes**: Works with all display modes (Raw Camera, Grid Overlay, Detection View, Monitoring View,
  Split View)

## Testing Different Display Modes

Press these keys while running to test each mode fits your screen:

- **'1'** - Raw Camera (smallest)
- **'2'** - Grid Overlay
- **'3'** - Detection View
- **'4'** - Monitoring View (tallest - includes info panel)
- **'5'** - Split View (shows 4 views in quadrants)

If any mode still doesn't fit, reduce the max values further.

## Troubleshooting

### Window Still Too Large

**Solution 1**: Reduce the max display size further:

```bash
python main.py --max-display-width 1024 --max-display-height 600
```

**Solution 2**: Edit `config.py` and set even smaller defaults:

```python
max_display_width: int = 1024
max_display_height: int = 600
```

### Display Too Small to See Details

**Solution**: Increase the values incrementally until you find the sweet spot:

```bash
# Try increasing by 100 pixels at a time
python main.py --max-display-width 1400 --max-display-height 800
```

### Split View (Mode 5) is Unreadable

**Solution**: Split view creates 4 quadrants which can be small. Options:

1. Use other display modes (1-4) instead
2. Increase max display size if your screen allows
3. Use larger monitor/external display

### Different Webcam Resolutions

- Low-res webcam (640x480): No scaling needed, displays at original size
- HD webcam (1280x720): May be scaled down depending on your settings
- Full HD webcam (1920x1080): Will be scaled down to fit max bounds
- 4K webcam (3840x2160): Will be significantly scaled down

## Technical Details

- The resize function checks frame dimensions before each display
- Scaling is calculated to fit within both width and height constraints
- The smaller scaling factor is used to ensure the frame fits completely
- Original frame data remains unchanged; only the display is resized
- Detection and processing happen at full resolution

## Files Modified

- `monitor.py`: Added `_resize_for_display()` method
- `config.py`: Added `max_display_width` and `max_display_height` parameters (default: 1280x720)
- `main.py`: Added command-line arguments for display size configuration

## Performance Impact

- **Negligible**: Resizing only happens once per frame for display
- **No processing overhead**: Detection runs on full-resolution frames
- **High quality**: Professional downscaling algorithm maintains visual quality
