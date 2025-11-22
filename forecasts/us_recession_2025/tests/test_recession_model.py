"""
Unit tests for US Recession 2025 forecast model.

Tests specific scenarios including historical recession data, economic expansion,
default parameters, and missing indicator handling.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from forecasts.us_recession_2025 import RecessionModel
from forecasts.us_recession_2025.data import fetch_economic_indicators, IndicatorFetchError
from forecasts.us_recession_2025.config import DEFAULT_PARAMS


class TestRecessionModelHistoricalData:
    """Test recession model with historical recession data."""
    
    def test_recession_period_indicators(self):
        """
        Test with indicators typical of a recession period (2008-2009 style).
        
        Expected: High recession probability (> 0.6)
        """
        with patch('forecasts.us_recession_2025.data.fetch_fred_data') as mock_fetch:
            def mock_recession_data(series_id, **kwargs):
                # Recession-like indicators
                values_map = {
                    'T10Y2Y': '-0.8',       # Inverted yield curve
                    'UNRATE': '8.5',        # High unemployment
                    'A191RL1Q225SBEA': '-2.5',  # Negative GDP growth
                    'UMCSENT': '60.0',      # Low consumer confidence
                    'USSLIND': '-2.0',      # Declining leading indicators
                    'ICSA': '450000'        # High jobless claims
                }
                return {
                    'observations': [
                        {'date': '2024-01-01', 'value': values_map.get(series_id, '1.0')}
                    ]
                }
            
            mock_fetch.side_effect = mock_recession_data
            
            model = RecessionModel()
            probability = model.calculate_probability()
            
            # During recession conditions, probability should be high
            assert probability > 0.6, \
                f"Expected high recession probability (>0.6) for recession indicators, got {probability}"
    
    def test_strong_recession_signals(self):
        """
        Test with very strong recession signals.
        
        Expected: Very high recession probability (> 0.8)
        """
        with patch('forecasts.us_recession_2025.data.fetch_fred_data') as mock_fetch:
            def mock_strong_recession_data(series_id, **kwargs):
                # Very strong recession signals
                values_map = {
                    'T10Y2Y': '-1.5',       # Deeply inverted yield curve
                    'UNRATE': '10.0',       # Very high unemployment
                    'A191RL1Q225SBEA': '-5.0',  # Severe GDP contraction
                    'UMCSENT': '50.0',      # Very low consumer confidence
                    'USSLIND': '-3.0',      # Sharply declining leading indicators
                    'ICSA': '600000'        # Very high jobless claims
                }
                return {
                    'observations': [
                        {'date': '2024-01-01', 'value': values_map.get(series_id, '1.0')}
                    ]
                }
            
            mock_fetch.side_effect = mock_strong_recession_data
            
            model = RecessionModel()
            probability = model.calculate_probability()
            
            # With very strong recession signals, probability should be very high
            assert probability > 0.8, \
                f"Expected very high recession probability (>0.8) for strong recession signals, got {probability}"


class TestRecessionModelExpansionData:
    """Test recession model with economic expansion data."""
    
    def test_expansion_period_indicators(self):
        """
        Test with indicators typical of economic expansion.
        
        Expected: Low recession probability (< 0.4)
        """
        with patch('forecasts.us_recession_2025.data.fetch_fred_data') as mock_fetch:
            def mock_expansion_data(series_id, **kwargs):
                # Expansion-like indicators
                values_map = {
                    'T10Y2Y': '1.5',        # Positive yield curve
                    'UNRATE': '3.5',        # Low unemployment
                    'A191RL1Q225SBEA': '3.5',  # Strong GDP growth
                    'UMCSENT': '95.0',      # High consumer confidence
                    'USSLIND': '1.5',       # Rising leading indicators
                    'ICSA': '200000'        # Low jobless claims
                }
                return {
                    'observations': [
                        {'date': '2024-01-01', 'value': values_map.get(series_id, '1.0')}
                    ]
                }
            
            mock_fetch.side_effect = mock_expansion_data
            
            model = RecessionModel()
            probability = model.calculate_probability()
            
            # During expansion, recession probability should be low
            assert probability < 0.4, \
                f"Expected low recession probability (<0.4) for expansion indicators, got {probability}"
    
    def test_strong_expansion_signals(self):
        """
        Test with very strong expansion signals.
        
        Expected: Very low recession probability (< 0.2)
        """
        with patch('forecasts.us_recession_2025.data.fetch_fred_data') as mock_fetch:
            def mock_strong_expansion_data(series_id, **kwargs):
                # Very strong expansion signals
                values_map = {
                    'T10Y2Y': '2.5',        # Steep positive yield curve
                    'UNRATE': '3.0',        # Very low unemployment
                    'A191RL1Q225SBEA': '5.0',  # Very strong GDP growth
                    'UMCSENT': '105.0',     # Very high consumer confidence
                    'USSLIND': '2.5',       # Strongly rising leading indicators
                    'ICSA': '180000'        # Very low jobless claims
                }
                return {
                    'observations': [
                        {'date': '2024-01-01', 'value': values_map.get(series_id, '1.0')}
                    ]
                }
            
            mock_fetch.side_effect = mock_strong_expansion_data
            
            model = RecessionModel()
            probability = model.calculate_probability()
            
            # With very strong expansion signals, probability should be very low
            assert probability < 0.2, \
                f"Expected very low recession probability (<0.2) for strong expansion signals, got {probability}"


class TestRecessionModelDefaultParameters:
    """Test recession model with default parameters."""
    
    def test_default_parameters_used(self):
        """
        Test that default parameters are used when none are provided.
        """
        with patch('forecasts.us_recession_2025.data.fetch_fred_data') as mock_fetch:
            def mock_neutral_data(series_id, **kwargs):
                # Neutral indicators
                values_map = {
                    'T10Y2Y': '0.8',
                    'UNRATE': '5.5',
                    'A191RL1Q225SBEA': '2.5',
                    'UMCSENT': '85.0',
                    'USSLIND': '0.0',
                    'ICSA': '220000'
                }
                return {
                    'observations': [
                        {'date': '2024-01-01', 'value': values_map.get(series_id, '1.0')}
                    ]
                }
            
            mock_fetch.side_effect = mock_neutral_data
            
            model = RecessionModel()
            
            # Calculate with no parameters (should use defaults)
            probability_default = model.calculate_probability()
            
            # Calculate with explicit default parameters
            probability_explicit = model.calculate_probability(DEFAULT_PARAMS)
            
            # Both should give the same result
            assert probability_default == probability_explicit, \
                "Default parameters should produce same result as explicit defaults"
    
    def test_default_parameters_values(self):
        """
        Test that default parameter values are reasonable.
        """
        model = RecessionModel()
        params = model.get_parameters()
        
        # Check that all expected parameters are present
        expected_params = [
            'yield_curve_weight',
            'unemployment_weight',
            'gdp_weight',
            'confidence_weight',
            'leading_indicators_weight',
            'lookback_days'
        ]
        
        for param_name in expected_params:
            assert param_name in params, f"Parameter '{param_name}' missing from model parameters"
        
        # Check that weights are in valid range
        weight_params = [
            'yield_curve_weight',
            'unemployment_weight',
            'gdp_weight',
            'confidence_weight',
            'leading_indicators_weight'
        ]
        
        for param_name in weight_params:
            default_value = params[param_name]['default']
            assert 0.0 <= default_value <= 1.0, \
                f"Default weight for '{param_name}' ({default_value}) is outside [0, 1]"
    
    def test_neutral_indicators_with_defaults(self):
        """
        Test with neutral economic indicators using default parameters.
        
        Expected: Moderate recession probability (around 0.3-0.7)
        """
        with patch('forecasts.us_recession_2025.data.fetch_fred_data') as mock_fetch:
            def mock_neutral_data(series_id, **kwargs):
                # Neutral indicators (close to historical means)
                values_map = {
                    'T10Y2Y': '0.8',
                    'UNRATE': '5.5',
                    'A191RL1Q225SBEA': '2.5',
                    'UMCSENT': '85.0',
                    'USSLIND': '0.0',
                    'ICSA': '220000'
                }
                return {
                    'observations': [
                        {'date': '2024-01-01', 'value': values_map.get(series_id, '1.0')}
                    ]
                }
            
            mock_fetch.side_effect = mock_neutral_data
            
            model = RecessionModel()
            probability = model.calculate_probability()
            
            # With neutral indicators, probability should be moderate
            assert 0.2 <= probability <= 0.8, \
                f"Expected moderate recession probability (0.2-0.8) for neutral indicators, got {probability}"


class TestRecessionModelMissingIndicators:
    """Test recession model handling of missing indicators."""
    
    def test_missing_indicator_raises_error(self):
        """
        Test that missing indicators cause an appropriate error.
        """
        with patch('forecasts.us_recession_2025.data.fetch_fred_data') as mock_fetch:
            # Simulate API failure for one indicator
            def mock_partial_failure(series_id, **kwargs):
                if series_id == 'UNRATE':
                    from lib.data_fetcher import DataFetchError
                    raise DataFetchError("API error")
                
                return {
                    'observations': [
                        {'date': '2024-01-01', 'value': '1.0'}
                    ]
                }
            
            mock_fetch.side_effect = mock_partial_failure
            
            model = RecessionModel()
            
            # Should raise IndicatorFetchError when an indicator is missing
            with pytest.raises(IndicatorFetchError):
                model.calculate_probability()
    
    def test_all_indicators_missing_raises_error(self):
        """
        Test that when all indicators fail to fetch, an error is raised.
        """
        with patch('forecasts.us_recession_2025.data.fetch_fred_data') as mock_fetch:
            # Simulate complete API failure
            from lib.data_fetcher import DataFetchError
            mock_fetch.side_effect = DataFetchError("Complete API failure")
            
            model = RecessionModel()
            
            # Should raise IndicatorFetchError
            with pytest.raises(IndicatorFetchError):
                model.calculate_probability()
    
    def test_empty_observations_raises_error(self):
        """
        Test that empty observations cause an appropriate error.
        """
        with patch('forecasts.us_recession_2025.data.fetch_fred_data') as mock_fetch:
            # Return empty observations
            mock_fetch.return_value = {'observations': []}
            
            model = RecessionModel()
            
            # Should raise IndicatorFetchError
            with pytest.raises(IndicatorFetchError):
                model.calculate_probability()


class TestRecessionModelInterface:
    """Test that RecessionModel implements the ForecastModel interface correctly."""
    
    def test_get_name(self):
        """Test get_name returns a string."""
        model = RecessionModel()
        name = model.get_name()
        assert isinstance(name, str)
        assert len(name) > 0
    
    def test_get_description(self):
        """Test get_description returns a string."""
        model = RecessionModel()
        description = model.get_description()
        assert isinstance(description, str)
        assert len(description) > 0
    
    def test_get_parameters(self):
        """Test get_parameters returns a dictionary."""
        model = RecessionModel()
        params = model.get_parameters()
        assert isinstance(params, dict)
        assert len(params) > 0
    
    def test_get_last_updated(self):
        """Test get_last_updated returns a datetime."""
        model = RecessionModel()
        last_updated = model.get_last_updated()
        assert isinstance(last_updated, datetime)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
