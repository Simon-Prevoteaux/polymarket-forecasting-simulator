#!/usr/bin/env python3
"""
Verification script for test organization and standalone forecast execution.

This script verifies that:
1. Tests are properly organized (generic vs forecast-specific)
2. Standalone forecast execution works
3. All tests can be run from their new locations
"""

import sys
import os
import subprocess

def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 70}")
    print(f"{title}")
    print('=' * 70)

def run_command(cmd, description):
    """Run a command and report success/failure."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✓ PASS: {description}")
            return True
        else:
            print(f"✗ FAIL: {description}")
            print(f"  Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ FAIL: {description} (timeout)")
        return False
    except Exception as e:
        print(f"✗ FAIL: {description} ({e})")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} missing: {filepath}")
        return False

def main():
    """Main verification function."""
    print_section("TEST ORGANIZATION VERIFICATION")
    
    all_passed = True
    
    # 1. Check file organization
    print_section("1. File Organization")
    
    files_to_check = [
        ("forecasts/us_recession_2025/run_forecast.py", "Standalone forecast script"),
        ("forecasts/us_recession_2025/tests/__init__.py", "Forecast tests package"),
        ("forecasts/us_recession_2025/tests/README.md", "Forecast tests README"),
        ("forecasts/us_recession_2025/tests/test_recession_model.py", "Model unit tests"),
        ("forecasts/us_recession_2025/tests/test_recession_model_properties.py", "Model property tests"),
        ("forecasts/us_recession_2025/tests/test_recession_database_integration.py", "Database integration tests"),
    ]
    
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_passed = False
    
    # Check that files were moved (should NOT exist in old location)
    old_files = [
        "tests/test_recession_model.py",
        "tests/test_recession_model_properties.py",
        "tests/test_recession_database_integration.py",
    ]
    
    print("\nVerifying files were moved from old location:")
    for filepath in old_files:
        if os.path.exists(filepath):
            print(f"✗ File still exists in old location: {filepath}")
            all_passed = False
        else:
            print(f"✓ File properly moved: {filepath}")
    
    # 2. Test standalone forecast execution
    print_section("2. Standalone Forecast Execution")
    
    if not run_command(
        "python forecasts/us_recession_2025/run_forecast.py --no-history",
        "Run forecast without history"
    ):
        all_passed = False
    
    # 3. Test forecast-specific tests
    print_section("3. Forecast-Specific Tests")
    
    if not run_command(
        "python -m pytest forecasts/us_recession_2025/tests/test_recession_model.py -v -x",
        "Run recession model unit tests"
    ):
        all_passed = False
    
    if not run_command(
        "python -m pytest forecasts/us_recession_2025/tests/test_recession_model_properties.py -v -x",
        "Run recession model property tests"
    ):
        all_passed = False
    
    # 4. Test generic tests still work
    print_section("4. Generic Tests")
    
    if not run_command(
        "python -m pytest tests/test_flask_app.py -v -x",
        "Run Flask app tests"
    ):
        all_passed = False
    
    if not run_command(
        "python -m pytest tests/test_database_properties.py -v -x",
        "Run database property tests"
    ):
        all_passed = False
    
    # 5. Test validation scripts
    print_section("5. Validation Scripts")
    
    if not run_command(
        "python forecasts/us_recession_2025/tests/validate_recession_model.py",
        "Run recession model validation"
    ):
        all_passed = False
    
    # 6. Check documentation
    print_section("6. Documentation")
    
    doc_files = [
        (".kiro/steering/polymarket-forecasting-simulator.md", "Steering document"),
        ("forecasts/us_recession_2025/tests/README.md", "Forecast tests README"),
        ("TEST_ORGANIZATION_SUMMARY.md", "Organization summary"),
    ]
    
    for filepath, description in doc_files:
        if not check_file_exists(filepath, description):
            all_passed = False
    
    # Check steering document has test organization section
    print("\nVerifying steering document content:")
    try:
        with open(".kiro/steering/polymarket-forecasting-simulator.md", 'r') as f:
            content = f.read()
            if "Test Organization Pattern" in content:
                print("✓ Steering document includes test organization pattern")
            else:
                print("✗ Steering document missing test organization pattern")
                all_passed = False
            
            if "Running Forecasts" in content:
                print("✓ Steering document includes running forecasts section")
            else:
                print("✗ Steering document missing running forecasts section")
                all_passed = False
    except Exception as e:
        print(f"✗ Error reading steering document: {e}")
        all_passed = False
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    
    if all_passed:
        print("\n✓ ALL VERIFICATIONS PASSED!")
        print("\nTest organization is correct:")
        print("  ✓ Generic tests in tests/")
        print("  ✓ Forecast-specific tests in forecasts/us_recession_2025/tests/")
        print("  ✓ Standalone forecast execution works")
        print("  ✓ All tests pass from new locations")
        print("  ✓ Documentation is complete")
        print("\nReady for future development!")
    else:
        print("\n✗ SOME VERIFICATIONS FAILED")
        print("Please review the output above for details.")
    
    print('=' * 70)
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
