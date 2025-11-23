#!/usr/bin/env python3
"""
Integration test to verify the template works with the actual v2 model.
"""

import sys
sys.path.append('.')

from web.app import app
from forecasts.us_recession_2025.model_v2 import RecessionModelV2

def test_v2_model_integration():
    """Test that the template integrates correctly with the v2 model."""
    
    print("Testing template integration with RecessionModelV2...")
    
    try:
        # Initialize the v2 model
        model = RecessionModelV2()
        
        # Get breakdown data
        breakdown = model.get_probability_breakdown()
        
        print(f"\n✓ Successfully retrieved breakdown from v2 model")
        print(f"  - Base probability: {breakdown['base_probability']:.4f}")
        print(f"  - Adjusted probability: {breakdown['adjusted_probability']:.4f}")
        print(f"  - Days remaining: {breakdown['days_remaining']}")
        
        # Verify breakdown has all required fields
        required_fields = [
            'base_probability',
            'adjusted_probability',
            'days_remaining',
            'indicator_signals',
            'indicators',
            'features',
            'temporal_metadata',
            'timestamps'
        ]
        
        missing_fields = [f for f in required_fields if f not in breakdown]
        if missing_fields:
            print(f"\n✗ Missing required fields: {missing_fields}")
            return False
        
        print(f"✓ All required fields present in breakdown")
        
        # Verify temporal metadata structure
        if breakdown['temporal_metadata']:
            print(f"\n✓ Temporal metadata present:")
            for key, value in breakdown['temporal_metadata'].items():
                print(f"  - {key}: {value}")
        
        # Test template rendering with this data
        with app.test_request_context():
            from flask import render_template
            from datetime import datetime
            
            forecast_data = {
                'name': 'us_recession_2025',
                'display_name': model.get_name(),
                'description': model.get_description(),
                'probability': breakdown['adjusted_probability'],
                'last_updated': model.get_last_updated(),
                'indicators': breakdown['indicators'],
                'history': [],
                'parameters': model.get_parameters(),
                'data_sources': model.get_data_sources(),
                'breakdown': breakdown
            }
            
            html = render_template(
                'forecast.html',
                forecast=forecast_data,
                forecasts=[],
                active_forecast='us_recession_2025',
                show_temporal=True
            )
            
            # Verify key elements are in the rendered HTML
            assert 'temporal-decay-section' in html
            assert 'Base Probability' in html
            assert 'Adjusted Probability' in html
            assert 'Days Remaining' in html
            assert 'temporalDecayChart' in html
            
            print(f"\n✓ Template renders successfully with v2 model data")
            print(f"✓ All temporal decay elements present in HTML")
            
            return True
            
    except Exception as e:
        print(f"\n✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("V2 Model Template Integration Test")
    print("=" * 60)
    
    if test_v2_model_integration():
        print("\n" + "=" * 60)
        print("✓ Integration test passed!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("✗ Integration test failed")
        print("=" * 60)
        sys.exit(1)
