"""
Unit tests for forecast discovery mechanism.

Tests that the forecast discovery system correctly identifies valid forecast
models and ignores invalid directories.
"""

import os
import sys
import tempfile
from pathlib import Path
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forecasts import discover_forecasts, ForecastRegistry, ForecastModel


def test_discover_valid_forecast():
    """Test discovery of a single valid forecast model."""
    with tempfile.TemporaryDirectory() as temp_dir:
        forecasts_dir = Path(temp_dir)
        
        # Create a valid forecast
        forecast_dir = forecasts_dir / "test_forecast"
        forecast_dir.mkdir()
        (forecast_dir / '__init__.py').write_text('')
        
        model_content = '''
from forecasts import ForecastModel
from datetime import datetime

class TestForecast(ForecastModel):
    def get_name(self):
        return "Test Forecast"
    def get_description(self):
        return "A test forecast"
    def get_parameters(self):
        return {}
    def calculate_probability(self, params=None):
        return 0.5
    def get_last_updated(self):
        return datetime.now()
'''
        (forecast_dir / 'model.py').write_text(model_content)
        
        # Discover forecasts
        registry = discover_forecasts(str(forecasts_dir))
        
        # Verify discovery
        assert len(registry.list_names()) == 1
        assert "test_forecast" in registry.list_names()
        
        # Verify model can be retrieved
        model = registry.get("test_forecast")
        assert model is not None
        assert isinstance(model, ForecastModel)
        assert model.get_name() == "Test Forecast"


def test_discover_multiple_forecasts():
    """Test discovery of multiple valid forecast models."""
    with tempfile.TemporaryDirectory() as temp_dir:
        forecasts_dir = Path(temp_dir)
        
        # Create multiple valid forecasts
        for i in range(3):
            forecast_dir = forecasts_dir / f"forecast{i}"
            forecast_dir.mkdir()
            (forecast_dir / '__init__.py').write_text('')
            
            model_content = f'''
from forecasts import ForecastModel
from datetime import datetime

class Forecast{i}(ForecastModel):
    def get_name(self):
        return "Forecast {i}"
    def get_description(self):
        return "Test forecast {i}"
    def get_parameters(self):
        return {{}}
    def calculate_probability(self, params=None):
        return 0.5
    def get_last_updated(self):
        return datetime.now()
'''
            (forecast_dir / 'model.py').write_text(model_content)
        
        # Discover forecasts
        registry = discover_forecasts(str(forecasts_dir))
        
        # Verify all forecasts discovered
        assert len(registry.list_names()) == 3
        assert "forecast0" in registry.list_names()
        assert "forecast1" in registry.list_names()
        assert "forecast2" in registry.list_names()


def test_ignore_directory_without_model_py():
    """Test that directories without model.py are ignored."""
    with tempfile.TemporaryDirectory() as temp_dir:
        forecasts_dir = Path(temp_dir)
        
        # Create directory without model.py
        invalid_dir = forecasts_dir / "invalid_forecast"
        invalid_dir.mkdir()
        (invalid_dir / '__init__.py').write_text('')
        (invalid_dir / 'data.py').write_text('# Some other file')
        
        # Discover forecasts
        registry = discover_forecasts(str(forecasts_dir))
        
        # Verify no forecasts discovered
        assert len(registry.list_names()) == 0


def test_ignore_directory_with_invalid_model():
    """Test that directories with invalid model.py are ignored."""
    with tempfile.TemporaryDirectory() as temp_dir:
        forecasts_dir = Path(temp_dir)
        
        # Create directory with invalid model.py (no ForecastModel subclass)
        invalid_dir = forecasts_dir / "invalid_forecast"
        invalid_dir.mkdir()
        (invalid_dir / '__init__.py').write_text('')
        
        model_content = '''
# This file doesn't contain a ForecastModel subclass
def some_function():
    return 42
'''
        (invalid_dir / 'model.py').write_text(model_content)
        
        # Discover forecasts
        registry = discover_forecasts(str(forecasts_dir))
        
        # Verify no forecasts discovered
        assert len(registry.list_names()) == 0


