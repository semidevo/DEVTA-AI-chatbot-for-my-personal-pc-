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
from colorama import Fore, Style, init

init(autoreset=True)

# ─────────────────────────────────────────────
#  Vosk model download (first-run only)
# ─────────────────────────────────────────────
VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
VOSK_MODEL_DIR = Path(__file__).parent / "vosk_model"
VOSK_MODEL_ZIP = Path(__file__).parent / "vosk_model.zip"


def _ensure_vosk_model():
    if VOSK_MODEL_DIR.exists() and any(VOSK_MODEL_DIR.iterdir()):
        return  # Already downloaded

    print(f"{Fore.CYAN}[DEVTA] Downloading Vosk model (~50MB) for offline wake-word detection...{Style.RESET_ALL}")
    print("    This happens only once. Please wait...")

    urllib.request.urlretrieve(VOSK_MODEL_URL, VOSK_MODEL_ZIP)

    print(f"{Fore.CYAN}[DEVTA] Extracting Vosk model...{Style.RESET_ALL}")
    with zipfile.ZipFile(VOSK_MODEL_ZIP, 'r') as z:
        z.extractall(Path(__file__).parent)

    # Rename extracted folder to vosk_model
    extracted = [d for d in Path(__file__).parent.iterdir()
                 if d.is_dir() and d.name.startswith("vosk-model")]
    if extracted:
        extracted[0].rename(VOSK_MODEL_DIR)

    VOSK_MODEL_ZIP.unlink(missing_ok=True)
    print(f"{Fore.GREEN}[DEVTA] Vosk model ready!{Style.RESET_ALL}")


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
        print(f"{Fore.GREEN}[DEVTA] Wake word listener started (always-on mic){Style.RESET_ALL}")

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
                print(f"{Fore.CYAN}[DEVTA] Using mic: [{mic_index}] {dev_info['name']}{Style.RESET_ALL}")
            else:
                try:
                    dev_info = pa.get_default_input_device_info()
                    mic_index = dev_info["index"]
                    print(f"{Fore.CYAN}[DEVTA] Using system default mic: [{mic_index}] {dev_info['name']}{Style.RESET_ALL}")
                except Exception:
                    print(f"{Fore.YELLOW}[DEVTA] Using system default mic (index unknown){Style.RESET_ALL}")

            stream = pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=mic_index,
                frames_per_buffer=4000
            )
            stream.start_stream()

            print(f"{Fore.MAGENTA}[DEVTA] Microphone ACTIVE! Say 'Hello Devta' or 'Bhai Devta' to wake me.{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}[DEVTA] Listening... (you'll see transcripts below){Style.RESET_ALL}")

            while self._running:
                # ── Mic pause: stop reading while voice session has the mic ──
                if not self._mic_released.is_set():
                    # Close the stream so speech.py can open the mic
                    stream.stop_stream()
                    stream.close()
                    pa.terminate()
                    print(f"\n{Fore.CYAN}[DEVTA] Mic handed to voice session...{Style.RESET_ALL}")

                    # Wait until acquire_mic() is called
                    self._mic_released.wait()

                    if not self._running:
                        return

                    # Re-open the stream
                    print(f"{Fore.CYAN}[DEVTA] Resuming wake word listening...{Style.RESET_ALL}")
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

                # Live transcription
                print(f"\r{Fore.YELLOW}[MIC] {text:<60}{Style.RESET_ALL}", end="", flush=True)

                # ── Stop phrase (highest priority) ──
                if STOP_PHRASE.lower() in text:
                    if self.suggestions_enabled:
                        self.suggestions_enabled = False
                        self.is_active = False
                        print(f"\n{Fore.YELLOW}[DEVTA] Stop phrase detected - going quiet{Style.RESET_ALL}")
                        self.on_stop()
                    continue

                # ── Resume phrases ──
                if any(rp.lower() in text for rp in RESUME_PHRASES):
                    if not self.suggestions_enabled:
                        self.suggestions_enabled = True
                        print(f"\n{Fore.GREEN}[DEVTA] Resume phrase detected{Style.RESET_ALL}")
                        self.on_resume()
                    continue

                # ── Wake words ──
                if not self.is_active:
                    if any(ww.lower() in text for ww in WAKE_WORDS):
                        self.is_active = True
                        print(f"\n{Fore.MAGENTA}[DEVTA] WAKE WORD DETECTED: '{text}' - Activating!{Style.RESET_ALL}")
                        # Release mic BEFORE calling on_wake so speech.py can use it
                        self.release_mic()
                        self.on_wake()

            stream.stop_stream()
            stream.close()
            pa.terminate()

        except ImportError:
            print(f"{Fore.RED}[DEVTA] Vosk/PyAudio not installed. Run setup.bat first.{Style.RESET_ALL}")
        except OSError as e:
            print(f"{Fore.RED}[DEVTA] Microphone error: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[DEVTA] Make sure your microphone is not in use by another app.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[DEVTA] Wake word error: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
