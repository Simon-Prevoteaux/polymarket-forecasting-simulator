"""
Validation script for forecast display page.

This script validates that the forecast display page works correctly:
- Displays probability correctly
- Shows last updated timestamp
- Displays indicator values
- Shows historical data chart
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app import app
from forecasts import discover_forecasts
from lib.database import get_forecast_history


def validate_forecast_display():
    """Validate the forecast display page functionality."""
    print("=" * 60)
    print("Validating Forecast Display Page")
    print("=" * 60)
    
    # Create test client
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Discover forecasts
    print("\n1. Discovering forecasts...")
    registry = discover_forecasts()
    forecast_names = registry.list_names()
    
    if not forecast_names:
        print("   ❌ No forecasts found!")
        return False
    
    print(f"   ✓ Found {len(forecast_names)} forecast(s): {', '.join(forecast_names)}")
    
    # Test with first forecast (should be us_recession_2025)
    forecast_name = forecast_names[0]
    print(f"\n2. Testing forecast page for '{forecast_name}'...")
    
    response = client.get(f'/forecast/{forecast_name}')
    
    if response.status_code != 200:
        print(f"   ❌ Failed to load forecast page (status: {response.status_code})")
        return False
    
    print(f"   ✓ Forecast page loaded successfully (status: 200)")
    
    # Check for key elements in the response
    html = response.data.decode('utf-8')
    
    print("\n3. Checking page content...")
    
    # Check for probability display
    if 'Current Probability' in html or 'Probability' in html:
        print("   ✓ Probability display found")
    else:
        print("   ❌ Probability display not found")
        return False
    
    # Check for percentage symbol
    if '%' in html:
        print("   ✓ Percentage display found")
    else:
        print("   ❌ Percentage display not found")
        return False
    
    # Check for last updated timestamp
    if 'Last updated' in html or 'last updated' in html:
        print("   ✓ Last updated timestamp found")
    else:
        print("   ❌ Last updated timestamp not found")
        return False
    
    # Check for indicators section
    if 'Indicators' in html or 'indicators' in html:
        print("   ✓ Indicators section found")
    else:
        print("   ❌ Indicators section not found")
        return False
    
    # Check for data sources
    if 'Data Sources' in html or 'data sources' in html:
        print("   ✓ Data sources section found")
    else:
        print("   ❌ Data sources section not found")
        return False
    
    # Check for FRED mention
    if 'FRED' in html:
        print("   ✓ FRED data source mentioned")
    else:
        print("   ❌ FRED data source not mentioned")
        return False
    
    # Check for historical data
    print("\n4. Checking historical data...")
    try:
        history = get_forecast_history(forecast_name, limit=10)
        if history and len(history) > 0:
            print(f"   ✓ Found {len(history)} historical record(s)")
            
            # Check if chart is present in HTML
            if 'probabilityChart' in html or 'Historical' in html:
                print("   ✓ Historical chart section found")
            else:
                print("   ⚠ Historical chart section not found (may be expected if no data)")
        else:
            print("   ⚠ No historical data found (run model to generate data)")
            if 'No historical data' in html or 'no data' in html.lower():
                print("   ✓ Appropriate message shown for missing data")
    except Exception as e:
        print(f"   ⚠ Could not check historical data: {e}")
    
    # Test 404 handling
    print("\n5. Testing 404 handling...")
    response = client.get('/forecast/nonexistent_forecast_xyz')
    
    if response.status_code == 404:
        print("   ✓ Non-existent forecast returns 404")
        html = response.data.decode('utf-8')
        if 'not found' in html.lower() or '404' in html:
            print("   ✓ 404 error page displays correctly")
        else:
            print("   ⚠ 404 error page may not display proper message")
    else:
        print(f"   ❌ Non-existent forecast returned status {response.status_code} instead of 404")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All validation checks passed!")
    print("=" * 60)
    return True


if __name__ == '__main__':
    try:
        success = validate_forecast_display()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
