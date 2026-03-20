"""
Devta AI System - Speech Module (v2)
======================================
UPGRADED:
  STT: OpenAI Whisper (offline, handles Indian accents perfectly)
  TTS: Microsoft Edge TTS (free neural voices, near-human quality)
"""

import os
import io
import wave
import tempfile
import threading
import asyncio
from typing import Optional
import numpy as np
from config import (
    LISTEN_TIMEOUT_SECONDS, EDGE_TTS_VOICE,
    EDGE_TTS_RATE, EDGE_TTS_PITCH, WHISPER_MODEL_SIZE
)
from logger import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────
#  Whisper STT (lazy-loaded singleton)
# ─────────────────────────────────────────────
_whisper_model = None
_whisper_lock = threading.Lock()


def _get_whisper_model():
    """Load Whisper model (lazy-loaded singleton)."""
    global _whisper_model
    if _whisper_model is None:
        with _whisper_lock:
            if _whisper_model is None:
                try:
                    import whisper
                    logger.info(f"Loading Whisper '{WHISPER_MODEL_SIZE}' model (first time may download ~150MB)...")
                    _whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
                    logger.info("Whisper model loaded successfully")
                except Exception as e:
                    logger.error(f"Failed to load Whisper model: {e}", exc_info=True)
                    raise
    return _whisper_model


# ─────────────────────────────────────────────
#  Edge TTS (async wrapper)
# ─────────────────────────────────────────────
_tts_lock = threading.Lock()
_speaking = False
_current_player = None  # Track current playback for stop


def _get_or_create_event_loop():
    """Get the current event loop or create a new one for this thread."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("closed")
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


async def _generate_and_play(text: str):
    """Generate speech with edge-tts and play it using pygame mixer."""
    import edge_tts
    import pygame

    # Generate speech to a temp file
    tmp_file = os.path.join(tempfile.gettempdir(), "devta_tts.mp3")

    rate_str = f"{EDGE_TTS_RATE:+d}%"
    pitch_str = f"{EDGE_TTS_PITCH:+d}Hz"

    communicate = edge_tts.Communicate(
        text=text,
        voice=EDGE_TTS_VOICE,
        rate=rate_str,
        pitch=pitch_str,
    )
    await communicate.save(tmp_file)

    # Play using pygame (non-blocking within this thread)
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    pygame.mixer.music.load(tmp_file)
    pygame.mixer.music.play()

    # Wait for playback to finish
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

    # Cleanup
    try:
        pygame.mixer.music.unload()
        os.remove(tmp_file)
    except Exception:
        pass


# ─────────────────────────────────────────────
#  Public: Speak
# ─────────────────────────────────────────────
def speak(text: str, on_done_callback: Optional[callable] = None) -> Optional[threading.Thread]:
    """
    Convert text to speech using Edge TTS (neural, high-quality).
    Runs in a separate thread to avoid blocking.
    
    Args:
        text: Text to speak
        on_done_callback: Optional callback when speech finishes
        
    Returns:
        Thread object or None
    """
    global _speaking

    if not text or not text.strip():
        logger.debug("Empty text provided to speak()")
        if on_done_callback:
            on_done_callback()
        return

    def _run():
        global _speaking
        _speaking = True
        with _tts_lock:
            try:
                logger.info(f"Speaking: {text[:50]}...")
                loop = _get_or_create_event_loop()
                loop.run_until_complete(_generate_and_play(text))
                logger.info("Speech completed")
            except Exception as e:
                logger.error(f"TTS Error: {e}", exc_info=True)
        _speaking = False
        if on_done_callback:
            on_done_callback()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t


def is_speaking() -> bool:
    """Check if currently speaking."""
    return _speaking


def stop_speaking() -> None:
    """Stop current speech immediately."""
    global _speaking
    try:
        import pygame
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            logger.info("Speech stopped")
    except Exception:
        pass
    _speaking = False


# ─────────────────────────────────────────────
#  Public: Listen (Whisper-based, after wake)
# ─────────────────────────────────────────────
def listen(timeout: int = LISTEN_TIMEOUT_SECONDS) -> str:
    """
    Listen for a full user utterance using Whisper.
    Records audio via PyAudio, transcribes with Whisper.
    Returns transcribed text string, or empty string on failure.
    
    Args:
        timeout: Listening timeout in seconds
        
    Returns:
        Transcribed text or empty string
    """
    import pyaudio

    RATE = 16000
    CHANNELS = 1
    CHUNK = 1024
    FORMAT = pyaudio.paInt16

    pa = pyaudio.PyAudio()
    
    logger.info("Starting listening mode")

    try:
        logger.debug("Opening audio stream")
        stream = pa.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        frames = []
        silence_threshold = 500   # RMS threshold for silence
        silence_chunks = 0
        max_silence_chunks = int(1.5 * RATE / CHUNK)  # 1.5s of silence = done
        max_total_chunks = int(timeout * RATE / CHUNK)
        min_speech_chunks = int(0.3 * RATE / CHUNK)    # Need at least 0.3s of speech
        speech_detected = False

        for i in range(max_total_chunks):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

            # Calculate RMS for silence detection
            audio_array = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))

            if rms > silence_threshold:
                silence_chunks = 0
                speech_detected = True
            else:
                silence_chunks += 1

            # Stop if enough silence after speech
            if speech_detected and silence_chunks > max_silence_chunks:
                break

        stream.stop_stream()
        stream.close()

        if not speech_detected or len(frames) < min_speech_chunks:
            logger.warning("No speech detected (timeout)")
            return ""

        # Convert frames to WAV for Whisper
        audio_data = b"".join(frames)

        # Save to temp WAV file
        tmp_wav = os.path.join(tempfile.gettempdir(), "devta_stt.wav")
        with wave.open(tmp_wav, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(pa.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(audio_data)

        logger.debug("Transcribing audio with Whisper")
        # Transcribe with Whisper
        model = _get_whisper_model()
        result = model.transcribe(
            tmp_wav,
            language="en",
            fp16=False,  # CPU-safe
        )
        text = result.get("text", "").strip()

        # Cleanup
        try:
            os.remove(tmp_wav)
        except Exception:
            pass

        if text:
            logger.info(f"Transcribed: {text}")
            return text
        else:
            logger.warning("Could not understand audio")
            return ""

    except ImportError:
        logger.error("PyAudio not installed", exc_info=True)
        return ""
    except Exception as e:
        logger.error(f"Listen error: {e}", exc_info=True)
        return ""
    finally:
        try:
            pa.terminate()
        except:
            pass
