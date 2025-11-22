"""
Unit tests for general utilities.

Tests specific examples and edge cases for configuration loading,
logging setup, and parameter validation.
"""

import pytest
import json
import logging
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.utils import load_config, setup_logging, validate_parameters, ParameterSchema


class TestLoadConfig:
    """Tests for load_config function."""
    
    def test_load_config_file_not_found(self):
        """Test that load_config raises FileNotFoundError for non-existent config."""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_config('nonexistent_forecast')
        
        assert 'Configuration file not found' in str(exc_info.value)
        assert 'nonexistent_forecast' in str(exc_info.value)
    
    def test_load_config_invalid_json(self, tmp_path):
        """Test that load_config raises JSONDecodeError for invalid JSON."""
        # Create a temporary forecast directory with invalid JSON config
        forecast_dir = tmp_path / "forecasts" / "test_forecast"
        forecast_dir.mkdir(parents=True)
        
        config_file = forecast_dir / "config.json"
        config_file.write_text("{ invalid json }")
        
        # Temporarily change to tmp_path
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(json.JSONDecodeError):
                load_config('test_forecast')
        finally:
            os.chdir(original_cwd)
    
    def test_load_config_success(self, tmp_path):
        """Test that load_config successfully loads valid JSON config."""
        # Create a temporary forecast directory with valid JSON config
        forecast_dir = tmp_path / "forecasts" / "test_forecast"
        forecast_dir.mkdir(parents=True)
        
        config_data = {
            'model_name': 'Test Model',
            'parameters': {
                'weight': 0.5,
                'threshold': 10
            }
        }
        
        config_file = forecast_dir / "config.json"
        config_file.write_text(json.dumps(config_data))
        
        # Temporarily change to tmp_path
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            loaded_config = load_config('test_forecast')
            assert loaded_config == config_data
            assert loaded_config['model_name'] == 'Test Model'
            assert loaded_config['parameters']['weight'] == 0.5
        finally:
            os.chdir(original_cwd)


class TestSetupLogging:
    """Tests for setup_logging function."""
    
    def test_setup_logging_returns_logger(self):
        """Test that setup_logging returns a logger instance."""
        logger = setup_logging('test_forecast')
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'forecasting.test_forecast'
    
    def test_setup_logging_root_logger(self):
        """Test that setup_logging with no name returns root forecasting logger."""
        logger = setup_logging()
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'forecasting'
    
    def test_setup_logging_level(self):
        """Test that setup_logging sets the correct logging level."""
        logger = setup_logging('test_forecast', level=logging.DEBUG)
        assert logger.level == logging.DEBUG
        
        logger2 = setup_logging('test_forecast2', level=logging.WARNING)
        assert logger2.level == logging.WARNING
    
    def test_setup_logging_with_file(self, tmp_path):
        """Test that setup_logging creates a file handler when log_file is provided."""
        log_file = tmp_path / "logs" / "test.log"
        logger = setup_logging('test_forecast', log_file=str(log_file))
        
        # Check that file handler was added
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0
        
        # Check that log directory was created
        assert log_file.parent.exists()
    
    def test_setup_logging_console_handler(self):
        """Test that setup_logging adds a console handler."""
        logger = setup_logging('test_forecast')
        
        # Check that console handler was added
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(console_handlers) > 0


