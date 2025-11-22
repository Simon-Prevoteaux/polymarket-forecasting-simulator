"""
General utilities for the Polymarket Forecasting Simulator.

Provides helper functions for configuration loading, logging setup,
and parameter validation.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass


@dataclass
class ParameterSchema:
    """Schema definition for a parameter."""
    name: str
    type: str  # 'float', 'int', 'bool', 'str', 'select'
    default: Any
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    options: Optional[list] = None
    required: bool = True
    description: str = ""


def load_config(forecast_name: str, config_file: str = "config.json") -> Dict[str, Any]:
    """
    Load configuration for a forecast model.
    
    Looks for configuration file in the forecast's directory:
    forecasts/{forecast_name}/{config_file}
    
    Args:
        forecast_name: Name of the forecast model
        config_file: Name of the configuration file (default: config.json)
    
    Returns:
        Dictionary containing configuration data
    
    Raises:
        FileNotFoundError: If configuration file doesn't exist
        json.JSONDecodeError: If configuration file is not valid JSON
    """
    config_path = Path("forecasts") / forecast_name / config_file
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}. "
            f"Expected config file for forecast '{forecast_name}' at {config_path}"
        )
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in configuration file {config_path}: {e.msg}",
            e.doc,
            e.pos
        )


def setup_logging(
    forecast_name: Optional[str] = None,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging for a forecast model or the application.
    
    Sets up logging with appropriate handlers and formatters.
    
    Args:
        forecast_name: Name of the forecast (used as logger name). If None, returns root logger.
        level: Logging level (default: logging.INFO)
        log_file: Optional path to log file. If provided, adds file handler.
        format_string: Optional custom format string. If None, uses default format.
    
    Returns:
        Configured logger instance
    
    Example:
        logger = setup_logging('us_recession_2025', level=logging.DEBUG)
        logger.info('Starting forecast calculation')
    """
    # Get or create logger
    logger_name = f"forecasting.{forecast_name}" if forecast_name else "forecasting"
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Default format
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if log_file specified
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def validate_parameters(
    params: Dict[str, Any],
    schema: Dict[str, ParameterSchema]
) -> Dict[str, str]:
    """
    Validate parameter inputs against a schema.
    
    Checks that parameters meet type, range, and constraint requirements
    defined in the schema.
    
    Args:
        params: Dictionary of parameter values to validate
        schema: Dictionary mapping parameter names to ParameterSchema objects
    
    Returns:
        Dictionary of validation errors (empty if all valid).
        Keys are parameter names, values are error messages.
    
    Example:
        schema = {
            'weight': ParameterSchema(
                name='weight',
                type='float',
                default=0.5,
                min_value=0.0,
                max_value=1.0
            )
        }
        errors = validate_parameters({'weight': 1.5}, schema)
        # Returns: {'weight': 'Value 1.5 exceeds maximum 1.0'}
    """
    errors = {}
    
    # Check for required parameters
    for param_name, param_schema in schema.items():
        if param_schema.required and param_name not in params:
            errors[param_name] = f"Required parameter '{param_name}' is missing"
    
    # Validate each provided parameter
    for param_name, param_value in params.items():
        # Check if parameter is in schema
        if param_name not in schema:
            errors[param_name] = f"Unknown parameter '{param_name}'"
            continue
        
        param_schema = schema[param_name]
        
        # Type validation
        expected_type = param_schema.type
        
        if expected_type == 'float':
            # Reject booleans explicitly (bool is subclass of int in Python)
            if isinstance(param_value, bool):
                errors[param_name] = f"Expected float, got {type(param_value).__name__}"
                continue
            if not isinstance(param_value, (int, float)):
                errors[param_name] = f"Expected float, got {type(param_value).__name__}"
                continue
            param_value = float(param_value)
            
            # Range validation for float
            if param_schema.min_value is not None and param_value < param_schema.min_value:
                errors[param_name] = f"Value {param_value} is below minimum {param_schema.min_value}"
                continue
            if param_schema.max_value is not None and param_value > param_schema.max_value:
                errors[param_name] = f"Value {param_value} exceeds maximum {param_schema.max_value}"
                continue
        
        elif expected_type == 'int':
            if not isinstance(param_value, int) or isinstance(param_value, bool):
                errors[param_name] = f"Expected int, got {type(param_value).__name__}"
                continue
            
            # Range validation for int
            if param_schema.min_value is not None and param_value < param_schema.min_value:
                errors[param_name] = f"Value {param_value} is below minimum {param_schema.min_value}"
                continue
            if param_schema.max_value is not None and param_value > param_schema.max_value:
                errors[param_name] = f"Value {param_value} exceeds maximum {param_schema.max_value}"
                continue
        
        elif expected_type == 'bool':
            if not isinstance(param_value, bool):
                errors[param_name] = f"Expected bool, got {type(param_value).__name__}"
                continue
        
        elif expected_type == 'str':
            if not isinstance(param_value, str):
                errors[param_name] = f"Expected str, got {type(param_value).__name__}"
                continue
        
        elif expected_type == 'select':
            # Validate against allowed options
            if param_schema.options is None:
                errors[param_name] = f"Parameter '{param_name}' has type 'select' but no options defined"
                continue
            
            if param_value not in param_schema.options:
                errors[param_name] = (
                    f"Value '{param_value}' is not in allowed options: {param_schema.options}"
                )
                continue
        
        else:
            errors[param_name] = f"Unknown parameter type '{expected_type}'"
    
    return errors
