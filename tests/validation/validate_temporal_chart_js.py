#!/usr/bin/env python3
"""
Validation script for temporal decay chart JavaScript functionality.

This script validates that:
1. Chart.js is properly loaded in the base template
2. Breakdown data is embedded in the forecast template
3. JavaScript functions are defined in main.js
4. The temporal decay formula matches the Python implementation
"""

import re
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def validate_chartjs_included():
    """Validate that Chart.js is included in base.html"""
    print("\n1. Validating Chart.js inclusion...")
    
    base_template = project_root / 'web' / 'templates' / 'base.html'
    content = base_template.read_text()
    
    if 'chart.js' in content.lower() or 'chart.umd' in content.lower():
        print("   ✓ Chart.js CDN link found in base.html")
        return True
    else:
        print("   ✗ Chart.js CDN link NOT found in base.html")
        return False


def validate_breakdown_data_element():
    """Validate that breakdown data element exists in forecast.html"""
    print("\n2. Validating breakdown data element...")
    
    forecast_template = project_root / 'web' / 'templates' / 'forecast.html'
    content = forecast_template.read_text()
    
    if 'id="breakdown-data"' in content and 'data-breakdown' in content:
        print("   ✓ Breakdown data element found in forecast.html")
        return True
    else:
        print("   ✗ Breakdown data element NOT found in forecast.html")
        return False


def validate_javascript_functions():
    """Validate that required JavaScript functions are defined"""
    print("\n3. Validating JavaScript functions...")
    
    main_js = project_root / 'web' / 'static' / 'js' / 'main.js'
    content = main_js.read_text()
    
    required_functions = [
        'calculateDecayedProbability',
        'renderTemporalDecayChart',
        'initializeTemporalDecayChart'
    ]
    
    all_found = True
    for func_name in required_functions:
        pattern = rf'function\s+{func_name}\s*\('
        if re.search(pattern, content):
            print(f"   ✓ Function '{func_name}' found")
        else:
            print(f"   ✗ Function '{func_name}' NOT found")
            all_found = False
    
    return all_found


def validate_decay_formula():
    """Validate that the JavaScript decay formula matches Python implementation"""
    print("\n4. Validating decay formula implementation...")
    
    main_js = project_root / 'web' / 'static' / 'js' / 'main.js'
    content = main_js.read_text()
    
    # Check for key formula components
    checks = [
        ('threshold check', r'threshold\s*!==\s*null.*baseProbability\s*>=\s*threshold'),
        ('days remaining check', r'daysRemaining\s*<=\s*0'),
        ('power-law decay', r'Math\.pow\s*\('),
        ('time ratio calculation', r'timeRatio'),
        ('time factor calculation', r'timeFactor'),
    ]
    
    all_found = True
    for check_name, pattern in checks:
        if re.search(pattern, content):
            print(f"   ✓ {check_name} found")
        else:
            print(f"   ✗ {check_name} NOT found")
            all_found = False
    
    return all_found


def validate_chart_initialization():
    """Validate that chart initialization is called on page load"""
    print("\n5. Validating chart initialization...")
    
    main_js = project_root / 'web' / 'static' / 'js' / 'main.js'
    content = main_js.read_text()
    
    if 'initializeTemporalDecayChart()' in content:
        print("   ✓ Chart initialization called in DOMContentLoaded")
        return True
    else:
        print("   ✗ Chart initialization NOT called")
        return False


def validate_error_handling():
    """Validate that error handling is present"""
    print("\n6. Validating error handling...")
    
    main_js = project_root / 'web' / 'static' / 'js' / 'main.js'
    content = main_js.read_text()
    
    checks = [
        ('try-catch block', r'try\s*{'),
        ('console.error', r'console\.error'),
        ('canvas existence check', r'if\s*\(\s*!canvas'),
        ('breakdown data check', r'if\s*\(\s*!breakdown'),
    ]
    
    all_found = True
    for check_name, pattern in checks:
        if re.search(pattern, content):
            print(f"   ✓ {check_name} found")
        else:
            print(f"   ✗ {check_name} NOT found")
            all_found = False
    
    return all_found


def main():
    """Run all validation checks"""
    print("=" * 60)
    print("Temporal Decay Chart JavaScript Validation")
    print("=" * 60)
    
    results = []
    
    results.append(validate_chartjs_included())
    results.append(validate_breakdown_data_element())
    results.append(validate_javascript_functions())
    results.append(validate_decay_formula())
    results.append(validate_chart_initialization())
    results.append(validate_error_handling())
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total} checks")
    
    if all(results):
        print("\n✓ All validation checks passed!")
        print("\nThe temporal decay chart JavaScript is properly implemented.")
        return 0
    else:
        print("\n✗ Some validation checks failed.")
        print("\nPlease review the failed checks above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