def test_ignore_hidden_directories():
    """Test that hidden directories (starting with _ or .) are ignored."""
    with tempfile.TemporaryDirectory() as temp_dir:
        forecasts_dir = Path(temp_dir)
        
        # Create hidden directories
        for name in ['_hidden', '.hidden', '__pycache__']:
            hidden_dir = forecasts_dir / name
            hidden_dir.mkdir()
            (hidden_dir / '__init__.py').write_text('')
            (hidden_dir / 'model.py').write_text('# Some content')
        
        # Discover forecasts
        registry = discover_forecasts(str(forecasts_dir))
        
        # Verify no forecasts discovered
        assert len(registry.list_names()) == 0


def test_ignore_files_in_forecasts_directory():
    """Test that files (not directories) in forecasts/ are ignored."""
    with tempfile.TemporaryDirectory() as temp_dir:
        forecasts_dir = Path(temp_dir)
        
        # Create some files
        (forecasts_dir / 'README.md').write_text('# Forecasts')
        (forecasts_dir / 'utils.py').write_text('# Utilities')
        
        # Discover forecasts
        registry = discover_forecasts(str(forecasts_dir))
        
        # Verify no forecasts discovered
        assert len(registry.list_names()) == 0


def test_mixed_valid_and_invalid_forecasts():
    """Test discovery with mix of valid and invalid forecasts."""
    with tempfile.TemporaryDirectory() as temp_dir:
        forecasts_dir = Path(temp_dir)
        
        # Create valid forecast
        valid_dir = forecasts_dir / "valid_forecast"
        valid_dir.mkdir()
        (valid_dir / '__init__.py').write_text('')
        model_content = '''
from forecasts import ForecastModel
from datetime import datetime

class ValidForecast(ForecastModel):
    def get_name(self):
        return "Valid"
    def get_description(self):
        return "Valid forecast"
    def get_parameters(self):
        return {}
    def calculate_probability(self, params=None):
        return 0.5
    def get_last_updated(self):
        return datetime.now()
'''
        (valid_dir / 'model.py').write_text(model_content)
        
        # Create invalid forecast (no model.py)
        invalid_dir = forecasts_dir / "invalid_forecast"
        invalid_dir.mkdir()
        (invalid_dir / '__init__.py').write_text('')
        
        # Create hidden directory
        hidden_dir = forecasts_dir / "_hidden"
        hidden_dir.mkdir()
        
        # Discover forecasts
        registry = discover_forecasts(str(forecasts_dir))
        
        # Verify only valid forecast discovered
        assert len(registry.list_names()) == 1
        assert "valid_forecast" in registry.list_names()
        assert "invalid_forecast" not in registry.list_names()
        assert "_hidden" not in registry.list_names()


def test_forecast_registry_operations():
    """Test ForecastRegistry operations."""
    registry = ForecastRegistry()
    
    # Test empty registry
    assert len(registry.list_names()) == 0
    assert registry.get("nonexistent") is None
    assert len(registry.get_all()) == 0
    
    # Create a mock forecast model
    class MockForecast(ForecastModel):
        def get_name(self):
            return "Mock"
        def get_description(self):
            return "Mock forecast"
        def get_parameters(self):
            return {}
        def calculate_probability(self, params=None):
            return 0.5
        def get_last_updated(self):
            from datetime import datetime
            return datetime.now()
    
    # Register a forecast
    mock_model = MockForecast()
    registry.register("mock_forecast", mock_model)
    
    # Test registry operations
    assert len(registry.list_names()) == 1
    assert "mock_forecast" in registry.list_names()
    assert registry.get("mock_forecast") is mock_model
    assert len(registry.get_all()) == 1
    
    # Test clear
    registry.clear()
    assert len(registry.list_names()) == 0


def test_discover_nonexistent_directory():
    """Test discovery with nonexistent directory."""
    registry = discover_forecasts("/nonexistent/path/to/forecasts")
    
    # Should return empty registry without crashing
    assert len(registry.list_names()) == 0


def test_discover_empty_directory():
    """Test discovery with empty directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        registry = discover_forecasts(temp_dir)
        
        # Should return empty registry
        assert len(registry.list_names()) == 0
