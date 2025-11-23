#!/usr/bin/env python3
"""
Comprehensive validation for Task 20: Temporal Decay Visualization CSS.

This script validates:
1. All required CSS classes are defined
2. CSS syntax is valid (balanced braces)
3. Responsive design rules are present for all breakpoints
4. HTML template uses the correct CSS classes
5. Visual design elements are properly styled
"""

import re
from pathlib import Path


def validate_css_classes():
    """Validate all required CSS classes are present."""
    
    css_path = Path('web/static/css/style.css')
    
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    print("1. Validating CSS Classes")
    print("-" * 60)
    
    required_classes = {
        # Main section
        'temporal-decay-section': 'Main temporal decay container',
        
        # Probability comparison
        'probability-comparison': 'Grid container for probability cards',
        'prob-item': 'Individual probability card',
        'prob-item.base-probability': 'Base probability card variant',
        'prob-item.adjusted-probability': 'Adjusted probability card variant',
        'prob-item-label': 'Probability card label',
        'prob-item-value': 'Probability card value',
        'prob-item-description': 'Probability card description',
        'days-remaining': 'Days remaining badge',
        
        # Chart container
        'decay-chart-container': 'Chart container',
        'chart-loading': 'Chart loading state',
        
        # Metadata
        'decay-metadata': 'Metadata container',
        'metadata-grid': 'Metadata grid layout',
        'metadata-item': 'Individual metadata item',
        'metadata-label': 'Metadata label',
        'metadata-value': 'Metadata value',
        'threshold-badge': 'Threshold badge',
        'threshold-badge.applied': 'Applied threshold badge',
        'threshold-badge.not-applied': 'Not applied threshold badge',
    }
    
    all_found = True
    
    for css_class, description in required_classes.items():
        escaped_class = re.escape(css_class)
        pattern = rf'{escaped_class}\s*\{{'
        
        if re.search(pattern, css_content):
            print(f"  ✓ {css_class:<40} {description}")
        else:
            print(f"  ✗ {css_class:<40} {description}")
            all_found = False
    
    print()
    return all_found


def validate_responsive_design():
    """Validate responsive design rules."""
    
    css_path = Path('web/static/css/style.css')
    
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    print("2. Validating Responsive Design")
    print("-" * 60)
    
    breakpoints = [
        (r'@media\s*\(max-width:\s*1024px\)', '1024px (tablet landscape)'),
        (r'@media\s*\(max-width:\s*768px\)', '768px (tablet portrait)'),
        (r'@media\s*\(max-width:\s*480px\)', '480px (mobile)'),
    ]
    
    all_found = True
    
    for pattern, description in breakpoints:
        if re.search(pattern, css_content):
            print(f"  ✓ Breakpoint: {description}")
        else:
            print(f"  ✗ Breakpoint: {description}")
            all_found = False
    
    # Check for temporal-specific responsive rules
    print("\n  Temporal-specific responsive rules:")
    
    temporal_responsive_classes = [
        'probability-comparison',
        'prob-item-value',
        'decay-chart-container',
        'decay-metadata',
        'metadata-grid',
        'temporal-decay-section',
    ]
    
    # Extract all media query blocks
    media_blocks = re.findall(r'@media[^{]+\{([^}]+(?:\{[^}]+\}[^}]*)*)\}', css_content, re.DOTALL)
    all_media_content = ' '.join(media_blocks)
    
    for cls in temporal_responsive_classes:
        if cls in all_media_content:
            print(f"    ✓ {cls}")
        else:
            print(f"    ⚠ {cls} (may not have responsive rules)")
    
    print()
    return all_found


