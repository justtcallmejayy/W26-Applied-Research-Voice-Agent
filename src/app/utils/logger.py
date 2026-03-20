
"""
src.app.utils.logger

Centralized logging configuration.
"""

import logging
from pathlib import Path
from datetime import datetime
import sys

_session_log_file = None

def setup_logger(
    name: str,
    log_type: str = "general",
    level: int = logging.INFO
) -> logging.Logger:
    """
    Set up logger with timestamped file and console output.
    
    Args:
        name: Logger name (usually __name__ from calling module)
        log_type: Category for organizing logs (e.g., "test", "dashboard", "agent")
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """

    global _session_log_file

    if _session_log_file is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_dir = Path(__file__).parent.parent / "logs" / log_type
        log_dir.mkdir(parents=True, exist_ok=True)
        _session_log_file = log_dir / f"{timestamp}.log"

    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '[%(levelname)s] %(filename)s:%(lineno)d - %(funcName)s() - %(message)s'
    )
    
    file_handler = logging.FileHandler(_session_log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger