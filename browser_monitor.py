"""
Devta AI System - Browser & Window Monitor
===========================================
Monitors the active window every N seconds.
When a known app/browser is detected, it sends a random productivity tip.
(Now entirely local — uses 0 API tokens to save quota!)
"""

import re
import time
import random
import threading
from colorama import Fore, Style, init
from config import NOTIFICATION_INTERVAL_SECONDS

init(autoreset=True)

BROWSER_KEYWORDS = ["chrome", "firefox", "edge", "opera", "brave", "browser"]

# Common search engine patterns to extract query from title
SEARCH_PATTERNS = [
    r"^(.*?)\s*[-–|]\s*Google Search$",
    r"^(.*?)\s*[-–|]\s*Bing$",
    r"^(.*?)\s*[-–|]\s*DuckDuckGo$",
    r"^(.*?)\s*[-–|]\s*Yahoo!?\s*Search$",
    r"^Search Results for:?\s*(.*?)$",
]

# Local productivity tips to avoid burning API quota
LOCAL_TIPS = [
    "Take a 5-minute break and stretch your legs! 🚶",
    "Drink a glass of water to stay hydrated. 💧",
    "Don't forget the 20-20-20 rule to rest your eyes! 👀",
    "Focus mode on! Keep at it, you're doing great. 🚀",
    "Remember to maintain good posture! 🪑",
    "Quick keyboard shortcut reminder: Win+D to show desktop.",
    "A clean workspace is a happy workspace. ✨"
]


def _get_active_window_title() -> str:
    """Get the title of the currently active window."""
    try:
        import pygetwindow as gw
        win = gw.getActiveWindow()
        if win and win.title:
            return win.title.strip()
    except Exception:
        pass
    return ""


def _extract_search_query(title: str) -> str | None:
    """Try to extract a search query from a browser window title."""
    for pattern in SEARCH_PATTERNS:
        match = re.match(pattern, title, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _is_browser_window(title: str) -> bool:
    """Check if the window title suggests a browser."""
    lower = title.lower()
    return any(kw in lower for kw in BROWSER_KEYWORDS)


class BrowserMonitor:
    """
    Runs in a background daemon thread.
    Periodically checks the active window and triggers suggestions.
    """

    def __init__(self, notifier, suggestions_enabled_flag: list):
        """
        notifier: Notifier instance
        suggestions_enabled_flag: a mutable list [bool] shared with main
        """
        self.notifier = notifier
        self._enabled = suggestions_enabled_flag  # [True/False], mutable reference
        self._thread  = None
        self._running = False
        self._last_title = ""

    def start(self):
        self._running = True
        self._thread  = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        print(f"{Fore.CYAN}🖥️  Browser monitor started (interval: {NOTIFICATION_INTERVAL_SECONDS}s){Style.RESET_ALL}")

    def stop(self):
        self._running = False

    def _monitor_loop(self):
        while self._running:
            time.sleep(NOTIFICATION_INTERVAL_SECONDS)

            if not self._enabled[0]:
                continue  # Suggestions disabled

            try:
                title = _get_active_window_title()
                if not title or title == self._last_title:
                    continue

                self._last_title = title
                context = self._build_context(title)

                if not context:
                    continue

                print(f"{Fore.MAGENTA}🔍 Monitoring: {context}{Style.RESET_ALL}")

                # Send a local tip instead of calling the API
                suggestion = random.choice(LOCAL_TIPS)
                self.notifier.send_async(
                    message=f"{context} → {suggestion}",
                    title="💡 Devta Tip"
                )

            except Exception as e:
                print(f"{Fore.RED}Monitor error: {e}{Style.RESET_ALL}")

    def _build_context(self, title: str) -> str | None:
        """Convert window title to a human-readable context string."""
        if not title:
            return None

        # Try to identify search query in browser
        if _is_browser_window(title):
            query = _extract_search_query(title)
            if query:
                return f"searching Google for '{query}'"
            return f"browsing a page titled '{title}'"

        # Any other productive app
        productive_keywords = [
            "word", "excel", "powerpoint", "notepad", "code", "visual studio",
            "pdf", "reader", "outlook", "teams", "zoom", "slack",
            "pycharm", "intellij", "android studio"
        ]
        lower = title.lower()
        if any(kw in lower for kw in productive_keywords):
            return f"working in: {title}"

        return None  # Don't suggest for games/media/random windows
