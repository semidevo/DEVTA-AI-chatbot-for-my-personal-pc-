"""
Devta AI System - Wake Word Detection
=======================================
Runs always in the background using Vosk (offline, CPU-only).
Downloads the small Vosk English model on first run (~50MB).
Fires events on:
  - Wake words  → ACTIVE mode (pauses mic stream so speech.py can use it)
  - Stop phrase → PASSIVE mode
  - Resume phrase → back to listening
"""

import os
import queue
import threading
import json
import zipfile
import urllib.request
from pathlib import Path
from logger import get_logger

logger = get_logger(__name__)

# ─────────────────────────────────────────────
#  Vosk model download (first-run only)
# ─────────────────────────────────────────────
VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
VOSK_MODEL_DIR = Path(__file__).parent / "vosk_model"
VOSK_MODEL_ZIP = Path(__file__).parent / "vosk_model.zip"


def _ensure_vosk_model():
    """Download and extract Vosk model if not already present."""
    if VOSK_MODEL_DIR.exists() and any(VOSK_MODEL_DIR.iterdir()):
        logger.debug("Vosk model already exists")
        return  # Already downloaded

    try:
        logger.info("Downloading Vosk model (~50MB) for offline wake-word detection...")
        urllib.request.urlretrieve(VOSK_MODEL_URL, VOSK_MODEL_ZIP)

        logger.info("Extracting Vosk model...")
        with zipfile.ZipFile(VOSK_MODEL_ZIP, 'r') as z:
            z.extractall(Path(__file__).parent)

        # Rename extracted folder to vosk_model
        extracted = [d for d in Path(__file__).parent.iterdir()
                     if d.is_dir() and d.name.startswith("vosk-model")]
        if extracted:
            extracted[0].rename(VOSK_MODEL_DIR)

        VOSK_MODEL_ZIP.unlink(missing_ok=True)
        logger.info("Vosk model ready!")
    except Exception as e:
        logger.error(f"Failed to download/extract Vosk model: {e}", exc_info=True)
        raise


# ─────────────────────────────────────────────
#  Auto-detect best microphone device index
# ─────────────────────────────────────────────
def _find_best_mic_index():
    """
    Returns the device index of the best available microphone.
    Prefers the built-in laptop mic (Intel Smart Sound / Realtek).
    Falls back to system default (index None).
    """
    try:
        import pyaudio
        pa = pyaudio.PyAudio()

        preferred_keywords = [
            "intel", "microphone array", "realtek", "built-in", "internal"
        ]
        fallback_keywords = ["microphone", "input", "mic"]

        best_idx = None
        fallback_idx = None

        for i in range(pa.get_device_count()):
            try:
                info = pa.get_device_info_by_index(i)
                if info["maxInputChannels"] < 1:
                    continue
                name_lower = info["name"].lower()

                if any(kw in name_lower for kw in preferred_keywords):
                    best_idx = i
                    break
                elif any(kw in name_lower for kw in fallback_keywords):
                    if fallback_idx is None:
                        fallback_idx = i
            except Exception:
                continue

        pa.terminate()

        chosen = best_idx if best_idx is not None else fallback_idx
        return chosen  # None = let PyAudio use system default

    except Exception as e:
        print(f"{Fore.YELLOW}[DEVTA] Could not enumerate mics: {e}. Using system default.{Style.RESET_ALL}")
        return None


# ─────────────────────────────────────────────
#  Wake Word Listener Class
# ─────────────────────────────────────────────
from config import WAKE_WORDS, STOP_PHRASE, RESUME_PHRASES


