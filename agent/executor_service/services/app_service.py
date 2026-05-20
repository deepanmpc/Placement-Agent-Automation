import subprocess
import time
import psutil
from typing import Optional, List
from rich.console import Console

from executor_service.config import Config

console = Console()


class AppService:
    """Launch, focus, and manage macOS applications."""

    def launch_app(self, app_name: str) -> str:
        """Launch an application, activate it, and wait for it to become frontmost."""
        try:
            # 1. Launch via open -a
            subprocess.run(["open", "-a", app_name], check=True, capture_output=True, timeout=10)
            console.print(f"  [dim][App] Launched: {app_name}[/dim]")

            # 2. Wait a beat for the app to initialize
            time.sleep(Config.APP_LAUNCH_WAIT)

            # 3. Force activate via AppleScript so it becomes the frontmost window
            self.focus_app(app_name)

            return f"Launched and focused: {app_name}"
        except subprocess.CalledProcessError as e:
            return f"Failed to launch '{app_name}': {e.stderr.decode().strip()}"
        except FileNotFoundError:
            return f"App '{app_name}' not found."

    def launch_via_spotlight(self, app_name: str) -> str:
        """Launch an app using Spotlight search (Cmd+Space)."""
        import pyautogui
        try:
            # Open Spotlight
            pyautogui.hotkey("command", "space")
            time.sleep(0.5)
            # Type app name
            pyautogui.write(app_name, interval=0.03)
            time.sleep(0.5)
            # Press Return to launch
            pyautogui.press("return")
            time.sleep(Config.APP_LAUNCH_WAIT)
            console.print(f"  [dim][App] Launched via Spotlight: {app_name}[/dim]")
            return f"Launched via Spotlight: {app_name}"
        except Exception as e:
            return f"Spotlight launch failed: {e}"

    def focus_app(self, app_name: str) -> str:
        """Bring an application to the foreground via AppleScript."""
        try:
            script = f'tell application "{app_name}" to activate'
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True, timeout=5)
            time.sleep(0.3)  # Let macOS finish the window transition
            console.print(f"  [dim][App] Focused: {app_name}[/dim]")
            return f"Focused app: {app_name}"
        except subprocess.CalledProcessError as e:
            return f"Failed to focus '{app_name}': {e.stderr.decode().strip()}"

    def hide_app(self, app_name: str) -> str:
        """Hide an application (minimize all its windows)."""
        try:
            script = f'tell application "System Events" to set visible of process "{app_name}" to false'
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True, timeout=5)
            console.print(f"  [dim][App] Hidden: {app_name}[/dim]")
            return f"Hidden: {app_name}"
        except subprocess.CalledProcessError as e:
            return f"Failed to hide '{app_name}': {e.stderr.decode().strip()}"

    def kill_app(self, app_name: str) -> str:
        """Kill an application by name."""
        try:
            script = f'tell application "{app_name}" to quit'
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True, timeout=5)
            console.print(f"  [dim][App] Killed: {app_name}[/dim]")
            return f"Killed app: {app_name}"
        except subprocess.CalledProcessError as e:
            return f"Failed to kill '{app_name}': {e.stderr.decode().strip()}"

    def is_app_running(self, app_name: str) -> bool:
        """Check if an application is currently running."""
        for proc in psutil.process_iter(['name']):
            try:
                if app_name.lower() in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def get_frontmost_app(self) -> str:
        """Get the name of the currently frontmost application."""
        try:
            result = subprocess.run(
                ["osascript", "-e",
                 'tell application "System Events" to get name of first process whose frontmost is true'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return ""

    def list_running_apps(self) -> List[str]:
        """Return a list of running GUI application names."""
        try:
            result = subprocess.run(
                ["osascript", "-e",
                 'tell application "System Events" to get name of every process whose background only is false'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return [a.strip() for a in result.stdout.strip().split(",")]
        except Exception:
            pass
        return []
