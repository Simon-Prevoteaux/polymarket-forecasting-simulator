"""
Validation script for forecast discovery mechanism.

This script validates that:
1. Existing forecasts are discovered correctly
2. Test forecasts can be created and discovered
3. Removed forecasts are no longer listed
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forecasts import discover_forecasts


def validate_existing_forecasts():
    """Validate that existing forecasts in the project are discovered."""
    print("=" * 60)
    print("Validating existing forecast discovery...")
    print("=" * 60)
    
    # Discover forecasts from the actual forecasts directory
    project_root = Path(__file__).parent.parent
    forecasts_dir = project_root / "forecasts"
    
    if not forecasts_dir.exists():
        print("❌ Forecasts directory not found")
        return False
    
    registry = discover_forecasts(str(forecasts_dir))
    discovered = registry.list_names()
    
    print(f"\nDiscovered {len(discovered)} forecast(s):")
    for name in discovered:
        model = registry.get(name)
        print(f"  ✓ {name}")
        print(f"    Name: {model.get_name()}")
        print(f"    Description: {model.get_description()}")
        print(f"    Last Updated: {model.get_last_updated()}")
    
    # We expect at least the us_recession_2025 forecast
    if "us_recession_2025" not in discovered:
        print("\n❌ Expected forecast 'us_recession_2025' not found")
        return False
    
    print("\n✓ Existing forecasts discovered successfully")
    return True


def validate_test_forecast_creation():
    """Validate that a test forecast can be created and discovered."""
    print("\n" + "=" * 60)
    print("Validating test forecast creation and discovery...")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        forecasts_dir = Path(temp_dir)
        
        # Create a test forecast
        test_forecast_dir = forecasts_dir / "test_validation_forecast"
        test_forecast_dir.mkdir()
        
        print(f"\nCreating test forecast at: {test_forecast_dir}")
        
        # Create __init__.py
        (test_forecast_dir / '__init__.py').write_text('')
        
        # Create model.py
        model_content = '''
from forecasts import ForecastModel
from datetime import datetime

class ValidationTestForecast(ForecastModel):
    def get_name(self):
        return "Validation Test Forecast"
    
    def get_description(self):
        return "A test forecast for validation purposes"
    
    def get_parameters(self):
        return {
            'test_param': {
                'name': 'test_param',
                'type': 'float',
                'default': 0.5,
                'min_value': 0.0,
                'max_value': 1.0,
                'description': 'Test parameter'
            }
        }
    
    def calculate_probability(self, params=None):
        if params is None:
            params = {}
        return params.get('test_param', 0.5)
    
    def get_last_updated(self):
        return datetime.now()
'''
        (test_forecast_dir / 'model.py').write_text(model_content)
        
        # Discover forecasts
        registry = discover_forecasts(str(forecasts_dir))
        discovered = registry.list_names()
        
        print(f"\nDiscovered forecasts: {discovered}")
        
        # Verify test forecast was discovered
        if "test_validation_forecast" not in discovered:
            print("❌ Test forecast was not discovered")
            return False
        
        # Verify model can be instantiated and used
        model = registry.get("test_validation_forecast")
        if model is None:
            print("❌ Could not retrieve test forecast model")
            return False
        
        print(f"\n✓ Test forecast discovered successfully")
        print(f"  Name: {model.get_name()}")
        print(f"  Description: {model.get_description()}")
        print(f"  Parameters: {list(model.get_parameters().keys())}")
        
        # Test probability calculation
        prob = model.calculate_probability({'test_param': 0.75})
        print(f"  Test calculation: {prob}")
        
        if prob != 0.75:
            print("❌ Probability calculation failed")
            return False
        
        print("\n✓ Test forecast creation and discovery validated")
        return True


def validate_forecast_removal():
    """Validate that removed forecasts are no longer discovered."""
    print("\n" + "=" * 60)
    print("Validating forecast removal detection...")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        forecasts_dir = Path(temp_dir)
        
        # Create two test forecasts
        for i in range(2):
            forecast_dir = forecasts_dir / f"test_forecast_{i}"
            forecast_dir.mkdir()
            (forecast_dir / '__init__.py').write_text('')
            
            model_content = f'''
from forecasts import ForecastModel
from datetime import datetime

class TestForecast{i}(ForecastModel):
    def get_name(self):
        return "Test Forecast {i}"
    def get_description(self):
        return "Test forecast {i}"
    def get_parameters(self):
        return {{}}
    def calculate_probability(self, params=None):
        return 0.5
    def get_last_updated(self):
        return datetime.now()
'''
            (forecast_dir / 'model.py').write_text(model_content)
        
        # First discovery
        registry1 = discover_forecasts(str(forecasts_dir))
        discovered1 = set(registry1.list_names())
        
        print(f"\nInitial discovery: {discovered1}")
        
        if len(discovered1) != 2:
            print(f"❌ Expected 2 forecasts, found {len(discovered1)}")
            return False
        
        # Remove one forecast
        removed_forecast = forecasts_dir / "test_forecast_0"
        print(f"\nRemoving forecast: {removed_forecast}")
        shutil.rmtree(removed_forecast)
        
        # Second discovery
        registry2 = discover_forecasts(str(forecasts_dir))
        discovered2 = set(registry2.list_names())
        
        print(f"After removal: {discovered2}")
        
        # Verify removed forecast is not discovered
        if "test_forecast_0" in discovered2:
            print("❌ Removed forecast still appears in discovery")
            return False
        
        # Verify remaining forecast is still discovered
        if "test_forecast_1" not in discovered2:
            print("❌ Remaining forecast not discovered")
            return False
        
        if len(discovered2) != 1:
            print(f"❌ Expected 1 forecast after removal, found {len(discovered2)}")
            return False
        
        print("\n✓ Forecast removal detection validated")
        return True


def main():
    """Run all validation checks."""
    print("\n" + "=" * 60)
    print("FORECAST DISCOVERY VALIDATION")
    print("=" * 60)
    
    results = []
    
    # Run validations
    results.append(("Existing forecasts", validate_existing_forecasts()))
    results.append(("Test forecast creation", validate_test_forecast_creation()))
    results.append(("Forecast removal", validate_forecast_removal()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All validations passed!")
        return 0
    else:
        print("\n❌ Some validations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
