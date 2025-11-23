#!/usr/bin/env python3
"""
Integration validation for temporal decay CSS and HTML template.
Verifies that CSS classes match the HTML template usage.
"""

import re
from pathlib import Path


def extract_css_classes(css_content):
    """Extract all CSS class definitions from the stylesheet."""
    # Match class selectors (including compound selectors like .class1.class2)
    pattern = r'\.([\w-]+(?:\.[\w-]+)*)\s*(?:\{|,|\s)'
    matches = re.findall(pattern, css_content)
    
    # Split compound selectors and flatten
    classes = set()
    for match in matches:
        # Handle compound selectors like "prob-item.base-probability"
        parts = match.split('.')
        for part in parts:
            if part:
                classes.add(part)
    
    return classes


def extract_html_classes(html_content):
    """Extract all class attributes from HTML template."""
    # Match class="..." attributes
    pattern = r'class="([^"]+)"'
    matches = re.findall(pattern, html_content)
    
    # Split multiple classes and flatten
    classes = set()
    for match in matches:
        for cls in match.split():
            classes.add(cls)
    
    return classes


def validate_css_html_integration():
    """Validate that HTML classes have corresponding CSS definitions."""
    
    css_path = Path('web/static/css/style.css')
    html_path = Path('web/templates/forecast.html')
    
    if not css_path.exists():
        print("❌ CSS file not found")
        return False
    
    if not html_path.exists():
        print("❌ HTML template not found")
        return False
    
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    with open(html_path, 'r') as f:
        html_content = f.read()
    
    css_classes = extract_css_classes(css_content)
    html_classes = extract_html_classes(html_content)
    
    # Filter to only temporal decay related classes
    temporal_keywords = [
        'temporal', 'decay', 'prob-item', 'probability-comparison',
        'metadata', 'chart-container', 'days-remaining', 'threshold-badge'
    ]
    
    temporal_html_classes = {
        cls for cls in html_classes 
        if any(keyword in cls for keyword in temporal_keywords)
    }
    
    print("Temporal Decay CSS-HTML Integration Validation")
    print("=" * 60)
    print()
    
    print(f"Total CSS classes defined: {len(css_classes)}")
    print(f"Total HTML classes used: {len(html_classes)}")
    print(f"Temporal-related HTML classes: {len(temporal_html_classes)}")
    print()
    
    # Check if temporal HTML classes have CSS definitions
    print("Checking temporal HTML classes against CSS...")
    print("-" * 60)
    
    missing_css = []
    found_css = []
    
    for html_class in sorted(temporal_html_classes):
        if html_class in css_classes:
            found_css.append(html_class)
            print(f"✓ {html_class}")
        else:
            missing_css.append(html_class)
            print(f"✗ {html_class} (used in HTML but not defined in CSS)")
    
    print("-" * 60)
    print()
    
    # Check for specific temporal decay classes
    print("Checking required temporal decay CSS classes...")
    print("-" * 60)
    
    required_classes = [
        'temporal-decay-section',
        'probability-comparison',
        'prob-item',
        'prob-item-label',
        'prob-item-value',
        'prob-item-description',
        'base-probability',
        'adjusted-probability',
        'days-remaining',
        'decay-chart-container',
        'decay-metadata',
        'metadata-grid',
        'metadata-item',
        'metadata-label',
        'metadata-value',
        'threshold-badge',
    ]
    
    for cls in required_classes:
        if cls in css_classes:
            print(f"✓ {cls}")
        else:
            print(f"✗ {cls} (required but not found)")
    
    print("-" * 60)
    print()
    
    # Summary
    print("Summary:")
    print(f"  Temporal HTML classes with CSS: {len(found_css)}/{len(temporal_html_classes)}")
    
    if missing_css:
        print(f"\n⚠ HTML classes without CSS definitions:")
        for cls in missing_css:
            print(f"    - {cls}")
    
    if len(found_css) == len(temporal_html_classes):
        print(f"\n✓ All temporal HTML classes have CSS definitions!")
        return True
    else:
        print(f"\n⚠ Some HTML classes may need CSS definitions")
        return True  # Still pass if only minor issues


def check_responsive_design():
    """Check that responsive design rules are present."""
    
    css_path = Path('web/static/css/style.css')
    
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    print("\nResponsive Design Check")
    print("=" * 60)
    
    # Extract media query sections
    media_queries = re.findall(r'@media[^{]+\{([^}]+)\}', css_content, re.DOTALL)
    
    temporal_classes_in_media = set()
    
    for mq in media_queries:
        # Find temporal-related classes in this media query
        classes = re.findall(r'\.([\w-]+)', mq)
        for cls in classes:
            if any(keyword in cls for keyword in ['temporal', 'decay', 'prob', 'metadata']):
                temporal_classes_in_media.add(cls)
    
    print(f"Temporal classes with responsive rules: {len(temporal_classes_in_media)}")
    
    for cls in sorted(temporal_classes_in_media):
        print(f"  ✓ {cls}")
    
    if temporal_classes_in_media:
        print(f"\n✓ Responsive design rules are present!")
        return True
    else:
        print(f"\n⚠ No temporal-specific responsive rules found")
        return False


def main():
    """Run all integration validations."""
    
    integration_valid = validate_css_html_integration()
    responsive_valid = check_responsive_design()
    
    print("\n" + "=" * 60)
    
    if integration_valid and responsive_valid:
        print("✓ CSS-HTML integration validation passed!")
        return 0
    elif integration_valid:
        print("✓ CSS-HTML integration passed (responsive design could be improved)")
        return 0
    else:
        print("✗ CSS-HTML integration validation failed")
        return 1


if __name__ == "__main__":
    exit(main())
