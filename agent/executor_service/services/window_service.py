import subprocess
from typing import Optional, Dict, Any, List

import Quartz
import AppKit
from rich.console import Console

console = Console()


class WindowService:
    """Track active windows and manage window focus using macOS Quartz/AppKit APIs."""

    def get_active_window(self) -> Optional[Dict[str, Any]]:
        """Return info about the currently focused window."""
        workspace = AppKit.NSWorkspace.sharedWorkspace()
        active_app = workspace.frontmostApplication()
        if not active_app:
            return None

        pid = active_app.processIdentifier()
        app_name = active_app.localizedName()

        options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
        window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

        largest = None
        max_area = 0
        for win in window_list:
            if win.get(Quartz.kCGWindowOwnerPID, -1) == pid and win.get(Quartz.kCGWindowLayer, -1) == 0:
                bounds = win.get(Quartz.kCGWindowBounds)
                if bounds:
                    area = bounds["Width"] * bounds["Height"]
                    if area > max_area:
                        max_area = area
                        largest = {
                            "app": app_name,
                            "pid": pid,
                            "title": win.get(Quartz.kCGWindowName, ""),
                            "x": int(bounds["X"]),
                            "y": int(bounds["Y"]),
                            "width": int(bounds["Width"]),
                            "height": int(bounds["Height"]),
                        }
        return largest

    def focus_window(self, app_name: str) -> str:
        """Bring a window to front by application name via AppleScript."""
        try:
            script = f'tell application "{app_name}" to activate'
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True, timeout=5)
            console.print(f"  [dim][Window] Focused: {app_name}[/dim]")
            return f"Focused window: {app_name}"
        except subprocess.CalledProcessError as e:
            return f"Failed to focus '{app_name}': {e.stderr.decode().strip()}"

    def list_windows(self) -> List[Dict[str, Any]]:
        """List all visible on-screen windows."""
        options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
        window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

        results = []
        for win in window_list:
            layer = win.get(Quartz.kCGWindowLayer, -1)
            if layer == 0:
                bounds = win.get(Quartz.kCGWindowBounds, {})
                results.append({
                    "app": win.get(Quartz.kCGWindowOwnerName, ""),
                    "title": win.get(Quartz.kCGWindowName, ""),
                    "x": int(bounds.get("X", 0)),
                    "y": int(bounds.get("Y", 0)),
                    "width": int(bounds.get("Width", 0)),
                    "height": int(bounds.get("Height", 0)),
                })
        return results

    def get_screen_size(self):
        """Return primary display dimensions."""
        main_display = Quartz.CGDisplayBounds(Quartz.CGMainDisplayID())
        return int(main_display.size.width), int(main_display.size.height)
