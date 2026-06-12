import subprocess
import json

def get_frontmost_window_applescript():
    script = """
    tell application "System Events"
        set frontApp to first application process whose frontmost is true
        set frontAppName to name of frontApp
        tell frontApp
            if exists (window 1) then
                set winBounds to position of window 1 & size of window 1
                return frontAppName & "|" & item 1 of winBounds & "|" & item 2 of winBounds & "|" & item 3 of winBounds & "|" & item 4 of winBounds
            end if
        end tell
    end tell
    """
    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split("|")
            return {
                "app": parts[0],
                "left": int(parts[1]),
                "top": int(parts[2]),
                "width": int(parts[3]),
                "height": int(parts[4])
            }
    except Exception as e:
        print("AppleScript error:", e)
    return None

print(get_frontmost_window_applescript())
