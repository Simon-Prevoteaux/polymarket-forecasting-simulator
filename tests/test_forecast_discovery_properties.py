"""
Property-based tests for forecast discovery mechanism.

Tests that the forecast discovery system correctly reflects the directory
structure and handles various scenarios.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forecasts import discover_forecasts, ForecastModel


# Feature: polymarket-forecasting-simulator, Property 8: Navigation reflects directory structure
@settings(max_examples=100)
@given(
    valid_forecast_names=st.lists(
        st.text(
            alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), min_codepoint=97, max_codepoint=122),
            min_size=3,
            max_size=20
        ).filter(lambda x: not x.startswith('_') and not x.startswith('.')),
        min_size=0,
        max_size=5,
        unique=True
    ),
    invalid_forecast_names=st.lists(
        st.text(
            alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), min_codepoint=97, max_codepoint=122),
            min_size=3,
            max_size=20
        ).filter(lambda x: not x.startswith('_') and not x.startswith('.')),
        min_size=0,
        max_size=3,
        unique=True
    )
)
def test_navigation_reflects_directory_structure(valid_forecast_names, invalid_forecast_names):
    # Ensure no overlap between valid and invalid names
    invalid_forecast_names = [name for name in invalid_forecast_names if name not in valid_forecast_names]
    """
    Property: For any set of forecast directories, the navigation must include
    exactly those forecasts that have valid model.py files, and exclude any
    that don't or have been removed.
    
    **Validates: Requirements 7.2, 7.3, 7.5**
    """
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        forecasts_dir = Path(temp_dir)
        
        # Create valid forecast directories with proper model.py files
        for name in valid_forecast_names:
            forecast_dir = forecasts_dir / name
            forecast_dir.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py
            (forecast_dir / '__init__.py').write_text('')
            
            # Create valid model.py with ForecastModel subclass
            model_content = f'''
from forecasts import ForecastModel
from datetime import datetime

class TestModel{name.capitalize()}(ForecastModel):
    def get_name(self):
        return "{name}"
    
    def get_description(self):
        return "Test forecast {name}"
    
    def get_parameters(self):
        return {{}}
    
    def calculate_probability(self, params=None):
        return 0.5
    
    def get_last_updated(self):
        return datetime.now()
'''
            (forecast_dir / 'model.py').write_text(model_content)
        
        # Create invalid forecast directories (no model.py or invalid structure)
        for name in invalid_forecast_names:
            forecast_dir = forecasts_dir / name
            forecast_dir.mkdir(parents=True, exist_ok=True)
            # Don't create model.py - this makes it invalid
            (forecast_dir / '__init__.py').write_text('')
            (forecast_dir / 'data.py').write_text('# Some other file')
        
        # Discover forecasts
        registry = discover_forecasts(str(forecasts_dir))
        
        # Get discovered forecast names
        discovered_names = set(registry.list_names())
        
        # Property: Discovered forecasts should exactly match valid forecasts
        expected_names = set(valid_forecast_names)
        
        # All valid forecasts should be discovered
        assert expected_names == discovered_names, (
            f"Discovery mismatch. Expected: {expected_names}, "
            f"Discovered: {discovered_names}"
        )
        
        # Invalid forecasts should not be discovered
        for invalid_name in invalid_forecast_names:
            assert invalid_name not in discovered_names, (
                f"Invalid forecast '{invalid_name}' was incorrectly discovered"
            )
        
        # Each discovered forecast should be instantiable
        for name in discovered_names:
            model = registry.get(name)
            assert model is not None, f"Forecast '{name}' was discovered but not instantiated"
            assert isinstance(model, ForecastModel), (
                f"Forecast '{name}' is not a ForecastModel instance"
            )


@settings(max_examples=100)
@given(
    initial_forecasts=st.lists(
        st.text(
            alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), min_codepoint=97, max_codepoint=122),
            min_size=3,
            max_size=15
        ).filter(lambda x: not x.startswith('_') and not x.startswith('.')),
        min_size=1,
        max_size=4,
        unique=True
    )
)
def test_forecast_removal_reflected_in_discovery(initial_forecasts):
    """
    Property: When a forecast directory is removed, it should not appear
    in subsequent discovery operations.
    
    **Validates: Requirements 7.5**
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        forecasts_dir = Path(temp_dir)
        
        # Create initial forecasts
        for name in initial_forecasts:
            forecast_dir = forecasts_dir / name
            forecast_dir.mkdir(parents=True, exist_ok=True)
            (forecast_dir / '__init__.py').write_text('')
            
            model_content = f'''
from forecasts import ForecastModel
from datetime import datetime

class Model{name.capitalize()}(ForecastModel):
    def get_name(self):
        return "{name}"
    def get_description(self):
        return "Test"
    def get_parameters(self):
        return {{}}
    def calculate_probability(self, params=None):
        return 0.5
    def get_last_updated(self):
        return datetime.now()
'''
            (forecast_dir / 'model.py').write_text(model_content)
        
        # First discovery - should find all
        registry1 = discover_forecasts(str(forecasts_dir))
        discovered1 = set(registry1.list_names())
        assert discovered1 == set(initial_forecasts)
        
        # Remove one forecast (if any exist)
        if initial_forecasts:
            removed_name = initial_forecasts[0]
            removed_dir = forecasts_dir / removed_name
            shutil.rmtree(removed_dir)
            
            # Second discovery - should not find removed forecast
            registry2 = discover_forecasts(str(forecasts_dir))
            discovered2 = set(registry2.list_names())
            
            # Removed forecast should not be in second discovery
            assert removed_name not in discovered2, (
                f"Removed forecast '{removed_name}' still appears in discovery"
            )
            
            # Remaining forecasts should still be discovered
            expected_remaining = set(initial_forecasts) - {removed_name}
            assert discovered2 == expected_remaining, (
                f"Expected {expected_remaining}, got {discovered2}"
            )


@settings(max_examples=100)
@given(
    forecast_name=st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), min_codepoint=97, max_codepoint=122),
        min_size=3,
        max_size=15
    ).filter(lambda x: not x.startswith('_') and not x.startswith('.'))
)
def test_forecast_addition_reflected_in_discovery(forecast_name):
    """
    Property: When a new valid forecast directory is added, it should appear
    in subsequent discovery operations.
    
    **Validates: Requirements 7.3**
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        forecasts_dir = Path(temp_dir)
        
        # First discovery - empty directory
        registry1 = discover_forecasts(str(forecasts_dir))
        discovered1 = set(registry1.list_names())
        assert len(discovered1) == 0
        
        # Add a new forecast
        forecast_dir = forecasts_dir / forecast_name
        forecast_dir.mkdir(parents=True, exist_ok=True)
        (forecast_dir / '__init__.py').write_text('')
        
        model_content = f'''
from forecasts import ForecastModel
from datetime import datetime

class NewModel(ForecastModel):
    def get_name(self):
        return "{forecast_name}"
    def get_description(self):
        return "New forecast"
    def get_parameters(self):
        return {{}}
    def calculate_probability(self, params=None):
        return 0.5
    def get_last_updated(self):
        return datetime.now()
'''
        (forecast_dir / 'model.py').write_text(model_content)
        
        # Second discovery - should find new forecast
        registry2 = discover_forecasts(str(forecasts_dir))
        discovered2 = set(registry2.list_names())
        
        assert forecast_name in discovered2, (
            f"New forecast '{forecast_name}' not discovered"
        )
        assert len(discovered2) == 1
