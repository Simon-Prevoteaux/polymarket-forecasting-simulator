"""
Integration test for Flask app with forecast discovery.

Tests that the Flask app correctly uses the discovery mechanism to
display forecasts.
"""

import os
import sys
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_page_lists_forecasts(client):
    """Test that the index page lists discovered forecasts."""
    response = client.get('/')
    
    assert response.status_code == 200
    
    # The page should contain forecast information
    # We expect at least the us_recession_2025 forecast
    data = response.data.decode('utf-8')
    
    # Check for forecast presence (the template should render forecast names)
    assert 'US Recession 2025' in data or 'us_recession_2025' in data


def test_api_forecasts_endpoint(client):
    """Test that the API endpoint returns forecast data."""
    response = client.get('/api/forecasts')
    
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    data = response.get_json()
    assert isinstance(data, list)
    
    # We expect at least one forecast (us_recession_2025)
    assert len(data) >= 1
    
    # Check structure of forecast data
    if len(data) > 0:
        forecast = data[0]
        assert 'directory_name' in forecast
        assert 'name' in forecast
        assert 'description' in forecast
        assert 'last_updated' in forecast


def test_api_forecasts_contains_us_recession(client):
    """Test that the API includes the us_recession_2025 forecast."""
    response = client.get('/api/forecasts')
    
    assert response.status_code == 200
    
    data = response.get_json()
    
    # Find us_recession_2025 forecast
    us_recession = None
    for forecast in data:
        if forecast['directory_name'] == 'us_recession_2025':
            us_recession = forecast
            break
    
    assert us_recession is not None, "us_recession_2025 forecast not found in API response"
    assert us_recession['name'] == 'US Recession 2025'
    assert 'recession' in us_recession['description'].lower()
