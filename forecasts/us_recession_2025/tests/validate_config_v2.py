"""
Validation script for config_v2.py

Tests that all configuration values are properly defined and accessible.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from forecasts.us_recession_2025.config_v2 import (
    V2_INDICATOR_SERIES,
    V2_INDICATOR_THRESHOLDS,
    TEMPORAL_DECAY_CONFIG,
    FORECAST_DEADLINE,
    FEATURE_ENGINEERING_CONFIG,
    V2_DEFAULT_WEIGHTS,
    V2_PARAMETER_SCHEMAS,
    V2_PARAMETER_SCHEMA,
    get_v2_default_parameters,
    get_all_indicator_thresholds,
    validate_v2_parameters
)


def validate_config():
    """Validate all configuration components."""
    print("=" * 80)
    print("VALIDATING CONFIG_V2.PY")
    print("=" * 80)
    
    # Test 1: V2 Indicator Series
    print("\n1. V2 Indicator Series:")
    print(f"   Number of new indicators: {len(V2_INDICATOR_SERIES)}")
    for name, series_id in V2_INDICATOR_SERIES.items():
        print(f"   - {name}: {series_id}")
    assert len(V2_INDICATOR_SERIES) == 6, "Should have 6 new indicators"
    print("   ✓ V2 indicator series validated")
    
    # Test 2: V2 Indicator Thresholds
    print("\n2. V2 Indicator Thresholds:")
    print(f"   Number of thresholds: {len(V2_INDICATOR_THRESHOLDS)}")
    for name, config in V2_INDICATOR_THRESHOLDS.items():
        print(f"   - {name}:")
        print(f"     Threshold: {config['recession_threshold']}")
        print(f"     Mean: {config['mean']}, Std: {config['std']}")
        assert 'recession_threshold' in config
        assert 'mean' in config
        assert 'std' in config
        assert 'description' in config
    assert len(V2_INDICATOR_THRESHOLDS) == 6, "Should have 6 threshold configs"
    print("   ✓ V2 indicator thresholds validated")
    
    # Test 3: Temporal Decay Config
    print("\n3. Temporal Decay Configuration:")
    for key, value in TEMPORAL_DECAY_CONFIG.items():
        print(f"   - {key}: {value}")
    assert 'method' in TEMPORAL_DECAY_CONFIG
    assert 'decay_rate' in TEMPORAL_DECAY_CONFIG
    assert 'threshold' in TEMPORAL_DECAY_CONFIG
    assert 'enabled' in TEMPORAL_DECAY_CONFIG
    assert TEMPORAL_DECAY_CONFIG['method'] in ['exponential', 'sigmoid']
    assert 0 < TEMPORAL_DECAY_CONFIG['decay_rate'] < 1
    assert 0 <= TEMPORAL_DECAY_CONFIG['threshold'] <= 1
    print("   ✓ Temporal decay config validated")
    
    # Test 4: Forecast Deadline
    print("\n4. Forecast Deadline:")
    print(f"   Deadline: {FORECAST_DEADLINE}")
    assert FORECAST_DEADLINE.year == 2025
    assert FORECAST_DEADLINE.month == 12
    assert FORECAST_DEADLINE.day == 31
    print("   ✓ Forecast deadline validated")
    
    # Test 5: Feature Engineering Config
    print("\n5. Feature Engineering Configuration:")
    for key, value in FEATURE_ENGINEERING_CONFIG.items():
        print(f"   - {key}: {value}")
    assert 'rate_of_change_periods' in FEATURE_ENGINEERING_CONFIG
    assert 'moving_average_windows' in FEATURE_ENGINEERING_CONFIG
    assert 'volatility_window' in FEATURE_ENGINEERING_CONFIG
    assert 'min_observations' in FEATURE_ENGINEERING_CONFIG
    print("   ✓ Feature engineering config validated")
    
    # Test 6: V2 Default Weights
    print("\n6. V2 Default Weights:")
    total_weight = sum(v for k, v in V2_DEFAULT_WEIGHTS.items() 
                      if k.endswith('_weight') and k != 'feature_weight_multiplier')
    print(f"   Total indicator weights: {total_weight:.2f}")
    for key, value in V2_DEFAULT_WEIGHTS.items():
        if key.endswith('_weight'):
            print(f"   - {key}: {value}")
    assert 0.95 <= total_weight <= 1.05, f"Weights should sum to ~1.0, got {total_weight}"
    print("   ✓ V2 default weights validated")
    
    # Test 7: Parameter Schemas
    print("\n7. V2 Parameter Schemas:")
    print(f"   Number of parameter schemas: {len(V2_PARAMETER_SCHEMAS)}")
    for name, schema in V2_PARAMETER_SCHEMAS.items():
        print(f"   - {name}: {schema.type}")
        assert hasattr(schema, 'name')
        assert hasattr(schema, 'type')
        assert hasattr(schema, 'default')
    print("   ✓ V2 parameter schemas validated")
    
    # Test 8: Web Interface Parameter Schema
    print("\n8. Web Interface Parameter Schema:")
    print(f"   Number of web parameters: {len(V2_PARAMETER_SCHEMA)}")
    for name, config in V2_PARAMETER_SCHEMA.items():
        print(f"   - {name}: {config['type']}")
        assert 'type' in config
        assert 'default' in config
        assert 'description' in config
    print("   ✓ Web interface parameter schema validated")
    
    # Test 9: get_v2_default_parameters()
    print("\n9. Default Parameters Function:")
    defaults = get_v2_default_parameters()
    print(f"   Number of default parameters: {len(defaults)}")
    assert 'apply_temporal_decay' in defaults
    assert 'decay_method' in defaults
    assert 'decay_rate' in defaults
    assert 'lookback_days' in defaults
    print("   ✓ Default parameters function validated")
    
    # Test 10: get_all_indicator_thresholds()
    print("\n10. All Indicator Thresholds Function:")
    all_thresholds = get_all_indicator_thresholds()
    print(f"    Total indicators (v1 + v2): {len(all_thresholds)}")
    assert len(all_thresholds) >= 11, "Should have at least 11 indicators (5 v1 + 6 v2)"
    print("    ✓ All indicator thresholds function validated")
    
    # Test 11: validate_v2_parameters()
    print("\n11. Parameter Validation Function:")
    
    # Test with valid parameters
    valid_params = {
        'decay_rate': 0.02,
        'decay_threshold': 0.5,
        'lookback_days': 500
    }
    validated = validate_v2_parameters(valid_params)
    assert validated['decay_rate'] == 0.02
    assert validated['decay_threshold'] == 0.5
    assert validated['lookback_days'] == 500
    print("    ✓ Valid parameters accepted")
    
    # Test with invalid parameters
    try:
        invalid_params = {'decay_rate': 1.5}  # Too high
        validate_v2_parameters(invalid_params)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"    ✓ Invalid parameters rejected: {e}")
    
    # Test with type conversion
    string_params = {'decay_rate': '0.025', 'lookback_days': '400'}
    validated = validate_v2_parameters(string_params)
    assert validated['decay_rate'] == 0.025
    assert validated['lookback_days'] == 400
    print("    ✓ Type conversion works")
    
    print("\n" + "=" * 80)
    print("ALL CONFIGURATION VALIDATIONS PASSED ✓")
    print("=" * 80)


if __name__ == '__main__':
    try:
        validate_config()
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
