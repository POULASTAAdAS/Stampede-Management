"""
Helpers for making OpenCV HighGUI windows visible across platforms.
"""

import platform
from typing import Optional

import cv2

from logger_config import get_logger

logger = get_logger(__name__)

IS_MACOS = platform.system() == "Darwin"


def pump_gui_events(iterations: int = 3, delay_ms: int = 1) -> None:
    """Give OpenCV's GUI backend a chance to create and repaint windows."""
    wait_ms = max(delay_ms, 10) if IS_MACOS else delay_ms
    for _ in range(iterations):
        cv2.waitKey(wait_ms)


def wait_key(delay_ms: int = 1) -> int:
    """Wait for a keypress while allowing Cocoa windows to repaint reliably."""
    wait_ms = max(delay_ms, 10) if IS_MACOS else delay_ms
    return cv2.waitKey(wait_ms)


def create_visible_window(
        name: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        x: int = 40,
        y: int = 40,
        topmost: bool = True,
) -> None:
    """
    Create an OpenCV window and nudge it onto the visible desktop.

    Cocoa sometimes delays showing HighGUI windows until the event queue is
    pumped. Explicit sizing and positioning also avoids windows opening partly
    off-screen on macOS multi-display setups.
    """
    if not IS_MACOS:
        try:
            cv2.startWindowThread()
        except Exception:
            pass

    cv2.namedWindow(name, cv2.WINDOW_NORMAL)

    if width is not None and height is not None:
        try:
            cv2.resizeWindow(name, max(1, int(width)), max(1, int(height)))
        except cv2.error as exc:
            logger.debug(f"Could not resize OpenCV window '{name}': {exc}")

    try:
        cv2.moveWindow(name, int(x), int(y))
    except cv2.error as exc:
        logger.debug(f"Could not move OpenCV window '{name}': {exc}")

    if topmost:
        topmost_property = getattr(cv2, "WND_PROP_TOPMOST", None)
        if topmost_property is not None:
            try:
                cv2.setWindowProperty(name, topmost_property, 1)
            except cv2.error as exc:
                logger.debug(f"Could not set OpenCV window '{name}' topmost: {exc}")

    pump_gui_events(5)


def set_window_title(name: str, title: str) -> None:
    """Set the window title when the local OpenCV build supports it."""
    set_title = getattr(cv2, "setWindowTitle", None)
    if set_title is None:
        return
    try:
        set_title(name, title)
    except cv2.error as exc:
        logger.debug(f"Could not set OpenCV window title '{title}': {exc}")
