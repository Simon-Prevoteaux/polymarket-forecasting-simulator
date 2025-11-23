"""
Tests for the optional get_probability_breakdown method in ForecastModel interface.

This test verifies that:
1. The base ForecastModel interface provides a default implementation that returns None
2. Models that don't implement the method (like v1) work correctly
3. Models that do implement the method (like v2) can override it
"""

import pytest
from forecasts import ForecastModel
from forecasts.us_recession_2025.model import RecessionModel
from forecasts.us_recession_2025.model_v2 import RecessionModelV2


def test_base_interface_has_optional_method():
    """Test that ForecastModel has get_probability_breakdown method."""
    assert hasattr(ForecastModel, 'get_probability_breakdown')
    
    # Verify it's not abstract (not in __abstractmethods__)
    assert 'get_probability_breakdown' not in ForecastModel.__abstractmethods__


def test_v1_model_returns_none_for_breakdown():
    """Test that v1 model (without implementation) returns None."""
    model = RecessionModel()
    
    # Should not raise an error
    breakdown = model.get_probability_breakdown()
    
    # Should return None (default implementation)
    assert breakdown is None


def test_v2_model_returns_breakdown():
    """Test that v2 model (with implementation) returns breakdown data."""
    model = RecessionModelV2()
    
    # Should not raise an error
    breakdown = model.get_probability_breakdown()
    
    # Should return a dictionary (not None)
    assert breakdown is not None
    assert isinstance(breakdown, dict)
    
    # Should contain expected keys
    expected_keys = [
        'base_probability',
        'adjusted_probability',
        'days_remaining',
        'indicator_signals',
        'indicators',
        'features',
        'temporal_metadata',
        'timestamps'
    ]
    
    for key in expected_keys:
        assert key in breakdown, f"Missing expected key: {key}"


def test_v1_model_implements_all_required_methods():
    """Test that v1 model still implements all required abstract methods."""
    model = RecessionModel()
    
    # All abstract methods should be implemented
    assert callable(model.get_name)
    assert callable(model.get_description)
    assert callable(model.get_parameters)
    assert callable(model.calculate_probability)
    assert callable(model.get_last_updated)
    assert callable(model.get_data_sources)
    
    # Optional method should also be callable (inherited from base)
    assert callable(model.get_probability_breakdown)


def test_v2_model_implements_all_required_methods():
    """Test that v2 model implements all required abstract methods."""
    model = RecessionModelV2()
    
    # All abstract methods should be implemented
    assert callable(model.get_name)
    assert callable(model.get_description)
    assert callable(model.get_parameters)
    assert callable(model.calculate_probability)
    assert callable(model.get_last_updated)
    assert callable(model.get_data_sources)
    
    # Optional method should be overridden
    assert callable(model.get_probability_breakdown)


def test_breakdown_method_signature():
    """Test that the breakdown method has the correct signature."""
    import inspect
    
    # Get the method from the base class
    method = ForecastModel.get_probability_breakdown
    
    # Check signature
    sig = inspect.signature(method)
    params = list(sig.parameters.keys())
    
    # Should have 'self' and 'params'
    assert 'self' in params
    assert 'params' in params
    
    # params should have Optional[Dict] type hint
    params_param = sig.parameters['params']
    assert params_param.default is None  # Optional means default is None


def test_backward_compatibility():
    """Test that existing models work without implementing the optional method."""
    # This test verifies that the addition of the optional method doesn't
    # break existing models that don't implement it
    
    model = RecessionModel()
    
    # Should be able to call all required methods
    name = model.get_name()
    assert isinstance(name, str)
    
    description = model.get_description()
    assert isinstance(description, str)
    
    params = model.get_parameters()
    assert isinstance(params, dict)
    
    # Optional method should return None without error
    breakdown = model.get_probability_breakdown()
    assert breakdown is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
