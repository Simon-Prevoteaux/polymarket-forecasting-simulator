"""
Test breakdown functionality with the actual v2 model.

This test directly instantiates the v2 model to verify that the breakdown
endpoint works correctly when a model provides breakdown data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest


def test_v2_model_provides_breakdown():
    """Test that the v2 model provides breakdown data."""
    from forecasts.us_recession_2025.model_v2 import RecessionModelV2
    
    model = RecessionModelV2()
    
    # Get breakdown
    breakdown = model.get_probability_breakdown()
    
    # Verify breakdown is not None
    assert breakdown is not None, "V2 model should provide breakdown"
    
    # Verify structure
    assert 'base_probability' in breakdown
    assert 'adjusted_probability' in breakdown
    assert 'days_remaining' in breakdown
    assert 'indicator_signals' in breakdown
    assert 'temporal_metadata' in breakdown
    
    # Verify types and ranges
    assert isinstance(breakdown['base_probability'], float)
    assert isinstance(breakdown['adjusted_probability'], float)
    assert isinstance(breakdown['days_remaining'], int)
    assert isinstance(breakdown['indicator_signals'], dict)
    assert isinstance(breakdown['temporal_metadata'], dict)
    
    # Verify probabilities are valid
    assert 0.0 <= breakdown['base_probability'] <= 1.0
    assert 0.0 <= breakdown['adjusted_probability'] <= 1.0
    assert breakdown['days_remaining'] >= 0
    
    print("\n✓ V2 model breakdown structure verified:")
    print(f"  - Base probability: {breakdown['base_probability']:.4f}")
    print(f"  - Adjusted probability: {breakdown['adjusted_probability']:.4f}")
    print(f"  - Days remaining: {breakdown['days_remaining']}")
    print(f"  - Temporal metadata: {breakdown['temporal_metadata']}")


def test_v1_model_returns_none():
    """Test that the v1 model returns None for breakdown."""
    from forecasts.us_recession_2025.model import RecessionModel
    
    model = RecessionModel()
    
    # Get breakdown
    breakdown = model.get_probability_breakdown()
    
    # V1 model should return None (uses default implementation)
    assert breakdown is None, "V1 model should return None for breakdown"
    
    print("\n✓ V1 model correctly returns None for breakdown")


def test_breakdown_endpoint_logic():
    """Test the breakdown endpoint logic with both model types."""
    # This simulates what the Flask endpoint does
    
    # Test with v2 model
    from forecasts.us_recession_2025.model_v2 import RecessionModelV2
    v2_model = RecessionModelV2()
    
    breakdown = v2_model.get_probability_breakdown()
    
    if breakdown is not None:
        # Model provides detailed breakdown
        response_data = {
            'success': True,
            'forecast': 'us_recession_2025',
            'has_breakdown': True,
            'breakdown': breakdown
        }
        assert response_data['has_breakdown'] is True
        assert 'breakdown' in response_data
        print("\n✓ V2 model endpoint logic: returns breakdown")
    else:
        # Should not happen with v2
        assert False, "V2 model should provide breakdown"
    
    # Test with v1 model
    from forecasts.us_recession_2025.model import RecessionModel
    v1_model = RecessionModel()
    
    breakdown = v1_model.get_probability_breakdown()
    
    if breakdown is not None:
        # Should not happen with v1
        assert False, "V1 model should not provide breakdown"
    else:
        # Model doesn't provide breakdown, return basic probability
        probability = v1_model.calculate_probability()
        response_data = {
            'success': True,
            'forecast': 'us_recession_2025',
            'has_breakdown': False,
            'probability': probability
        }
        assert response_data['has_breakdown'] is False
        assert 'probability' in response_data
        print("✓ V1 model endpoint logic: returns basic probability")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
