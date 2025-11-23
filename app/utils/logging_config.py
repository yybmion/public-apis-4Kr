"""
Logging Configuration

중앙 집중식 로깅 설정

Features:
- 파일 로깅 (rotation, retention)
- 콘솔 로깅
- JSON 포맷 로깅
- 로그 레벨별 분리
- 성능 모니터링

Author: AI Assistant
Created: 2025-11-22
"""

import os
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any


# Log directory
LOG_DIR = Path(os.getenv('LOG_DIR', 'logs'))
LOG_DIR.mkdir(exist_ok=True)

# Log levels
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data

        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m'    # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    name: str = 'stock_intelligence',
    log_to_file: bool = True,
    log_to_console: bool = True,
    json_logs: bool = False
) -> logging.Logger:
    """
    Setup centralized logging

    Args:
        name: Logger name
        log_to_file: Enable file logging
        log_to_console: Enable console logging
        json_logs: Use JSON format for file logs

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # Remove existing handlers
    logger.handlers.clear()

    # File handler - All logs
    if log_to_file:
        all_log_file = LOG_DIR / 'stock_intelligence.log'

        if json_logs:
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

        file_handler = logging.handlers.RotatingFileHandler(
            all_log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # File handler - Error logs only
    if log_to_file:
        error_log_file = LOG_DIR / 'errors.log'

        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
            'File: %(pathname)s:%(lineno)d\n'
            'Function: %(funcName)s\n'
        )

        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(error_formatter)
        logger.addHandler(error_handler)

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get logger for a module

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f'stock_intelligence.{name}')


class PerformanceLogger:
    """Performance monitoring logger"""

    def __init__(self, logger: logging.Logger):
        """
        Initialize performance logger

        Args:
            logger: Logger instance
        """
        self.logger = logger
        self.start_time = None

    def __enter__(self):
        """Start timing"""
        self.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log"""
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            self.logger.info(f"Performance: {elapsed:.3f}s")


class ErrorTracker:
    """Error tracking and statistics"""

    def __init__(self):
        """Initialize error tracker"""
        self.errors: Dict[str, int] = {}
        self.recent_errors: list = []
        self.max_recent = 100

    def log_error(self, error_type: str, message: str, details: Dict[str, Any] = None):
        """
        Log an error

        Args:
            error_type: Error type/category
            message: Error message
            details: Additional details
        """
        # Count errors
        self.errors[error_type] = self.errors.get(error_type, 0) + 1

        # Store recent errors
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': message,
            'details': details or {}
        }

        self.recent_errors.append(error_record)

        # Keep only recent errors
        if len(self.recent_errors) > self.max_recent:
            self.recent_errors = self.recent_errors[-self.max_recent:]

    def get_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            'total_errors': sum(self.errors.values()),
            'errors_by_type': self.errors.copy(),
            'recent_errors': self.recent_errors[-10:]  # Last 10
        }

    def clear(self):
        """Clear error statistics"""
        self.errors.clear()
        self.recent_errors.clear()


# Global error tracker
error_tracker = ErrorTracker()


# Initialize main logger
main_logger = setup_logging()


# Example usage
if __name__ == '__main__':
    # Get logger
    logger = get_logger(__name__)

    # Test logs
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    try:
        raise ValueError("Test exception")
    except Exception as e:
        logger.exception("Exception occurred")

    # Performance logging
    with PerformanceLogger(logger):
        import time
        time.sleep(1)

    # Error tracking
    error_tracker.log_error(
        'API_ERROR',
        'Failed to fetch data from API',
        {'api': 'FRED', 'status_code': 500}
    )

    print("\nError Stats:")
    print(error_tracker.get_stats())
