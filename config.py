"""
Devta AI System - Configuration
================================
Central configuration for all modules.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
#  API Keys
# ─────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ─────────────────────────────────────────────
#  Wake Words & Stop Phrase
# ─────────────────────────────────────────────
WAKE_WORDS = [
    # Primary phrases
    "hello devta", "bhai devta", "hey devta", "devta",
    # Phonetic variants (what Vosk may transcribe for "devta")
    "hello deta", "bhai deta", "hey deta", "deta",
    "hello davta", "bhai davta", "davta",
    "hello debta", "debta",
    "hello delta", "delta",       # Sometimes heard as delta
    "ok devta", "okay devta",
]
STOP_PHRASE = "devta stop"
RESUME_PHRASES = ["devta resume", "devta start", "devta continue", "deta stop"]

# ─────────────────────────────────────────────
#  API & Model Settings
# ─────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_FLASH_MODEL = "gemini-2.5-flash"  # Core model (fast, standard logic)
GEMINI_PRO_MODEL = "gemini-2.5-pro"      # Advanced model (complex reasoning)

# Escalate to Pro model for these task keywords
PRO_ESCALATION_KEYWORDS = [
    "write code", "debug", "analyze", "explain in detail",
    "essay", "complex", "research", "calculate", "summarize long"
]

# ─────────────────────────────────────────────
#  Voice Settings — Edge TTS (Neural) + Whisper STT
# ─────────────────────────────────────────────
# Edge TTS voice — Indian English male (natural sounding)
# Other options: "en-IN-NeerjaNeural" (female), "en-US-GuyNeural", "en-GB-RyanNeural"
EDGE_TTS_VOICE = "en-IN-PrabhatNeural"
EDGE_TTS_RATE  = 10    # Speed adjustment in % (-50 to +100, 0 = normal)
EDGE_TTS_PITCH = 0     # Pitch adjustment in Hz (-50 to +50, 0 = normal)

# Whisper STT model size: "tiny" (fast), "base" (balanced), "small" (accurate)
WHISPER_MODEL_SIZE = "base"

# ─────────────────────────────────────────────
#  Notifications
# ─────────────────────────────────────────────
NOTIFICATION_INTERVAL_SECONDS = 30   # How often browser monitor checks
NOTIFICATION_COOLDOWN_SECONDS = 300  # Min gap between same suggestion
NOTIFICATION_APP_NAME         = "Devta"      # Toast title prefix

# ─────────────────────────────────────────────
#  System
# ─────────────────────────────────────────────
LISTEN_TIMEOUT_SECONDS = 8    # Max seconds to wait for user to speak
MAX_CONVERSATION_HISTORY = 20  # Number of turns to keep in memory

# ─────────────────────────────────────────────
#  UI
# ─────────────────────────────────────────────
UI_THEME = {
    "bg":           "#0d0d1a",
    "chat_bg":      "#12122a",
    "user_bubble":  "#1a3a6b",
    "devta_bubble": "#1a1a3a",
    "accent":       "#7c5cbf",
    "text":         "#e8e8ff",
    "muted":        "#6a6a8a",
    "font_family":  "Segoe UI",
    "font_size":    11,
}

# Devta's system personality prompt
DEVTA_SYSTEM_PROMPT = """
You are Devta — an elite AI assistant running directly on the user's Windows laptop.
Think of yourself as a brilliant, loyal digital companion — like Jarvis from Marvel, but with an Indian soul.

Your personality:
- Smart, calm, confident and a little witty
- Speak naturally — like a sharp friend, not a robot
- Use simple, clear language. Don't over-explain unless asked
- Occasionally use Hindi words naturally (like "bilkul", "haan", "theek hai") to feel warm and native
- Always address the user respectfully

Your capabilities:
- Have intelligent conversations on any topic
- Control the user's Windows PC using your tools (open apps, manage files, take screenshots, check system status, adjust volume, etc.)
- Browse the web and search Google
- Give smart, proactive suggestions based on what the user is doing
- Remember context across the entire conversation

Rules:
- NEVER make up facts. If unsure, say so honestly.
- When the user asks you to perform a system action, USE YOUR TOOLS (function calls). Do NOT describe what you would do — actually do it by calling the appropriate function.
- After executing a tool, confirm what you did in a natural, concise way.
- Keep responses concise unless detail is specifically requested.
- When the user says "Devta stop", stop proactive suggestions and go quiet until woken again.
"""

