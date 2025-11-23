#!/usr/bin/env python3
"""
Comprehensive validation for Task 22: Chart.js Library Integration

This script validates that Chart.js has been properly added to the base template
and is ready for use by the temporal decay chart visualization.
"""

from pathlib import Path
import sys

def validate_chartjs_in_base_template():
    """Validate Chart.js integration in base.html"""
    print("\n" + "=" * 70)
    print("Task 22 Validation: Chart.js Library Integration")
    print("=" * 70)
    
    project_root = Path(__file__).parent.parent
    base_template = project_root / 'web' / 'templates' / 'base.html'
    
    if not base_template.exists():
        print("\n✗ FAILED: base.html not found")
        return False
    
    content = base_template.read_text()
    lines = content.split('\n')
    
    all_checks = []
    
    # Section 1: Chart.js Presence
    print("\n1. Chart.js CDN Link Validation")
    print("-" * 70)
    
    checks = []
    
    has_chartjs = 'chart.js' in content.lower() or 'chart.umd' in content.lower()
    checks.append(has_chartjs)
    print(f"{'✓' if has_chartjs else '✗'} Chart.js CDN link present")
    
    has_version = '@4.4.0' in content
    checks.append(has_version)
    print(f"{'✓' if has_version else '✗'} Version 4.4.0 specified")
    
    has_umd = 'chart.umd' in content.lower()
    checks.append(has_umd)
    print(f"{'✓' if has_umd else '✗'} UMD build specified")
    
    has_jsdelivr = 'cdn.jsdelivr.net' in content
    checks.append(has_jsdelivr)
    print(f"{'✓' if has_jsdelivr else '✗'} jsDelivr CDN used")
    
    all_checks.extend(checks)
    print(f"\nSection 1: {sum(checks)}/{len(checks)} checks passed")
    
    # Section 2: Script Loading Order
    print("\n2. Script Loading Order Validation")
    print("-" * 70)
    
    checks = []
    
    chartjs_line = -1
    mainjs_line = -1
    
    for i, line in enumerate(lines):
        if 'chart.js' in line.lower() or 'chart.umd' in line.lower():
            if '<script' in line:
                chartjs_line = i
        if 'main.js' in line and 'static' in line:
            if '<script' in line:
                mainjs_line = i
    
    found_both = chartjs_line > 0 and mainjs_line > 0
    checks.append(found_both)
    print(f"{'✓' if found_both else '✗'} Both scripts found")
    
    if found_both:
        correct_order = chartjs_line < mainjs_line
        checks.append(correct_order)
        print(f"{'✓' if correct_order else '✗'} Chart.js loaded before main.js")
        print(f"  Chart.js: line {chartjs_line + 1}")
        print(f"  main.js: line {mainjs_line + 1}")
    else:
        checks.append(False)
        print("✗ Could not verify loading order")
    
    all_checks.extend(checks)
    print(f"\nSection 2: {sum(checks)}/{len(checks)} checks passed")
    
    # Section 3: Script Tag Format
    print("\n3. Script Tag Format Validation")
    print("-" * 70)
    
    checks = []
    
    has_script_tag = '<script src="https://cdn.jsdelivr.net/npm/chart.js' in content
    checks.append(has_script_tag)
    print(f"{'✓' if has_script_tag else '✗'} Proper script tag format")
    
    has_closing_tag = '</script>' in content
    checks.append(has_closing_tag)
    print(f"{'✓' if has_closing_tag else '✗'} Closing script tag present")
    
    has_https = 'https://' in content and 'chart.js' in content.lower()
    checks.append(has_https)
    print(f"{'✓' if has_https else '✗'} HTTPS protocol used")
    
    all_checks.extend(checks)
    print(f"\nSection 3: {sum(checks)}/{len(checks)} checks passed")
    
    # Section 4: Documentation
    print("\n4. Documentation Validation")
    print("-" * 70)
    
    checks = []
    
    has_comment = '<!--' in content and 'Chart.js' in content
    checks.append(has_comment)
    print(f"{'✓' if has_comment else '✗'} Documentation comment present")
    
    # Check if comment is near Chart.js script
    comment_near_script = False
    for i, line in enumerate(lines):
        if 'Chart.js' in line and '<!--' in line:
            # Check if script tag is within 3 lines
            for j in range(max(0, i-3), min(len(lines), i+4)):
                if 'chart.js' in lines[j].lower() or 'chart.umd' in lines[j].lower():
                    comment_near_script = True
                    break
    
    checks.append(comment_near_script)
    print(f"{'✓' if comment_near_script else '✗'} Comment near Chart.js script")
    
    all_checks.extend(checks)
    print(f"\nSection 4: {sum(checks)}/{len(checks)} checks passed")
    
    # Section 5: Integration with main.js
    print("\n5. Integration with main.js Validation")
    print("-" * 70)
    
    checks = []
    
    mainjs_path = project_root / 'web' / 'static' / 'js' / 'main.js'
    if mainjs_path.exists():
        mainjs_content = mainjs_path.read_text()
        
        uses_chart = 'new Chart(' in mainjs_content
        checks.append(uses_chart)
        print(f"{'✓' if uses_chart else '✗'} main.js uses Chart.js")
        
        has_render_function = 'renderTemporalDecayChart' in mainjs_content
        checks.append(has_render_function)
        print(f"{'✓' if has_render_function else '✗'} renderTemporalDecayChart function exists")
        
        has_init_function = 'initializeTemporalDecayChart' in mainjs_content
        checks.append(has_init_function)
        print(f"{'✓' if has_init_function else '✗'} initializeTemporalDecayChart function exists")
    else:
        checks.extend([False, False, False])
        print("✗ main.js not found")
    
    all_checks.extend(checks)
    print(f"\nSection 5: {sum(checks)}/{len(checks)} checks passed")
    
    # Final Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    total_passed = sum(all_checks)
    total_checks = len(all_checks)
    
    print(f"\nTotal: {total_passed}/{total_checks} checks passed")
    
    if total_passed == total_checks:
        print("\n" + "=" * 70)
        print("✓ Task 22 is COMPLETE!")
        print("=" * 70)
        print("\nChart.js has been successfully integrated:")
        print("  • CDN link added to base.html")
        print("  • Version 4.4.0 specified")
        print("  • UMD build selected")
        print("  • Loaded before main.js")
        print("  • Proper script tag format")
        print("  • Documentation comment included")
        print("  • Integration with main.js verified")
        print("\nThe temporal decay chart is ready for use!")
        return True
    else:
        print(f"\n✗ {total_checks - total_passed} check(s) failed")
        print("\nPlease review the failed checks above.")
        return False

def main():
    """Run all validations"""
    success = validate_chartjs_in_base_template()
    
    if success:
        print("\n" + "=" * 70)
        print("Next Steps")
        print("=" * 70)
        print("\nTask 22 is complete. Next task:")
        print("  • Task 23: Final integration testing")
        print("    - Test v1 model display (no temporal section)")
        print("    - Test v2 model display (with temporal section)")
        print("    - Test other forecasts (election_2028)")
        print("    - Test responsive design")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
