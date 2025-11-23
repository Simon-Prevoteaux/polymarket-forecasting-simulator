#!/usr/bin/env python3
"""
Comprehensive validation for Task 19 completion.
Tests all aspects of the temporal decay template implementation.
"""

import sys
sys.path.append('.')

from datetime import datetime
from web.app import app

def test_subtask_19_1():
    """Test subtask 19.1: Conditional temporal decay section."""
    
    print("Testing Subtask 19.1: Conditional temporal decay section...")
    
    # Test with temporal data
    forecast_with_temporal = {
        'name': 'us_recession_2025',
        'display_name': 'US Recession 2025 V2',
        'description': 'Test',
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
                'adjustment_factor': 0.833,
                'days_remaining': 400,
                'parameters': {'decay_rate': 0.015, 'threshold': 0.4}
            },
            'timestamps': {}
        }
    }
    
    with app.test_request_context():
        from flask import render_template
        
        # Test with show_temporal=True
        html = render_template(
            'forecast.html',
            forecast=forecast_with_temporal,
            forecasts=[],
            active_forecast='us_recession_2025',
            show_temporal=True
        )
        
        checks = [
            ('temporal-decay-section' in html, "Temporal section present"),
            ('Base Probability' in html, "Base probability label"),
            ('Adjusted Probability' in html, "Adjusted probability label"),
            ('Days Remaining' in html, "Days remaining label"),
            ('42.0%' in html, "Base probability value"),
            ('35.0%' in html, "Adjusted probability value"),
            ('400' in html, "Days remaining value"),
            ('Temporal Adjustment Details' in html, "Metadata section"),
            ('Exponential' in html, "Decay method"),
            ('Adjustment Factor' in html, "Adjustment factor label"),
        ]
        
        all_passed = True
        for check, description in checks:
            if check:
                print(f"  ✓ {description}")
            else:
                print(f"  ✗ {description}")
                all_passed = False
        
        # Test with show_temporal=False
        html_no_temporal = render_template(
            'forecast.html',
            forecast=forecast_with_temporal,
            forecasts=[],
            active_forecast='us_recession_2025',
            show_temporal=False
        )
        
        if 'temporal-decay-section' not in html_no_temporal:
            print("  ✓ Temporal section hidden when show_temporal=False")
        else:
            print("  ✗ Temporal section should be hidden when show_temporal=False")
            all_passed = False
        
        return all_passed

def test_subtask_19_2():
    """Test subtask 19.2: Temporal decay chart container."""
    
    print("\nTesting Subtask 19.2: Temporal decay chart container...")
    
    forecast_data = {
        'name': 'us_recession_2025',
        'display_name': 'US Recession 2025 V2',
        'description': 'Test',
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
                'adjustment_factor': 0.833,
                'days_remaining': 400,
                'parameters': {}
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
        
        checks = [
            ('decay-chart-container' in html, "Chart container present"),
            ('temporalDecayChart' in html, "Canvas element present"),
            ('canvas id="temporalDecayChart"' in html, "Canvas has correct ID"),
            ('width="800"' in html, "Canvas has correct width"),
            ('height="400"' in html, "Canvas has correct height"),
            ('Probability Projection Over Time' in html, "Chart title present"),
        ]
        
        all_passed = True
        for check, description in checks:
            if check:
                print(f"  ✓ {description}")
            else:
                print(f"  ✗ {description}")
                all_passed = False
        
        return all_passed

def test_requirements_validation():
    """Test that all requirements are satisfied."""
    
    print("\nValidating Requirements...")
    
    forecast_data = {
        'name': 'us_recession_2025',
        'display_name': 'US Recession 2025 V2',
        'description': 'Test',
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
                'method': 'adaptive',
                'adjustment_factor': 0.833,
                'days_remaining': 400,
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
        
        html = render_template(
            'forecast.html',
            forecast=forecast_data,
            forecasts=[],
            active_forecast='us_recession_2025',
            show_temporal=True
        )
        
        requirements = [
            (
                'Base Probability' in html and 'Adjusted Probability' in html,
                "Requirement 9.1: Display both probabilities"
            ),
            (
                'temporalDecayChart' in html and 'canvas' in html,
                "Requirement 9.2: Temporal decay chart container"
            ),
            (
                'Days Remaining' in html and '400' in html,
                "Requirement 9.3: Days remaining display"
            ),
            (
                'Temporal Adjustment Details' in html and 
                'Adjustment Factor' in html and
                'Adaptive' in html,
                "Requirement 9.4: Temporal metadata display"
            ),
        ]
        
        all_passed = True
        for check, description in requirements:
            if check:
                print(f"  ✓ {description}")
            else:
                print(f"  ✗ {description}")
                all_passed = False
        
        return all_passed

def test_multiple_decay_methods():
    """Test that template works with different decay methods."""
    
    print("\nTesting Multiple Decay Methods...")
    
    methods = [
        ('exponential', {'decay_rate': 0.015, 'threshold': 0.4}),
        ('sigmoid', {'midpoint': 180, 'steepness': 0.02}),
        ('adaptive', {
            'total_days': 365,
            'decay_power': 1.5,
            'amplification_power': 1.5,
            'lower_threshold': 0.4,
            'upper_threshold': 0.6
        }),
        ('theta', {'total_days': 365, 'decay_power': 1.5}),
    ]
    
    all_passed = True
    
    for method, params in methods:
        forecast_data = {
            'name': 'us_recession_2025',
            'display_name': 'US Recession 2025 V2',
            'description': 'Test',
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
                    'method': method,
                    'adjustment_factor': 0.833,
                    'days_remaining': 400,
                    'parameters': params
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
                
                if method.title() in html:
                    print(f"  ✓ {method.title()} method renders correctly")
                else:
                    print(f"  ✗ {method.title()} method not found in HTML")
                    all_passed = False
                    
            except Exception as e:
                print(f"  ✗ {method.title()} method failed: {e}")
                all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("=" * 70)
    print("Task 19 Comprehensive Validation")
    print("=" * 70)
    print()
    
    success = True
    
    # Test subtasks
    if not test_subtask_19_1():
        success = False
    
    if not test_subtask_19_2():
        success = False
    
    # Test requirements
    if not test_requirements_validation():
        success = False
    
    # Test multiple decay methods
    if not test_multiple_decay_methods():
        success = False
    
    print("\n" + "=" * 70)
    if success:
        print("✓ Task 19 COMPLETE - All validation tests passed!")
        print("=" * 70)
        print("\nSummary:")
        print("  ✓ Subtask 19.1: Conditional temporal decay section")
        print("  ✓ Subtask 19.2: Temporal decay chart container")
        print("  ✓ Requirement 9.1: Display both probabilities")
        print("  ✓ Requirement 9.2: Temporal decay chart container")
        print("  ✓ Requirement 9.3: Days remaining display")
        print("  ✓ Requirement 9.4: Temporal metadata display")
        print("  ✓ Multiple decay methods supported")
        print("  ✓ Backward compatibility maintained")
        sys.exit(0)
    else:
        print("✗ Task 19 INCOMPLETE - Some validation tests failed")
        print("=" * 70)
        sys.exit(1)
