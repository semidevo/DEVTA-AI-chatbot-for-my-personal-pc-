"""
Devta AI System - Custom API Layer
=====================================
Wraps Gemini with native function calling for reliable system command execution.
Instead of asking the model to embed JSON in text, we declare structured tools
that Gemini can call directly → 100% reliable action execution.
"""

import time
from typing import Optional, Any
from google import genai
from google.genai import types
from config import (
    GEMINI_API_KEY, GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL,
    PRO_ESCALATION_KEYWORDS, DEVTA_SYSTEM_PROMPT, MAX_CONVERSATION_HISTORY
)
from logger import get_logger

# Initialize logger for this module
logger = get_logger(__name__)


# ─────────────────────────────────────────────
#  Function Declarations (Tools for Gemini)
# ─────────────────────────────────────────────
DEVTA_TOOLS = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="open_app",
            description="Open an application on the user's Windows PC. Use common app names like 'notepad', 'chrome', 'calculator', 'spotify', 'vscode', etc.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "app": types.Schema(type="STRING", description="Name of the application to open (e.g. 'notepad', 'chrome', 'calculator')")
                },
                required=["app"]
            )
        ),
        types.FunctionDeclaration(
            name="close_app",
            description="Close/kill a running application on the user's PC.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "app": types.Schema(type="STRING", description="Name of the application to close")
                },
                required=["app"]
            )
        ),
        types.FunctionDeclaration(
            name="web_search",
            description="Search Google for a query. Opens the browser with search results.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "query": types.Schema(type="STRING", description="The search query")
                },
                required=["query"]
            )
        ),
        types.FunctionDeclaration(
            name="open_url",
            description="Open a specific URL in the default web browser.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "url": types.Schema(type="STRING", description="The full URL to open")
                },
                required=["url"]
            )
        ),
        types.FunctionDeclaration(
            name="take_screenshot",
            description="Take a screenshot of the user's screen and save it to Desktop.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "filename": types.Schema(type="STRING", description="Optional custom filename for the screenshot")
                },
            )
        ),
        types.FunctionDeclaration(
            name="volume_up",
            description="Increase the system volume.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "steps": types.Schema(type="INTEGER", description="Number of volume steps to increase (default 5)")
                },
            )
        ),
        types.FunctionDeclaration(
            name="volume_down",
            description="Decrease the system volume.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "steps": types.Schema(type="INTEGER", description="Number of volume steps to decrease (default 5)")
                },
            )
        ),
        types.FunctionDeclaration(
            name="volume_mute",
            description="Toggle mute/unmute the system volume.",
            parameters=types.Schema(
                type="OBJECT",
                properties={},
            )
        ),
        types.FunctionDeclaration(
            name="get_system_info",
            description="Get current system information including CPU usage, RAM usage, and disk usage.",
            parameters=types.Schema(
                type="OBJECT",
                properties={},
            )
        ),
        types.FunctionDeclaration(
            name="get_time",
            description="Get the current date and time.",
            parameters=types.Schema(
                type="OBJECT",
                properties={},
            )
        ),
        types.FunctionDeclaration(
            name="get_battery",
            description="Get the current battery level and charging status.",
            parameters=types.Schema(
                type="OBJECT",
                properties={},
            )
        ),
        types.FunctionDeclaration(
            name="copy_to_clipboard",
            description="Copy text to the system clipboard.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "text": types.Schema(type="STRING", description="Text to copy to clipboard")
                },
                required=["text"]
            )
        ),
        types.FunctionDeclaration(
            name="get_clipboard",
            description="Get the current contents of the system clipboard.",
            parameters=types.Schema(
                type="OBJECT",
                properties={},
            )
        ),
        types.FunctionDeclaration(
            name="create_file",
            description="Create a new file with optional content.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "path": types.Schema(type="STRING", description="File path to create (supports ~ for home directory)"),
                    "content": types.Schema(type="STRING", description="Content to write to the file")
                },
                required=["path"]
            )
        ),
        types.FunctionDeclaration(
            name="read_file",
            description="Read the contents of a file.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "path": types.Schema(type="STRING", description="File path to read (supports ~ for home directory)")
                },
                required=["path"]
            )
        ),
        types.FunctionDeclaration(
            name="run_command",
            description="Run a shell command on the user's PC. Use for tasks like checking installed software, listing files, etc. Be careful with destructive commands.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "command": types.Schema(type="STRING", description="The shell command to execute")
                },
                required=["command"]
            )
        ),
        types.FunctionDeclaration(
            name="lock_screen",
            description="Lock the user's Windows screen.",
            parameters=types.Schema(
                type="OBJECT",
                properties={},
            )
        ),
        types.FunctionDeclaration(
            name="shutdown",
            description="Shut down the user's PC (with a 30 second delay so user can cancel).",
            parameters=types.Schema(
                type="OBJECT",
                properties={},
            )
        ),
        types.FunctionDeclaration(
            name="restart",
            description="Restart the user's PC (with a 30 second delay so user can cancel).",
            parameters=types.Schema(
                type="OBJECT",
                properties={},
            )
        ),
    ])
]


