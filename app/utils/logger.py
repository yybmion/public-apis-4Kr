"""
Logging System
Stock Intelligence System
"""

import logging
import sys
from typing import Optional
from pathlib import Path
from pythonjsonlogger import jsonlogger
from app.config import settings


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up logger with JSON formatting

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set level
    log_level = level or settings.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers = []

    # JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        rename_fields={
            'asctime': 'timestamp',
            'name': 'logger',
            'levelname': 'level'
        }
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


# Pre-configured loggers
api_logger = setup_logger('stock_api', log_file='logs/api.log')
collector_logger = setup_logger('collectors', log_file='logs/collectors.log')
analyzer_logger = setup_logger('analyzers', log_file='logs/analyzers.log')
db_logger = setup_logger('database', log_file='logs/database.log')


class LoggerMixin:
    """Mixin to add logging capabilities to classes"""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        if not hasattr(self, '_logger'):
            self._logger = setup_logger(self.__class__.__name__)
        return self._logger

    def log_info(self, message: str, **extra):
        """Log info level message"""
        self.logger.info(message, extra=extra)

    def log_error(self, message: str, **extra):
        """Log error level message"""
        self.logger.error(message, extra=extra, exc_info=True)

    def log_warning(self, message: str, **extra):
        """Log warning level message"""
        self.logger.warning(message, extra=extra)

    def log_debug(self, message: str, **extra):
        """Log debug level message"""
        self.logger.debug(message, extra=extra)


# Usage example logging decorator
def log_execution(logger: logging.Logger):
    """Decorator to log function execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(
                f'Executing {func.__name__}',
                extra={
                    'function': func.__name__,
                    'args': str(args)[:100],  # Truncate long args
                    'kwargs': str(kwargs)[:100]
                }
            )
            try:
                result = func(*args, **kwargs)
                logger.info(
                    f'Completed {func.__name__}',
                    extra={'function': func.__name__, 'status': 'success'}
                )
                return result
            except Exception as e:
                logger.error(
                    f'Failed {func.__name__}: {str(e)}',
                    extra={
                        'function': func.__name__,
                        'status': 'failed',
                        'error': str(e)
                    },
                    exc_info=True
                )
                raise
        return wrapper
    return decorator
