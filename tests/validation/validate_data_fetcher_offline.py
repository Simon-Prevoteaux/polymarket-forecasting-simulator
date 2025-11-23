"""
Offline validation script for data fetching utilities.

This script validates the data fetcher functionality without requiring a real API key.
It tests caching, error handling, and the overall structure.

Run with: python tests/validate_data_fetcher_offline.py
"""

import os
import sys
import time
from unittest.mock import patch, Mock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data_fetcher import (
    fetch_fred_data,
    cache_data,
    get_cached_data,
    clear_cache,
    DataFetchError,
    RateLimitError
)


def test_cache_functionality():
    """Test cache storage, retrieval, and expiration."""
    print("=" * 60)
    print("Test 1: Cache Functionality")
    print("=" * 60)
    
    # Clear any existing cache
    clear_cache()
    print("✓ Cache cleared")
    
    # Test basic caching
    test_data = {
        'observations': [
            {'date': '2024-01-01', 'value': '3.7'},
            {'date': '2024-02-01', 'value': '3.8'}
        ]
    }
    
    cache_data('test_series', test_data, ttl=3600)
    print("✓ Data cached with 1 hour TTL")
    
    # Retrieve cached data
    retrieved = get_cached_data('test_series')
    if retrieved == test_data:
        print("✓ Cached data retrieved successfully")
    else:
        print("✗ Cached data doesn't match!")
        return False
    
    # Test cache expiration
    cache_data('expire_test', {'value': 1}, ttl=1)
    print("✓ Data cached with 1 second TTL")
    
    time.sleep(1.1)
    expired = get_cached_data('expire_test')
    if expired is None:
        print("✓ Cache correctly expired after TTL")
    else:
        print("✗ Cache didn't expire!")
        return False
    
    # Test cache miss
    missing = get_cached_data('nonexistent')
    if missing is None:
        print("✓ Cache miss returns None")
    else:
        print("✗ Cache miss should return None!")
        return False
    
    clear_cache()
    print("✓ Cache cleared successfully")
    
    return True


def test_error_handling():
    """Test error handling for various failure scenarios."""
    print("\n" + "=" * 60)
    print("Test 2: Error Handling")
    print("=" * 60)
    
    # Test missing API key
    with patch.dict('os.environ', {}, clear=True):
        try:
            fetch_fred_data('UNRATE')
            print("✗ Should have raised ValueError for missing API key!")
            return False
        except ValueError as e:
            if "API key is required" in str(e):
                print("✓ Correctly raises ValueError for missing API key")
            else:
                print(f"✗ Wrong error message: {e}")
                return False
    
    # Test rate limit error
    with patch('lib.data_fetcher.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        try:
            fetch_fred_data('UNRATE', api_key='test_key')
            print("✗ Should have raised RateLimitError!")
            return False
        except RateLimitError as e:
            if "rate limit" in str(e).lower():
                print("✓ Correctly raises RateLimitError for 429 status")
            else:
                print(f"✗ Wrong error message: {e}")
                return False
    
    # Test network error with retries
    with patch('lib.data_fetcher.requests.get') as mock_get:
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
        
        try:
            fetch_fred_data('UNRATE', api_key='test_key')
            print("✗ Should have raised DataFetchError!")
            return False
        except DataFetchError as e:
            if "Network connection error" in str(e):
                print("✓ Correctly raises DataFetchError for network errors")
                if mock_get.call_count == 3:
                    print("✓ Correctly retries 3 times before failing")
                else:
                    print(f"⚠️  Expected 3 retries, got {mock_get.call_count}")
            else:
                print(f"✗ Wrong error message: {e}")
                return False
    
    return True


def test_successful_fetch_with_caching():
    """Test successful data fetch and caching behavior."""
    print("\n" + "=" * 60)
    print("Test 3: Successful Fetch with Caching")
    print("=" * 60)
    
    clear_cache()
    
    mock_data = {
        'observations': [
            {'date': '2024-01-01', 'value': '3.7'},
            {'date': '2024-02-01', 'value': '3.8'},
            {'date': '2024-03-01', 'value': '3.9'}
        ]
    }
    
    with patch('lib.data_fetcher.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        
        # First fetch should hit API
        start_time = time.time()
        data1 = fetch_fred_data('UNRATE', api_key='test_key')
        elapsed1 = time.time() - start_time
        
        if data1 == mock_data:
            print(f"✓ First fetch successful ({elapsed1:.4f}s)")
        else:
            print("✗ First fetch returned wrong data!")
            return False
        
        if mock_get.call_count == 1:
            print("✓ API called once for first fetch")
        else:
            print(f"✗ Expected 1 API call, got {mock_get.call_count}")
            return False
        
        # Second fetch should use cache
        start_time = time.time()
        data2 = fetch_fred_data('UNRATE', api_key='test_key')
        elapsed2 = time.time() - start_time
        
        if data2 == mock_data:
            print(f"✓ Second fetch successful ({elapsed2:.4f}s)")
        else:
            print("✗ Second fetch returned wrong data!")
            return False
        
        if mock_get.call_count == 1:
            print("✓ API not called for cached data")
        else:
            print(f"✗ Expected 1 total API call, got {mock_get.call_count}")
            return False
        
        if elapsed2 < elapsed1:
            print("✓ Cached fetch faster than API fetch")
        else:
            print("⚠️  Cached fetch not faster (may be due to mocking)")
    
    clear_cache()
    return True


def test_date_parameters():
    """Test that date parameters are correctly passed to API."""
    print("\n" + "=" * 60)
    print("Test 4: Date Parameters")
    print("=" * 60)
    
    with patch('lib.data_fetcher.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'observations': []}
        mock_get.return_value = mock_response
        
        fetch_fred_data(
            'UNRATE',
            start_date='2024-01-01',
            end_date='2024-12-31',
            api_key='test_key'
        )
        
        # Check that parameters were passed correctly
        call_args = mock_get.call_args
        params = call_args[1]['params']
        
        if params['series_id'] == 'UNRATE':
            print("✓ Series ID passed correctly")
        else:
            print(f"✗ Wrong series ID: {params['series_id']}")
            return False
        
        if params['observation_start'] == '2024-01-01':
            print("✓ Start date passed correctly")
        else:
            print(f"✗ Wrong start date: {params.get('observation_start')}")
            return False
        
        if params['observation_end'] == '2024-12-31':
            print("✓ End date passed correctly")
        else:
            print(f"✗ Wrong end date: {params.get('observation_end')}")
            return False
        
        if params['file_type'] == 'json':
            print("✓ File type set to JSON")
        else:
            print(f"✗ Wrong file type: {params.get('file_type')}")
            return False
    
    return True


def main():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print("Data Fetcher Offline Validation")
    print("=" * 60 + "\n")
    
    tests = [
        test_cache_functionality,
        test_error_handling,
        test_successful_fetch_with_caching,
        test_date_parameters
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✓ All validation tests passed!")
        print("\nNote: To test with real FRED API, run:")
        print("  export FRED_API_KEY='your_key'")
        print("  python tests/validate_data_fetcher.py")
        return True
    else:
        print("\n✗ Some tests failed!")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
