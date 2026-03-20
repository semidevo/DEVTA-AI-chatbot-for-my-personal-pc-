"""
Devta AI System - Main Orchestrator
=====================================
Entry point. Ties together:
  - Wake word listener (background thread)
  - Speech (STT + TTS)
  - AI Brain (Gemini)
  - System Control
  - Browser Monitor + Notifier
  - Chat UI (main thread)
"""

import sys
import time
import threading
from colorama import Fore, Style
from logger import get_logger

logger = get_logger(__name__)

# Fix Windows encoding for Unicode/box-drawing characters
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ─────────────────────────────────────────────
#  Startup Banner
# ─────────────────────────────────────────────
BANNER = f"""
{Fore.MAGENTA}
  ██████╗ ███████╗██╗   ██╗████████╗ █████╗ 
  ██╔══██╗██╔════╝██║   ██║╚══██╔══╝██╔══██╗
  ██║  ██║█████╗  ██║   ██║   ██║   ███████║
  ██║  ██║██╔══╝  ╚██╗ ██╔╝   ██║   ██╔══██║
  ██████╔╝███████╗ ╚████╔╝    ██║   ██║  ██║
  ╚═════╝ ╚══════╝  ╚═══╝     ╚═╝   ╚═╝  ╚═╝
{Style.RESET_ALL}
  {Fore.CYAN}Your personal AI assistant is awakening...{Style.RESET_ALL}
  {Fore.YELLOW}Say 'Hello Devta' or 'Bhai Devta' to activate.{Style.RESET_ALL}
  {Fore.YELLOW}Say 'Devta stop' to silence suggestions.{Style.RESET_ALL}
"""


# ─────────────────────────────────────────────
#  Global State
# ─────────────────────────────────────────────
suggestions_enabled = [True]   # Mutable list so threads can share it
_conversation_lock  = threading.Lock()
_ui = None   # Global UI reference


# ─────────────────────────────────────────────
#  Core Interaction Handler
# ─────────────────────────────────────────────
def handle_input(user_text: str, brain: any, system_ctrl: any, speech_module: any, source: str = "text") -> None:
    """
    Process user input (from voice or text) through the brain.
    System actions are now executed automatically by the API layer.
    
    Args:
        user_text: User input text
        brain: DevtaBrain instance
        system_ctrl: SystemController instance
        speech_module: Speech module with speak() function
        source: Source of input ('text' or 'voice')
    """
    if not user_text.strip():
        return

    global _ui

    with _conversation_lock:
        if _ui:
            _ui.set_thinking(True)

        logger.info(f"User [{source}]: {user_text}")

        # Get AI response (actions are auto-executed by the API)
        result = brain.ask(user_text)
        response_text    = result["text"]
        model_used       = result["model_used"]
        actions_executed  = result.get("actions_executed", [])

        logger.info(f"Devta [{model_used}]: {response_text}")

        # Update UI
        if _ui:
            _ui.add_devta_message(response_text)
            _ui.set_thinking(False)

        # Show executed actions in UI
        for action_result in actions_executed:
            if action_result and _ui:
                _ui.add_system_message(f"⚙ {action_result}")
                logger.info(f"Action executed: {action_result}")

        # Speak the response
        if source == "voice":
            speech_module.speak(response_text, on_done_callback=lambda: _ui and _ui.set_listening(False) if _ui else None)
        else:
            speech_module.speak(response_text)

        # Re-enable wake mode after voice interaction
        if source == "voice" and hasattr(handle_input, '_wake_listener'):
            handle_input._wake_listener.is_active = False


# ─────────────────────────────────────────────
#  Voice Interaction Session
# ─────────────────────────────────────────────
def start_voice_session(brain, system_ctrl, speech_module, wake_listener):
    """Called when wake word is detected. Listens for command and responds."""
    global _ui

    # Greet user
    greetings = ["Haan bolo, main sun raha hoon!", "Yes, how can I help you?", "Bilkul, boliye!"]
    import random
    greeting = random.choice(greetings)

    if _ui:
        _ui.set_listening(True)
        _ui.add_devta_message(greeting)

    speech_module.speak(greeting)
    time.sleep(0.5)

    # Listen for user command
    user_text = speech_module.listen()

    if user_text:
        if _ui:
            _ui.add_user_message(user_text)
        handle_input(user_text, brain, system_ctrl, speech_module, source="voice")
    else:
        if _ui:
            _ui.set_listening(False)

    # Always return mic to wake word listener after session
    wake_listener.acquire_mic()


