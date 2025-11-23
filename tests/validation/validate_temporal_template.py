#!/usr/bin/env python3
"""
Validation script to verify the temporal decay template rendering.
"""

import sys
sys.path.append('.')

from datetime import datetime
from flask import Flask
from web.app import app

def test_template_with_temporal_data():
    """Test that the template renders correctly with temporal decay data."""
    
    print("Testing forecast.html template with temporal decay data...")
    
    # Create test data structure matching what the app provides
    forecast_data = {
        'name': 'us_recession_2025',
        'display_name': 'US Recession 2025 Forecast',
        'description': 'Test forecast with temporal decay',
        'probability': 0.35,
        'last_updated': datetime.now(),
        'indicators': {
            'yield_curve': -0.5,
            'unemployment': 4.2,
            'gdp': 2.1
        },
        'history': [],
        'parameters': {},
        'data_sources': ['FRED'],
        'breakdown': {
            'base_probability': 0.42,
            'adjusted_probability': 0.35,
            'days_remaining': 400,
            'indicator_signals': {},
            'indicators': {},
            'features': {},
            'temporal_metadata': {
                'decay_method': 'exponential',
                'decay_rate': 0.015,
                'threshold': 0.4,
                'threshold_applied': True,
                'adjustment_factor': 0.833
            },
            'timestamps': {}
        }
    }
    
    forecasts = []
    show_temporal = True
    
    with app.test_request_context():
        from flask import render_template
        
        try:
            # Render the template
            html = render_template(
                'forecast.html',
                forecast=forecast_data,
                forecasts=forecasts,
                active_forecast='us_recession_2025',
                show_temporal=show_temporal
            )
            
            # Check that temporal section is present
            assert 'temporal-decay-section' in html, "Temporal decay section not found"
            assert 'Base Probability' in html, "Base probability label not found"
            assert 'Adjusted Probability' in html, "Adjusted probability label not found"
            assert 'Days Remaining' in html, "Days remaining label not found"
            assert 'temporalDecayChart' in html, "Temporal decay chart canvas not found"
            assert 'Temporal Adjustment Details' in html, "Temporal metadata section not found"
            
            # Check that values are rendered
            assert '42.0%' in html, "Base probability value not rendered"
            assert '35.0%' in html, "Adjusted probability value not rendered"
            assert '400' in html, "Days remaining value not rendered"
            assert 'Exponential' in html, "Decay method not rendered"
            
            print("✓ Template renders correctly with temporal decay data")
            print("✓ All required sections are present")
            print("✓ Values are correctly displayed")
            return True
            
        except Exception as e:
            print(f"✗ Template rendering failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_template_without_temporal_data():
    """Test that the template renders correctly without temporal decay data."""
    
    print("\nTesting forecast.html template without temporal decay data...")
    
    # Create test data structure without breakdown
    forecast_data = {
        'name': 'election_2028',
        'display_name': 'Election 2028 Forecast',
        'description': 'Test forecast without temporal decay',
        'probability': 0.55,
        'last_updated': datetime.now(),
        'indicators': {},
        'history': [],
        'parameters': {},
        'data_sources': ['Random'],
        'breakdown': None
    }
    
    forecasts = []
    show_temporal = False
    
    with app.test_request_context():
        from flask import render_template
        
        try:
            # Render the template
            html = render_template(
                'forecast.html',
                forecast=forecast_data,
                forecasts=forecasts,
                active_forecast='election_2028',
                show_temporal=show_temporal
            )
            
            # Check that temporal section is NOT present
            assert 'temporal-decay-section' not in html, "Temporal decay section should not be present"
            assert 'temporalDecayChart' not in html, "Temporal decay chart should not be present"
            
            # Check that regular probability is still shown
            assert '55.0%' in html, "Regular probability not rendered"
            
            print("✓ Template renders correctly without temporal decay data")
            print("✓ Temporal section is correctly hidden")
            print("✓ Regular probability display works")
            return True
            
        except Exception as e:
            print(f"✗ Template rendering failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("Temporal Decay Template Validation")
    print("=" * 60)
    
    success = True
    
    # Test with temporal data
    if not test_template_with_temporal_data():
        success = False
    
    # Test without temporal data
    if not test_template_without_temporal_data():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All template validation tests passed!")
        sys.exit(0)
    else:
        print("✗ Some template validation tests failed")
        sys.exit(1)
