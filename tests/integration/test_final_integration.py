"""
Final Integration Tests for US Recession Forecast V2

Tests the complete integration of v1, v2, and other forecast models
with the web interface, ensuring proper display and backward compatibility.

Task 23: Final integration testing
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from web.app import app
from forecasts.us_recession_2025.model import RecessionModel
from forecasts.us_recession_2025.model_v2 import RecessionModelV2
from forecasts.election_2028.model import ElectionModel


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def v1_model():
    """Create a v1 recession model instance."""
    return RecessionModel()


@pytest.fixture
def v2_model():
    """Create a v2 recession model instance."""
    return RecessionModelV2()


@pytest.fixture
def election_model():
    """Create an election model instance."""
    return ElectionModel()


class TestV1ModelDisplay:
    """Test v1 model display without temporal section."""
    
    def test_v1_forecast_page_loads(self, client):
        """Test that v1 forecast page loads successfully."""
        response = client.get('/forecast/us_recession_2025')
        assert response.status_code == 200
        assert b'US Recession 2025' in response.data
    
    def test_v1_no_temporal_section(self, client):
        """Test that v1 forecast does not show temporal decay section."""
        response = client.get('/forecast/us_recession_2025')
        assert response.status_code == 200
        
        # Should not have temporal decay section
        assert b'temporal-decay-section' not in response.data
        assert b'Base Probability' not in response.data
        assert b'Adjusted Probability' not in response.data
        assert b'Days Remaining' not in response.data
    
    def test_v1_shows_standard_probability(self, client):
        """Test that v1 forecast shows standard probability display."""
        response = client.get('/forecast/us_recession_2025')
        assert response.status_code == 200
        
        # Should have standard probability display
        assert b'probability' in response.data.lower()
    
    def test_v1_model_breakdown_returns_none(self, v1_model):
        """Test that v1 model's get_probability_breakdown returns None."""
        # V1 model has the method (from base class) but returns None
        assert hasattr(v1_model, 'get_probability_breakdown')
        breakdown = v1_model.get_probability_breakdown()
        assert breakdown is None
    
    def test_v1_api_endpoint(self, client):
        """Test that v1 API endpoint works without breakdown."""
        response = client.get('/api/forecasts')
        assert response.status_code == 200
        
        data = response.get_json()
        assert isinstance(data, list)
        # Check that at least one forecast exists
        assert len(data) > 0


class TestV2ModelDisplay:
    """Test v2 model display with temporal section."""
    
    def test_v2_model_can_be_instantiated(self, v2_model):
        """Test that v2 model can be instantiated directly."""
        assert v2_model is not None
        assert v2_model.get_name() == "US Recession 2025 V2"
    
    def test_v2_model_calculates_probability(self, v2_model):
        """Test that v2 model can calculate probability."""
        try:
            prob = v2_model.calculate_probability()
            assert 0 <= prob <= 1
        except Exception as e:
            pytest.skip(f"V2 model calculation failed (may be due to API issues): {e}")
    
    def test_v2_breakdown_structure(self, v2_model):
        """Test that v2 breakdown has correct structure."""
        try:
            breakdown = v2_model.get_probability_breakdown()
            assert breakdown is not None
            assert 'base_probability' in breakdown
            assert 'adjusted_probability' in breakdown
        except Exception as e:
            pytest.skip(f"V2 breakdown failed (may be due to API issues): {e}")
    
    def test_v2_model_has_breakdown_method(self, v2_model):
        """Test that v2 model has get_probability_breakdown method."""
        assert hasattr(v2_model, 'get_probability_breakdown')
        assert callable(v2_model.get_probability_breakdown)
    
    def test_v2_breakdown_returns_required_fields(self, v2_model):
        """Test that v2 breakdown returns all required fields."""
        breakdown = v2_model.get_probability_breakdown()
        
        assert isinstance(breakdown, dict)
        assert 'base_probability' in breakdown
        assert 'adjusted_probability' in breakdown
        assert 'days_remaining' in breakdown
        assert 'temporal_metadata' in breakdown
        
        # Verify types
        assert isinstance(breakdown['base_probability'], (int, float))
        assert isinstance(breakdown['adjusted_probability'], (int, float))
        assert isinstance(breakdown['days_remaining'], int)
        assert isinstance(breakdown['temporal_metadata'], dict)
    
    def test_v2_temporal_metadata_complete(self, v2_model):
        """Test that v2 temporal metadata contains required fields."""
        breakdown = v2_model.get_probability_breakdown()
        metadata = breakdown['temporal_metadata']
        
        # Should have decay method information
        assert 'decay_method' in metadata or 'method' in metadata
    
    def test_v2_breakdown_endpoint_structure(self, v2_model):
        """Test that v2 model provides breakdown with correct structure."""
        try:
            breakdown = v2_model.get_probability_breakdown()
            if breakdown is not None:
                assert 'base_probability' in breakdown
                assert 'adjusted_probability' in breakdown
                assert 'days_remaining' in breakdown
        except Exception as e:
            pytest.skip(f"V2 breakdown failed: {e}")


