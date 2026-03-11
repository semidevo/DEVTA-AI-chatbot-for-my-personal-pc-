"""
Devta AI System - Brain Module
================================
Handles all AI inference via Google Gemini (new google-genai SDK).
Automatically escalates to Pro model for complex tasks.
"""

import json
import re
from google import genai
from google.genai import types
from colorama import Fore, Style, init
from config import (
    GEMINI_API_KEY, GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL,
    PRO_ESCALATION_KEYWORDS, DEVTA_SYSTEM_PROMPT, MAX_CONVERSATION_HISTORY
)

init(autoreset=True)


class DevtaBrain:
    def __init__(self):
        if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
            raise ValueError(
                "\n❌ Gemini API key not found!\n"
                "Please create a .env file with your key:\n"
                "  GEMINI_API_KEY=your_key_here\n"
                "Get a free key at: https://aistudio.google.com/"
            )

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.history = []          # list of {"role": "user"|"model", "parts": [str]}
        self.suggestions_enabled = True

        print(f"{Fore.CYAN}[DEVTA] Brain initialized - Gemini 2.0 Flash + 1.5 Pro hybrid{Style.RESET_ALL}")

    # ──────────────────────────────────────────
    #  Internals
    # ──────────────────────────────────────────
    def _should_escalate(self, user_input: str) -> bool:
        lower = user_input.lower()
        return any(kw in lower for kw in PRO_ESCALATION_KEYWORDS)

    def _trim_history(self):
        max_turns = MAX_CONVERSATION_HISTORY * 2
        if len(self.history) > max_turns:
            self.history = self.history[-max_turns:]

    def _build_contents(self, extra_user_msg: str) -> list:
        """Build the contents list (history + new message) for the API call."""
        contents = []
        for turn in self.history:
            contents.append(
                types.Content(
                    role=turn["role"],
                    parts=[types.Part(text=turn["parts"][0])]
                )
            )
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=extra_user_msg)]
            )
        )
        return contents

    # ──────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────
    def ask(self, user_input: str, context: str = None) -> dict:
        """
        Ask Devta something. Returns:
          {"text": str, "system_action": dict|None, "model_used": str}
        Automatically retries on 429 quota errors with backoff.
        """
        import time

        prompt = user_input
        if context:
            prompt = f"[Context: {context}]\n\nUser: {user_input}"

        use_pro    = self._should_escalate(user_input)
        model_name = GEMINI_PRO_MODEL if use_pro else GEMINI_FLASH_MODEL
        model_label = "Gemini 2.5 Flash (Pro)" if use_pro else "Gemini 2.0 Flash Lite"

        contents = self._build_contents(prompt)
        config = types.GenerateContentConfig(
            system_instruction=DEVTA_SYSTEM_PROMPT,
            temperature=0.8,
            max_output_tokens=1024,
        )

        # Retry up to 3 times on quota/rate limit errors
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )
                response_text = response.text or ""

                self.history.append({"role": "user",  "parts": [prompt]})
                self.history.append({"role": "model", "parts": [response_text]})
                self._trim_history()

                system_action = self._extract_system_action(response_text)
                clean_text    = self._clean_response(response_text)

                return {
                    "text":          clean_text,
                    "system_action": system_action,
                    "model_used":    model_label,
                }

            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    wait = (attempt + 1) * 15  # 15s, 30s, 45s
                    print(f"{Fore.YELLOW}[DEVTA] Rate limit hit. Waiting {wait}s before retry {attempt+1}/3...{Style.RESET_ALL}")
                    time.sleep(wait)
                    if attempt == 2:
                        # Final failure — tell user gracefully
                        return {
                            "text": "Yaar, mera Gemini quota abhi exhausted hai. Kal phir try karo, ya aaj ka daily limit reset hoga midnight ke baad.",
                            "system_action": None,
                            "model_used": "quota-exhausted",
                        }
                else:
                    error_msg = f"Kuch gadbad ho gayi: {err_str[:100]}"
                    print(f"{Fore.RED}Brain Error: {e}{Style.RESET_ALL}")
                    return {"text": error_msg, "system_action": None, "model_used": "error"}

        return {"text": "Quota exhausted, please try again later.", "system_action": None, "model_used": "error"}

    def suggest(self, context: str) -> str:
        """Generate a short proactive suggestion for notification popups."""
        if not self.suggestions_enabled:
            return None
        try:
            prompt = (
                f"The user is currently: {context}\n\n"
                "Give ONE short helpful tip or fact (under 15 words). "
                "Be genuinely useful, not generic. Don't start with 'I' or 'You should'."
            )
            config = types.GenerateContentConfig(
                system_instruction=DEVTA_SYSTEM_PROMPT,
                temperature=0.9,
                max_output_tokens=60,
            )
            response = self.client.models.generate_content(
                model=GEMINI_FLASH_MODEL,
                contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
                config=config,
            )
            return (response.text or "").strip()
        except Exception as e:
            print(f"{Fore.YELLOW}Suggestion error: {e}{Style.RESET_ALL}")
            return None

    def _extract_system_action(self, text: str) -> dict:
        try:
            json_pattern = r'\{[^{}]*"system_action"[^{}]*\}'
            matches = re.findall(json_pattern, text, re.DOTALL)
            if matches:
                return json.loads(matches[0])
        except (json.JSONDecodeError, IndexError):
            pass
        return None

    def _clean_response(self, text: str) -> str:
        clean = re.sub(r'\{[^{}]*"system_action"[^{}]*\}', '', text, flags=re.DOTALL)
        clean = re.sub(r'\n{3,}', '\n\n', clean).strip()
        return clean

    def reset_conversation(self):
        self.history = []
        print(f"{Fore.YELLOW}🔄 Conversation history cleared{Style.RESET_ALL}")

    def enable_suggestions(self):
        self.suggestions_enabled = True

    def disable_suggestions(self):
        self.suggestions_enabled = False
