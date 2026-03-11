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
import pyautogui
import psutil
import pyperclip
from colorama import Fore, Style, init

init(autoreset=True)

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
    def execute(self, action: dict) -> str:
        """Execute a system action dict from Devta's AI response."""
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
                print(f"{Fore.YELLOW}⚠️  {result}{Style.RESET_ALL}")

        except Exception as e:
            result = f"Error executing {action_type}: {e}"
            print(f"{Fore.RED}❌ System Control Error: {e}{Style.RESET_ALL}")

        return result

    # ──────────────────────────────────────────
    #  App Control
    # ──────────────────────────────────────────
    def open_app(self, app_name: str) -> str:
        name_lower = app_name.lower().strip()
        exe = APP_MAP.get(name_lower, app_name)

        try:
            if exe.startswith("ms-") or exe.startswith("microsoft."):
                os.startfile(exe)
            else:
                subprocess.Popen(exe, shell=True)
            return f"Opened {app_name}"
        except Exception as e:
            return f"Couldn't open {app_name}: {e}"

    def close_app(self, app_name: str) -> str:
        killed = []
        for proc in psutil.process_iter(['name']):
            if app_name.lower() in proc.info['name'].lower():
                proc.kill()
                killed.append(proc.info['name'])
        if killed:
            return f"Closed: {', '.join(killed)}"
        return f"No running process found for '{app_name}'"

    # ──────────────────────────────────────────
    #  Web
    # ──────────────────────────────────────────
    def web_search(self, query: str) -> str:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching Google for: {query}"

    def open_url(self, url: str) -> str:
        webbrowser.open(url)
        return f"Opened: {url}"

    # ──────────────────────────────────────────
    #  Screenshot
    # ──────────────────────────────────────────
    def take_screenshot(self, filename: str = None) -> str:
        if not filename:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(os.path.expanduser("~"), "Desktop",
                                    f"devta_screenshot_{ts}.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return f"Screenshot saved to: {filename}"

    # ──────────────────────────────────────────
    #  Volume
    # ──────────────────────────────────────────
    def volume_up(self, steps: int = 5) -> str:
        for _ in range(steps):
            pyautogui.press("volumeup")
        return f"Volume increased by {steps} steps"

    def volume_down(self, steps: int = 5) -> str:
        for _ in range(steps):
            pyautogui.press("volumedown")
        return f"Volume decreased by {steps} steps"

    def volume_mute(self) -> str:
        pyautogui.press("volumemute")
        return "Volume toggled mute"

    # ──────────────────────────────────────────
    #  System Information
    # ──────────────────────────────────────────
    def get_system_info(self) -> str:
        cpu    = psutil.cpu_percent(interval=1)
        ram    = psutil.virtual_memory()
        disk   = psutil.disk_usage('/')
        info = (
            f"CPU: {cpu}% | "
            f"RAM: {ram.percent}% used ({ram.used // 1024**3}GB / {ram.total // 1024**3}GB) | "
            f"Disk: {disk.percent}% used"
        )
        return info

    def get_time(self) -> str:
        now = datetime.datetime.now()
        return now.strftime("It's %I:%M %p on %A, %B %d, %Y")

    def get_battery(self) -> str:
        batt = psutil.sensors_battery()
        if batt:
            status = "charging" if batt.power_plugged else "on battery"
            return f"Battery: {batt.percent:.0f}% — {status}"
        return "No battery info available"

    # ──────────────────────────────────────────
    #  Clipboard
    # ──────────────────────────────────────────
    def copy_to_clipboard(self, text: str) -> str:
        pyperclip.copy(text)
        return f"Copied to clipboard: {text[:50]}..."

    def get_clipboard(self) -> str:
        content = pyperclip.paste()
        return f"Clipboard: {content[:200]}"

    # ──────────────────────────────────────────
    #  File Operations
    # ──────────────────────────────────────────
    def create_file(self, path: str, content: str = "") -> str:
        path = os.path.expanduser(path)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File created: {path}"

    def read_file(self, path: str) -> str:
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            return f"File not found: {path}"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(2000)  # Limit to 2000 chars
        return f"File contents:\n{content}"

    # ──────────────────────────────────────────
    #  Shell Commands
    # ──────────────────────────────────────────
    def run_shell(self, command: str) -> str:
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True,
                text=True, timeout=10
            )
            output = result.stdout or result.stderr or "Command executed."
            return output[:500]
        except subprocess.TimeoutExpired:
            return "Command timed out after 10 seconds"

    # ──────────────────────────────────────────
    #  Power Management
    # ──────────────────────────────────────────
    def lock_screen(self) -> str:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "Screen locked"

    def shutdown(self) -> str:
        os.system("shutdown /s /t 30")
        return "Shutting down in 30 seconds. Say 'cancel shutdown' to abort."

    def restart(self) -> str:
        os.system("shutdown /r /t 30")
        return "Restarting in 30 seconds."
