"""
Validation script for data fetching utilities.

This script tests the data fetcher with real FRED API calls.
Requires FRED_API_KEY environment variable to be set.

Run with: python tests/validate_data_fetcher.py
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data_fetcher import (
    fetch_fred_data,
    get_cached_data,
    clear_cache,
    DataFetchError,
    RateLimitError
)


def test_real_fred_api():
    """Test fetching real data from FRED API."""
    print("=" * 60)
    print("Testing FRED API Data Fetching")
    print("=" * 60)
    
    # Check for API key
    api_key = os.environ.get('FRED_API_KEY')
    if not api_key:
        print("\n⚠️  FRED_API_KEY environment variable not set.")
        print("To run this validation, get a free API key from:")
        print("https://fred.stlouisfed.org/docs/api/api_key.html")
        print("\nThen set it with: export FRED_API_KEY='your_key_here'")
        return False
    
    print(f"\n✓ API key found: {api_key[:8]}...")
    
    # Clear cache to ensure fresh fetch
    clear_cache()
    print("✓ Cache cleared")
    
    # Test 1: Fetch unemployment rate data
    print("\n" + "-" * 60)
    print("Test 1: Fetching unemployment rate (UNRATE)")
    print("-" * 60)
    
    try:
        start_time = time.time()
        data = fetch_fred_data(
            'UNRATE',
            start_date='2024-01-01',
            end_date='2024-12-31',
            api_key=api_key
        )
        elapsed = time.time() - start_time
        
        print(f"✓ Data fetched successfully in {elapsed:.2f}s")
        print(f"  Observations: {len(data.get('observations', []))}")
        
        if data.get('observations'):
            latest = data['observations'][-1]
            print(f"  Latest data point: {latest.get('date')} = {latest.get('value')}")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 2: Verify caching works
    print("\n" + "-" * 60)
    print("Test 2: Verifying cache functionality")
    print("-" * 60)
    
    try:
        start_time = time.time()
        cached_data = fetch_fred_data(
            'UNRATE',
            start_date='2024-01-01',
            end_date='2024-12-31',
            api_key=api_key
        )
        elapsed = time.time() - start_time
        
        print(f"✓ Cached data retrieved in {elapsed:.2f}s")
        
        if elapsed < 0.1:
            print("  ✓ Cache significantly faster than API call")
        else:
            print("  ⚠️  Cache may not be working (took longer than expected)")
        
        if data == cached_data:
            print("  ✓ Cached data matches original data")
        else:
            print("  ✗ Cached data doesn't match!")
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 3: Test with different series
    print("\n" + "-" * 60)
    print("Test 3: Fetching GDP data (GDP)")
    print("-" * 60)
    
    try:
        gdp_data = fetch_fred_data(
            'GDP',
            start_date='2023-01-01',
            api_key=api_key
        )
        
        print(f"✓ GDP data fetched successfully")
        print(f"  Observations: {len(gdp_data.get('observations', []))}")
        
        if gdp_data.get('observations'):
            latest = gdp_data['observations'][-1]
            print(f"  Latest data point: {latest.get('date')} = {latest.get('value')}")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 4: Test error handling with invalid series
    print("\n" + "-" * 60)
    print("Test 4: Testing error handling with invalid series ID")
    print("-" * 60)
    
    try:
        invalid_data = fetch_fred_data(
            'INVALID_SERIES_ID_12345',
            api_key=api_key
        )
        print("✗ Should have raised an error for invalid series!")
        return False
    
    except DataFetchError as e:
        print(f"✓ Correctly raised DataFetchError: {str(e)[:80]}...")
    
    except Exception as e:
        print(f"✗ Unexpected error type: {type(e).__name__}: {e}")
        return False
    
    # Test 5: Verify multiple series can be cached independently
    print("\n" + "-" * 60)
    print("Test 5: Testing independent caching of multiple series")
    print("-" * 60)
    
    try:
        # Fetch yield curve data
        yield_data = fetch_fred_data('T10Y2Y', api_key=api_key)
        print(f"✓ Yield curve data fetched")
        
        # Verify both are cached independently
        cached_unrate = get_cached_data('fred_UNRATE_2024-01-01_2024-12-31')
        cached_gdp = get_cached_data('fred_GDP_2023-01-01_None')
        cached_yield = get_cached_data('fred_T10Y2Y_None_None')
        
        if cached_unrate and cached_gdp and cached_yield:
            print("✓ All three series cached independently")
        else:
            print("⚠️  Some cache entries missing")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All validation tests passed!")
    print("=" * 60)
    return True


if __name__ == '__main__':
    success = test_real_fred_api()
    sys.exit(0 if success else 1)
