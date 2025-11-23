#!/usr/bin/env python3
"""
Validation script for temporal decay CSS styles.
Verifies that all required CSS classes are present and properly formatted.
"""

import re
from pathlib import Path


def validate_temporal_css():
    """Validate that temporal decay CSS styles are present and properly formatted."""
    
    css_path = Path('web/static/css/style.css')
    
    if not css_path.exists():
        print("❌ CSS file not found at web/static/css/style.css")
        return False
    
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    # Required CSS classes for temporal decay visualization
    required_classes = [
        # Main section
        '.temporal-decay-section',
        
        # Probability comparison
        '.probability-comparison',
        '.prob-item',
        '.prob-item.base-probability',
        '.prob-item.adjusted-probability',
        '.prob-item-label',
        '.prob-item-value',
        '.prob-item-description',
        '.days-remaining',
        
        # Chart container
        '.decay-chart-container',
        '.chart-loading',
        
        # Metadata
        '.decay-metadata',
        '.metadata-grid',
        '.metadata-item',
        '.metadata-label',
        '.metadata-value',
        '.threshold-badge',
        '.threshold-badge.applied',
        '.threshold-badge.not-applied',
    ]
    
    print("Validating temporal decay CSS styles...")
    print("=" * 60)
    
    missing_classes = []
    found_classes = []
    
    for css_class in required_classes:
        # Escape special characters for regex
        escaped_class = re.escape(css_class)
        pattern = rf'{escaped_class}\s*\{{' 
        
        if re.search(pattern, css_content):
            found_classes.append(css_class)
            print(f"✓ Found: {css_class}")
        else:
            missing_classes.append(css_class)
            print(f"✗ Missing: {css_class}")
    
    print("=" * 60)
    
    # Check for responsive design rules
    print("\nChecking responsive design...")
    
    responsive_checks = [
        (r'@media\s*\(max-width:\s*1024px\)', '1024px breakpoint'),
        (r'@media\s*\(max-width:\s*768px\)', '768px breakpoint'),
        (r'@media\s*\(max-width:\s*480px\)', '480px breakpoint'),
    ]
    
    for pattern, description in responsive_checks:
        if re.search(pattern, css_content):
            print(f"✓ Found: {description}")
        else:
            print(f"✗ Missing: {description}")
    
    # Check for temporal-specific responsive rules
    print("\nChecking temporal-specific responsive rules...")
    
    temporal_responsive_rules = [
        '.probability-comparison',
        '.prob-item-value',
        '.decay-chart-container',
        '.decay-metadata',
        '.metadata-grid',
        '.temporal-decay-section',
    ]
    
    # Check if these appear in media queries
    media_query_sections = re.findall(r'@media[^{]+\{[^}]+\}', css_content, re.DOTALL)
    
    for rule in temporal_responsive_rules:
        found_in_media = False
        for section in media_query_sections:
            if rule in section:
                found_in_media = True
                break
        
        if found_in_media:
            print(f"✓ {rule} has responsive rules")
        else:
            print(f"⚠ {rule} may not have responsive rules")
    
    print("=" * 60)
    
    # Summary
    print(f"\nSummary:")
    print(f"  Found classes: {len(found_classes)}/{len(required_classes)}")
    print(f"  Missing classes: {len(missing_classes)}")
    
    if missing_classes:
        print(f"\n❌ Missing CSS classes:")
        for css_class in missing_classes:
            print(f"    - {css_class}")
        return False
    else:
        print(f"\n✓ All required CSS classes are present!")
        return True


def check_css_syntax():
    """Basic CSS syntax validation."""
    
    css_path = Path('web/static/css/style.css')
    
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    print("\nChecking CSS syntax...")
    
    # Count opening and closing braces
    open_braces = css_content.count('{')
    close_braces = css_content.count('}')
    
    if open_braces == close_braces:
        print(f"✓ Braces balanced: {open_braces} opening, {close_braces} closing")
        return True
    else:
        print(f"✗ Braces unbalanced: {open_braces} opening, {close_braces} closing")
        return False


def main():
    """Run all CSS validations."""
    
    print("Temporal Decay CSS Validation")
    print("=" * 60)
    print()
    
    syntax_valid = check_css_syntax()
    classes_valid = validate_temporal_css()
    
    print("\n" + "=" * 60)
    
    if syntax_valid and classes_valid:
        print("✓ All CSS validations passed!")
        return 0
    else:
        print("✗ Some CSS validations failed")
        return 1


if __name__ == "__main__":
    exit(main())
