#!/usr/bin/env python3
"""
Verify the HTML structure of the temporal decay section.
"""

import sys
sys.path.append('.')

from datetime import datetime
from flask import Flask
from web.app import app

def verify_html_structure():
    """Verify the HTML structure contains all required elements."""
    
    print("Verifying HTML structure of temporal decay section...")
    
    forecast_data = {
        'name': 'us_recession_2025',
        'display_name': 'US Recession 2025 Forecast V2',
        'description': 'Enhanced forecast with temporal decay',
        'probability': 0.35,
        'last_updated': datetime.now(),
        'indicators': {'yield_curve': -0.5},
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
    
    with app.test_request_context():
        from flask import render_template
        
        html = render_template(
            'forecast.html',
            forecast=forecast_data,
            forecasts=[],
            active_forecast='us_recession_2025',
            show_temporal=True
        )
        
        # Check for required HTML elements
        checks = [
            ('temporal-decay-section', 'Temporal decay section container'),
            ('probability-comparison', 'Probability comparison container'),
            ('prob-item', 'Probability item cards'),
            ('decay-chart-container', 'Chart container'),
            ('temporalDecayChart', 'Canvas element for chart'),
            ('decay-metadata', 'Metadata section'),
            ('metadata-grid', 'Metadata grid'),
            ('Decay Method:', 'Decay method label'),
            ('Decay Rate:', 'Decay rate label'),
            ('Threshold:', 'Threshold label'),
            ('Threshold Applied:', 'Threshold applied label'),
            ('Adjustment Factor:', 'Adjustment factor label'),
            ('Base Probability', 'Base probability label'),
            ('Adjusted Probability', 'Adjusted probability label'),
            ('Days Remaining', 'Days remaining label'),
            ('Probability Projection Over Time', 'Chart title'),
        ]
        
        all_passed = True
        for element, description in checks:
            if element in html:
                print(f"  ✓ {description}")
            else:
                print(f"  ✗ {description} - NOT FOUND")
                all_passed = False
        
        # Check for specific values
        value_checks = [
            ('42.0%', 'Base probability value (42.0%)'),
            ('35.0%', 'Adjusted probability value (35.0%)'),
            ('400', 'Days remaining value (400)'),
            ('Exponential', 'Decay method value (Exponential)'),
            ('0.0150', 'Decay rate value (0.0150)'),
            ('0.40', 'Threshold value (0.40)'),
            ('Yes', 'Threshold applied value (Yes)'),
            ('0.8330', 'Adjustment factor value (0.8330)'),
        ]
        
        print("\nVerifying rendered values:")
        for value, description in value_checks:
            if value in html:
                print(f"  ✓ {description}")
            else:
                print(f"  ✗ {description} - NOT FOUND")
                all_passed = False
        
        return all_passed

if __name__ == "__main__":
    print("=" * 60)
    print("HTML Structure Verification")
    print("=" * 60)
    print()
    
    if verify_html_structure():
        print("\n" + "=" * 60)
        print("✓ All HTML structure checks passed!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("✗ Some HTML structure checks failed")
        print("=" * 60)
        sys.exit(1)
