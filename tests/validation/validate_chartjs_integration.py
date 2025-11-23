#!/usr/bin/env python3
"""
Validation script for Chart.js integration in base template.

This script validates that:
1. Chart.js CDN link is present in base.html
2. Chart.js is loaded before main.js
3. The correct version is specified
4. The script tag is properly formatted
"""

from pathlib import Path

def validate_chartjs_integration():
    """Validate Chart.js integration in base template"""
    print("=" * 70)
    print("Chart.js Integration Validation")
    print("=" * 70)
    
    project_root = Path(__file__).parent.parent
    base_template = project_root / 'web' / 'templates' / 'base.html'
    
    if not base_template.exists():
        print("\n✗ FAILED: base.html not found")
        return False
    
    content = base_template.read_text()
    lines = content.split('\n')
    
    checks = []
    
    # Check 1: Chart.js CDN link present
    print("\n1. Checking Chart.js CDN link presence...")
    has_chartjs = 'chart.js' in content.lower() or 'chart.umd' in content.lower()
    checks.append(has_chartjs)
    if has_chartjs:
        print("   ✓ Chart.js CDN link found")
    else:
        print("   ✗ Chart.js CDN link NOT found")
    
    # Check 2: Correct version specified
    print("\n2. Checking Chart.js version...")
    has_version = '@4.4.0' in content or 'chart.js@4' in content.lower()
    checks.append(has_version)
    if has_version:
        print("   ✓ Chart.js version 4.4.0 specified")
    else:
        print("   ✗ Chart.js version not specified or incorrect")
    
    # Check 3: Chart.js loaded before main.js
    print("\n3. Checking script loading order...")
    chartjs_line = -1
    mainjs_line = -1
    
    for i, line in enumerate(lines):
        if 'chart.js' in line.lower() or 'chart.umd' in line.lower():
            chartjs_line = i
        if 'main.js' in line and 'static' in line:
            mainjs_line = i
    
    if chartjs_line > 0 and mainjs_line > 0:
        correct_order = chartjs_line < mainjs_line
        checks.append(correct_order)
        if correct_order:
            print(f"   ✓ Chart.js (line {chartjs_line + 1}) loaded before main.js (line {mainjs_line + 1})")
        else:
            print(f"   ✗ Chart.js (line {chartjs_line + 1}) loaded AFTER main.js (line {mainjs_line + 1})")
    else:
        checks.append(False)
        print("   ✗ Could not determine script loading order")
    
    # Check 4: Script tag properly formatted
    print("\n4. Checking script tag format...")
    has_script_tag = '<script src="https://cdn.jsdelivr.net/npm/chart.js' in content
    checks.append(has_script_tag)
    if has_script_tag:
        print("   ✓ Script tag properly formatted")
    else:
        print("   ✗ Script tag format incorrect")
    
    # Check 5: UMD build specified
    print("\n5. Checking UMD build...")
    has_umd = 'chart.umd' in content.lower()
    checks.append(has_umd)
    if has_umd:
        print("   ✓ UMD build specified (chart.umd.min.js)")
    else:
        print("   ✗ UMD build not specified")
    
    # Check 6: Comment present
    print("\n6. Checking documentation comment...")
    has_comment = 'Chart.js' in content and '<!--' in content
    checks.append(has_comment)
    if has_comment:
        print("   ✓ Documentation comment found")
    else:
        print("   ✗ Documentation comment not found")
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"\nPassed: {passed}/{total} checks")
    
    if passed == total:
        print("\n✓ All validation checks passed!")
        print("\nChart.js is properly integrated in base.html:")
        print("  • CDN link present")
        print("  • Version 4.4.0 specified")
        print("  • Loaded before main.js")
        print("  • Script tag properly formatted")
        print("  • UMD build specified")
        print("  • Documentation comment present")
        return True
    else:
        print(f"\n✗ {total - passed} check(s) failed")
        return False

if __name__ == "__main__":
    success = validate_chartjs_integration()
    exit(0 if success else 1)
