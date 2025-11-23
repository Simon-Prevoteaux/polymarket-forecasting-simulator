#!/usr/bin/env python3
"""
Validation script for UI styling and appearance.
Checks that all CSS and JavaScript files exist and are properly structured.
"""

import os
import sys

def validate_css_file():
    """Validate that the CSS file exists and contains required styles."""
    css_path = 'web/static/css/style.css'
    
    if not os.path.exists(css_path):
        print(f"❌ CSS file not found: {css_path}")
        return False
    
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    # Check for key style sections
    required_sections = [
        '/* Reset and Base Styles */',
        '/* Sidebar Styles */',
        '/* Main Content Styles */',
        '/* Forecast Page Styles */',
        '/* Parameters Section */',
        '/* Responsive Design */',
        '.sidebar',
        '.main-content',
        '.probability-value',
        '.parameter-control',
        '.btn-primary',
        '.btn-secondary',
        '@media (max-width: 768px)',
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in css_content:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"❌ CSS file missing required sections:")
        for section in missing_sections:
            print(f"   - {section}")
        return False
    
    print(f"✅ CSS file exists and contains all required sections")
    print(f"   File size: {len(css_content)} bytes")
    return True

def validate_js_file():
    """Validate that the JavaScript file exists and contains required functions."""
    js_path = 'web/static/js/main.js'
    
    if not os.path.exists(js_path):
        print(f"❌ JavaScript file not found: {js_path}")
        return False
    
    with open(js_path, 'r') as f:
        js_content = f.read()
    
    # Check for key functions
    required_functions = [
        'initializeParameterControls',
        'resetParameters',
        'simulateParameters',
        'collectParameterValues',
        'formatProbability',
    ]
    
    missing_functions = []
    for func in required_functions:
        if f'function {func}' not in js_content and f'{func}(' not in js_content:
            missing_functions.append(func)
    
    if missing_functions:
        print(f"❌ JavaScript file missing required functions:")
        for func in missing_functions:
            print(f"   - {func}")
        return False
    
    print(f"✅ JavaScript file exists and contains all required functions")
    print(f"   File size: {len(js_content)} bytes")
    return True

def validate_templates():
    """Validate that all template files exist."""
    templates = [
        'web/templates/base.html',
        'web/templates/index.html',
        'web/templates/forecast.html',
        'web/templates/error.html',
    ]
    
    all_exist = True
    for template in templates:
        if os.path.exists(template):
            print(f"✅ Template exists: {template}")
        else:
            print(f"❌ Template missing: {template}")
            all_exist = False
    
    return all_exist

def validate_responsive_design():
    """Validate that responsive design breakpoints are defined."""
    css_path = 'web/static/css/style.css'
    
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    # Check for responsive breakpoints
    breakpoints = [
        '@media (max-width: 768px)',
        '@media (max-width: 480px)',
    ]
    
    found_breakpoints = []
    for breakpoint in breakpoints:
        if breakpoint in css_content:
            found_breakpoints.append(breakpoint)
    
    if len(found_breakpoints) >= 1:
        print(f"✅ Responsive design breakpoints found:")
        for bp in found_breakpoints:
            print(f"   - {bp}")
        return True
    else:
        print(f"❌ No responsive design breakpoints found")
        return False

def validate_animations():
    """Validate that CSS animations are defined."""
    css_path = 'web/static/css/style.css'
    
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    # Check for animations
    animations = ['@keyframes', 'animation:', 'transition:']
    
    found_animations = []
    for anim in animations:
        if anim in css_content:
            found_animations.append(anim)
    
    if found_animations:
        print(f"✅ CSS animations and transitions found")
        return True
    else:
        print(f"⚠️  No CSS animations found (optional)")
        return True  # Not critical

def main():
    """Run all validation checks."""
    print("=" * 60)
    print("UI Styling Validation")
    print("=" * 60)
    print()
    
    results = []
    
    print("1. Validating CSS file...")
    results.append(validate_css_file())
    print()
    
    print("2. Validating JavaScript file...")
    results.append(validate_js_file())
    print()
    
    print("3. Validating template files...")
    results.append(validate_templates())
    print()
    
    print("4. Validating responsive design...")
    results.append(validate_responsive_design())
    print()
    
    print("5. Validating animations...")
    results.append(validate_animations())
    print()
    
    print("=" * 60)
    if all(results):
        print("✅ All UI styling validations passed!")
        print("=" * 60)
        return 0
    else:
        print("❌ Some UI styling validations failed")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
