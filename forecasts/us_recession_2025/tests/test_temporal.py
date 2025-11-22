"""
Unit tests for temporal decay module
"""

import pytest
from datetime import datetime
import math

from forecasts.us_recession_2025.temporal import (
    calculate_time_to_event,
    exponential_decay_adjustment,
    sigmoid_decay_adjustment,
    TemporalAdjuster
)


class TestCalculateTimeToEvent:
    """Tests for calculate_time_to_event function"""
    
    def test_basic_calculation(self):
        """Test basic time-to-event calculation"""
        current = datetime(2025, 1, 1)
        deadline = datetime(2025, 12, 31)
        days = calculate_time_to_event(current, deadline)
        assert days == 364
    
    def test_same_date(self):
        """Test when current date equals deadline"""
        date = datetime(2025, 12, 31)
        days = calculate_time_to_event(date, date)
        assert days == 0
    
    def test_past_deadline(self):
        """Test when current date is past deadline"""
        current = datetime(2026, 1, 1)
        deadline = datetime(2025, 12, 31)
        days = calculate_time_to_event(current, deadline)
        assert days == -1
    
    def test_far_future(self):
        """Test with date far in the future"""
        current = datetime(2024, 1, 1)
        deadline = datetime(2025, 12, 31)
        days = calculate_time_to_event(current, deadline)
        assert days == 730


class TestExponentialDecayAdjustment:
    """Tests for exponential_decay_adjustment function"""
    
    def test_no_decay_above_threshold(self):
        """Test that no decay is applied when probability is above threshold"""
        base_prob = 0.5
        days_remaining = 100
        adjusted = exponential_decay_adjustment(base_prob, days_remaining, threshold=0.4)
        assert adjusted == base_prob
    
    def test_no_decay_far_from_deadline(self):
        """Test that no decay is applied when far from deadline"""
        base_prob = 0.3
        days_remaining = 400
        adjusted = exponential_decay_adjustment(base_prob, days_remaining, threshold=0.4)
        assert adjusted == base_prob
    
    def test_no_decay_past_deadline(self):
        """Test that no decay is applied when past deadline"""
        base_prob = 0.3
        days_remaining = -10
        adjusted = exponential_decay_adjustment(base_prob, days_remaining, threshold=0.4)
        assert adjusted == base_prob
    
    def test_decay_applied_below_threshold(self):
        """Test that decay is applied when conditions are met"""
        base_prob = 0.3
        days_remaining = 100
        decay_rate = 0.01
        adjusted = exponential_decay_adjustment(base_prob, days_remaining, decay_rate, threshold=0.4)
        
        # Should be less than base probability
        assert adjusted < base_prob
        # Should still be in valid range
        assert 0 <= adjusted <= 1
    
    def test_decay_increases_as_deadline_approaches(self):
        """Test that decay effect increases as deadline approaches"""
        base_prob = 0.3
        decay_rate = 0.01
        
        adjusted_300 = exponential_decay_adjustment(base_prob, 300, decay_rate, threshold=0.4)
        adjusted_200 = exponential_decay_adjustment(base_prob, 200, decay_rate, threshold=0.4)
        adjusted_100 = exponential_decay_adjustment(base_prob, 100, decay_rate, threshold=0.4)
        
        # As days decrease, adjusted probability should decrease
        assert adjusted_300 > adjusted_200 > adjusted_100
    
    def test_bounds_validation(self):
        """Test that output is always in [0, 1]"""
        base_prob = 0.1
        days_remaining = 10
        decay_rate = 10.0  # Very high decay rate
        adjusted = exponential_decay_adjustment(base_prob, days_remaining, decay_rate, threshold=0.4)
        assert 0 <= adjusted <= 1
    
    def test_invalid_probability_raises_error(self):
        """Test that invalid probability raises ValueError"""
        with pytest.raises(ValueError):
            exponential_decay_adjustment(1.5, 100)
        with pytest.raises(ValueError):
            exponential_decay_adjustment(-0.1, 100)
    
    def test_invalid_decay_rate_raises_error(self):
        """Test that invalid decay rate raises ValueError"""
        with pytest.raises(ValueError):
            exponential_decay_adjustment(0.3, 100, decay_rate=-0.01)
        with pytest.raises(ValueError):
            exponential_decay_adjustment(0.3, 100, decay_rate=0)
    
    def test_invalid_threshold_raises_error(self):
        """Test that invalid threshold raises ValueError"""
        with pytest.raises(ValueError):
            exponential_decay_adjustment(0.3, 100, threshold=1.5)
        with pytest.raises(ValueError):
            exponential_decay_adjustment(0.3, 100, threshold=-0.1)


