"""
Logging utilities for gesture control library.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


class GestureControlLogger:
    """
    Configurable logging for the gesture control system.

    Provides console and file logging with different log levels.
    """

    def __init__(self,
                 name: str = "gesture_control",
                 level: str = "INFO",
                 log_file: Optional[str] = None,
                 max_bytes: int = 10*1024*1024,  # 10MB
                 backup_count: int = 5):
        """
        Initialize logger.

        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to log file (optional)
            max_bytes: Maximum log file size in bytes
            backup_count: Number of backup log files to keep
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler (if specified)
        if log_file:
            # Ensure log directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.logger.info(f"Logger initialized with level {level}")

    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger

    def set_level(self, level: str):
        """Set the logging level."""
        self.logger.setLevel(getattr(logging, level.upper()))
        self.logger.info(f"Log level changed to {level}")

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)


# Global logger instance
_logger_instance = None


def get_logger(name: str = "gesture_control",
               level: str = "INFO",
               log_file: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name
        level: Log level
        log_file: Optional log file path

    Returns:
        Configured logger instance
    """
    global _logger_instance

    if _logger_instance is None or _logger_instance.logger.name != name:
        _logger_instance = GestureControlLogger(name, level, log_file)

    return _logger_instance.get_logger()


def setup_default_logging(level: str = "INFO", log_file: Optional[str] = None):
    """
    Set up default logging for the gesture control library.

    Args:
        level: Log level
        log_file: Optional log file path
    """
    # Set up basic logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logging.getLogger().addHandler(file_handler)
