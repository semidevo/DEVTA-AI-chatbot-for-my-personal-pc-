"""
Devta AI System - Logging Configuration
=========================================
Centralized logging setup for all modules.
Logs to console with color-coding and optionally to file.
"""

import logging
import sys
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file path
LOG_FILE = LOGS_DIR / "devta.log"


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED,
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelno, Fore.WHITE)
        level_name = record.levelname
        
        # Format: [LEVEL] module.function: message
        formatted = f"{log_color}[{level_name}]{Style.RESET_ALL} {record.name}: {record.getMessage()}"
        
        if record.exc_info:
            formatted += f"\n{log_color}{self.formatException(record.exc_info)}{Style.RESET_ALL}"
        
        return formatted


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger instance for the given module name.
    
    Args:
        name: Module name (typically __name__)
        level: Logging level (default: INFO)
    
    Returns:
        Configured Logger instance
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)
    
    # File handler (always INFO level for debugging)
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")
    
    return logger


# Default logger for the main system
logger = get_logger("devta", level=logging.INFO)
