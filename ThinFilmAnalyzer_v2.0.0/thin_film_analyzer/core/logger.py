"""
Error logging with rotation and diagnostic export functionality.
"""

import logging
import sys
import platform
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Optional
from ..config.defaults import (
    get_settings_dir,
    ERROR_LOG_FILE,
    MAX_LOG_SIZE_MB,
    LOG_BACKUP_COUNT,
    APP_NAME,
    APP_VERSION
)


class ErrorLogger:
    """
    Manages error logging with automatic rotation and diagnostic export.
    """

    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize error logger with rotating file handler.

        Args:
            log_dir: Directory for log files (uses settings dir if None)
        """
        self.log_dir = log_dir or get_settings_dir()
        self.log_path = self.log_dir / ERROR_LOG_FILE

        # Create logger
        self.logger = logging.getLogger(APP_NAME)
        self.logger.setLevel(logging.ERROR)

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Create rotating file handler
        max_bytes = MAX_LOG_SIZE_MB * 1024 * 1024  # Convert MB to bytes
        file_handler = RotatingFileHandler(
            self.log_path,
            maxBytes=max_bytes,
            backupCount=LOG_BACKUP_COUNT,
            encoding='utf-8'
        )

        # Create formatter with timestamp, level, and message
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(file_handler)

        # Also log to console for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log_error(
        self,
        error_type: str,
        error_message: str,
        context_info: Optional[str] = None,
        stack_trace: Optional[str] = None
    ) -> None:
        """
        Log an error with context information.

        Args:
            error_type: Category of error (e.g., "FileReadError", "ProcessingError")
            error_message: The error message
            context_info: Additional context (e.g., file being processed)
            stack_trace: Optional stack trace
        """
        log_msg = f"[{error_type}] {error_message}"

        if context_info:
            log_msg += f" | Context: {context_info}"

        if stack_trace:
            log_msg += f"\nStack trace:\n{stack_trace}"

        self.logger.error(log_msg)

    def export_diagnostics(self, output_path: Path) -> None:
        """
        Export diagnostic information including error logs and system info.

        Creates a text file with:
        - System information
        - Application version
        - Recent error logs

        Args:
            output_path: Path where diagnostic file should be saved
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"Diagnostic Report - {APP_NAME}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            # System information
            f.write("SYSTEM INFORMATION\n")
            f.write("-" * 80 + "\n")
            f.write(f"Application Version: {APP_VERSION}\n")
            f.write(f"Platform: {platform.system()} {platform.release()}\n")
            f.write(f"Python Version: {platform.python_version()}\n")
            f.write(f"Machine: {platform.machine()}\n")
            f.write(f"Processor: {platform.processor()}\n")
            f.write("\n")

            # Error log contents
            f.write("ERROR LOG\n")
            f.write("-" * 80 + "\n")

            if self.log_path.exists():
                try:
                    with open(self.log_path, 'r', encoding='utf-8') as log_file:
                        f.write(log_file.read())
                except Exception as e:
                    f.write(f"Could not read error log: {e}\n")
            else:
                f.write("No error log file found.\n")

    def clear_logs(self) -> None:
        """Clear all error logs (including backups)."""
        if self.log_path.exists():
            self.log_path.unlink()

        # Clear backup logs
        for i in range(1, LOG_BACKUP_COUNT + 1):
            backup_path = self.log_path.with_suffix(f'.log.{i}')
            if backup_path.exists():
                backup_path.unlink()


# Global logger instance
_logger_instance: Optional[ErrorLogger] = None


def get_logger() -> ErrorLogger:
    """Get or create the global error logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ErrorLogger()
    return _logger_instance
