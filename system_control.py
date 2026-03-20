"""
Devta AI System - System Control Module
=========================================
Executes system commands parsed from Devta's AI responses.
Supports: open apps, volume, clipboard, screenshots,
          file ops, web search, system info, window management.
"""

import os
import subprocess
import webbrowser
import datetime
import platform
from typing import Optional, Any
import pyautogui
import psutil
import pyperclip
from logger import get_logger

# Initialize logger for this module
logger = get_logger(__name__)

# ─────────────────────────────────────────────
#  App name → executable mapping (Windows)
# ─────────────────────────────────────────────
APP_MAP = {
    "notepad":         "notepad.exe",
    "calculator":      "calc.exe",
    "paint":           "mspaint.exe",
    "word":            "winword.exe",
    "excel":           "excel.exe",
    "powerpoint":      "powerpnt.exe",
    "chrome":          "chrome.exe",
    "firefox":         "firefox.exe",
    "edge":            "msedge.exe",
    "explorer":        "explorer.exe",
    "task manager":    "taskmgr.exe",
    "cmd":             "cmd.exe",
    "terminal":        "wt.exe",
    "settings":        "ms-settings:",
    "camera":          "microsoft.windows.camera:",
    "spotify":         "spotify.exe",
    "vlc":             "vlc.exe",
    "vs code":         "code.exe",
    "vscode":          "code.exe",
    "visual studio code": "code.exe",
    "discord":         "discord.exe",
    "whatsapp":        "whatsapp.exe",
    "teams":           "teams.exe",
    "zoom":            "zoom.exe",
    "file manager":    "explorer.exe",
}


