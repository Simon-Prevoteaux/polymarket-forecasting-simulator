"""
Validation script for API endpoints.

This script validates that:
1. /api/forecasts returns correct JSON structure with all forecast metadata
2. /api/forecast/<name>/simulate works with valid parameters
3. /api/forecast/<name>/simulate properly validates and rejects invalid parameters

Run this script to manually verify API endpoint functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))

from app import app
import json


def validate_api_forecasts():
    """Validate /api/forecasts endpoint returns correct JSON structure."""
    print("\n" + "="*70)
    print("VALIDATING /api/forecasts ENDPOINT")
    print("="*70)
    
    with app.test_client() as client:
        response = client.get('/api/forecasts')
        
        print(f"\nStatus Code: {response.status_code}")
        assert response.status_code == 200, "Expected status code 200"
        print("✓ Status code is 200")
        
        assert response.is_json, "Response should be JSON"
        print("✓ Response is JSON")
        
        data = response.get_json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Response is a list with {len(data)} forecast(s)")
        
        if len(data) > 0:
            print("\nValidating forecast metadata structure:")
            for forecast in data:
                print(f"\n  Forecast: {forecast.get('name', 'UNKNOWN')}")
                
                # Check required fields
                assert 'directory_name' in forecast, "Missing 'directory_name' field"
                print(f"    ✓ directory_name: {forecast['directory_name']}")
                
                assert 'name' in forecast, "Missing 'name' field"
                print(f"    ✓ name: {forecast['name']}")
                
                assert 'description' in forecast, "Missing 'description' field"
                print(f"    ✓ description: {forecast['description'][:50]}...")
                
                assert 'last_updated' in forecast, "Missing 'last_updated' field"
                print(f"    ✓ last_updated: {forecast['last_updated']}")
                
                # Validate last_updated is ISO format timestamp
                from datetime import datetime
                try:
                    datetime.fromisoformat(forecast['last_updated'])
                    print(f"    ✓ last_updated is valid ISO format timestamp")
                except ValueError:
                    raise AssertionError(f"last_updated is not valid ISO format: {forecast['last_updated']}")
        
        print("\n" + "="*70)
        print("✓ /api/forecasts VALIDATION PASSED")
        print("="*70)
        return True


def validate_api_simulate_valid_params():
    """Validate /api/forecast/<name>/simulate with valid parameters."""
    print("\n" + "="*70)
    print("VALIDATING /api/forecast/<name>/simulate WITH VALID PARAMETERS")
    print("="*70)
    
    with app.test_client() as client:
        # Test with valid parameters
        valid_params = {
            'yield_curve_weight': 0.4,
            'unemployment_weight': 0.3,
            'gdp_weight': 0.15,
            'confidence_weight': 0.10,
            'leading_indicators_weight': 0.05,
            'lookback_days': 365
        }
        
        print(f"\nSending POST request to /api/forecast/us_recession_2025/simulate")
        print(f"Parameters: {json.dumps(valid_params, indent=2)}")
        
        response = client.post('/api/forecast/us_recession_2025/simulate',
                              json=valid_params)
        
        print(f"\nStatus Code: {response.status_code}")
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        print("✓ Status code is 200")
        
        assert response.is_json, "Response should be JSON"
        print("✓ Response is JSON")
        
        data = response.get_json()
        print(f"\nResponse data: {json.dumps(data, indent=2)}")
        
        # Validate response structure
        assert 'success' in data, "Missing 'success' field"
        assert data['success'] is True, "Expected success=True"
        print("✓ success field is True")
        
        assert 'probability' in data, "Missing 'probability' field"
        probability = data['probability']
        assert 0.0 <= probability <= 1.0, f"Probability {probability} not in [0, 1]"
        print(f"✓ probability is valid: {probability}")
        
        assert 'parameters' in data, "Missing 'parameters' field"
        print(f"✓ parameters field present: {data['parameters']}")
        
        assert 'forecast' in data, "Missing 'forecast' field"
        print(f"✓ forecast field present: {data['forecast']}")
        
        print("\n" + "="*70)
        print("✓ VALID PARAMETERS VALIDATION PASSED")
        print("="*70)
        return True


def validate_api_simulate_invalid_params():
    """Validate /api/forecast/<name>/simulate rejects invalid parameters."""
    print("\n" + "="*70)
    print("VALIDATING /api/forecast/<name>/simulate WITH INVALID PARAMETERS")
    print("="*70)
    
    with app.test_client() as client:
        # Test with invalid parameters (weight > 1.0)
        invalid_params = {
            'yield_curve_weight': 1.5,  # Invalid: > 1.0
            'unemployment_weight': 0.25,
            'gdp_weight': 0.20,
            'confidence_weight': 0.10,
            'leading_indicators_weight': 0.10,
            'lookback_days': 365
        }
        
        print(f"\nSending POST request with INVALID parameters")
        print(f"Parameters: {json.dumps(invalid_params, indent=2)}")
        print("(Note: yield_curve_weight=1.5 exceeds maximum of 1.0)")
        
        response = client.post('/api/forecast/us_recession_2025/simulate',
                              json=invalid_params)
        
        print(f"\nStatus Code: {response.status_code}")
        assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
        print("✓ Status code is 400 (Bad Request)")
        
        assert response.is_json, "Response should be JSON"
        print("✓ Response is JSON")
        
        data = response.get_json()
        print(f"\nResponse data: {json.dumps(data, indent=2)}")
        
        # Validate error response structure
        assert 'error' in data, "Missing 'error' field"
        assert data['error'] == 'Invalid parameters', f"Expected error='Invalid parameters', got '{data['error']}'"
        print("✓ error field is 'Invalid parameters'")
        
        assert 'validation_errors' in data, "Missing 'validation_errors' field"
        print(f"✓ validation_errors field present: {data['validation_errors']}")
        
        print("\n" + "="*70)
        print("✓ INVALID PARAMETERS VALIDATION PASSED")
        print("="*70)
        return True


def validate_api_simulate_nonexistent_forecast():
    """Validate /api/forecast/<name>/simulate returns 404 for nonexistent forecast."""
    print("\n" + "="*70)
    print("VALIDATING /api/forecast/<name>/simulate WITH NONEXISTENT FORECAST")
    print("="*70)
    
    with app.test_client() as client:
        print(f"\nSending POST request to /api/forecast/nonexistent_forecast_xyz/simulate")
        
        response = client.post('/api/forecast/nonexistent_forecast_xyz/simulate',
                              json={'param1': 0.5})
        
        print(f"\nStatus Code: {response.status_code}")
        assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"
        print("✓ Status code is 404 (Not Found)")
        
        assert response.is_json, "Response should be JSON"
        print("✓ Response is JSON")
        
        data = response.get_json()
        print(f"\nResponse data: {json.dumps(data, indent=2)}")
        
        assert 'error' in data, "Missing 'error' field"
        assert data['error'] == 'Forecast not found', f"Expected error='Forecast not found', got '{data['error']}'"
        print("✓ error field is 'Forecast not found'")
        
        print("\n" + "="*70)
        print("✓ NONEXISTENT FORECAST VALIDATION PASSED")
        print("="*70)
        return True


def validate_api_simulate_empty_params():
    """Validate /api/forecast/<name>/simulate handles empty parameters (uses defaults)."""
    print("\n" + "="*70)
    print("VALIDATING /api/forecast/<name>/simulate WITH EMPTY PARAMETERS")
    print("="*70)
    
    with app.test_client() as client:
        print(f"\nSending POST request with empty parameters (should use defaults)")
        
        response = client.post('/api/forecast/us_recession_2025/simulate',
                              json={})
        
        print(f"\nStatus Code: {response.status_code}")
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        print("✓ Status code is 200")
        
        assert response.is_json, "Response should be JSON"
        print("✓ Response is JSON")
        
        data = response.get_json()
        print(f"\nResponse data: {json.dumps(data, indent=2)}")
        
        assert 'probability' in data, "Missing 'probability' field"
        probability = data['probability']
        assert 0.0 <= probability <= 1.0, f"Probability {probability} not in [0, 1]"
        print(f"✓ probability is valid: {probability}")
        
        print("\n" + "="*70)
        print("✓ EMPTY PARAMETERS VALIDATION PASSED")
        print("="*70)
        return True


def main():
    """Run all API endpoint validations."""
    print("\n" + "="*70)
    print("API ENDPOINTS VALIDATION SUITE")
    print("="*70)
    print("\nThis script validates the following API endpoints:")
    print("  1. GET /api/forecasts - List all forecasts with metadata")
    print("  2. POST /api/forecast/<name>/simulate - Simulate with parameters")
    print("     - Valid parameters")
    print("     - Invalid parameters (validation)")
    print("     - Nonexistent forecast (404)")
    print("     - Empty parameters (defaults)")
    
    try:
        # Run all validations
        validate_api_forecasts()
        validate_api_simulate_valid_params()
        validate_api_simulate_invalid_params()
        validate_api_simulate_nonexistent_forecast()
        validate_api_simulate_empty_params()
        
        print("\n" + "="*70)
        print("✓✓✓ ALL API ENDPOINT VALIDATIONS PASSED ✓✓✓")
        print("="*70)
        print("\nSummary:")
        print("  ✓ /api/forecasts returns correct JSON structure")
        print("  ✓ /api/forecast/<name>/simulate works with valid parameters")
        print("  ✓ /api/forecast/<name>/simulate validates parameters")
        print("  ✓ /api/forecast/<name>/simulate handles nonexistent forecasts")
        print("  ✓ /api/forecast/<name>/simulate handles empty parameters")
        print("\n" + "="*70)
        
        return 0
    
    except AssertionError as e:
        print("\n" + "="*70)
        print("✗✗✗ VALIDATION FAILED ✗✗✗")
        print("="*70)
        print(f"\nError: {e}")
        return 1
    
    except Exception as e:
        print("\n" + "="*70)
        print("✗✗✗ UNEXPECTED ERROR ✗✗✗")
        print("="*70)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
