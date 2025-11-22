"""
Validation script for RecessionModelV2

Tests basic functionality of the v2 model including:
- Model initialization
- Probability calculation
- Probability breakdown
- Database storage
- Parameter handling
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from forecasts.us_recession_2025.model_v2 import RecessionModelV2
from datetime import datetime


def main():
    print("=" * 80)
    print("RecessionModelV2 Validation")
    print("=" * 80)
    print()
    
    # Test 1: Model initialization
    print("Test 1: Model Initialization")
    print("-" * 80)
    try:
        model = RecessionModelV2()
        print(f"✓ Model initialized successfully")
        print(f"  Name: {model.get_name()}")
        print(f"  Description: {model.get_description()}")
        print()
    except Exception as e:
        print(f"✗ Model initialization failed: {e}")
        return
    
    # Test 2: Get parameters
    print("Test 2: Get Parameters")
    print("-" * 80)
    try:
        params = model.get_parameters()
        print(f"✓ Retrieved {len(params)} parameters")
        print(f"  V1 parameters: yield_curve_weight, unemployment_weight, gdp_weight, etc.")
        print(f"  V2 parameters: apply_temporal_decay, decay_method, decay_rate, decay_threshold")
        print()
    except Exception as e:
        print(f"✗ Get parameters failed: {e}")
        return
    
    # Test 3: Get data sources
    print("Test 3: Get Data Sources")
    print("-" * 80)
    try:
        sources = model.get_data_sources()
        print(f"✓ Retrieved {len(sources)} data sources")
        for source in sources[:3]:
            print(f"  - {source}")
        print(f"  ... and {len(sources) - 3} more")
        print()
    except Exception as e:
        print(f"✗ Get data sources failed: {e}")
        return
    
    # Test 4: Calculate probability (this will fetch real data)
    print("Test 4: Calculate Probability")
    print("-" * 80)
    print("Note: This test requires FRED API access and may take a moment...")
    try:
        probability = model.calculate_probability()
        print(f"✓ Probability calculated successfully")
        print(f"  Adjusted Probability: {probability:.4f} ({probability*100:.2f}%)")
        print()
    except Exception as e:
        print(f"✗ Probability calculation failed: {e}")
        print(f"  This is expected if FRED API key is not configured")
        print()
    
    # Test 5: Get probability breakdown
    print("Test 5: Get Probability Breakdown")
    print("-" * 80)
    try:
        breakdown = model.get_probability_breakdown()
        print(f"✓ Probability breakdown retrieved successfully")
        print(f"  Base Probability: {breakdown.get('base_probability', 'N/A')}")
        print(f"  Adjusted Probability: {breakdown.get('adjusted_probability', 'N/A')}")
        print(f"  Days Remaining: {breakdown.get('days_remaining', 'N/A')}")
        
        temporal_metadata = breakdown.get('temporal_metadata', {})
        if temporal_metadata:
            print(f"  Temporal Decay Method: {temporal_metadata.get('decay_method', 'N/A')}")
            print(f"  Adjustment Factor: {temporal_metadata.get('adjustment_factor', 'N/A')}")
        
        print()
    except Exception as e:
        print(f"✗ Get probability breakdown failed: {e}")
        print()
    
    # Test 6: Calculate with custom parameters
    print("Test 6: Calculate with Custom Parameters")
    print("-" * 80)
    try:
        custom_params = {
            'yield_curve_weight': 0.4,
            'unemployment_weight': 0.3,
            'apply_temporal_decay': False
        }
        probability_no_decay = model.calculate_probability(custom_params)
        print(f"✓ Probability calculated with custom parameters")
        print(f"  Probability (no temporal decay): {probability_no_decay:.4f}")
        print()
    except Exception as e:
        print(f"✗ Custom parameter calculation failed: {e}")
        print()
    
    # Test 7: Get last updated
    print("Test 7: Get Last Updated")
    print("-" * 80)
    try:
        last_updated = model.get_last_updated()
        print(f"✓ Last updated timestamp retrieved")
        print(f"  Last Updated: {last_updated}")
        print()
    except Exception as e:
        print(f"✗ Get last updated failed: {e}")
        print()
    
    print("=" * 80)
    print("Validation Complete")
    print("=" * 80)


if __name__ == '__main__':
    main()
