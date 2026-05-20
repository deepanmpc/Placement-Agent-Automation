import Quartz
import AppKit

def get_active_window_bounds():
    # Get the active app
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    active_app = workspace.frontmostApplication()
    if not active_app:
        return None
    
    pid = active_app.processIdentifier()
    app_name = active_app.localizedName()
    
    # Get all windows
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
    
    largest_window = None
    max_area = 0

    for window in window_list:
        win_pid = window.get(Quartz.kCGWindowOwnerPID, -1)
        layer = window.get(Quartz.kCGWindowLayer, -1)
        # layer 0 is the normal app window layer
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

print(get_active_window_bounds())
