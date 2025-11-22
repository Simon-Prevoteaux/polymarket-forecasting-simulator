"""
Quick verification that parameters are rendered correctly in the HTML.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))

from app import app

def verify_rendering():
    """Verify that parameters are rendered in the forecast page."""
    print("Verifying parameter rendering...")
    
    with app.test_client() as client:
        response = client.get('/forecast/us_recession_2025')
        html = response.data.decode('utf-8')
        
        # Check for parameter section
        if 'parameters-section' not in html:
            print("❌ FAIL: parameters-section not found in HTML")
            return False
        print("✓ parameters-section found")
        
        # Check for specific parameters
        expected_params = [
            'yield_curve_weight',
            'unemployment_weight',
            'gdp_weight',
            'confidence_weight',
            'leading_indicators_weight',
            'lookback_days'
        ]
        
        for param in expected_params:
            if f'param-{param}' not in html:
                print(f"❌ FAIL: Parameter {param} not found in HTML")
                return False
            print(f"✓ Parameter {param} found")
        
        # Check for buttons
        if 'reset-parameters' not in html:
            print("❌ FAIL: reset-parameters button not found")
            return False
        print("✓ reset-parameters button found")
        
        if 'simulate-parameters' not in html:
            print("❌ FAIL: simulate-parameters button not found")
            return False
        print("✓ simulate-parameters button found")
        
        # Check for default values
        if '0.35' not in html:  # yield_curve_weight default
            print("❌ FAIL: Default value 0.35 not found")
            return False
        print("✓ Default values found")
        
        print("\n✓ All parameter rendering checks passed!")
        return True

if __name__ == '__main__':
    success = verify_rendering()
    sys.exit(0 if success else 1)
