"""
Validation script for feature engineering module.

This script demonstrates the feature engineering functionality by:
1. Fetching real economic data
2. Calculating all engineered features
3. Displaying feature values and statistics
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from forecasts.us_recession_2025.features import FeatureEngineer
from forecasts.us_recession_2025.data_v2 import fetch_economic_indicators_v2
from datetime import datetime


def main():
    """Run feature engineering validation."""
    print("=" * 80)
    print("Feature Engineering Validation")
    print("=" * 80)
    print()
    
    # Initialize feature engineer
    engineer = FeatureEngineer()
    print("✓ FeatureEngineer initialized")
    print()
    
    # Fetch economic data
    print("Fetching economic indicators...")
    try:
        indicators = fetch_economic_indicators_v2(lookback_days=365)
        print(f"✓ Fetched data as of: {indicators['as_of_date']}")
        print()
    except Exception as e:
        print(f"✗ Error fetching data: {e}")
        print("Note: This requires a FRED API key in environment variable FRED_API_KEY")
        return
    
    # Engineer features
    print("Calculating engineered features...")
    features = engineer.engineer_features(indicators, indicators['raw_data'])
    print(f"✓ Generated {len(features)} features")
    print()
    
    # Display features by category
    print("=" * 80)
    print("Feature Summary")
    print("=" * 80)
    print()
    
    # Group features by type
    roc_features = {k: v for k, v in features.items() if 'roc_' in k}
    ma_features = {k: v for k, v in features.items() if 'ma_' in k}
    vol_features = {k: v for k, v in features.items() if 'volatility' in k}
    
    print(f"Rate of Change Features: {len(roc_features)}")
    print(f"Moving Average Features: {len(ma_features)}")
    print(f"Volatility Features: {len(vol_features)}")
    print()
    
    # Display sample features
    print("=" * 80)
    print("Sample Features (Rate of Change)")
    print("=" * 80)
    print()
    
    sample_indicators = ['unemployment', 'gdp', 'yield_curve']
    for indicator in sample_indicators:
        print(f"{indicator.upper()}:")
        for period in ['30d', '90d', '180d']:
            key = f'{indicator}_roc_{period}'
            if key in features:
                value = features[key]
                if value is not None:
                    print(f"  {period}: {value:+.4f} ({value*100:+.2f}%)")
                else:
                    print(f"  {period}: None (insufficient data)")
        print()
    
    print("=" * 80)
    print("Sample Features (Moving Averages)")
    print("=" * 80)
    print()
    
    for indicator in sample_indicators:
        print(f"{indicator.upper()}:")
        for window in ['30d', '90d']:
            key = f'{indicator}_ma_{window}'
            if key in features:
                value = features[key]
                if value is not None:
                    print(f"  {window}: {value:.4f}")
                else:
                    print(f"  {window}: None (insufficient data)")
        print()
    
    print("=" * 80)
    print("Sample Features (Volatility)")
    print("=" * 80)
    print()
    
    for indicator in sample_indicators:
        key = f'{indicator}_volatility'
        if key in features:
            value = features[key]
            if value is not None:
                print(f"{indicator.upper()}: {value:.4f}")
            else:
                print(f"{indicator.upper()}: None (insufficient data)")
    print()
    
    # Statistics
    print("=" * 80)
    print("Feature Statistics")
    print("=" * 80)
    print()
    
    total_features = len(features)
    non_null_features = sum(1 for v in features.values() if v is not None)
    null_features = total_features - non_null_features
    
    print(f"Total features: {total_features}")
    print(f"Non-null features: {non_null_features} ({non_null_features/total_features*100:.1f}%)")
    print(f"Null features: {null_features} ({null_features/total_features*100:.1f}%)")
    print()
    
    if null_features > 0:
        print("Note: Null features indicate insufficient historical data for calculation.")
        print("This is expected for features requiring long lookback periods (e.g., 180d).")
    
    print()
    print("=" * 80)
    print("Validation Complete")
    print("=" * 80)


if __name__ == '__main__':
    main()
