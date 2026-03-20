"""
Devta AI System - Brain Module
================================
Thin wrapper around DevtaAPI. Manages the AI brain lifecycle
and provides a clean interface for the rest of the system.
"""

from typing import Optional, Any
from devta_api import DevtaAPI
from system_control import SystemController
from logger import get_logger

logger = get_logger(__name__)


class DevtaBrain:
    def __init__(self, system_controller: Optional[SystemController] = None) -> None:
        """
        Initialize Devta's brain.
        
        Args:
            system_controller: Optional SystemController instance.
                              If not provided, a new one is created.
        """
        if system_controller is None:
            system_controller = SystemController()

        self.api = DevtaAPI(system_controller)
        self.suggestions_enabled = True

        logger.info("Brain initialized — Custom API with Function Calling")

    # ──────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────
    def ask(self, user_input: str, context: Optional[str] = None) -> dict[str, Any]:
        """
        Ask Devta something. Returns:
          {"text": str, "system_action": dict|None, "model_used": str}
        
        Note: system_action is kept for backward compatibility with main.py,
        but actual actions are now executed automatically by the API layer.
        """
        result = self.api.chat(user_input, context=context)

        return {
            "text": result["text"],
            "system_action": None,  # Actions already executed by API
            "model_used": result["model_used"],
            "actions_executed": result.get("actions_executed", []),
        }

    def suggest(self, context: str) -> Optional[str]:
        """Generate a short proactive suggestion for notification popups."""
        if not self.suggestions_enabled:
            return None
        return self.api.suggest(context)

    def reset_conversation(self) -> None:
        """Reset conversation history."""
        self.api.reset_conversation()
        logger.info("Conversation reset by user")

    def enable_suggestions(self) -> None:
        """Enable proactive suggestions."""
        self.suggestions_enabled = True
        logger.info("Suggestions enabled")

    def disable_suggestions(self) -> None:
        """Disable proactive suggestions."""
        self.suggestions_enabled = False
        logger.info("Suggestions disabled")
