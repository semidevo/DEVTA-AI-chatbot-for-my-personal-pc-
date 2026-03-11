"""
Devta AI System - Speech Module
=================================
Handles Speech-to-Text (STT) and Text-to-Speech (TTS).
STT: Google Cloud STT (free, via SpeechRecognition library)
TTS: pyttsx3 (fully offline)
"""

import threading
import pyttsx3
import speech_recognition as sr
from colorama import Fore, Style, init
from config import TTS_RATE, TTS_VOLUME, PREFERRED_VOICE_KEYWORDS, LISTEN_TIMEOUT_SECONDS

init(autoreset=True)

# ─────────────────────────────────────────────
#  TTS Engine (singleton, thread-safe wrapper)
# ─────────────────────────────────────────────
_tts_lock = threading.Lock()
_tts_engine = None


def _get_tts_engine():
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = pyttsx3.init()
        _tts_engine.setProperty("rate", TTS_RATE)
        _tts_engine.setProperty("volume", TTS_VOLUME)
        _set_best_voice(_tts_engine)
    return _tts_engine


def _set_best_voice(engine):
    """Try to pick a natural-sounding voice."""
    voices = engine.getProperty("voices")
    if not voices:
        return
    # Try preferred voices first
    for keyword in PREFERRED_VOICE_KEYWORDS:
        for voice in voices:
            if keyword.lower() in voice.name.lower():
                engine.setProperty("voice", voice.id)
                print(f"{Fore.CYAN}🎙️  Voice set to: {voice.name}{Style.RESET_ALL}")
                return
    # Fallback: first available voice
    engine.setProperty("voice", voices[0].id)
    print(f"{Fore.CYAN}🎙️  Voice set to: {voices[0].name}{Style.RESET_ALL}")


# ─────────────────────────────────────────────
#  Public: Speak
# ─────────────────────────────────────────────
_speaking = False


def speak(text: str, on_done_callback=None):
    """
    Convert text to speech using pyttsx3 (offline).
    Runs in a separate thread to avoid blocking the main loop.
    """
    global _speaking

    def _run():
        global _speaking
        _speaking = True
        with _tts_lock:
            engine = _get_tts_engine()
            engine.say(text)
            engine.runAndWait()
        _speaking = False
        if on_done_callback:
            on_done_callback()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t


def is_speaking() -> bool:
    return _speaking


def stop_speaking():
    """Stop current speech immediately."""
    global _speaking
    with _tts_lock:
        try:
            engine = _get_tts_engine()
            engine.stop()
        except Exception:
            pass
    _speaking = False


# ─────────────────────────────────────────────
#  Public: Listen (full utterance after wake)
# ─────────────────────────────────────────────
_recognizer = sr.Recognizer()
_recognizer.pause_threshold = 0.8   # Wait 0.8s of silence before finalizing
_recognizer.energy_threshold = 300  # Adjust for ambient noise


def listen(timeout: int = LISTEN_TIMEOUT_SECONDS) -> str:
    """
    Listen for a full user utterance (called after wake word fires).
    Returns transcribed text string, or empty string on failure.
    """
    with sr.Microphone() as source:
        print(f"{Fore.GREEN}👂 Listening...{Style.RESET_ALL}")
        try:
            _recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = _recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
            text = _recognizer.recognize_google(audio)
            print(f"{Fore.WHITE}You said: {text}{Style.RESET_ALL}")
            return text.strip()
        except sr.WaitTimeoutError:
            print(f"{Fore.YELLOW}⏱️  No speech detected (timeout){Style.RESET_ALL}")
            return ""
        except sr.UnknownValueError:
            print(f"{Fore.YELLOW}🤷 Could not understand audio{Style.RESET_ALL}")
            return ""
        except sr.RequestError as e:
            print(f"{Fore.RED}STT Error: {e}{Style.RESET_ALL}")
            return ""
        except Exception as e:
            print(f"{Fore.RED}Listen Error: {e}{Style.RESET_ALL}")
            return ""