# ─────────────────────────────────────────────
#  DevtaAPI — Custom API with Function Calling
# ─────────────────────────────────────────────
class DevtaAPI:
    """
    Custom API layer that wraps Gemini with native function calling.
    
    Usage:
        api = DevtaAPI(system_controller)
        result = api.chat("Open Notepad")
        # result = {"text": "Done! Notepad is open.", "actions_executed": ["Opened notepad"], "model_used": "Gemini 2.0 Flash Lite"}
    """

    def __init__(self, system_controller: Any) -> None:
        """
        Initialize DevtaAPI.
        
        Args:
            system_controller: SystemController instance for executing actions
            
        Raises:
            ValueError: If GEMINI_API_KEY is not set or invalid
        """
        if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
            error_msg = (
                "\nGemini API key not found!\n"
                "Please create a .env file with your key:\n"
                "  GEMINI_API_KEY=your_key_here\n"
                "Get a free key at: https://aistudio.google.com/"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.system_ctrl = system_controller
        self.history = []  # Conversation history as Content objects
        self._method_map = system_controller.get_method_map()

        logger.info("Custom API initialized — Function Calling enabled")
        logger.info(f"Registered {len(self._method_map)} system tools")

    # ──────────────────────────────────────────
    #  Model Selection
    # ──────────────────────────────────────────
    def _should_escalate(self, user_input: str) -> bool:
        """Check if input requires Pro model escalation."""
        lower = user_input.lower()
        return any(kw in lower for kw in PRO_ESCALATION_KEYWORDS)

    # ──────────────────────────────────────────
    #  History Management
    # ──────────────────────────────────────────
    def _trim_history(self) -> None:
        """Trim conversation history to max_items."""
        max_items = MAX_CONVERSATION_HISTORY * 2
        if len(self.history) > max_items:
            self.history = self.history[-max_items:]
            logger.debug(f"Trimmed history to {max_items} items")

    def reset_conversation(self) -> None:
        """Clear conversation history."""
        self.history = []
        logger.info("Conversation history cleared")

    # ──────────────────────────────────────────
    #  Execute a Function Call
    # ──────────────────────────────────────────
    def _execute_function_call(self, function_call: Any) -> str:
        """Execute a function call from Gemini and return the result string.
        
        Args:
            function_call: Function call object from Gemini
            
        Returns:
            Result string from execution
        """
        fn_name = function_call.name
        fn_args = dict(function_call.args) if function_call.args else {}

        logger.info(f"Executing: {fn_name}({fn_args})")

        method = self._method_map.get(fn_name)
        if not method:
            logger.warning(f"Unknown function: {fn_name}")
            return f"Unknown function: {fn_name}"

        try:
            result = method(**fn_args)
            logger.info(f"✓ Result: {result}")
            return str(result)
        except TypeError as e:
            error_msg = f"Invalid arguments for {fn_name}: {e}"
            logger.error(error_msg, exc_info=True)
            return error_msg
        except Exception as e:
            error_msg = f"Error executing {fn_name}: {e}"
            logger.error(error_msg, exc_info=True)
            return error_msg

    # ──────────────────────────────────────────
    #  Main Chat Method
    # ──────────────────────────────────────────
    def chat(self, user_input: str, context: Optional[str] = None) -> dict[str, Any]:
        """
        Send a message to Devta and get a response.
        Handles function calling automatically.

        Args:
            user_input: The user's message
            context: Optional context (e.g. from browser monitor)

        Returns:
            {
                "text": str,              # Devta's text response
                "actions_executed": list,  # List of action result strings
                "model_used": str          # Which model was used
            }
        """
        prompt = user_input
        if context:
            prompt = f"[Context: {context}]\n\nUser: {user_input}"

        # Model selection
        use_pro = self._should_escalate(user_input)
        model_name = GEMINI_PRO_MODEL if use_pro else GEMINI_FLASH_MODEL
        model_label = "Gemini 2.5 Flash (Pro)" if use_pro else "Gemini 2.0 Flash Lite"

        # Build contents: history + new user message
        contents = list(self.history)  # copy
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=prompt)]
            )
        )

        config = types.GenerateContentConfig(
            system_instruction=DEVTA_SYSTEM_PROMPT,
            temperature=0.8,
            max_output_tokens=1024,
            tools=DEVTA_TOOLS,
        )

        actions_executed = []

        # Retry up to 3 times on quota errors
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )

                # Process the response — handle function calls in a loop
                while response.candidates and response.candidates[0].content:
                    candidate = response.candidates[0]
                    parts = candidate.content.parts

                    # Check if there are any function calls
                    function_calls = [p for p in parts if p.function_call]

                    if not function_calls:
                        # No function calls — we have the final text response
                        break

                    # Add the model's response (with function calls) to contents
                    contents.append(candidate.content)

                    # Execute each function call and collect results
                    function_responses = []
                    for part in function_calls:
                        result = self._execute_function_call(part.function_call)
                        actions_executed.append(result)
                        function_responses.append(
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=part.function_call.name,
                                    response={"result": result}
                                )
                            )
                        )

                    # Send function results back to the model
                    contents.append(
                        types.Content(
                            role="user",
                            parts=function_responses
                        )
                    )

                    # Get next response (model will now generate text based on function results)
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=config,
                    )

                # Extract final text
                response_text = ""
                if response.candidates and response.candidates[0].content:
                    text_parts = [
                        p.text for p in response.candidates[0].content.parts
                        if p.text
                    ]
                    response_text = "\n".join(text_parts)

                # Update conversation history (store user message + final model response)
                self.history.append(
                    types.Content(role="user", parts=[types.Part(text=prompt)])
                )
                if response_text:
                    self.history.append(
                        types.Content(role="model", parts=[types.Part(text=response_text)])
                    )
                self._trim_history()

                return {
                    "text": response_text.strip(),
                    "actions_executed": actions_executed,
                    "model_used": model_label,
                }

            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    wait = (attempt + 1) * 15
                    logger.warning(f"Rate limit hit. Waiting {wait}s (attempt {attempt+1}/3)...")
                    time.sleep(wait)
                    if attempt == 2:
                        return {
                            "text": "Yaar, mera API quota abhi exhausted hai. Thodi der baad try karo.",
                            "actions_executed": [],
                            "model_used": "quota-exhausted",
                        }
                else:
                    error_msg = f"API Error: {err_str[:100]}"
                    logger.error(error_msg, exc_info=True)
                    return {
                        "text": error_msg,
                        "actions_executed": [],
                        "model_used": "error",
                    }

        logger.error("Chat failed after 3 retries")
        return {
            "text": "Quota exhausted, please try again later.",
            "actions_executed": [],
            "model_used": "error",
        }

    # ──────────────────────────────────────────
    #  (The suggest method was removed to save quota)
    # ──────────────────────────────────────────
