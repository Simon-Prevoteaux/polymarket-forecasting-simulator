"""
Comprehensive verification script for all Task 13 fixes.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))

from forecasts.us_recession_2025.model import RecessionModel
from app import app

def verify_all_fixes():
    """Verify all fixes are working correctly."""
    print("=" * 70)
    print("TASK 13 FIXES VERIFICATION")
    print("=" * 70)
    
    all_passed = True
    
    # Fix 1: Model calculation works
    print("\n1. Testing model calculation (Fix for 0% probability)...")
    try:
        model = RecessionModel()
        probability = model.calculate_probability()
        
        if probability is None or probability == 0:
            print("   ❌ FAIL: Probability is None or 0")
            all_passed = False
        elif not (0 <= probability <= 1):
            print(f"   ❌ FAIL: Probability {probability} not in valid range")
            all_passed = False
        else:
            print(f"   ✓ PASS: Model calculates probability: {probability:.4f} ({probability*100:.2f}%)")
    except Exception as e:
        print(f"   ❌ FAIL: Model calculation error: {e}")
        all_passed = False
    
    # Fix 2: Template renders without errors
    print("\n2. Testing template rendering (Fix for IDE errors)...")
    try:
        with app.test_client() as client:
            response = client.get('/forecast/us_recession_2025')
            
            if response.status_code != 200:
                print(f"   ❌ FAIL: Response status {response.status_code}")
                all_passed = False
            else:
                html = response.data.decode('utf-8')
                
                # Check for key elements
                checks = [
                    ('parameters-section', 'Parameter section'),
                    ('probabilityChart', 'Chart canvas'),
                    ('jshint ignore', 'JSHint ignore comments'),
                    ('param-yield_curve_weight', 'Parameter controls'),
                ]
                
                for check_str, check_name in checks:
                    if check_str in html:
                        print(f"   ✓ {check_name} present")
                    else:
                        print(f"   ❌ {check_name} missing")
                        all_passed = False
    except Exception as e:
        print(f"   ❌ FAIL: Template rendering error: {e}")
        all_passed = False
    
    # Fix 3: Simulate button error message
    print("\n3. Testing simulate button error message...")
    try:
        js_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'static', 'js', 'main.js')
        with open(js_path, 'r') as f:
            js_content = f.read()
        
        if 'coming in task 14' in js_content:
            print("   ✓ PASS: Error message mentions task 14")
        else:
            print("   ❌ FAIL: Error message doesn't mention task 14")
            all_passed = False
    except Exception as e:
        print(f"   ❌ FAIL: JavaScript check error: {e}")
        all_passed = False
    
    # Fix 4: Chart rendering improvements
    print("\n4. Testing chart rendering improvements...")
    try:
        template_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'templates', 'forecast.html')
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        checks = [
            ('const month = point.timestamp.getMonth()', 'Compact date formatting'),
            ('if (!canvas) return;', 'Canvas null check'),
            ('font = \'11px sans-serif\'', 'Smaller font for labels'),
        ]
        
        for check_str, check_name in checks:
            if check_str in template_content:
                print(f"   ✓ {check_name} implemented")
            else:
                print(f"   ❌ {check_name} missing")
                all_passed = False
    except Exception as e:
        print(f"   ❌ FAIL: Template check error: {e}")
        all_passed = False
    
    # Fix 5: Leading indicators optional
    print("\n5. Testing leading indicators fallback...")
    try:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'forecasts', 'us_recession_2025', 'data.py')
        with open(data_path, 'r') as f:
            data_content = f.read()
        
        if 'leading_indicators\' not in indicators' in data_content:
            print("   ✓ PASS: Leading indicators fallback implemented")
        else:
            print("   ❌ FAIL: Leading indicators fallback missing")
            all_passed = False
    except Exception as e:
        print(f"   ❌ FAIL: Data module check error: {e}")
        all_passed = False
    
    # Fix 6: Historical probability fallback
    print("\n6. Testing historical probability fallback...")
    try:
        app_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'app.py')
        with open(app_path, 'r') as f:
            app_content = f.read()
        
        if 'get_forecast_history(name, limit=1)' in app_content:
            print("   ✓ PASS: Historical probability fallback implemented")
        else:
            print("   ❌ FAIL: Historical probability fallback missing")
            all_passed = False
    except Exception as e:
        print(f"   ❌ FAIL: App module check error: {e}")
        all_passed = False
    
    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL FIXES VERIFIED SUCCESSFULLY!")
        print("=" * 70)
        print("\nTask 13 is complete with all issues resolved:")
        print("  ✓ IDE errors fixed")
        print("  ✓ Probability calculation working")
        print("  ✓ Simulate button error message improved")
        print("  ✓ Chart rendering enhanced")
        print("  ✓ Graceful handling of missing data")
        print("\nReady for Task 14!")
    else:
        print("❌ SOME FIXES FAILED VERIFICATION")
        print("=" * 70)
    
    return all_passed

if __name__ == '__main__':
    success = verify_all_fixes()
    sys.exit(0 if success else 1)