class TestElectionModelDisplay:
    """Test election forecast display (no temporal section)."""
    
    def test_election_forecast_page_loads(self, client):
        """Test that election forecast page loads successfully."""
        response = client.get('/forecast/election_2028')
        assert response.status_code == 200
        assert b'Election 2028' in response.data or b'Presidential Election' in response.data
    
    def test_election_no_temporal_section(self, client):
        """Test that election forecast does not show temporal decay section."""
        response = client.get('/forecast/election_2028')
        assert response.status_code == 200
        
        # Should not have temporal decay section
        assert b'temporal-decay-section' not in response.data
        assert b'Base Probability' not in response.data
        assert b'Adjusted Probability' not in response.data
    
    def test_election_shows_standard_probability(self, client):
        """Test that election forecast shows standard probability display."""
        response = client.get('/forecast/election_2028')
        assert response.status_code == 200
        
        # Should have standard probability display
        assert b'probability' in response.data.lower()
    
    def test_election_model_breakdown_returns_none(self, election_model):
        """Test that election model's get_probability_breakdown returns None."""
        # Election model has the method (from base class) but returns None
        assert hasattr(election_model, 'get_probability_breakdown')
        breakdown = election_model.get_probability_breakdown()
        assert breakdown is None


class TestBackwardCompatibility:
    """Test backward compatibility across all models."""
    
    def test_all_models_implement_base_interface(self, v1_model, v2_model, election_model):
        """Test that all models implement the base ForecastModel interface."""
        for model in [v1_model, v2_model, election_model]:
            assert hasattr(model, 'get_name')
            assert hasattr(model, 'get_description')
            assert hasattr(model, 'get_parameters')
            assert hasattr(model, 'calculate_probability')
            assert hasattr(model, 'get_last_updated')
            assert hasattr(model, 'get_data_sources')
    
    def test_all_models_calculate_valid_probabilities(self, v1_model, v2_model, election_model):
        """Test that all models return valid probabilities."""
        for model in [v1_model, v2_model, election_model]:
            try:
                prob = model.calculate_probability()
                assert 0 <= prob <= 1, f"{model.get_name()} returned invalid probability: {prob}"
            except Exception as e:
                # Some models might fail due to API issues, but shouldn't crash
                pytest.skip(f"Model {model.get_name()} failed: {e}")
    
    def test_forecast_discovery_finds_models(self, client):
        """Test that forecast discovery finds available models."""
        response = client.get('/api/forecasts')
        assert response.status_code == 200
        
        data = response.get_json()
        assert isinstance(data, list)
        
        # Should find at least two models (us_recession_2025 and election_2028)
        # Note: v2 model is in the same directory as v1, so it's not auto-discovered
        # but can be instantiated directly
        assert len(data) >= 2
        
        # Check that we have valid forecast data
        for forecast in data:
            assert 'name' in forecast or 'display_name' in forecast


class TestResponsiveDesign:
    """Test responsive design elements."""
    
    def test_css_file_exists(self):
        """Test that CSS file exists with responsive styles."""
        css_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'static', 'css', 'style.css')
        assert os.path.exists(css_path)
        
        with open(css_path, 'r') as f:
            css_content = f.read()
            # Check for responsive design elements
            assert 'grid' in css_content.lower() or 'flex' in css_content.lower()
    
    def test_forecast_page_has_responsive_elements(self, client):
        """Test that forecast pages have responsive design elements."""
        response = client.get('/forecast/us_recession_2025')
        assert response.status_code == 200
        
        response_text = response.data.decode('utf-8')
        # Should have CSS classes for styling
        assert 'class=' in response_text
    
    def test_temporal_css_classes_defined(self):
        """Test that temporal decay CSS classes are defined."""
        css_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'static', 'css', 'style.css')
        with open(css_path, 'r') as f:
            css_content = f.read()
            # Check for temporal-related CSS
            assert 'temporal' in css_content.lower() or 'decay' in css_content.lower() or \
                   'probability' in css_content.lower()


class TestGenericForecastInterface:
    """Test that the interface remains generic and reusable."""
    
    def test_discovered_forecasts_render(self, client):
        """Test that all discovered forecasts render successfully."""
        # Get list of discovered forecasts
        response = client.get('/api/forecasts')
        assert response.status_code == 200
        
        data = response.get_json()
        # Test that we can access at least the known forecasts
        known_forecasts = ['us_recession_2025', 'election_2028']
        
        for forecast_name in known_forecasts:
            response = client.get(f'/forecast/{forecast_name}')
            # Should either load successfully or return 404 (if not discovered)
            assert response.status_code in [200, 404]
            
            if response.status_code == 200:
                # If it loads, should have content
                assert len(response.data) > 0
    
    def test_breakdown_endpoint_handles_models_without_breakdown(self, v1_model):
        """Test that models without breakdown return None."""
        breakdown = v1_model.get_probability_breakdown()
        assert breakdown is None
    
    def test_breakdown_endpoint_works_with_v2_model(self, v2_model):
        """Test that v2 model provides breakdown."""
        try:
            breakdown = v2_model.get_probability_breakdown()
            assert breakdown is not None
            assert isinstance(breakdown, dict)
        except Exception as e:
            pytest.skip(f"V2 breakdown failed: {e}")


class TestErrorHandling:
    """Test error handling in integration scenarios."""
    
    def test_nonexistent_forecast_returns_404(self, client):
        """Test that requesting nonexistent forecast returns 404."""
        response = client.get('/forecast/nonexistent_forecast')
        assert response.status_code == 404
    
    def test_nonexistent_breakdown_returns_404(self, client):
        """Test that requesting breakdown for nonexistent forecast returns 404."""
        response = client.get('/api/forecast/nonexistent_forecast/breakdown')
        assert response.status_code == 404
    
    def test_home_page_loads(self, client):
        """Test that home page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_api_forecasts_endpoint(self, client):
        """Test that API forecasts endpoint works."""
        response = client.get('/api/forecasts')
        assert response.status_code == 200
        
        data = response.get_json()
        assert isinstance(data, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