class TestValidateParameters:
    """Tests for validate_parameters function."""
    
    def test_validate_parameters_valid_float(self):
        """Test validation accepts valid float parameter."""
        schema = {
            'weight': ParameterSchema(
                name='weight',
                type='float',
                default=0.5,
                min_value=0.0,
                max_value=1.0
            )
        }
        
        params = {'weight': 0.7}
        errors = validate_parameters(params, schema)
        assert len(errors) == 0
    
    def test_validate_parameters_float_below_min(self):
        """Test validation rejects float below minimum."""
        schema = {
            'weight': ParameterSchema(
                name='weight',
                type='float',
                default=0.5,
                min_value=0.0,
                max_value=1.0
            )
        }
        
        params = {'weight': -0.1}
        errors = validate_parameters(params, schema)
        assert 'weight' in errors
        assert 'below minimum' in errors['weight']
    
    def test_validate_parameters_float_above_max(self):
        """Test validation rejects float above maximum."""
        schema = {
            'weight': ParameterSchema(
                name='weight',
                type='float',
                default=0.5,
                min_value=0.0,
                max_value=1.0
            )
        }
        
        params = {'weight': 1.5}
        errors = validate_parameters(params, schema)
        assert 'weight' in errors
        assert 'exceeds maximum' in errors['weight']
    
    def test_validate_parameters_valid_int(self):
        """Test validation accepts valid int parameter."""
        schema = {
            'count': ParameterSchema(
                name='count',
                type='int',
                default=50,
                min_value=1,
                max_value=100
            )
        }
        
        params = {'count': 75}
        errors = validate_parameters(params, schema)
        assert len(errors) == 0
    
    def test_validate_parameters_int_out_of_range(self):
        """Test validation rejects int out of range."""
        schema = {
            'count': ParameterSchema(
                name='count',
                type='int',
                default=50,
                min_value=1,
                max_value=100
            )
        }
        
        params = {'count': 150}
        errors = validate_parameters(params, schema)
        assert 'count' in errors
        assert 'exceeds maximum' in errors['count']
    
    def test_validate_parameters_valid_bool(self):
        """Test validation accepts valid bool parameter."""
        schema = {
            'enabled': ParameterSchema(
                name='enabled',
                type='bool',
                default=True
            )
        }
        
        params = {'enabled': False}
        errors = validate_parameters(params, schema)
        assert len(errors) == 0
    
    def test_validate_parameters_valid_string(self):
        """Test validation accepts valid string parameter."""
        schema = {
            'name': ParameterSchema(
                name='name',
                type='str',
                default='default'
            )
        }
        
        params = {'name': 'test_name'}
        errors = validate_parameters(params, schema)
        assert len(errors) == 0
    
    def test_validate_parameters_valid_select(self):
        """Test validation accepts valid select option."""
        schema = {
            'mode': ParameterSchema(
                name='mode',
                type='select',
                default='fast',
                options=['fast', 'normal', 'slow']
            )
        }
        
        params = {'mode': 'normal'}
        errors = validate_parameters(params, schema)
        assert len(errors) == 0
    
    def test_validate_parameters_invalid_select(self):
        """Test validation rejects invalid select option."""
        schema = {
            'mode': ParameterSchema(
                name='mode',
                type='select',
                default='fast',
                options=['fast', 'normal', 'slow']
            )
        }
        
        params = {'mode': 'invalid'}
        errors = validate_parameters(params, schema)
        assert 'mode' in errors
        assert 'not in allowed options' in errors['mode']
    
    def test_validate_parameters_missing_required(self):
        """Test validation rejects missing required parameter."""
        schema = {
            'required_param': ParameterSchema(
                name='required_param',
                type='float',
                default=0.5,
                required=True
            )
        }
        
        params = {}
        errors = validate_parameters(params, schema)
        assert 'required_param' in errors
        assert 'Required parameter' in errors['required_param']
    
    def test_validate_parameters_missing_optional(self):
        """Test validation accepts missing optional parameter."""
        schema = {
            'optional_param': ParameterSchema(
                name='optional_param',
                type='float',
                default=0.5,
                required=False
            )
        }
        
        params = {}
        errors = validate_parameters(params, schema)
        assert len(errors) == 0
    
    def test_validate_parameters_unknown_parameter(self):
        """Test validation rejects unknown parameter."""
        schema = {
            'known_param': ParameterSchema(
                name='known_param',
                type='float',
                default=0.5
            )
        }
        
        params = {'unknown_param': 0.7}
        errors = validate_parameters(params, schema)
        assert 'unknown_param' in errors
        assert 'Unknown parameter' in errors['unknown_param']
    
    def test_validate_parameters_wrong_type(self):
        """Test validation rejects wrong type."""
        schema = {
            'weight': ParameterSchema(
                name='weight',
                type='float',
                default=0.5
            )
        }
        
        params = {'weight': 'not_a_float'}
        errors = validate_parameters(params, schema)
        assert 'weight' in errors
        assert 'Expected float' in errors['weight']
    
    def test_validate_parameters_bool_not_accepted_as_float(self):
        """Test that boolean values are not accepted for float parameters."""
        schema = {
            'weight': ParameterSchema(
                name='weight',
                type='float',
                default=0.5
            )
        }
        
        params = {'weight': True}
        errors = validate_parameters(params, schema)
        assert 'weight' in errors
        assert 'Expected float' in errors['weight']
    
    def test_validate_parameters_bool_not_accepted_as_int(self):
        """Test that boolean values are not accepted for int parameters."""
        schema = {
            'count': ParameterSchema(
                name='count',
                type='int',
                default=50
            )
        }
        
        params = {'count': False}
        errors = validate_parameters(params, schema)
        assert 'count' in errors
        assert 'Expected int' in errors['count']
    
    def test_validate_parameters_multiple_errors(self):
        """Test validation returns multiple errors when multiple parameters are invalid."""
        schema = {
            'weight': ParameterSchema(
                name='weight',
                type='float',
                default=0.5,
                min_value=0.0,
                max_value=1.0
            ),
            'count': ParameterSchema(
                name='count',
                type='int',
                default=50,
                min_value=1,
                max_value=100
            )
        }
        
        params = {'weight': 1.5, 'count': 150}
        errors = validate_parameters(params, schema)
        assert len(errors) == 2
        assert 'weight' in errors
        assert 'count' in errors


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