class TestSigmoidDecayAdjustment:
    """Tests for sigmoid_decay_adjustment function"""
    
    def test_basic_sigmoid_adjustment(self):
        """Test basic sigmoid adjustment"""
        base_prob = 0.5
        days_remaining = 180
        adjusted = sigmoid_decay_adjustment(base_prob, days_remaining, midpoint=180)
        
        # Should be in valid range
        assert 0 <= adjusted <= 1
    
    def test_sigmoid_at_midpoint(self):
        """Test sigmoid behavior at midpoint"""
        base_prob = 0.5
        midpoint = 180
        adjusted = sigmoid_decay_adjustment(base_prob, midpoint, midpoint=midpoint)
        
        # At midpoint, time_factor should be 0.5
        # adjusted = base * (1 - (1 - base) * 0.5) = 0.5 * (1 - 0.5 * 0.5) = 0.5 * 0.75 = 0.375
        assert 0 <= adjusted <= 1
    
    def test_sigmoid_far_from_deadline(self):
        """Test sigmoid when far from deadline"""
        base_prob = 0.5
        days_remaining = 365
        adjusted = sigmoid_decay_adjustment(base_prob, days_remaining, midpoint=180)
        
        # Should be close to base probability
        assert adjusted <= base_prob
    
    def test_sigmoid_near_deadline(self):
        """Test sigmoid when near deadline"""
        base_prob = 0.5
        days_remaining = 10
        adjusted = sigmoid_decay_adjustment(base_prob, days_remaining, midpoint=180)
        
        # Should be significantly reduced
        assert adjusted < base_prob
    
    def test_invalid_probability_raises_error(self):
        """Test that invalid probability raises ValueError"""
        with pytest.raises(ValueError):
            sigmoid_decay_adjustment(1.5, 100)
        with pytest.raises(ValueError):
            sigmoid_decay_adjustment(-0.1, 100)
    
    def test_invalid_steepness_raises_error(self):
        """Test that invalid steepness raises ValueError"""
        with pytest.raises(ValueError):
            sigmoid_decay_adjustment(0.5, 100, steepness=-0.01)
        with pytest.raises(ValueError):
            sigmoid_decay_adjustment(0.5, 100, steepness=0)


class TestTemporalAdjuster:
    """Tests for TemporalAdjuster class"""
    
    def test_exponential_initialization(self):
        """Test initialization with exponential method"""
        adjuster = TemporalAdjuster(method='exponential', decay_rate=0.02, threshold=0.5)
        assert adjuster.method == 'exponential'
        assert adjuster.decay_rate == 0.02
        assert adjuster.threshold == 0.5
    
    def test_exponential_default_parameters(self):
        """Test exponential method with default parameters"""
        adjuster = TemporalAdjuster(method='exponential')
        assert adjuster.decay_rate == 0.015
        assert adjuster.threshold == 0.4
    
    def test_sigmoid_initialization(self):
        """Test initialization with sigmoid method"""
        adjuster = TemporalAdjuster(method='sigmoid', midpoint=200, steepness=0.03)
        assert adjuster.method == 'sigmoid'
        assert adjuster.midpoint == 200
        assert adjuster.steepness == 0.03
    
    def test_sigmoid_default_parameters(self):
        """Test sigmoid method with default parameters"""
        adjuster = TemporalAdjuster(method='sigmoid')
        assert adjuster.midpoint == 180
        assert adjuster.steepness == 0.02
    
    def test_invalid_method_raises_error(self):
        """Test that invalid method raises ValueError"""
        with pytest.raises(ValueError):
            TemporalAdjuster(method='invalid')
    
    def test_adjust_probability_exponential(self):
        """Test adjust_probability with exponential method"""
        adjuster = TemporalAdjuster(method='exponential', decay_rate=0.01, threshold=0.4)
        base_prob = 0.3
        current_date = datetime(2025, 10, 1)
        deadline = datetime(2025, 12, 31)
        
        adjusted_prob, metadata = adjuster.adjust_probability(base_prob, current_date, deadline)
        
        # Check adjusted probability is valid
        assert 0 <= adjusted_prob <= 1
        assert adjusted_prob <= base_prob  # Should be reduced
        
        # Check metadata
        assert metadata['decay_method'] == 'exponential'
        assert metadata['decay_rate'] == 0.01
        assert metadata['threshold'] == 0.4
        assert 'threshold_applied' in metadata
        assert 'adjustment_factor' in metadata
    
    def test_adjust_probability_sigmoid(self):
        """Test adjust_probability with sigmoid method"""
        adjuster = TemporalAdjuster(method='sigmoid', midpoint=180, steepness=0.02)
        base_prob = 0.5
        current_date = datetime(2025, 10, 1)
        deadline = datetime(2025, 12, 31)
        
        adjusted_prob, metadata = adjuster.adjust_probability(base_prob, current_date, deadline)
        
        # Check adjusted probability is valid
        assert 0 <= adjusted_prob <= 1
        
        # Check metadata
        assert metadata['decay_method'] == 'sigmoid'
        assert metadata['midpoint'] == 180
        assert metadata['steepness'] == 0.02
        assert 'adjustment_factor' in metadata
    
    def test_adjust_probability_no_decay_above_threshold(self):
        """Test that no decay is applied when above threshold"""
        adjuster = TemporalAdjuster(method='exponential', decay_rate=0.01, threshold=0.4)
        base_prob = 0.6
        current_date = datetime(2025, 10, 1)
        deadline = datetime(2025, 12, 31)
        
        adjusted_prob, metadata = adjuster.adjust_probability(base_prob, current_date, deadline)
        
        # Should be unchanged
        assert adjusted_prob == base_prob
        assert metadata['threshold_applied'] == False
    
    def test_calibrate_from_historical_data(self):
        """Test calibrate_from_historical_data method"""
        adjuster = TemporalAdjuster(method='exponential')
        
        # Currently returns empty dict (to be implemented later)
        result = adjuster.calibrate_from_historical_data([], [])
        assert isinstance(result, dict)