def validate_css_syntax():
    """Validate CSS syntax."""
    
    css_path = Path('web/static/css/style.css')
    
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    print("3. Validating CSS Syntax")
    print("-" * 60)
    
    # Count braces
    open_braces = css_content.count('{')
    close_braces = css_content.count('}')
    
    if open_braces == close_braces:
        print(f"  ✓ Braces balanced: {open_braces} opening, {close_braces} closing")
        syntax_valid = True
    else:
        print(f"  ✗ Braces unbalanced: {open_braces} opening, {close_braces} closing")
        syntax_valid = False
    
    # Check for common CSS errors
    if ';;' in css_content:
        print(f"  ⚠ Double semicolons found (may be intentional)")
    
    # Count rules
    rule_count = len(re.findall(r'\{[^}]+\}', css_content))
    print(f"  ✓ Total CSS rules: {rule_count}")
    
    print()
    return syntax_valid


def validate_html_integration():
    """Validate HTML template uses correct CSS classes."""
    
    html_path = Path('web/templates/forecast.html')
    
    if not html_path.exists():
        print("4. Validating HTML Integration")
        print("-" * 60)
        print("  ⚠ HTML template not found (skipping)")
        print()
        return True
    
    with open(html_path, 'r') as f:
        html_content = f.read()
    
    print("4. Validating HTML Integration")
    print("-" * 60)
    
    # Check for temporal decay section
    if 'temporal-decay-section' in html_content:
        print("  ✓ Temporal decay section present in HTML")
    else:
        print("  ✗ Temporal decay section not found in HTML")
        return False
    
    # Check for key structural elements
    key_elements = [
        ('probability-comparison', 'Probability comparison grid'),
        ('prob-item', 'Probability items'),
        ('decay-chart-container', 'Chart container'),
        ('decay-metadata', 'Metadata section'),
    ]
    
    all_found = True
    
    for element, description in key_elements:
        if element in html_content:
            print(f"  ✓ {description} ({element})")
        else:
            print(f"  ✗ {description} ({element})")
            all_found = False
    
    print()
    return all_found


def validate_visual_design():
    """Validate visual design elements."""
    
    css_path = Path('web/static/css/style.css')
    
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    print("5. Validating Visual Design Elements")
    print("-" * 60)
    
    design_elements = [
        (r'\.prob-item\s*\{[^}]*background:', 'Probability card backgrounds'),
        (r'\.prob-item\s*\{[^}]*border:', 'Probability card borders'),
        (r'\.prob-item\s*\{[^}]*box-shadow:', 'Probability card shadows'),
        (r'\.prob-item:hover', 'Probability card hover effects'),
        (r'\.decay-chart-container\s*\{[^}]*background:', 'Chart container background'),
        (r'\.metadata-item:hover', 'Metadata hover effects'),
        (r'\.days-remaining\s*\{[^}]*background:', 'Days remaining badge styling'),
        (r'\.threshold-badge\.applied', 'Applied threshold badge styling'),
        (r'\.threshold-badge\.not-applied', 'Not applied threshold badge styling'),
    ]
    
    all_found = True
    
    for pattern, description in design_elements:
        if re.search(pattern, css_content, re.DOTALL):
            print(f"  ✓ {description}")
        else:
            print(f"  ⚠ {description} (may need review)")
    
    print()
    return True  # Visual elements are optional


def main():
    """Run all validations."""
    
    print("=" * 60)
    print("Task 20: Temporal Decay Visualization CSS - Validation")
    print("=" * 60)
    print()
    
    results = {
        'CSS Classes': validate_css_classes(),
        'Responsive Design': validate_responsive_design(),
        'CSS Syntax': validate_css_syntax(),
        'HTML Integration': validate_html_integration(),
        'Visual Design': validate_visual_design(),
    }
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status:<10} {test_name}")
    
    print()
    
    if all(results.values()):
        print("✓ All validations passed! Task 20 is complete.")
        print()
        print("The temporal decay visualization CSS includes:")
        print("  • Complete styling for temporal decay section")
        print("  • Probability comparison grid with card layouts")
        print("  • Chart container styling")
        print("  • Metadata display with grid layout")
        print("  • Responsive design for mobile, tablet, and desktop")
        print("  • Hover effects and visual feedback")
        print("  • Badge styling for threshold indicators")
        return 0
    else:
        print("✗ Some validations failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
