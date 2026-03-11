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
#  AI Models
# ─────────────────────────────────────────────
# Primary: fast, free-tier friendly (1500 req/day)
GEMINI_FLASH_MODEL = "gemini-2.0-flash-lite"
# Secondary: used for complex tasks (coding, deep analysis)
GEMINI_PRO_MODEL   = "gemini-2.5-flash"

# Escalate to Pro model for these task keywords
PRO_ESCALATION_KEYWORDS = [
    "write code", "debug", "analyze", "explain in detail",
    "essay", "complex", "research", "calculate", "summarize long"
]

# ─────────────────────────────────────────────
#  Voice Settings
# ─────────────────────────────────────────────
TTS_RATE    = 175   # Words per minute
TTS_VOLUME  = 1.0   # 0.0 – 1.0
# Preferred voice (will search for Indian/male voice first, fallback to default)
PREFERRED_VOICE_KEYWORDS = ["zira", "hazel", "david", "indian", "ravi", "heera"]

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
- Control the user's Windows PC (open apps, manage files, take screenshots, check system status)
- Browse the web and summarize information
- Give smart, proactive suggestions based on what the user is doing
- Remember context across the entire conversation

Rules:
- NEVER make up facts. If unsure, say so honestly.
- For system commands, output a special JSON block like:
  {"system_action": "open_app", "app": "notepad"}
  This tells the system what to actually execute.
- Keep responses concise unless detail is specifically requested.
- When the user says "Devta stop", stop proactive suggestions and go quiet until woken again.
"""
