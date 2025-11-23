#!/usr/bin/env python3
"""
Test only the temporal decay section rendering.
"""

import sys
sys.path.append('.')

from datetime import datetime
from web.app import app

def test_temporal_section_with_adaptive_method():
    """Test temporal section with adaptive decay method (current default)."""
    
    print("Testing temporal section with adaptive decay method...")
    
    forecast_data = {
        'name': 'us_recession_2025',
        'display_name': 'US Recession 2025 V2',
        'description': 'Test with adaptive decay',
        'probability': 0.0877,
        'last_updated': datetime.now(),
        'indicators': {},
        'history': [],
        'parameters': {},  # Empty to avoid parameter section issues
        'data_sources': ['FRED'],
        'breakdown': {
            'base_probability': 0.4882,
            'adjusted_probability': 0.0877,
            'days_remaining': 37,
            'indicator_signals': {},
            'indicators': {},
            'features': {},
            'temporal_metadata': {
                'method': 'adaptive',
                'days_remaining': 37,
                'adjustment_factor': 0.17965182969406945,
                'parameters': {
                    'total_days': 365,
                    'decay_power': 1.5,
                    'amplification_power': 1.5,
                    'lower_threshold': 0.4,
                    'upper_threshold': 0.6
                }
            },
            'timestamps': {}
        }
    }
    
    with app.test_request_context():
        from flask import render_template
        
        try:
            html = render_template(
                'forecast.html',
                forecast=forecast_data,
                forecasts=[],
                active_forecast='us_recession_2025',
                show_temporal=True
            )
            
            # Check temporal section elements
            assert 'temporal-decay-section' in html
            assert 'Base Probability' in html
            assert 'Adjusted Probability' in html
            assert '48.8%' in html  # Base probability
            assert '8.8%' in html   # Adjusted probability
            assert '37' in html     # Days remaining
            assert 'Adaptive' in html  # Method name
            assert 'temporalDecayChart' in html
            
            # Check metadata
            assert 'Temporal Adjustment Details' in html
            assert 'Adjustment Factor' in html
            assert '0.1797' in html  # Adjustment factor
            
            # Check parameters are rendered
            assert 'Total Days' in html
            assert 'Decay Power' in html
            assert 'Amplification Power' in html
            assert 'Lower Threshold' in html
            assert 'Upper Threshold' in html
            
            print("✓ Temporal section renders correctly with adaptive method")
            print("✓ All probabilities displayed correctly")
            print("✓ Days remaining displayed correctly")
            print("✓ Metadata displayed correctly")
            print("✓ Method-specific parameters displayed correctly")
            return True
            
        except Exception as e:
            print(f"✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_temporal_section_with_exponential_method():
    """Test temporal section with exponential decay method."""
    
    print("\nTesting temporal section with exponential decay method...")
    
    forecast_data = {
        'name': 'us_recession_2025',
        'display_name': 'US Recession 2025 V2',
        'description': 'Test with exponential decay',
        'probability': 0.35,
        'last_updated': datetime.now(),
        'indicators': {},
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
                'method': 'exponential',
                'days_remaining': 400,
                'adjustment_factor': 0.833,
                'parameters': {
                    'decay_rate': 0.015,
                    'threshold': 0.4
                }
            },
            'timestamps': {}
        }
    }
    
    with app.test_request_context():
        from flask import render_template
        
        try:
            html = render_template(
                'forecast.html',
                forecast=forecast_data,
                forecasts=[],
                active_forecast='us_recession_2025',
                show_temporal=True
            )
            
            # Check temporal section elements
            assert 'temporal-decay-section' in html
            assert '42.0%' in html  # Base probability
            assert '35.0%' in html  # Adjusted probability
            assert '400' in html    # Days remaining
            assert 'Exponential' in html  # Method name
            
            # Check exponential-specific parameters
            assert 'Decay Rate' in html
            assert 'Threshold' in html
            assert '0.0150' in html  # Decay rate
            assert '0.4000' in html  # Threshold
            
            print("✓ Temporal section renders correctly with exponential method")
            print("✓ Exponential-specific parameters displayed correctly")
            return True
            
        except Exception as e:
            print(f"✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("Temporal Section Rendering Tests")
    print("=" * 60)
    print()
    
    success = True
    
    if not test_temporal_section_with_adaptive_method():
        success = False
    
    if not test_temporal_section_with_exponential_method():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All temporal section tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