# ─────────────────────────────────────────────
#  Wake Word Callbacks
# ─────────────────────────────────────────────
def make_callbacks(brain, system_ctrl, speech_module, wake_listener, notifier):
    """Build the wake/stop/resume event callbacks."""

    def on_wake():
        if _ui:
            _ui.set_status("Activated!", "#c4a8ff")
        threading.Thread(
            target=start_voice_session,
            args=(brain, system_ctrl, speech_module, wake_listener),
            daemon=True
        ).start()

    def on_stop():
        global suggestions_enabled
        suggestions_enabled[0] = False
        brain.disable_suggestions()
        speech_module.speak("Theek hai, main chup ho jaata hoon. Zaroorat ho to 'Hello Devta' bol dena.")
        if _ui:
            _ui.add_devta_message("🔕 Suggestions paused. Say 'Hello Devta' to resume.")
            _ui.set_status("Silent Mode", "#ff8c69")

    def on_resume():
        global suggestions_enabled
        suggestions_enabled[0] = True
        brain.enable_suggestions()
        speech_module.speak("Main wapas aa gaya! Suggestions phir se shuru.")
        if _ui:
            _ui.add_devta_message("🔔 Suggestions resumed!")
            _ui.set_status("Standby", None)

    return on_wake, on_stop, on_resume


# ─────────────────────────────────────────────
#  UI Text Input Handler
# ─────────────────────────────────────────────
def make_text_handler(brain, system_ctrl, speech_module):
    def handler(text: str):
        handle_input(text, brain, system_ctrl, speech_module, source="text")
    return handler


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────
def main():
    """Main entry point for Devta AI system."""
    global _ui

    print(BANNER)

    # ── Import modules ────────────────────────
    try:
        from brain          import DevtaBrain
        from speech         import speak, listen
        from wake_word      import WakeWordListener
        from system_control import SystemController
        from browser_monitor import BrowserMonitor
        from notifier       import Notifier
        from ui             import DevtaUI
        import speech as speech_module
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"Please run setup.bat first to install dependencies.")
        sys.exit(1)

    # ── Initialize components ─────────────────
    logger.info("Initializing Devta components...")

    system_ctrl = SystemController()

    try:
        brain       = DevtaBrain(system_controller=system_ctrl)
    except ValueError as e:
        logger.error(str(e))
        print(str(e))
        sys.exit(1)
    notifier    = Notifier()

    # ── Wake word listener ────────────────────
    wake_listener = WakeWordListener()
    on_wake, on_stop, on_resume = make_callbacks(
        brain, system_ctrl, speech_module, wake_listener, notifier
    )
    wake_listener.on_wake   = on_wake
    wake_listener.on_stop   = on_stop
    wake_listener.on_resume = on_resume
    handle_input._wake_listener = wake_listener  # share reference

    # ── Browser monitor ───────────────────────
    monitor = BrowserMonitor(notifier, suggestions_enabled)

    # ── UI ────────────────────────────────────
    text_handler = make_text_handler(brain, system_ctrl, speech_module)

    _ui = DevtaUI(
        on_user_message=text_handler,
        on_close=lambda: (
            wake_listener.stop(),
            monitor.stop(),
            logger.info("Devta shutting down.")
        )
    )

    # ── Start background services ──────────────
    wake_listener.start()
    monitor.start()
    logger.info("Background services started")

    # Startup notification
    notifier.send(
        "Devta is online! Say 'Hello Devta' to start.",
        title="✦ Devta AI"
    )

    logger.info("Devta is fully operational!")
    print(f"\n✅ Devta is fully operational!")
    print(f"Wake words: Hello Devta, Bhai Devta")
    print(f"Stop phrase: Devta stop\n")

    # ── Run UI (blocking — main thread) ───────
    _ui.run()


if __name__ == "__main__":
    main()
