"""
Tests for the new lib.temporal_adjustment library

These tests verify that the new generic temporal adjustment library
works correctly with the recession forecast.
"""

import pytest
from datetime import datetime, timedelta
from lib.temporal_adjustment import (
    calculate_time_to_event,
    simple_decay,
    theta_decay,
    threshold_aware_decay,
    trend_amplification,
    confidence_convergence,
    adaptive_adjustment,
    TemporalAdjuster
)


class TestNewLibraryBasics:
    """Test basic functionality of new library"""
    
    def test_calculate_time_to_event(self):
        """Test time-to-event calculation"""
        current = datetime(2025, 11, 22)
        deadline = datetime(2025, 12, 31)
        days = calculate_time_to_event(current, deadline)
        assert days == 39  # 39 days between these dates
    
    def test_theta_decay_basic(self):
        """Test theta decay function"""
        adjusted = theta_decay(0.5, 180, total_days=365, decay_power=1.5)
        assert 0 < adjusted < 0.5  # Should be reduced
        assert 0 <= adjusted <= 1  # Should be valid probability
    
    def test_adaptive_weak_signal(self):
        """Test adaptive method with weak signal"""
        # Weak signal should decay
        adjusted = adaptive_adjustment(
            0.25, 38, total_days=365,
            decay_power=1.5, amplification_power=1.5,
            lower_threshold=0.4, upper_threshold=0.6
        )
        assert adjusted < 0.25  # Should decay
        assert adjusted > 0  # Should not go to zero
    
    def test_adaptive_strong_signal(self):
        """Test adaptive method with strong signal"""
        # Strong signal should amplify
        adjusted = adaptive_adjustment(
            0.75, 38, total_days=365,
            decay_power=1.5, amplification_power=1.5,
            lower_threshold=0.4, upper_threshold=0.6
        )
        assert adjusted > 0.75  # Should amplify
        assert adjusted <= 1.0  # Should not exceed 1
    
    def test_adaptive_uncertain_signal(self):
        """Test adaptive method with uncertain signal"""
        # Uncertain signal should have gentle decay
        adjusted = adaptive_adjustment(
            0.5, 38, total_days=365,
            decay_power=1.5, amplification_power=1.5,
            lower_threshold=0.4, upper_threshold=0.6
        )
        assert adjusted < 0.5  # Should decay gently
        assert adjusted > 0.05  # Should not decay too much (adjusted threshold)


class TestTemporalAdjusterClass:
    """Test the TemporalAdjuster class"""
    
    def test_theta_method(self):
        """Test theta method via TemporalAdjuster"""
        adjuster = TemporalAdjuster(method='theta', total_days=365, decay_power=1.5)
        
        current_date = datetime(2025, 11, 22)
        deadline = datetime(2025, 12, 31)
        
        adjusted, metadata = adjuster.adjust_probability(0.5, current_date, deadline)
        
        assert 0 < adjusted < 0.5
        assert metadata['method'] == 'theta'
        assert 'days_remaining' in metadata
    
    def test_adaptive_method(self):
        """Test adaptive method via TemporalAdjuster"""
        adjuster = TemporalAdjuster(
            method='adaptive',
            total_days=365,
            decay_power=1.5,
            amplification_power=1.5,
            lower_threshold=0.4,
            upper_threshold=0.6
        )
        
        current_date = datetime(2025, 11, 22)
        deadline = datetime(2025, 12, 31)
        
        adjusted, metadata = adjuster.adjust_probability(0.48, current_date, deadline)
        
        assert 0 < adjusted < 0.48
        assert metadata['method'] == 'adaptive'
    
    def test_none_method(self):
        """Test none method (no adjustment)"""
        adjuster = TemporalAdjuster(method='none')
        
        current_date = datetime(2025, 11, 22)
        deadline = datetime(2025, 12, 31)
        
        adjusted, metadata = adjuster.adjust_probability(0.48, current_date, deadline)
        
        assert adjusted == 0.48  # Should be unchanged
        assert metadata['method'] == 'none'
    
    def test_list_methods(self):
        """Test that we can list available methods"""
        methods = TemporalAdjuster.list_methods()
        
        assert 'theta' in methods
        assert 'adaptive' in methods
        assert 'none' in methods
        assert len(methods) >= 6  # Should have at least 6 methods


class TestRecessionForecastIntegration:
    """Test integration with recession forecast"""
    
    def test_model_uses_new_library(self):
        """Test that RecessionModelV2 uses the new library"""
        from forecasts.us_recession_2025.model_v2 import RecessionModelV2
        
        model = RecessionModelV2()
        
        # Check that model has temporal_adjuster
        assert hasattr(model, 'temporal_adjuster')
        assert isinstance(model.temporal_adjuster, TemporalAdjuster)
    
    def test_model_calculate_probability(self):
        """Test that model can calculate probability with new library"""
        from forecasts.us_recession_2025.model_v2 import RecessionModelV2
        
        model = RecessionModelV2()
        
        # This should work without errors
        probability = model.calculate_probability()
        
        assert 0 <= probability <= 1
        assert isinstance(probability, float)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
