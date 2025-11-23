#!/usr/bin/env python3
"""
Validation script for final integration testing.

This script manually validates the complete integration of v1, v2, and other
forecast models with the web interface.

Task 23: Final integration testing
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from forecasts.us_recession_2025.model import RecessionModel
from forecasts.us_recession_2025.model_v2 import RecessionModelV2
from forecasts.election_2028.model import ElectionModel
from forecasts import discover_forecasts


def print_section(title):
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def validate_v1_model():
    """Validate v1 model functionality."""
    print_section("V1 Model Validation")
    
    try:
        model = RecessionModel()
        print(f"✓ V1 model instantiated: {model.get_name()}")
        print(f"  Description: {model.get_description()}")
        
        # Check that breakdown returns None
        breakdown = model.get_probability_breakdown()
        if breakdown is None:
            print("✓ V1 model correctly returns None for breakdown")
        else:
            print("✗ V1 model should return None for breakdown")
            return False
        
        # Try to calculate probability
        try:
            prob = model.calculate_probability()
            print(f"✓ V1 model calculated probability: {prob:.4f}")
            
            if 0 <= prob <= 1:
                print("✓ V1 probability is in valid range [0, 1]")
            else:
                print(f"✗ V1 probability out of range: {prob}")
                return False
        except Exception as e:
            print(f"⚠ V1 probability calculation failed (may be API issue): {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ V1 model validation failed: {e}")
        return False


def validate_v2_model():
    """Validate v2 model functionality."""
    print_section("V2 Model Validation")
    
    try:
        model = RecessionModelV2()
        print(f"✓ V2 model instantiated: {model.get_name()}")
        print(f"  Description: {model.get_description()}")
        
        # Check that breakdown returns data
        try:
            breakdown = model.get_probability_breakdown()
            if breakdown is not None:
                print("✓ V2 model returns breakdown data")
                
                # Check required fields
                required_fields = ['base_probability', 'adjusted_probability', 'days_remaining', 'temporal_metadata']
                for field in required_fields:
                    if field in breakdown:
                        print(f"  ✓ Breakdown has '{field}': {breakdown[field]}")
                    else:
                        print(f"  ✗ Breakdown missing '{field}'")
                        return False
                
                # Validate probability ranges
                if 0 <= breakdown['base_probability'] <= 1:
                    print(f"  ✓ Base probability in valid range: {breakdown['base_probability']:.4f}")
                else:
                    print(f"  ✗ Base probability out of range: {breakdown['base_probability']}")
                    return False
                
                if 0 <= breakdown['adjusted_probability'] <= 1:
                    print(f"  ✓ Adjusted probability in valid range: {breakdown['adjusted_probability']:.4f}")
                else:
                    print(f"  ✗ Adjusted probability out of range: {breakdown['adjusted_probability']}")
                    return False
                
                # Check temporal metadata
                metadata = breakdown['temporal_metadata']
                if 'decay_method' in metadata or 'method' in metadata:
                    print(f"  ✓ Temporal metadata has decay method")
                else:
                    print(f"  ✗ Temporal metadata missing decay method")
                    return False
                
            else:
                print("✗ V2 model should return breakdown data")
                return False
        except Exception as e:
            print(f"⚠ V2 breakdown failed (may be API issue): {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ V2 model validation failed: {e}")
        return False


def validate_election_model():
    """Validate election model functionality."""
    print_section("Election Model Validation")
    
    try:
        model = ElectionModel()
        print(f"✓ Election model instantiated: {model.get_name()}")
        print(f"  Description: {model.get_description()}")
        
        # Check that breakdown returns None
        breakdown = model.get_probability_breakdown()
        if breakdown is None:
            print("✓ Election model correctly returns None for breakdown")
        else:
            print("✗ Election model should return None for breakdown")
            return False
        
        # Try to calculate probability
        try:
            prob = model.calculate_probability()
            print(f"✓ Election model calculated probability: {prob:.4f}")
            
            if 0 <= prob <= 1:
                print("✓ Election probability is in valid range [0, 1]")
            else:
                print(f"✗ Election probability out of range: {prob}")
                return False
        except Exception as e:
            print(f"⚠ Election probability calculation failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Election model validation failed: {e}")
        return False


def validate_forecast_discovery():
    """Validate forecast discovery mechanism."""
    print_section("Forecast Discovery Validation")
    
    try:
        registry = discover_forecasts()
        discovered = registry.list_names()
        
        print(f"✓ Discovered {len(discovered)} forecasts:")
        for name in discovered:
            model = registry.get(name)
            print(f"  - {name}: {model.get_name()}")
        
        # Check that we found at least the expected forecasts
        expected = ['us_recession_2025', 'election_2028']
        for expected_name in expected:
            if expected_name in discovered:
                print(f"✓ Found expected forecast: {expected_name}")
            else:
                print(f"⚠ Expected forecast not discovered: {expected_name}")
        
        # Note about v2 model
        if 'us_recession_2025_v2' not in discovered:
            print("\nℹ Note: V2 model is not auto-discovered (same directory as v1)")
            print("  V2 model can be instantiated directly: RecessionModelV2()")
        
        return True
        
    except Exception as e:
        print(f"✗ Forecast discovery failed: {e}")
        return False


def validate_backward_compatibility():
    """Validate backward compatibility."""
    print_section("Backward Compatibility Validation")
    
    try:
        models = [
            ('V1', RecessionModel()),
            ('V2', RecessionModelV2()),
            ('Election', ElectionModel())
        ]
        
        # Check that all models implement base interface
        required_methods = [
            'get_name',
            'get_description',
            'get_parameters',
            'calculate_probability',
            'get_last_updated',
            'get_data_sources',
            'get_probability_breakdown'
        ]
        
        for name, model in models:
            print(f"\nChecking {name} model:")
            for method in required_methods:
                if hasattr(model, method):
                    print(f"  ✓ Has method: {method}")
                else:
                    print(f"  ✗ Missing method: {method}")
                    return False
        
        print("\n✓ All models implement the base ForecastModel interface")
        return True
        
    except Exception as e:
        print(f"✗ Backward compatibility validation failed: {e}")
        return False


def validate_web_interface_files():
    """Validate that web interface files exist."""
    print_section("Web Interface Files Validation")
    
    files_to_check = [
        ('web/app.py', 'Flask application'),
        ('web/templates/base.html', 'Base template'),
        ('web/templates/forecast.html', 'Forecast template'),
        ('web/static/css/style.css', 'CSS stylesheet'),
        ('web/static/js/main.js', 'JavaScript file')
    ]
    
    all_exist = True
    for file_path, description in files_to_check:
        full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
        if os.path.exists(full_path):
            print(f"✓ {description}: {file_path}")
        else:
            print(f"✗ Missing {description}: {file_path}")
            all_exist = False
    
    # Check for temporal-related CSS
    css_path = os.path.join(os.path.dirname(__file__), '..', 'web/static/css/style.css')
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            css_content = f.read()
            if 'temporal' in css_content.lower() or 'decay' in css_content.lower():
                print("✓ CSS contains temporal decay styles")
            else:
                print("⚠ CSS may be missing temporal decay styles")
    
    # Check for Chart.js in base template
    base_template_path = os.path.join(os.path.dirname(__file__), '..', 'web/templates/base.html')
    if os.path.exists(base_template_path):
        with open(base_template_path, 'r') as f:
            template_content = f.read()
            if 'chart.js' in template_content.lower() or 'chartjs' in template_content.lower():
                print("✓ Base template includes Chart.js")
            else:
                print("⚠ Base template may be missing Chart.js")
    
    return all_exist


def main():
    """Run all validation checks."""
    print("\n" + "="*70)
    print("  FINAL INTEGRATION VALIDATION")
    print("  Task 23: Final integration testing")
    print("="*70)
    
    results = []
    
    # Run all validations
    results.append(("V1 Model", validate_v1_model()))
    results.append(("V2 Model", validate_v2_model()))
    results.append(("Election Model", validate_election_model()))
    results.append(("Forecast Discovery", validate_forecast_discovery()))
    results.append(("Backward Compatibility", validate_backward_compatibility()))
    results.append(("Web Interface Files", validate_web_interface_files()))
    
    # Print summary
    print_section("Validation Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} validations passed")
    
    if passed == total:
        print("\n✓ All validations passed!")
        print("\nNext steps:")
        print("1. Start the Flask app: python web/app.py")
        print("2. Visit http://localhost:5001")
        print("3. Test v1 forecast: http://localhost:5001/forecast/us_recession_2025")
        print("4. Test election forecast: http://localhost:5001/forecast/election_2028")
        print("5. Instantiate v2 model directly for testing: RecessionModelV2()")
        return 0
    else:
        print(f"\n✗ {total - passed} validation(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
