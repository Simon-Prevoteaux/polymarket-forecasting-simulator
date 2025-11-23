"""
Validation script for parameter adjustment interface.

This script validates that the parameter interface is properly implemented
in the forecast detail page.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forecasts.us_recession_2025.model import RecessionModel


def validate_parameter_interface():
    """Validate that parameter interface components are present."""
    print("=" * 60)
    print("Parameter Adjustment Interface Validation")
    print("=" * 60)
    
    # Test 1: Model provides parameters
    print("\n1. Testing model parameter retrieval...")
    model = RecessionModel()
    params = model.get_parameters()
    
    if not params:
        print("   ❌ FAIL: Model does not provide parameters")
        return False
    
    print(f"   ✓ Model provides {len(params)} parameters")
    
    # Test 2: Parameters have required metadata
    print("\n2. Testing parameter metadata...")
    required_fields = ['name', 'type', 'default', 'min_value', 'max_value', 'description']
    
    for param_name, param_info in params.items():
        missing_fields = [field for field in required_fields if field not in param_info]
        if missing_fields:
            print(f"   ❌ FAIL: Parameter '{param_name}' missing fields: {missing_fields}")
            return False
        print(f"   ✓ Parameter '{param_name}' has all required metadata")
    
    # Test 3: Parameter types are valid
    print("\n3. Testing parameter types...")
    valid_types = ['float', 'int', 'bool', 'select']
    
    for param_name, param_info in params.items():
        param_type = param_info['type']
        if param_type not in valid_types:
            print(f"   ❌ FAIL: Parameter '{param_name}' has invalid type: {param_type}")
            return False
        print(f"   ✓ Parameter '{param_name}' has valid type: {param_type}")
    
    # Test 4: Default values are within bounds
    print("\n4. Testing parameter bounds...")
    
    for param_name, param_info in params.items():
        default = param_info['default']
        min_val = param_info['min_value']
        max_val = param_info['max_value']
        
        if param_info['type'] in ['float', 'int']:
            if min_val is not None and default < min_val:
                print(f"   ❌ FAIL: Parameter '{param_name}' default {default} < min {min_val}")
                return False
            if max_val is not None and default > max_val:
                print(f"   ❌ FAIL: Parameter '{param_name}' default {default} > max {max_val}")
                return False
            print(f"   ✓ Parameter '{param_name}' default is within bounds")
    
    # Test 5: Check template file exists
    print("\n5. Testing template file...")
    template_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'templates', 'forecast.html')
    
    if not os.path.exists(template_path):
        print(f"   ❌ FAIL: Template file not found: {template_path}")
        return False
    
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Check for parameter section
    if 'parameters-section' not in template_content:
        print("   ❌ FAIL: Template missing parameters-section")
        return False
    
    print("   ✓ Template contains parameters-section")
    
    # Check for parameter controls
    if 'parameter-slider' not in template_content:
        print("   ❌ FAIL: Template missing parameter-slider")
        return False
    
    print("   ✓ Template contains parameter-slider")
    
    # Check for reset button
    if 'reset-parameters' not in template_content:
        print("   ❌ FAIL: Template missing reset-parameters button")
        return False
    
    print("   ✓ Template contains reset-parameters button")
    
    # Check for simulate button
    if 'simulate-parameters' not in template_content:
        print("   ❌ FAIL: Template missing simulate-parameters button")
        return False
    
    print("   ✓ Template contains simulate-parameters button")
    
    # Test 6: Check JavaScript file
    print("\n6. Testing JavaScript file...")
    js_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'static', 'js', 'main.js')
    
    if not os.path.exists(js_path):
        print(f"   ❌ FAIL: JavaScript file not found: {js_path}")
        return False
    
    with open(js_path, 'r') as f:
        js_content = f.read()
    
    # Check for required functions
    required_functions = [
        'initializeParameterControls',
        'resetParameters',
        'collectParameterValues',
        'simulateParameters'
    ]
    
    for func_name in required_functions:
        if func_name not in js_content:
            print(f"   ❌ FAIL: JavaScript missing function: {func_name}")
            return False
        print(f"   ✓ JavaScript contains function: {func_name}")
    
    # Test 7: Check CSS file
    print("\n7. Testing CSS file...")
    css_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'static', 'css', 'style.css')
    
    if not os.path.exists(css_path):
        print(f"   ❌ FAIL: CSS file not found: {css_path}")
        return False
    
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    # Check for parameter styles
    required_styles = [
        '.parameters-section',
        '.parameter-slider',
        '.parameter-number',
        '.btn-primary',
        '.btn-secondary',
        '.simulation-result'
    ]
    
    for style_name in required_styles:
        if style_name not in css_content:
            print(f"   ❌ FAIL: CSS missing style: {style_name}")
            return False
        print(f"   ✓ CSS contains style: {style_name}")
    
    print("\n" + "=" * 60)
    print("✓ All parameter interface validations passed!")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    success = validate_parameter_interface()
    sys.exit(0 if success else 1)
