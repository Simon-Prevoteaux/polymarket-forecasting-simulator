"""
Validation script for error handling and logging.

Tests:
1. Accessing non-existent forecast (should show 404)
2. Invalid parameters (should show validation error)
3. Simulated data fetching error (graceful handling)
4. Logging functionality
"""

import sys
import os
import json
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_404_error():
    """Test that accessing a non-existent forecast returns 404."""
    print("\n" + "=" * 60)
    print("TEST 1: 404 Error Handling")
    print("=" * 60)
    
    base_url = "http://localhost:5001"
    
    # Test non-existent forecast page
    print("\n1. Testing non-existent forecast page...")
    response = requests.get(f"{base_url}/forecast/nonexistent_forecast")
    
    if response.status_code == 404:
        print("✓ Correctly returned 404 status code")
        if "not found" in response.text.lower() or "does not exist" in response.text.lower():
            print("✓ Error page contains helpful message")
        else:
            print("✗ Error page missing helpful message")
    else:
        print(f"✗ Expected 404, got {response.status_code}")
    
    # Test API endpoint with non-existent forecast
    print("\n2. Testing API endpoint with non-existent forecast...")
    response = requests.post(
        f"{base_url}/api/forecast/nonexistent_forecast/simulate",
        json={"param": "value"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 404:
        print("✓ API correctly returned 404 status code")
        try:
            data = response.json()
            if 'error' in data:
                print(f"✓ API error response: {data['error']}")
            else:
                print("✗ API response missing 'error' field")
        except json.JSONDecodeError:
            print("✗ API response is not valid JSON")
    else:
        print(f"✗ Expected 404, got {response.status_code}")


def test_invalid_parameters():
    """Test that invalid parameters return validation errors."""
    print("\n" + "=" * 60)
    print("TEST 2: Invalid Parameter Handling")
    print("=" * 60)
    
    base_url = "http://localhost:5001"
    
    # Test with invalid parameter values
    print("\n1. Testing with out-of-range parameter values...")
    invalid_params = {
        "yield_curve_weight": 2.0,  # Should be between 0 and 1
        "unemployment_weight": -0.5  # Should be non-negative
    }
    
    response = requests.post(
        f"{base_url}/api/forecast/us_recession_2025/simulate",
        json=invalid_params,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 400:
        print("✓ Correctly returned 400 status code for invalid parameters")
        try:
            data = response.json()
            if 'error' in data:
                print(f"✓ Error message: {data['error']}")
                if 'message' in data:
                    print(f"  Details: {data['message']}")
            else:
                print("✗ Response missing 'error' field")
        except json.JSONDecodeError:
            print("✗ Response is not valid JSON")
    else:
        print(f"✗ Expected 400, got {response.status_code}")
        print(f"  Response: {response.text[:200]}")
    
    # Test with missing request body
    print("\n2. Testing with missing request body...")
    response = requests.post(
        f"{base_url}/api/forecast/us_recession_2025/simulate",
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 400:
        print("✓ Correctly returned 400 status code for missing body")
    else:
        print(f"✗ Expected 400, got {response.status_code}")


def test_logging():
    """Test that logging is working correctly."""
    print("\n" + "=" * 60)
    print("TEST 3: Logging Functionality")
    print("=" * 60)
    
    logs_dir = Path(__file__).parent.parent / "logs"
    
    print(f"\n1. Checking logs directory: {logs_dir}")
    if logs_dir.exists():
        print("✓ Logs directory exists")
        
        # List log files
        log_files = list(logs_dir.glob("*.log"))
        if log_files:
            print(f"✓ Found {len(log_files)} log file(s):")
            for log_file in log_files:
                size = log_file.stat().st_size
                print(f"  - {log_file.name} ({size} bytes)")
                
                # Check if log file has recent content
                if size > 0:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"    Last entry: {lines[-1].strip()[:80]}...")
        else:
            print("✗ No log files found")
    else:
        print("✗ Logs directory does not exist")
    
    # Check application log specifically
    print("\n2. Checking application.log...")
    app_log = logs_dir / "application.log"
    if app_log.exists():
        print("✓ application.log exists")
        with open(app_log, 'r') as f:
            lines = f.readlines()
            print(f"  Total lines: {len(lines)}")
            
            # Check for key log messages
            log_content = ''.join(lines)
            if "Application Started" in log_content:
                print("✓ Contains application startup message")
            if "ERROR" in log_content or "WARNING" in log_content:
                print("✓ Contains error/warning messages")
    else:
        print("✗ application.log does not exist")


def test_graceful_degradation():
    """Test that the application handles errors gracefully."""
    print("\n" + "=" * 60)
    print("TEST 4: Graceful Error Handling")
    print("=" * 60)
    
    base_url = "http://localhost:5001"
    
    # Test that home page still works even if one forecast fails
    print("\n1. Testing home page resilience...")
    response = requests.get(f"{base_url}/")
    
    if response.status_code == 200:
        print("✓ Home page loads successfully")
        if "forecast" in response.text.lower():
            print("✓ Home page contains forecast information")
    else:
        print(f"✗ Home page returned {response.status_code}")
    
    # Test API forecasts endpoint
    print("\n2. Testing API forecasts endpoint...")
    response = requests.get(f"{base_url}/api/forecasts")
    
    if response.status_code == 200:
        print("✓ API forecasts endpoint works")
        try:
            data = response.json()
            if isinstance(data, list):
                print(f"✓ Returns list of {len(data)} forecast(s)")
            else:
                print("✗ Response is not a list")
        except json.JSONDecodeError:
            print("✗ Response is not valid JSON")
    else:
        print(f"✗ API endpoint returned {response.status_code}")


def main():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print("ERROR HANDLING AND LOGGING VALIDATION")
    print("=" * 60)
    print("\nNOTE: Flask application must be running on http://localhost:5001")
    print("Start it with: python web/app.py")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5001/", timeout=2)
        print("✓ Flask application is running")
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Flask application is not running!")
        print("Please start it with: python web/app.py")
        return 1
    except requests.exceptions.Timeout:
        print("\n✗ ERROR: Flask application is not responding!")
        return 1
    
    # Run tests
    try:
        test_404_error()
        test_invalid_parameters()
        test_logging()
        test_graceful_degradation()
        
        print("\n" + "=" * 60)
        print("VALIDATION COMPLETE")
        print("=" * 60)
        print("\nReview the results above to ensure all error handling")
        print("and logging features are working correctly.")
        
        return 0
    
    except Exception as e:
        print(f"\n✗ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
