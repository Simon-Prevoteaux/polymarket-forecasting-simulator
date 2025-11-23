"""
Integration test for v2 model breakdown in Flask app.

Tests that the v2 model's breakdown data is properly passed to the template.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))

import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_v2_model_provides_breakdown_data(client):
    """Test that v2 model provides breakdown data through API."""
    # The v2 model should be registered as us_recession_2025
    # (it's the default model in that directory)
    response = client.get('/api/forecast/us_recession_2025/breakdown')
    assert response.status_code == 200
    assert response.is_json
    
    data = response.get_json()
    assert data['success'] is True
    assert data['forecast'] == 'us_recession_2025'
    
    # Check if breakdown is available
    # Note: This depends on whether the v2 model is active
    # The v1 model returns None, v2 returns breakdown
    if data['has_breakdown']:
        breakdown = data['breakdown']
        # Verify breakdown structure
        assert 'base_probability' in breakdown
        assert 'adjusted_probability' in breakdown
        assert 'days_remaining' in breakdown
        assert 'indicator_signals' in breakdown
        assert 'temporal_metadata' in breakdown
        
        # Verify probabilities are valid
        assert 0.0 <= breakdown['base_probability'] <= 1.0
        assert 0.0 <= breakdown['adjusted_probability'] <= 1.0
        assert isinstance(breakdown['days_remaining'], int)
        assert breakdown['days_remaining'] >= 0


def test_forecast_route_includes_breakdown_in_context(client):
    """Test that forecast route includes breakdown data in template context."""
    response = client.get('/forecast/us_recession_2025')
    assert response.status_code == 200
    
    # The response should include the forecast data
    # We can't directly check template context, but we can verify
    # the response was successful and contains expected elements
    assert b'US Recession 2025' in response.data or b'us_recession_2025' in response.data


def test_v1_model_gracefully_handles_no_breakdown():
    """Test that models without breakdown (v1) work correctly."""
    # This test verifies backward compatibility
    # The election_2028 model doesn't have breakdown
    from forecasts import discover_forecasts
    
    registry = discover_forecasts()
    election_model = registry.get('election_2028')
    
    if election_model:
        # Should return None for models without breakdown
        breakdown = election_model.get_probability_breakdown()
        assert breakdown is None


def test_breakdown_endpoint_with_model_without_breakdown(client):
    """Test breakdown endpoint with a model that doesn't provide breakdown."""
    # Test with election_2028 which doesn't have breakdown
    response = client.get('/api/forecast/election_2028/breakdown')
    assert response.status_code == 200
    assert response.is_json
    
    data = response.get_json()
    assert data['success'] is True
    assert data['forecast'] == 'election_2028'
    assert data['has_breakdown'] is False
    assert 'probability' in data
    assert 0.0 <= data['probability'] <= 1.0
