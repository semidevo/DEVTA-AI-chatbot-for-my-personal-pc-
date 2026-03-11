"""
Devta AI System - Notification Module
=======================================
Sends Windows toast notification popups with Devta's smart suggestions.
Respects the global suggestions_enabled flag.
Deduplicates: won't repeat same suggestion within cooldown window.
"""

import time
import threading
from plyer import notification
from colorama import Fore, Style, init
from config import NOTIFICATION_APP_NAME, NOTIFICATION_COOLDOWN_SECONDS

init(autoreset=True)


class Notifier:
    def __init__(self):
        self._recent: dict[str, float] = {}  # message → last_sent timestamp
        self._lock = threading.Lock()

    def send(self, message: str, title: str = None, timeout: int = 8) -> bool:
        """
        Send a Windows toast notification.
        Returns False if the message was sent recently (deduplication).
        """
        if not message or not message.strip():
            return False

        title = title or f"✨ {NOTIFICATION_APP_NAME}"
        now   = time.time()

        with self._lock:
            # Deduplicate
            last_sent = self._recent.get(message.strip())
            if last_sent and (now - last_sent) < NOTIFICATION_COOLDOWN_SECONDS:
                print(f"{Fore.YELLOW}🔕 Notification suppressed (cooldown): {message[:40]}{Style.RESET_ALL}")
                return False

            self._recent[message.strip()] = now
            # Clean old entries
            self._recent = {
                k: v for k, v in self._recent.items()
                if now - v < NOTIFICATION_COOLDOWN_SECONDS
            }

        try:
            notification.notify(
                title=title,
                message=message[:256],   # Windows toast limit
                app_name=NOTIFICATION_APP_NAME,
                timeout=timeout,
            )
            print(f"{Fore.CYAN}🔔 Notification sent: {message[:60]}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}Notification error: {e}{Style.RESET_ALL}")
            return False

    def send_async(self, message: str, title: str = None):
        """Send notification in a background thread (non-blocking)."""
        t = threading.Thread(target=self.send, args=(message, title), daemon=True)
        t.start()
