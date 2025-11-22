"""
Centralized logging configuration for the Polymarket Forecasting Simulator.

This module provides consistent logging setup across all components of the application.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


# Logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging(
    name: str = None,
    level: int = logging.INFO,
    log_to_file: bool = True,
    log_to_console: bool = True
) -> logging.Logger:
    """
    Set up logging configuration for a module or forecast.
    
    Creates a logger with both file and console handlers. File logs are stored
    in the logs/ directory with rotation to prevent excessive disk usage.
    
    Args:
        name: Logger name (typically __name__ of the calling module)
        level: Logging level (default: INFO)
        log_to_file: Whether to log to file (default: True)
        log_to_console: Whether to log to console (default: True)
    
    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name or 'polymarket_forecasting')
    
    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_to_file:
        # Create a log file for this logger
        log_filename = name.replace('.', '_') if name else 'app'
        log_file = LOGS_DIR / f"{log_filename}.log"
        
        # Rotating file handler: max 10MB per file, keep 5 backup files
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_application_logging(level: int = logging.INFO):
    """
    Set up logging for the entire application.
    
    Configures the root logger and creates a main application log file.
    
    Args:
        level: Logging level for the application (default: INFO)
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Main application log file
    app_log_file = LOGS_DIR / "application.log"
    file_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Log startup message
    root_logger.info("=" * 60)
    root_logger.info("Polymarket Forecasting Simulator - Application Started")
    root_logger.info(f"Logging level: {logging.getLevelName(level)}")
    root_logger.info(f"Log directory: {LOGS_DIR}")
    root_logger.info("=" * 60)


def log_error_with_context(
    logger: logging.Logger,
    error: Exception,
    context: dict = None
):
    """
    Log an error with additional context information.
    
    Args:
        logger: Logger instance to use
        error: Exception that occurred
        context: Optional dictionary of context information
    """
    error_msg = f"Error: {type(error).__name__}: {str(error)}"
    
    if context:
        context_str = ", ".join([f"{k}={v}" for k, v in context.items()])
        error_msg += f" | Context: {context_str}"
    
    logger.error(error_msg, exc_info=True)