class WakeWordListener:
    """
    Continuously listens to the microphone using Vosk (offline).
    IMPORTANT: When a wake word fires, it STOPS the PyAudio stream
    so that speech.py can open its own mic session without conflict.
    The stream is restarted after the voice session completes.

    Callbacks:
      on_wake   → called when a wake word is detected
      on_stop   → called when "devta stop" is detected
      on_resume → called when resume phrase is detected
    """

    def __init__(self, on_wake=None, on_stop=None, on_resume=None):
        self.on_wake   = on_wake   or (lambda: None)
        self.on_stop   = on_stop   or (lambda: None)
        self.on_resume = on_resume or (lambda: None)

        self._running  = False
        self._thread   = None

        # State flags
        self.is_active           = False   # True while voice session is going
        self.suggestions_enabled = True

        # ── Mic release/resume mechanism ──────────
        # When True, the listen loop pauses reading and waits
        self._mic_released = threading.Event()
        self._mic_released.set()  # Start in "mic available" state

    def start(self):
        """Start the background listening thread."""
        _ensure_vosk_model()
        self._running = True
        self._thread  = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        logger.info("Wake word listener started (always-on mic)")

    def stop(self):
        self._running = False
        self._mic_released.set()  # Unblock any waiting

    def release_mic(self):
        """
        Called BEFORE starting a voice session.
        Signals the listen loop to stop reading from the stream.
        """
        self._mic_released.clear()

    def acquire_mic(self):
        """
        Called AFTER a voice session ends.
        Signals the listen loop to resume reading from the stream.
        """
        self.is_active = False
        self._mic_released.set()

    def _listen_loop(self):
        """Main loop: continuously process mic audio and detect key phrases."""
        try:
            import vosk
            import pyaudio

            model      = vosk.Model(str(VOSK_MODEL_DIR))
            recognizer = vosk.KaldiRecognizer(model, 16000)
            recognizer.SetWords(False)

            # Find and log the microphone
            mic_index = _find_best_mic_index()

            pa = pyaudio.PyAudio()

            if mic_index is not None:
                dev_info = pa.get_device_info_by_index(mic_index)
                logger.info(f"Using mic: [{mic_index}] {dev_info['name']}")
            else:
                try:
                    dev_info = pa.get_default_input_device_info()
                    mic_index = dev_info["index"]
                    logger.info(f"Using system default mic: [{mic_index}] {dev_info['name']}")
                except Exception:
                    logger.info("Using system default mic (index unknown)")

            stream = pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=mic_index,
                frames_per_buffer=4000
            )
            stream.start_stream()

            logger.info("Microphone ACTIVE! Say 'Hello Devta' or 'Bhai Devta' to wake me.")
            logger.info("Listening... (you'll see transcripts below)")

            while self._running:
                # ── Mic pause: stop reading while voice session has the mic ──
                if not self._mic_released.is_set():
                    # Close the stream so speech.py can open the mic
                    stream.stop_stream()
                    stream.close()
                    pa.terminate()
                    logger.info("Mic handed to voice session...")

                    # Wait until acquire_mic() is called
                    self._mic_released.wait()

                    if not self._running:
                        return

                    # Re-open the stream
                    logger.info("Resuming wake word listening...")
                    pa = pyaudio.PyAudio()
                    stream = pa.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        input_device_index=mic_index,
                        frames_per_buffer=4000
                    )
                    stream.start_stream()
                    recognizer = vosk.KaldiRecognizer(model, 16000)
                    recognizer.SetWords(False)
                    continue

                data = stream.read(4000, exception_on_overflow=False)

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text   = result.get("text", "").lower().strip()
                else:
                    partial = json.loads(recognizer.PartialResult())
                    text    = partial.get("partial", "").lower().strip()

                if not text:
                    continue

                logger.debug(f"Detected: {text}")

                # ── Stop phrase (highest priority) ──
                if STOP_PHRASE.lower() in text:
                    if self.suggestions_enabled:
                        self.suggestions_enabled = False
                        self.is_active = False
                        logger.info("Stop phrase detected - going quiet")
                        self.on_stop()
                    continue

                # ── Resume phrases ──
                if any(rp.lower() in text for rp in RESUME_PHRASES):
                    if not self.suggestions_enabled:
                        self.suggestions_enabled = True
                        logger.info("Resume phrase detected")
                        self.on_resume()
                    continue

                # ── Wake words ──
                if not self.is_active:
                    if any(ww.lower() in text for ww in WAKE_WORDS):
                        self.is_active = True
                        logger.info(f"WAKE WORD DETECTED: '{text}' - Activating!")
                        # Release mic BEFORE calling on_wake so speech.py can use it
                        self.release_mic()
                        self.on_wake()

            stream.stop_stream()
            stream.close()
            pa.terminate()

        except ImportError:
            logger.error("Vosk/PyAudio not installed. Run setup.bat first.")
        except OSError as e:
            logger.error(f"Microphone error: {e}")
            logger.warning("Make sure your microphone is not in use by another app.")
        except Exception as e:
            logger.error(f"Wake word error: {e}", exc_info=True)
