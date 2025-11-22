"""
Validation script for US Recession 2025 forecast model.

This script validates that:
1. The model can run with current economic data (or mocked data)
2. Probability output is between 0 and 1
3. All indicators are fetched successfully
4. Result is stored in database

Run this script to validate the recession model implementation.
"""

import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from forecasts.us_recession_2025.model import RecessionModel
from lib.database import get_forecast_history


def validate_recession_model():
    """
    Validate the recession model implementation.
    
    Returns:
        bool: True if all validations pass, False otherwise
    """
    print("=" * 70)
    print("VALIDATING US RECESSION 2025 FORECAST MODEL")
    print("=" * 70)
    
    all_passed = True
    
    # Mock the FRED API to avoid requiring an API key for validation
    with patch('forecasts.us_recession_2025.data.fetch_fred_data') as mock_fetch:
        def mock_current_data(series_id, **kwargs):
            """Mock current economic data (realistic 2024 values)."""
            values_map = {
                'T10Y2Y': '0.3',        # Slightly positive yield curve
                'UNRATE': '4.2',        # Low unemployment
                'A191RL1Q225SBEA': '2.8',  # Moderate GDP growth
                'UMCSENT': '78.0',      # Moderate consumer confidence
                'USSLIND': '0.5',       # Slightly positive leading indicators
                'ICSA': '215000'        # Moderate jobless claims
            }
            return {
                'observations': [
                    {'date': '2024-11-01', 'value': values_map.get(series_id, '1.0')}
                ]
            }
        
        mock_fetch.side_effect = mock_current_data
        
        # Test 1: Model initialization
        print("\n[1/4] Testing model initialization...")
        try:
            model = RecessionModel()
            print("✓ Model initialized successfully")
            print(f"  - Name: {model.get_name()}")
            print(f"  - Description: {model.get_description()[:80]}...")
        except Exception as e:
            print(f"✗ Model initialization failed: {e}")
            all_passed = False
            return all_passed
        
        # Test 2: Calculate probability with current data
        print("\n[2/4] Testing probability calculation with current economic data...")
        try:
            probability = model.calculate_probability()
            print(f"✓ Probability calculated: {probability:.4f} ({probability*100:.2f}%)")
            
            # Validate probability is in range [0, 1]
            if 0.0 <= probability <= 1.0:
                print("✓ Probability is within valid range [0, 1]")
            else:
                print(f"✗ Probability {probability} is outside valid range [0, 1]")
                all_passed = False
        except Exception as e:
            print(f"✗ Probability calculation failed: {e}")
            all_passed = False
            return all_passed
        
        # Test 3: Verify all indicators were fetched
        print("\n[3/4] Verifying all indicators were fetched successfully...")
        try:
            if model._last_indicators:
                indicators = model._last_indicators
                required_indicators = [
                    'yield_curve',
                    'unemployment',
                    'gdp',
                    'consumer_confidence',
                    'leading_indicators',
                    'jobless_claims'
                ]
                
                all_present = True
                for indicator in required_indicators:
                    if indicator in indicators:
                        value = indicators[indicator]
                        print(f"✓ {indicator}: {value}")
                    else:
                        print(f"✗ {indicator}: MISSING")
                        all_present = False
                        all_passed = False
                
                if all_present:
                    print("✓ All indicators fetched successfully")
            else:
                print("✗ No indicators found in model")
                all_passed = False
        except Exception as e:
            print(f"✗ Indicator verification failed: {e}")
            all_passed = False
        
        # Test 4: Verify result was stored in database
        print("\n[4/4] Verifying result was stored in database...")
        try:
            history = get_forecast_history('us_recession_2025', limit=1)
            if history:
                latest = history[0]
                print(f"✓ Result stored in database")
                print(f"  - Probability: {latest['probability']:.4f}")
                print(f"  - Timestamp: {latest['calculated_at']}")
                print(f"  - Yield curve: {latest.get('yield_curve_value', 'N/A')}")
                print(f"  - Unemployment: {latest.get('unemployment_rate', 'N/A')}")
                print(f"  - GDP growth: {latest.get('gdp_growth', 'N/A')}")
            else:
                print("✗ No results found in database")
                all_passed = False
        except Exception as e:
            print(f"✗ Database verification failed: {e}")
            all_passed = False
    
    # Test 5: Test with custom parameters
    print("\n[5/5] Testing with custom parameters...")
    with patch('forecasts.us_recession_2025.data.fetch_fred_data') as mock_fetch:
        mock_fetch.side_effect = mock_current_data
        
        try:
            custom_params = {
                'yield_curve_weight': 0.40,
                'unemployment_weight': 0.30,
                'gdp_weight': 0.20,
                'confidence_weight': 0.05,
                'leading_indicators_weight': 0.05,
                'lookback_days': 180
            }
            
            probability_custom = model.calculate_probability(custom_params)
            print(f"✓ Custom parameters accepted")
            print(f"  - Probability with custom weights: {probability_custom:.4f} ({probability_custom*100:.2f}%)")
            
            if 0.0 <= probability_custom <= 1.0:
                print("✓ Custom probability is within valid range [0, 1]")
            else:
                print(f"✗ Custom probability {probability_custom} is outside valid range [0, 1]")
                all_passed = False
        except Exception as e:
            print(f"✗ Custom parameter test failed: {e}")
            all_passed = False
    
    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL VALIDATIONS PASSED")
        print("The recession model is working correctly!")
    else:
        print("✗ SOME VALIDATIONS FAILED")
        print("Please review the errors above.")
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    success = validate_recession_model()
    sys.exit(0 if success else 1)