class SystemController:

    # ──────────────────────────────────────────
    #  Entry Point: Execute parsed action
    # ──────────────────────────────────────────
    def execute(self, action: Optional[dict[str, Any]]) -> Optional[str]:
        """Execute a system action dict from Devta's AI response.
        
        Args:
            action: Dictionary containing action type and parameters
            
        Returns:
            Result string or None
        """
        if not action:
            return None

        action_type = action.get("system_action", "").lower()
        result = f"Action '{action_type}' executed."

        try:
            if action_type == "open_app":
                result = self.open_app(action.get("app", ""))

            elif action_type == "close_app":
                result = self.close_app(action.get("app", ""))

            elif action_type == "web_search":
                result = self.web_search(action.get("query", ""))

            elif action_type == "open_url":
                result = self.open_url(action.get("url", ""))

            elif action_type == "screenshot":
                result = self.take_screenshot(action.get("filename"))

            elif action_type == "volume_up":
                result = self.volume_up(action.get("steps", 5))

            elif action_type == "volume_down":
                result = self.volume_down(action.get("steps", 5))

            elif action_type == "volume_mute":
                result = self.volume_mute()

            elif action_type == "get_system_info":
                result = self.get_system_info()

            elif action_type == "get_time":
                result = self.get_time()

            elif action_type == "get_battery":
                result = self.get_battery()

            elif action_type == "copy_to_clipboard":
                result = self.copy_to_clipboard(action.get("text", ""))

            elif action_type == "get_clipboard":
                result = self.get_clipboard()

            elif action_type == "create_file":
                result = self.create_file(
                    action.get("path", ""), action.get("content", ""))

            elif action_type == "read_file":
                result = self.read_file(action.get("path", ""))

            elif action_type == "run_command":
                result = self.run_shell(action.get("command", ""))

            elif action_type == "lock_screen":
                result = self.lock_screen()

            elif action_type == "shutdown":
                result = self.shutdown()

            elif action_type == "restart":
                result = self.restart()

            else:
                result = f"Unknown system action: {action_type}"
                logger.warning(f"Unknown action: {action_type}")

        except Exception as e:
            result = f"Error executing {action_type}: {e}"
            logger.error(f"System control error: {e}", exc_info=True)

        return result

    # ──────────────────────────────────────────
    #  App Control
    # ──────────────────────────────────────────
    def open_app(self, app_name: str) -> str:
        """Open an application by name.
        
        Args:
            app_name: Name of the application to open
            
        Returns:
            Status message
        """
        name_lower = app_name.lower().strip()
        exe = APP_MAP.get(name_lower, app_name)

        try:
            if exe.startswith("ms-") or exe.startswith("microsoft."):
                os.startfile(exe)
            else:
                subprocess.Popen(exe, shell=True)
            msg = f"Opened {app_name}"
            logger.info(msg)
            return msg
        except FileNotFoundError as e:
            msg = f"Application not found: {app_name}"
            logger.warning(msg)
            return msg
        except Exception as e:
            msg = f"Couldn't open {app_name}: {e}"
            logger.error(msg, exc_info=True)
            return msg

    def close_app(self, app_name: str) -> str:
        """Close a running application by name.
        
        Args:
            app_name: Name of the application to close
            
        Returns:
            Status message with closed processes
        """
        try:
            killed = []
            for proc in psutil.process_iter(['name']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.kill()
                    killed.append(proc.info['name'])
            
            if killed:
                msg = f"Closed: {', '.join(killed)}"
                logger.info(msg)
                return msg
            else:
                msg = f"No running process found for '{app_name}'"
                logger.warning(msg)
                return msg
        except Exception as e:
            msg = f"Error closing {app_name}: {e}"
            logger.error(msg, exc_info=True)
            return msg

    # ──────────────────────────────────────────
    #  Web
    # ──────────────────────────────────────────
    def web_search(self, query: str) -> str:
        """Search Google for a query.
        
        Args:
            query: Search query
            
        Returns:
            Status message
        """
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            msg = f"Searching Google for: {query}"
            logger.info(msg)
            return msg
        except Exception as e:
            msg = f"Error opening search: {e}"
            logger.error(msg, exc_info=True)
            return msg

    def open_url(self, url: str) -> str:
        """Open a URL in the default browser.
        
        Args:
            url: URL to open
            
        Returns:
            Status message
        """
        try:
            webbrowser.open(url)
            msg = f"Opened: {url}"
            logger.info(msg)
            return msg
        except Exception as e:
            msg = f"Error opening URL: {e}"
            logger.error(msg, exc_info=True)
            return msg

    # ──────────────────────────────────────────
    #  Screenshot
    # ──────────────────────────────────────────
    def take_screenshot(self, filename: Optional[str] = None) -> str:
        """Take a screenshot and save it to Desktop.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to saved screenshot
        """
        try:
            if not filename:
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(os.path.expanduser("~"), "Desktop",
                                        f"devta_screenshot_{ts}.png")
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            msg = f"Screenshot saved to: {filename}"
            logger.info(msg)
            return msg
        except Exception as e:
            msg = f"Screenshot error: {e}"
            logger.error(msg, exc_info=True)
            return msg

    # ──────────────────────────────────────────
    #  Volume
    # ──────────────────────────────────────────
    def volume_up(self, steps: int = 5) -> str:
        """Increase system volume.
        
        Args:
            steps: Number of volume steps to increase
            
        Returns:
            Status message
        """
        try:
            for _ in range(steps):
                pyautogui.press("volumeup")
            msg = f"Volume increased by {steps} steps"
            logger.info(msg)
            return msg
        except Exception as e:
            msg = f"Volume control error: {e}"
            logger.error(msg, exc_info=True)
            return msg

    def volume_down(self, steps: int = 5) -> str:
        """Decrease system volume.
        
        Args:
            steps: Number of volume steps to decrease
            
        Returns:
            Status message
        """
        try:
            for _ in range(steps):
                pyautogui.press("volumedown")
            msg = f"Volume decreased by {steps} steps"
            logger.info(msg)
            return msg
        except Exception as e:
            msg = f"Volume control error: {e}"
            logger.error(msg, exc_info=True)
            return msg

    def volume_mute(self) -> str:
        """Toggle mute/unmute.
        
        Returns:
            Status message
        """
        try:
            pyautogui.press("volumemute")
            msg = "Volume toggled mute"
            logger.info(msg)
            return msg
        except Exception as e:
            msg = f"Volume control error: {e}"
            logger.error(msg, exc_info=True)
            return msg

    # ──────────────────────────────────────────
    #  System Information
    # ──────────────────────────────────────────
    def get_system_info(self) -> str:
        """Get current system resource usage.
        
        Returns:
            System info string
        """
        try:
            cpu    = psutil.cpu_percent(interval=1)
            ram    = psutil.virtual_memory()
            disk   = psutil.disk_usage('/')
            info = (
                f"CPU: {cpu}% | "
                f"RAM: {ram.percent}% used ({ram.used // 1024**3}GB / {ram.total // 1024**3}GB) | "
                f"Disk: {disk.percent}% used"
            )
            logger.info(f"System info retrieved: {info}")
            return info
        except Exception as e:
            msg = f"Error getting system info: {e}"
            logger.error(msg, exc_info=True)
            return msg

    def get_time(self) -> str:
        """Get current date and time.
        
        Returns:
            Formatted time string
        """
        try:
            now = datetime.datetime.now()
            return now.strftime("It's %I:%M %p on %A, %B %d, %Y")
        except Exception as e:
            logger.error(f"Error getting time: {e}", exc_info=True)
            return "Error getting time"

    def get_battery(self) -> str:
        """Get current battery status.
        
        Returns:
            Battery info string
        """
        try:
            batt = psutil.sensors_battery()
            if batt:
                status = "charging" if batt.power_plugged else "on battery"
                msg = f"Battery: {batt.percent:.0f}% — {status}"
                logger.info(msg)
                return msg
            else:
                msg = "No battery info available"
                logger.warning(msg)
                return msg
        except Exception as e:
            msg = f"Error getting battery: {e}"
            logger.error(msg, exc_info=True)
            return msg

    # ──────────────────────────────────────────
    #  Clipboard
    # ──────────────────────────────────────────
    def copy_to_clipboard(self, text: str) -> str:
        """Copy text to clipboard.
        
        Args:
            text: Text to copy
            
        Returns:
            Status message
        """
        try:
            pyperclip.copy(text)
            msg = f"Copied to clipboard: {text[:50]}..."
            logger.info(msg)
            return msg
        except Exception as e:
            msg = f"Clipboard error: {e}"
            logger.error(msg, exc_info=True)
            return msg

    def get_clipboard(self) -> str:
        """Get current clipboard contents.
        
        Returns:
            Clipboard contents string
        """
        try:
            content = pyperclip.paste()
            msg = f"Clipboard: {content[:200]}"
            logger.info("Clipboard content retrieved")
            return msg
        except Exception as e:
            msg = f"Clipboard error: {e}"
            logger.error(msg, exc_info=True)
            return msg

    # ──────────────────────────────────────────
    #  File Operations
    # ──────────────────────────────────────────
    def create_file(self, path: str, content: str = "") -> str:
        """Create a new file with optional content.
        
        Args:
            path: File path (supports ~)
            content: File content
            
        Returns:
            Status message
        """
        try:
            path = os.path.expanduser(path)
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            msg = f"File created: {path}"
            logger.info(msg)
            return msg
        except PermissionError:
            msg = f"Permission denied: {path}"
            logger.error(msg)
            return msg
        except Exception as e:
            msg = f"File creation error: {e}"
            logger.error(msg, exc_info=True)
            return msg

    def read_file(self, path: str) -> str:
        """Read file contents.
        
        Args:
            path: File path to read (supports ~)
            
        Returns:
            File contents (limited to 2000 chars)
        """
        try:
            path = os.path.expanduser(path)
            if not os.path.exists(path):
                msg = f"File not found: {path}"
                logger.warning(msg)
                return msg
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(2000)  # Limit to 2000 chars
            logger.info(f"File read: {path}")
            return f"File contents:\n{content}"
        except PermissionError:
            msg = f"Permission denied: {path}"
            logger.error(msg)
            return msg
        except Exception as e:
            msg = f"Error reading file: {e}"
            logger.error(msg, exc_info=True)
            return msg

    # ──────────────────────────────────────────
    #  Shell Commands
    # ──────────────────────────────────────────
    def run_shell(self, command: str) -> str:
        """Execute a shell command.
        
        Args:
            command: Shell command to execute
            
        Returns:
            Command output (limited to 500 chars)
        """
        try:
            logger.info(f"Executing command: {command[:100]}")
            result = subprocess.run(
                command, shell=True, capture_output=True,
                text=True, timeout=10
            )
            output = result.stdout or result.stderr or "Command executed."
            logger.info("Command executed successfully")
            return output[:500]
        except subprocess.TimeoutExpired:
            msg = "Command timed out after 10 seconds"
            logger.warning(msg)
            return msg
        except Exception as e:
            msg = f"Command execution error: {e}"
            logger.error(msg, exc_info=True)
            return msg

    # ──────────────────────────────────────────
    #  Power Management
    # ──────────────────────────────────────────
    def lock_screen(self) -> str:
        """Lock the Windows screen.
        
        Returns:
            Status message
        """
        try:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            msg = "Screen locked"
            logger.info(msg)
            return msg
        except Exception as e:
            msg = f"Error locking screen: {e}"
            logger.error(msg, exc_info=True)
            return msg

    def shutdown(self) -> str:
        """Shutdown the system after 30 seconds.
        
        Returns:
            Status message
        """
        try:
            os.system("shutdown /s /t 30")
            msg = "Shutting down in 30 seconds. Say 'cancel shutdown' to abort."
            logger.warning(msg)
            return msg
        except Exception as e:
            msg = f"Error initiating shutdown: {e}"
            logger.error(msg, exc_info=True)
            return msg

    def restart(self) -> str:
        """Restart the system after 30 seconds.
        
        Returns:
            Status message
        """
        try:
            os.system("shutdown /r /t 30")
            msg = "Restarting in 30 seconds."
            logger.warning(msg)
            return msg
        except Exception as e:
            msg = f"Error initiating restart: {e}"
            logger.error(msg, exc_info=True)
            return msg

    # ──────────────────────────────────────────
    #  Method Map for Dynamic Dispatch
    # ──────────────────────────────────────────
    def get_method_map(self) -> dict[str, callable]:
        """Returns a dict mapping function names → callable methods.
        Used by DevtaAPI to dispatch Gemini function calls dynamically."""
        return {
            "open_app":          lambda app, **kw: self.open_app(app),
            "close_app":         lambda app, **kw: self.close_app(app),
            "web_search":        lambda query, **kw: self.web_search(query),
            "open_url":          lambda url, **kw: self.open_url(url),
            "take_screenshot":   lambda filename=None, **kw: self.take_screenshot(filename),
            "volume_up":         lambda steps=5, **kw: self.volume_up(int(steps)),
            "volume_down":       lambda steps=5, **kw: self.volume_down(int(steps)),
            "volume_mute":       lambda **kw: self.volume_mute(),
            "get_system_info":   lambda **kw: self.get_system_info(),
            "get_time":          lambda **kw: self.get_time(),
            "get_battery":       lambda **kw: self.get_battery(),
            "copy_to_clipboard": lambda text, **kw: self.copy_to_clipboard(text),
            "get_clipboard":     lambda **kw: self.get_clipboard(),
            "create_file":       lambda path, content="", **kw: self.create_file(path, content),
            "read_file":         lambda path, **kw: self.read_file(path),
            "run_command":       lambda command, **kw: self.run_shell(command),
            "lock_screen":       lambda **kw: self.lock_screen(),
            "shutdown":          lambda **kw: self.shutdown(),
            "restart":           lambda **kw: self.restart(),
        }
