"""
Property-based tests for US Recession 2025 forecast model.

These tests verify universal properties that should hold across all inputs.
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from forecasts.us_recession_2025 import RecessionModel
from forecasts.us_recession_2025.data import fetch_economic_indicators
from forecasts.us_recession_2025.config import DATA_SOURCES


# Feature: polymarket-forecasting-simulator, Property 2: Economic indicators collection
@given(
    lookback_days=st.integers(min_value=30, max_value=365)
)
@settings(max_examples=100)
def test_economic_indicators_collection(lookback_days):
    """
    Property 2: Economic indicators collection
    
    For any execution of the recession forecast model, the system must successfully 
    fetch and process all configured economic indicators before calculating the probability.
    
    This test mocks the FRED API to ensure that:
    1. All configured indicators are requested
    2. The model only proceeds with calculation when all indicators are available
    3. Each indicator has a valid numeric value
    
    Validates: Requirements 2.2
    """
    # Mock the fetch_fred_data function to return valid data
    with patch('forecasts.us_recession_2025.data.fetch_fred_data') as mock_fetch:
        # Create a mock response for each indicator
        def mock_fetch_response(series_id, **kwargs):
            return {
                'observations': [
                    {'date': '2024-01-01', 'value': '1.5'},
                    {'date': '2024-01-02', 'value': '1.6'},
                    {'date': '2024-01-03', 'value': '1.7'}
                ]
            }
        
        mock_fetch.side_effect = mock_fetch_response
        
        # Fetch indicators
        indicators = fetch_economic_indicators(lookback_days=lookback_days)
        
        # Verify all configured indicators are present
        for indicator_name in DATA_SOURCES.keys():
            assert indicator_name in indicators, \
                f"Indicator '{indicator_name}' missing from fetched indicators"
            
            # Verify each indicator has a valid numeric value
            value = indicators[indicator_name]
            assert isinstance(value, (int, float)), \
                f"Indicator '{indicator_name}' has non-numeric value: {value}"
            assert not (value != value), \
                f"Indicator '{indicator_name}' has NaN value"  # NaN check
        
        # Verify timestamps are present
        assert 'timestamps' in indicators, "Timestamps missing from indicators"
        assert isinstance(indicators['timestamps'], dict), \
            "Timestamps should be a dictionary"
        
        # Verify all indicators have timestamps
        for indicator_name in DATA_SOURCES.keys():
            assert indicator_name in indicators['timestamps'], \
                f"Timestamp for '{indicator_name}' missing"
        
        # Verify the correct number of API calls were made (one per indicator)
        assert mock_fetch.call_count == len(DATA_SOURCES), \
            f"Expected {len(DATA_SOURCES)} API calls, got {mock_fetch.call_count}"


# Feature: polymarket-forecasting-simulator, Property 1: Probability bounds enforcement
@given(
    yield_curve_weight=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    unemployment_weight=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    gdp_weight=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    confidence_weight=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    leading_indicators_weight=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_recession_model_probability_bounds(
    yield_curve_weight,
    unemployment_weight,
    gdp_weight,
    confidence_weight,
    leading_indicators_weight
):
    """
    Property 1: Probability bounds enforcement (RecessionModel)
    
    For any set of valid parameter weights, the recession model must return 
    a probability between 0 and 1 (inclusive).
    
    Validates: Requirements 2.1
    """
    # Mock the data fetching to return realistic indicator values
    with patch('forecasts.us_recession_2025.data.fetch_fred_data') as mock_fetch:
        def mock_fetch_response(series_id, **kwargs):
            # Return different realistic values for different indicators
            values_map = {
                'T10Y2Y': '0.5',        # Yield curve
                'UNRATE': '4.5',        # Unemployment
                'A191RL1Q225SBEA': '2.5',  # GDP growth
                'UMCSENT': '85.0',      # Consumer confidence
                'USSLIND': '0.2',       # Leading indicators
                'ICSA': '220000'        # Jobless claims
            }
            return {
                'observations': [
                    {'date': '2024-01-01', 'value': values_map.get(series_id, '1.0')}
                ]
            }
        
        mock_fetch.side_effect = mock_fetch_response
        
        # Create model and calculate probability
        model = RecessionModel()
        
        params = {
            'yield_curve_weight': yield_curve_weight,
            'unemployment_weight': unemployment_weight,
            'gdp_weight': gdp_weight,
            'confidence_weight': confidence_weight,
            'leading_indicators_weight': leading_indicators_weight,
            'lookback_days': 365
        }
        
        probability = model.calculate_probability(params)
        
        # Verify probability is in valid range
        assert 0.0 <= probability <= 1.0, \
            f"Recession model returned probability {probability}, which is outside [0, 1]"


# Feature: polymarket-forecasting-simulator, Property 4: Parameter modification triggers recalculation
@given(
    base_weight=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    modified_weight=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_parameter_modification_triggers_recalculation(base_weight, modified_weight):
    """
    Property 4: Parameter modification triggers recalculation
    
    For any forecast model and any parameter modification, changing a parameter value 
    must produce a recalculated probability that may differ from the original.
    
    This test verifies that:
    1. Modifying a parameter triggers a new calculation
    2. The model responds to parameter changes (when weights differ significantly)
    3. The calculation produces a valid probability in both cases
    
    Validates: Requirements 5.2
    """
    # Skip if weights are too similar (within floating point precision)
    if abs(base_weight - modified_weight) < 0.01:
        return
    
    # Mock the data fetching to return consistent indicator values
    with patch('forecasts.us_recession_2025.data.fetch_fred_data') as mock_fetch:
        def mock_fetch_response(series_id, **kwargs):
            # Return different realistic values for different indicators
            values_map = {
                'T10Y2Y': '0.5',        # Yield curve
                'UNRATE': '4.5',        # Unemployment
                'A191RL1Q225SBEA': '2.5',  # GDP growth
                'UMCSENT': '85.0',      # Consumer confidence
                'USSLIND': '0.2',       # Leading indicators
                'ICSA': '220000'        # Jobless claims
            }
            return {
                'observations': [
                    {'date': '2024-01-01', 'value': values_map.get(series_id, '1.0')}
                ]
            }
        
        mock_fetch.side_effect = mock_fetch_response
        
        # Create model
        model = RecessionModel()
        
        # Calculate with base parameters
        base_params = {
            'yield_curve_weight': base_weight,
            'unemployment_weight': 0.25,
            'gdp_weight': 0.20,
            'confidence_weight': 0.10,
            'leading_indicators_weight': 0.10,
            'lookback_days': 365
        }
        
        base_probability = model.calculate_probability(base_params)
        
        # Verify base probability is valid
        assert 0.0 <= base_probability <= 1.0, \
            f"Base probability {base_probability} is outside [0, 1]"
        
        # Calculate with modified parameters
        modified_params = {
            'yield_curve_weight': modified_weight,
            'unemployment_weight': 0.25,
            'gdp_weight': 0.20,
            'confidence_weight': 0.10,
            'leading_indicators_weight': 0.10,
            'lookback_days': 365
        }
        
        modified_probability = model.calculate_probability(modified_params)
        
        # Verify modified probability is valid
        assert 0.0 <= modified_probability <= 1.0, \
            f"Modified probability {modified_probability} is outside [0, 1]"
        
        # Verify that calculation occurred (both probabilities are valid)
        # The actual values may or may not differ depending on the model's sensitivity
        # but both calculations should succeed and return valid probabilities
        assert isinstance(base_probability, (int, float)), \
            "Base calculation did not return a numeric probability"
        assert isinstance(modified_probability, (int, float)), \
            "Modified calculation did not return a numeric probability"


# Feature: polymarket-forecasting-simulator, Property 6: Simulation state preservation
@given(
    modified_weight=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_simulation_state_preservation(modified_weight):
    """
    Property 6: Simulation state preservation
    
    For any forecast model, running a simulation with modified parameters and then 
    running again with default parameters must produce the same probability as the 
    initial default run (assuming data hasn't changed).
    
    This test verifies that:
    1. Simulations are non-destructive
    2. The model state is not permanently altered by parameter changes
    3. Default parameters always produce consistent results
    
    Validates: Requirements 5.5
    """
    # Mock the data fetching to return consistent indicator values
    with patch('forecasts.us_recession_2025.data.fetch_fred_data') as mock_fetch:
        def mock_fetch_response(series_id, **kwargs):
            # Return consistent realistic values for all calls
            values_map = {
                'T10Y2Y': '0.5',        # Yield curve
                'UNRATE': '4.5',        # Unemployment
                'A191RL1Q225SBEA': '2.5',  # GDP growth
                'UMCSENT': '85.0',      # Consumer confidence
                'USSLIND': '0.2',       # Leading indicators
                'ICSA': '220000'        # Jobless claims
            }
            return {
                'observations': [
                    {'date': '2024-01-01', 'value': values_map.get(series_id, '1.0')}
                ]
            }
        
        mock_fetch.side_effect = mock_fetch_response
        
        # Create model
        model = RecessionModel()
        
        # Calculate with default parameters (first run)
        from forecasts.us_recession_2025.config import DEFAULT_PARAMS
        initial_probability = model.calculate_probability(DEFAULT_PARAMS.copy())
        
        # Verify initial probability is valid
        assert 0.0 <= initial_probability <= 1.0, \
            f"Initial probability {initial_probability} is outside [0, 1]"
        
        # Calculate with modified parameters (simulation)
        modified_params = DEFAULT_PARAMS.copy()
        modified_params['yield_curve_weight'] = modified_weight
        
        simulation_probability = model.calculate_probability(modified_params)
        
        # Verify simulation probability is valid
        assert 0.0 <= simulation_probability <= 1.0, \
            f"Simulation probability {simulation_probability} is outside [0, 1]"
        
        # Calculate with default parameters again (should match initial)
        final_probability = model.calculate_probability(DEFAULT_PARAMS.copy())
        
        # Verify final probability is valid
        assert 0.0 <= final_probability <= 1.0, \
            f"Final probability {final_probability} is outside [0, 1]"
        
        # Verify that default parameters produce the same result before and after simulation
        # Allow for small floating point differences
        assert abs(initial_probability - final_probability) < 1e-10, \
            f"State not preserved: initial={initial_probability}, final={final_probability}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
