"""
Unit tests for feature engineering module.
"""

import pytest
from forecasts.us_recession_2025.features import FeatureEngineer


class TestFeatureEngineer:
    """Test suite for FeatureEngineer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engineer = FeatureEngineer()
    
    def test_calculate_rate_of_change_basic(self):
        """Test rate of change calculation with known values."""
        # Simple test: 100 -> 110 is 10% increase
        values = [100.0] * 30 + [110.0]  # 31 values total
        
        result = self.engineer.calculate_rate_of_change(values, periods=[30])
        
        assert 'roc_30d' in result
        assert result['roc_30d'] is not None
        assert abs(result['roc_30d'] - 0.1) < 0.001  # 10% increase
    
    def test_calculate_rate_of_change_insufficient_data(self):
        """Test rate of change returns None with insufficient data."""
        values = [100.0, 110.0]  # Only 2 values
        
        result = self.engineer.calculate_rate_of_change(values, periods=[30])
        
        assert 'roc_30d' in result
        assert result['roc_30d'] is None
    
    def test_calculate_rate_of_change_zero_denominator(self):
        """Test rate of change handles zero denominator."""
        values = [0.0] * 30 + [10.0]
        
        result = self.engineer.calculate_rate_of_change(values, periods=[30])
        
        assert 'roc_30d' in result
        assert result['roc_30d'] is None
    
    def test_calculate_moving_averages_basic(self):
        """Test moving average calculation with known values."""
        values = [10.0] * 30  # All values are 10
        
        result = self.engineer.calculate_moving_averages(values, windows=[30])
        
        assert 'ma_30d' in result
        assert result['ma_30d'] is not None
        assert abs(result['ma_30d'] - 10.0) < 0.001
    
    def test_calculate_moving_averages_insufficient_data(self):
        """Test moving average returns None with insufficient data."""
        values = [10.0, 20.0]  # Only 2 values
        
        result = self.engineer.calculate_moving_averages(values, windows=[30])
        
        assert 'ma_30d' in result
        assert result['ma_30d'] is None
    
    def test_calculate_volatility_basic(self):
        """Test volatility calculation."""
        # Values with known standard deviation
        values = [10.0] * 15 + [20.0] * 15  # 30 values
        
        result = self.engineer.calculate_volatility(values, window=30)
        
        assert result is not None
        assert result > 0  # Should have some volatility
    
    def test_calculate_volatility_insufficient_data(self):
        """Test volatility returns None with insufficient data."""
        values = [10.0]  # Only 1 value
        
        result = self.engineer.calculate_volatility(values, window=30)
        
        assert result is None
    
    def test_engineer_features_with_valid_data(self):
        """Test engineer_features with valid raw data."""
        # Create mock raw data structure
        raw_data = {
            'unemployment': {
                'observations': [
                    {'date': '2024-01-01', 'value': '3.5'},
                    {'date': '2024-01-02', 'value': '3.6'},
                    {'date': '2024-01-03', 'value': '3.7'},
                ]
            }
        }
        
        indicators = {'unemployment': 3.7}
        
        features = self.engineer.engineer_features(indicators, raw_data)
        
        # Should return a dictionary (may have None values due to insufficient data)
        assert isinstance(features, dict)
    
    def test_engineer_features_with_missing_indicator(self):
        """Test engineer_features handles missing indicators gracefully."""
        raw_data = {}  # No data
        indicators = {}
        
        features = self.engineer.engineer_features(indicators, raw_data)
        
        # Should return empty dict or dict with no features for missing indicators
        assert isinstance(features, dict)
    
    def test_extract_time_series_basic(self):
        """Test time series extraction from raw data."""
        raw_data = {
            'unemployment': {
                'observations': [
                    {'date': '2024-01-01', 'value': '3.5'},
                    {'date': '2024-01-02', 'value': '3.6'},
                    {'date': '2024-01-03', 'value': '3.7'},
                ]
            }
        }
        
        result = self.engineer._extract_time_series(raw_data, 'unemployment')
        
        assert result is not None
        assert len(result) == 3
        assert result == [3.5, 3.6, 3.7]
    
    def test_extract_time_series_with_missing_values(self):
        """Test time series extraction filters out missing values."""
        raw_data = {
            'unemployment': {
                'observations': [
                    {'date': '2024-01-01', 'value': '3.5'},
                    {'date': '2024-01-02', 'value': '.'},  # Missing
                    {'date': '2024-01-03', 'value': '3.7'},
                ]
            }
        }
        
        result = self.engineer._extract_time_series(raw_data, 'unemployment')
        
        assert result is not None
        assert len(result) == 2
        assert result == [3.5, 3.7]
    
    def test_extract_time_series_missing_indicator(self):
        """Test time series extraction returns None for missing indicator."""
        raw_data = {}
        
        result = self.engineer._extract_time_series(raw_data, 'unemployment')
        
        assert result is None
    
    def test_forward_fill_basic(self):
        """Test forward fill with no gaps."""
        values = [1.0, 2.0, 3.0]
        
        result = self.engineer._forward_fill(values)
        
        assert result == [1.0, 2.0, 3.0]
    
    def test_forward_fill_with_none(self):
        """Test forward fill handles None values."""
        values = [1.0, None, 3.0]
        
        result = self.engineer._forward_fill(values)
        
        assert result == [1.0, 1.0, 3.0]  # None filled with previous value
    
    def test_forward_fill_empty(self):
        """Test forward fill with empty list."""
        values = []
        
        result = self.engineer._forward_fill(values)
        
        assert result == []
