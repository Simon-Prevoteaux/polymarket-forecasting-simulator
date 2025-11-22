"""
Unit tests for Flask web application structure.

Tests basic routing and template rendering for the web interface.
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


def test_app_exists():
    """Test that the Flask app is created successfully."""
    assert app is not None


def test_index_route(client):
    """Test that the home page route works."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Polymarket Forecasting Simulator' in response.data


def test_forecast_detail_route_with_valid_forecast(client):
    """Test that the forecast detail route works with a valid forecast."""
    # Test with the us_recession_2025 forecast which should exist
    response = client.get('/forecast/us_recession_2025')
    assert response.status_code == 200
    # Check that key elements are present
    assert b'US Recession 2025' in response.data or b'us_recession_2025' in response.data


def test_forecast_detail_displays_probability(client):
    """Test that forecast page displays probability."""
    response = client.get('/forecast/us_recession_2025')
    assert response.status_code == 200
    # Check for probability display elements
    assert b'Current Probability' in response.data or b'Probability' in response.data
    assert b'%' in response.data  # Probability should be displayed as percentage


def test_forecast_detail_displays_last_updated(client):
    """Test that forecast page displays last updated timestamp."""
    response = client.get('/forecast/us_recession_2025')
    assert response.status_code == 200
    # Check for last updated timestamp
    assert b'Last updated' in response.data or b'last updated' in response.data


def test_forecast_detail_displays_indicators(client):
    """Test that forecast page displays economic indicators."""
    response = client.get('/forecast/us_recession_2025')
    assert response.status_code == 200
    # Check for indicators section
    assert b'Indicators' in response.data or b'indicators' in response.data


def test_forecast_detail_displays_data_sources(client):
    """Test that forecast page displays data sources."""
    response = client.get('/forecast/us_recession_2025')
    assert response.status_code == 200
    # Check for data sources section
    assert b'Data Sources' in response.data or b'data sources' in response.data
    assert b'FRED' in response.data  # Should mention FRED as data source


def test_forecast_detail_nonexistent_forecast_404(client):
    """Test handling of non-existent forecast (404)."""
    response = client.get('/forecast/nonexistent_forecast_xyz')
    assert response.status_code == 404
    # Should show error page
    assert b'not found' in response.data or b'Not Found' in response.data or b'404' in response.data


def test_api_forecasts_route(client):
    """Test that the API forecasts endpoint works."""
    response = client.get('/api/forecasts')
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert isinstance(data, list)


def test_api_simulate_route_with_valid_parameters(client):
    """Test that the API simulate endpoint works with valid parameters."""
    # Test with valid parameters for us_recession_2025
    response = client.post('/api/forecast/us_recession_2025/simulate',
                          json={
                              'yield_curve_weight': 0.4,
                              'unemployment_weight': 0.3,
                              'gdp_weight': 0.15,
                              'confidence_weight': 0.10,
                              'leading_indicators_weight': 0.05,
                              'lookback_days': 365
                          })
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert 'success' in data
    assert data['success'] is True
    assert 'probability' in data
    assert 0.0 <= data['probability'] <= 1.0
    assert 'parameters' in data


def test_api_simulate_route_with_invalid_parameters(client):
    """Test that the API simulate endpoint validates parameters."""
    # Test with invalid parameter (weight > 1.0)
    response = client.post('/api/forecast/us_recession_2025/simulate',
                          json={
                              'yield_curve_weight': 1.5,  # Invalid: > 1.0
                              'unemployment_weight': 0.25,
                              'gdp_weight': 0.20,
                              'confidence_weight': 0.10,
                              'leading_indicators_weight': 0.10,
                              'lookback_days': 365
                          })
    assert response.status_code == 400
    assert response.is_json
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Invalid parameters'
    assert 'message' in data
    # Check that the error message mentions the validation issue
    assert 'yield_curve_weight' in data['message']
    assert '1.5' in data['message'] or 'exceeds' in data['message'].lower()


def test_api_simulate_route_with_nonexistent_forecast(client):
    """Test that the API simulate endpoint returns 404 for nonexistent forecast."""
    response = client.post('/api/forecast/nonexistent_forecast/simulate',
                          json={'param1': 0.5})
    assert response.status_code == 404
    assert response.is_json
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Forecast not found'


def test_api_simulate_route_without_parameters(client):
    """Test that the API simulate endpoint requires parameters."""
    response = client.post('/api/forecast/us_recession_2025/simulate',
                          json={})  # Empty JSON object
    assert response.status_code == 200  # Empty params will use defaults
    assert response.is_json
    data = response.get_json()
    assert 'success' in data or 'probability' in data


def test_api_simulate_route_reset_to_defaults(client):
    """Test that resetting to defaults produces consistent results."""
    from forecasts.us_recession_2025.config import DEFAULT_PARAMS
    
    # First call with defaults
    response1 = client.post('/api/forecast/us_recession_2025/simulate',
                           json=DEFAULT_PARAMS)
    assert response1.status_code == 200
    data1 = response1.get_json()
    probability1 = data1['probability']
    
    # Call with modified parameters
    modified_params = DEFAULT_PARAMS.copy()
    modified_params['yield_curve_weight'] = 0.5
    response2 = client.post('/api/forecast/us_recession_2025/simulate',
                           json=modified_params)
    assert response2.status_code == 200
    
    # Call with defaults again
    response3 = client.post('/api/forecast/us_recession_2025/simulate',
                           json=DEFAULT_PARAMS)
    assert response3.status_code == 200
    data3 = response3.get_json()
    probability3 = data3['probability']
    
    # Probabilities should be the same (within floating point precision)
    assert abs(probability1 - probability3) < 1e-6


def test_404_error_handler(client):
    """Test that 404 errors are handled gracefully."""
    response = client.get('/nonexistent')
    assert response.status_code == 404


def test_routes_registered():
    """Test that all expected routes are registered."""
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    
    assert '/' in routes
    assert '/forecast/<name>' in routes
    assert '/api/forecasts' in routes
    assert '/api/forecast/<name>/simulate' in routes


def test_forecast_detail_displays_parameters(client):
    """Test that forecast page displays parameter adjustment interface."""
    response = client.get('/forecast/us_recession_2025')
    assert response.status_code == 200
    # Check for parameters section
    assert b'parameters-section' in response.data or b'Parameters' in response.data
    # Check for parameter controls
    assert b'parameter-slider' in response.data
    # Check for reset button
    assert b'reset-parameters' in response.data or b'Reset to Defaults' in response.data
    # Check for simulate button
    assert b'simulate-parameters' in response.data or b'Simulate' in response.data
