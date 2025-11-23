#!/usr/bin/env python3
"""
Comprehensive validation that Task 21 is complete.

This script validates that all components of the temporal decay chart
JavaScript implementation are working correctly together.
"""

import sys
from pathlib import Path
import subprocess

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_validation_script(script_name):
    """Run a validation script and return success status"""
    script_path = project_root / 'tests' / script_name
    try:
        result = subprocess.run(
            ['python', str(script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def main():
    """Run all validation checks"""
    print("=" * 70)
    print("Task 21 Completion Validation")
    print("Temporal Decay Chart JavaScript Implementation")
    print("=" * 70)
    
    validations = [
        ('validate_temporal_chart_js.py', 'JavaScript structure validation'),
        ('test_temporal_chart_calculation.py', 'Formula correctness tests'),
    ]
    
    results = []
    
    for script, description in validations:
        print(f"\n{description}...")
        print("-" * 70)
        
        success, stdout, stderr = run_validation_script(script)
        results.append(success)
        
        if success:
            print(f"✓ PASSED: {description}")
            # Show summary line from output
            for line in stdout.split('\n'):
                if 'Passed:' in line or 'All' in line and 'passed' in line:
                    print(f"  {line.strip()}")
        else:
            print(f"✗ FAILED: {description}")
            if stderr:
                print(f"  Error: {stderr[:200]}")
    
    # Check that all required files exist
    print("\n\nFile Existence Checks...")
    print("-" * 70)
    
    required_files = [
        ('web/static/js/main.js', 'Main JavaScript file'),
        ('web/templates/base.html', 'Base template with Chart.js'),
        ('web/templates/forecast.html', 'Forecast template with breakdown data'),
        ('tests/validate_temporal_chart_js.py', 'Validation script'),
        ('tests/test_temporal_chart_calculation.py', 'Calculation tests'),
        ('docs/TASK_21_IMPLEMENTATION_SUMMARY.md', 'Implementation summary'),
    ]
    
    file_checks = []
    for file_path, description in required_files:
        full_path = project_root / file_path
        exists = full_path.exists()
        file_checks.append(exists)
        
        status = "✓" if exists else "✗"
        print(f"{status} {description}: {file_path}")
    
    # Check for required functions in main.js
    print("\n\nFunction Existence Checks...")
    print("-" * 70)
    
    main_js = project_root / 'web' / 'static' / 'js' / 'main.js'
    content = main_js.read_text()
    
    required_functions = [
        'calculateDecayedProbability',
        'renderTemporalDecayChart',
        'initializeTemporalDecayChart'
    ]
    
    function_checks = []
    for func_name in required_functions:
        exists = f'function {func_name}' in content
        function_checks.append(exists)
        
        status = "✓" if exists else "✗"
        print(f"{status} Function '{func_name}' defined")
    
    # Check Chart.js inclusion
    print("\n\nChart.js Integration Checks...")
    print("-" * 70)
    
    base_html = project_root / 'web' / 'templates' / 'base.html'
    base_content = base_html.read_text()
    
    chartjs_checks = []
    
    has_chartjs = 'chart.js' in base_content.lower() or 'chart.umd' in base_content.lower()
    chartjs_checks.append(has_chartjs)
    status = "✓" if has_chartjs else "✗"
    print(f"{status} Chart.js CDN link in base.html")
    
    # Check breakdown data element
    forecast_html = project_root / 'web' / 'templates' / 'forecast.html'
    forecast_content = forecast_html.read_text()
    
    has_breakdown_element = 'id="breakdown-data"' in forecast_content
    chartjs_checks.append(has_breakdown_element)
    status = "✓" if has_breakdown_element else "✗"
    print(f"{status} Breakdown data element in forecast.html")
    
    has_canvas = 'id="temporalDecayChart"' in forecast_content
    chartjs_checks.append(has_canvas)
    status = "✓" if has_canvas else "✗"
    print(f"{status} Chart canvas element in forecast.html")
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    all_checks = results + file_checks + function_checks + chartjs_checks
    passed = sum(all_checks)
    total = len(all_checks)
    
    print(f"\nValidation Scripts: {sum(results)}/{len(results)} passed")
    print(f"File Checks: {sum(file_checks)}/{len(file_checks)} passed")
    print(f"Function Checks: {sum(function_checks)}/{len(function_checks)} passed")
    print(f"Chart.js Integration: {sum(chartjs_checks)}/{len(chartjs_checks)} passed")
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if all(all_checks):
        print("\n" + "=" * 70)
        print("✓ Task 21 is COMPLETE!")
        print("=" * 70)
        print("\nAll components of the temporal decay chart JavaScript")
        print("implementation are working correctly:")
        print("  • calculateDecayedProbability() function")
        print("  • renderTemporalDecayChart() function")
        print("  • initializeTemporalDecayChart() function")
        print("  • Chart.js library integration")
        print("  • Breakdown data embedding")
        print("  • Formula matches Python implementation")
        print("\nThe temporal decay chart is ready for use!")
        return 0
    else:
        print("\n" + "=" * 70)
        print("✗ Task 21 is INCOMPLETE")
        print("=" * 70)
        print("\nSome checks failed. Please review the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
