import os
import time
from datetime import datetime
from typing import Tuple, Dict, Any

import mss
import numpy as np
from PIL import Image
import Quartz
import AppKit
import pyautogui

from vision_service.config import Config
from vision_service.utils.logger import logger
from vision_service.utils.timings import global_metrics

class ScreenshotCapturer:
    def __init__(self):
        self.sct = mss.mss()
        self.last_capture_info: Dict[str, Any] = {}

    def _process_and_save(
        self,
        monitor: Dict[str, int],
        capture_info: Dict[str, Any] | None = None,
    ) -> Tuple[np.ndarray, Image.Image, str]:
        with global_metrics.measure("screenshot_capture"):
            try:
                # Capture raw pixels
                sct_img = self.sct.grab(monitor)
                
                # Convert to numpy array (BGRA) and drop alpha channel (BGR)
                img_bgra = np.array(sct_img)
                img_bgr = img_bgra[:, :, :3]
                
                # Convert BGR to RGB for PIL Image
                img_rgb = img_bgr[:, :, ::-1]
                img_pil = Image.fromarray(img_rgb)
                
                # Save screenshot with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filepath = os.path.join(Config.SCREENSHOTS_DIR, f"capture_{timestamp}.jpg")
                
                # Optimize/compress save
                img_pil.save(filepath, "JPEG", quality=Config.COMPRESSION_QUALITY, optimize=True)

                cursor_x, cursor_y = pyautogui.position()
                self.last_capture_info = {
                    "origin_x": int(monitor.get("left", 0)),
                    "origin_y": int(monitor.get("top", 0)),
                    "width": int(monitor.get("width", img_pil.width)),
                    "height": int(monitor.get("height", img_pil.height)),
                    "coordinate_system": "screen",
                    "screenshot_path": filepath,
                    "cursor": [int(cursor_x), int(cursor_y)],
                    **(capture_info or {}),
                }
                
                logger.debug(f"Saved screenshot to {filepath} | Size: {img_pil.size}")
                return img_bgr, img_pil, filepath
                
            except Exception as e:
                logger.error(f"Failed to capture screenshot: {e}")
                raise

    def capture_fullscreen(self) -> Tuple[np.ndarray, Image.Image, str]:
        """Captures all monitors combined into a single fullscreen virtual display."""
        monitor = self.sct.monitors[0]
        return self._process_and_save(monitor, {"capture_scope": "fullscreen"})

    def get_active_window_bounds(self) -> dict:
        workspace = AppKit.NSWorkspace.sharedWorkspace()
        active_app = workspace.frontmostApplication()
        if not active_app:
            return None
        
        pid = active_app.processIdentifier()
        app_name = active_app.localizedName()
        
        options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
        window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
        
        largest_window = None
        max_area = 0

        for window in window_list:
            win_pid = window.get(Quartz.kCGWindowOwnerPID, -1)
            layer = window.get(Quartz.kCGWindowLayer, -1)
            if win_pid == pid and layer == 0:
                bounds = window.get(Quartz.kCGWindowBounds)
                area = bounds["Width"] * bounds["Height"]
                if area > max_area:
                    max_area = area
                    largest_window = {
                        "app": app_name,
                        "title": window.get(Quartz.kCGWindowName, ""),
                        "x": int(bounds["X"]),
                        "y": int(bounds["Y"]),
                        "width": int(bounds["Width"]),
                        "height": int(bounds["Height"])
                    }
        return largest_window

    def capture_active_window(self) -> Tuple[np.ndarray, Image.Image, str]:
        """Captures only the currently active foreground window."""
        bounds = self.get_active_window_bounds()
        if bounds:
            logger.debug(f"Capturing active window: {bounds['app']} ({bounds['width']}x{bounds['height']})")
            return self.capture_region(
                bounds["x"],
                bounds["y"],
                bounds["width"],
                bounds["height"],
                metadata={
                    "capture_scope": "active_window",
                    "app": bounds.get("app"),
                    "title": bounds.get("title", ""),
                },
            )
        else:
            logger.warning("Could not determine active window bounds. Falling back to fullscreen.")
            return self.capture_fullscreen()

    def capture_monitor(self, monitor_id: int = 1) -> Tuple[np.ndarray, Image.Image, str]:
        """Captures a specific monitor (1-indexed)."""
        if monitor_id >= len(self.sct.monitors):
            raise ValueError(f"Monitor {monitor_id} does not exist.")
        monitor = self.sct.monitors[monitor_id]
        return self._process_and_save(monitor, {"capture_scope": f"monitor_{monitor_id}"})

    def capture_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        metadata: Dict[str, Any] | None = None,
    ) -> Tuple[np.ndarray, Image.Image, str]:
        """Captures a specific bounding box region."""
        monitor = {"top": y, "left": x, "width": width, "height": height}
        capture_info = {"capture_scope": "region", **(metadata or {})}
        return self._process_and_save(monitor, capture_info)
