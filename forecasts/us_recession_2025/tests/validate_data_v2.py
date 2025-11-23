"""
Validation script for data_v2.py

Tests the enhanced data fetcher with real API calls.
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from forecasts.us_recession_2025.data_v2 import fetch_economic_indicators_v2


def validate_current_data():
    """Test fetching current data."""
    print("=" * 60)
    print("Testing fetch_economic_indicators_v2 with current data")
    print("=" * 60)
    
    try:
        indicators = fetch_economic_indicators_v2(lookback_days=365)
        
        print("\n✓ Successfully fetched indicators")
        print(f"\nAs of date: {indicators['as_of_date']}")
        
        # V1 indicators
        print("\n--- V1 Indicators ---")
        v1_indicators = ['yield_curve', 'unemployment', 'gdp', 'consumer_confidence', 
                        'leading_indicators', 'jobless_claims']
        for name in v1_indicators:
            value = indicators.get(name)
            timestamp = indicators['timestamps'].get(name)
            print(f"{name:25s}: {value:10.2f} (as of {timestamp})")
        
        # V2 indicators
        print("\n--- V2 Indicators (New) ---")
        v2_indicators = ['credit_spread', 'housing_starts', 'manufacturing_pmi',
                        'retail_sales', 'oil_price', 'vix']
        for name in v2_indicators:
            value = indicators.get(name)
            timestamp = indicators['timestamps'].get(name)
            print(f"{name:25s}: {value:10.2f} (as of {timestamp})")
        
        print("\n✓ All indicators fetched successfully")
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def validate_historical_data():
    """Test fetching historical data with as_of_date parameter."""
    print("\n" + "=" * 60)
    print("Testing fetch_economic_indicators_v2 with historical data")
    print("=" * 60)
    
    # Test with a date 1 year ago
    historical_date = datetime.now() - timedelta(days=365)
    print(f"\nFetching data as of: {historical_date.strftime('%Y-%m-%d')}")
    
    try:
        indicators = fetch_economic_indicators_v2(
            lookback_days=365,
            as_of_date=historical_date
        )
        
        print("\n✓ Successfully fetched historical indicators")
        print(f"\nAs of date: {indicators['as_of_date']}")
        
        # Verify no future data
        as_of_dt = datetime.strptime(indicators['as_of_date'], '%Y-%m-%d')
        
        print("\n--- Checking temporal consistency ---")
        all_valid = True
        for name, timestamp in indicators['timestamps'].items():
            ts_dt = datetime.strptime(timestamp, '%Y-%m-%d')
            if ts_dt > as_of_dt:
                print(f"✗ {name}: timestamp {timestamp} is after as_of_date {indicators['as_of_date']}")
                all_valid = False
            else:
                print(f"✓ {name}: {timestamp} <= {indicators['as_of_date']}")
        
        if all_valid:
            print("\n✓ All timestamps are on or before as_of_date (no future data)")
        else:
            print("\n✗ Some timestamps are after as_of_date (future data leak!)")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def validate_missing_indicator_handling():
    """Test that missing indicators are handled with neutral defaults."""
    print("\n" + "=" * 60)
    print("Testing missing indicator handling")
    print("=" * 60)
    
    try:
        # Fetch with very short lookback to potentially miss some indicators
        indicators = fetch_economic_indicators_v2(lookback_days=7)
        
        print("\n✓ Function completed without crashing")
        
        # Check that all expected indicators are present
        expected_indicators = [
            'yield_curve', 'unemployment', 'gdp', 'consumer_confidence',
            'leading_indicators', 'jobless_claims',
            'credit_spread', 'housing_starts', 'manufacturing_pmi',
            'retail_sales', 'oil_price', 'vix'
        ]
        
        missing = []
        for name in expected_indicators:
            if name not in indicators:
                missing.append(name)
        
        if missing:
            print(f"\n✗ Missing indicators: {missing}")
            return False
        else:
            print("\n✓ All expected indicators present (with defaults if needed)")
            return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def main():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print("DATA_V2.PY VALIDATION SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: Current data
    results.append(("Current data fetch", validate_current_data()))
    
    # Test 2: Historical data
    results.append(("Historical data fetch", validate_historical_data()))
    
    # Test 3: Missing indicator handling
    results.append(("Missing indicator handling", validate_missing_indicator_handling()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All validation tests passed!")
        return 0
    else:
        print("\n✗ Some validation tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
