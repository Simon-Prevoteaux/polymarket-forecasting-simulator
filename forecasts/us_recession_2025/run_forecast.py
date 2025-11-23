#!/usr/bin/env python3
"""
Standalone script to run the US Recession 2025 forecast model.

This script can be run directly without starting the web interface:
    python forecasts/us_recession_2025/run_forecast.py
    python forecasts/us_recession_2025/run_forecast.py --version v2

Or as a module:
    python -m forecasts.us_recession_2025.run_forecast
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from forecasts.us_recession_2025.model import RecessionModel
from forecasts.us_recession_2025.model_v2 import RecessionModelV2
from forecasts.us_recession_2025.config import DEFAULT_PARAMS, PARAMETER_SCHEMAS
from lib.database import get_forecast_history


def print_separator(char='=', length=70):
    """Print a separator line."""
    print(char * length)


def print_section(title):
    """Print a section header."""
    print(f"\n{title}")
    print("-" * len(title))


def run_forecast(show_history=True, history_limit=10, version='v1'):
    """
    Run the US Recession 2025 forecast and display results.
    
    Args:
        show_history: Whether to display historical forecasts
        history_limit: Number of historical entries to show
        version: Model version to use ('v1' or 'v2')
    """
    print_separator()
    print(f"US RECESSION 2025 FORECAST ({version.upper()})")
    print_separator()
    
    # Initialize model
    print("\nInitializing model...")
    try:
        if version == 'v2':
            model = RecessionModelV2()
        else:
            model = RecessionModel()
        print(f"✓ Model: {model.get_name()}")
        print(f"  Description: {model.get_description()}")
    except Exception as e:
        print(f"✗ Failed to initialize model: {e}")
        return False
    
    # Display parameters
    print_section("Model Parameters")
    params = model.get_parameters()
    for param_name, param_info in params.items():
        print(f"  {param_info['description']}")
        # Handle different parameter formats (v1 vs v2)
        if 'min_value' in param_info and 'max_value' in param_info:
            print(f"    Default: {param_info['default']} (range: {param_info['min_value']} - {param_info['max_value']})")
        elif 'min' in param_info and 'max' in param_info:
            print(f"    Default: {param_info['default']} (range: {param_info['min']} - {param_info['max']})")
        elif 'options' in param_info:
            print(f"    Default: {param_info['default']} (options: {', '.join(param_info['options'])})")
        else:
            print(f"    Default: {param_info['default']}")
    
    # Calculate probability
    print_section("Calculating Forecast")
    print("Fetching economic indicators and calculating probability...")
    
    try:
        probability = model.calculate_probability()
        print(f"\n✓ Calculation successful!")
    except Exception as e:
        print(f"\n✗ Calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Display results
    print_section("Current Forecast Results")
    print(f"\n  RECESSION PROBABILITY: {probability * 100:.2f}%")
    print(f"  Last Updated: {model.get_last_updated().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display V2-specific information if available
    if version == 'v2' and hasattr(model, 'get_probability_breakdown'):
        try:
            breakdown = model.get_probability_breakdown()
            if breakdown and 'base_probability' in breakdown:
                print_section("V2 Enhanced Information")
                print(f"\n  Base Probability: {breakdown['base_probability'] * 100:.2f}%")
                print(f"  Adjusted Probability: {breakdown['adjusted_probability'] * 100:.2f}%")
                print(f"  Days Remaining: {breakdown.get('days_remaining', 'N/A')}")
                
                if 'temporal_metadata' in breakdown:
                    meta = breakdown['temporal_metadata']
                    print(f"\n  Temporal Adjustment:")
                    print(f"    Method: {meta.get('decay_method', 'N/A')}")
                    print(f"    Decay Rate: {meta.get('decay_rate', 'N/A')}")
                    print(f"    Threshold Applied: {meta.get('threshold_applied', 'N/A')}")
        except Exception as e:
            print(f"\n  (V2 breakdown not available: {e})")
    
    # Display indicator values
    indicators = None
    timestamps = {}
    
    if version == 'v2' and hasattr(model, 'get_probability_breakdown'):
        try:
            breakdown = model.get_probability_breakdown()
            indicators = breakdown.get('indicators', {})
            timestamps = breakdown.get('timestamps', {})
        except:
            pass
    elif hasattr(model, '_last_indicators') and model._last_indicators:
        indicators = model._last_indicators
        timestamps = indicators.get('timestamps', {})
    
    if indicators:
        print_section("Economic Indicators")
        
        if 'yield_curve' in indicators:
            print(f"  Yield Curve (10Y-2Y): {indicators['yield_curve']:.2f}")
            if 'yield_curve' in timestamps:
                print(f"    Date: {timestamps['yield_curve']}")
        
        if 'unemployment' in indicators:
            print(f"\n  Unemployment Rate: {indicators['unemployment']:.2f}%")
            if 'unemployment' in timestamps:
                print(f"    Date: {timestamps['unemployment']}")
        
        if 'gdp' in indicators:
            print(f"\n  GDP Growth: {indicators['gdp']:.2f}%")
            if 'gdp' in timestamps:
                print(f"    Date: {timestamps['gdp']}")
        
        if 'consumer_confidence' in indicators:
            print(f"\n  Consumer Confidence: {indicators['consumer_confidence']:.2f}")
            if 'consumer_confidence' in timestamps:
                print(f"    Date: {timestamps['consumer_confidence']}")
        
        if 'leading_indicators' in indicators:
            print(f"\n  Leading Indicators: {indicators['leading_indicators']:.2f}")
            if 'leading_indicators' in timestamps:
                print(f"    Date: {timestamps['leading_indicators']}")
        
        if 'jobless_claims' in indicators:
            print(f"\n  Jobless Claims: {indicators['jobless_claims']:,.0f}")
            if 'jobless_claims' in timestamps:
                print(f"    Date: {timestamps['jobless_claims']}")
        
        # V2-specific indicators
        if version == 'v2':
            if 'credit_spread' in indicators:
                print(f"\n  Credit Spread (BAA-10Y): {indicators['credit_spread']:.2f}")
                if 'credit_spread' in timestamps:
                    print(f"    Date: {timestamps['credit_spread']}")
            
            if 'housing_starts' in indicators:
                print(f"\n  Housing Starts: {indicators['housing_starts']:,.0f}")
                if 'housing_starts' in timestamps:
                    print(f"    Date: {timestamps['housing_starts']}")
            
            if 'manufacturing_pmi' in indicators:
                print(f"\n  Manufacturing PMI: {indicators['manufacturing_pmi']:.2f}")
                if 'manufacturing_pmi' in timestamps:
                    print(f"    Date: {timestamps['manufacturing_pmi']}")
            
            if 'retail_sales' in indicators:
                print(f"\n  Retail Sales: {indicators['retail_sales']:.2f}")
                if 'retail_sales' in timestamps:
                    print(f"    Date: {timestamps['retail_sales']}")
            
            if 'oil_price' in indicators:
                print(f"\n  Oil Price (WTI): ${indicators['oil_price']:.2f}")
                if 'oil_price' in timestamps:
                    print(f"    Date: {timestamps['oil_price']}")
            
            if 'vix' in indicators:
                print(f"\n  VIX (Volatility Index): {indicators['vix']:.2f}")
                if 'vix' in timestamps:
                    print(f"    Date: {timestamps['vix']}")
    
    # Display historical data
    if show_history:
        print_section(f"Historical Forecasts (Last {history_limit})")
        try:
            # Use appropriate table name based on version
            table_name = 'us_recession_2025_v2' if version == 'v2' else 'us_recession_2025'
            history = get_forecast_history(table_name, limit=history_limit)
            
            if history and len(history) > 0:
                if version == 'v2':
                    # V2 shows both base and adjusted probabilities
                    print(f"\n  {'Date':<20} {'Base':<12} {'Adjusted':<12} {'Trend'}")
                    print("  " + "-" * 60)
                    
                    prev_prob = None
                    for entry in history:
                        date_str = entry['calculated_at'][:19]  # Remove microseconds
                        base_prob = entry.get('base_probability', entry.get('probability', 0))
                        adj_prob = entry.get('adjusted_probability', base_prob)
                        base_str = f"{base_prob * 100:.2f}%"
                        adj_str = f"{adj_prob * 100:.2f}%"
                        
                        # Calculate trend based on adjusted probability
                        if prev_prob is not None:
                            diff = adj_prob - prev_prob
                            if abs(diff) < 0.001:
                                trend = "→"
                            elif diff > 0:
                                trend = f"↑ +{diff * 100:.2f}%"
                            else:
                                trend = f"↓ {diff * 100:.2f}%"
                        else:
                            trend = ""
                        
                        print(f"  {date_str:<20} {base_str:<12} {adj_str:<12} {trend}")
                        prev_prob = adj_prob
                else:
                    # V1 shows single probability
                    print(f"\n  {'Date':<20} {'Probability':<15} {'Trend'}")
                    print("  " + "-" * 50)
                    
                    prev_prob = None
                    for entry in history:
                        date_str = entry['calculated_at'][:19]  # Remove microseconds
                        prob = entry['probability']
                        prob_str = f"{prob * 100:.2f}%"
                        
                        # Calculate trend
                        if prev_prob is not None:
                            diff = prob - prev_prob
                            if abs(diff) < 0.001:
                                trend = "→ (no change)"
                            elif diff > 0:
                                trend = f"↑ (+{diff * 100:.2f}%)"
                            else:
                                trend = f"↓ ({diff * 100:.2f}%)"
                        else:
                            trend = ""
                        
                        print(f"  {date_str:<20} {prob_str:<15} {trend}")
                        prev_prob = prob
            else:
                print("  No historical data available yet.")
        except Exception as e:
            print(f"  Error fetching history: {e}")
    
    # Summary
    print_section("Interpretation")
    if probability < 0.15:
        interpretation = "Very Low - Economic indicators suggest minimal recession risk"
    elif probability < 0.30:
        interpretation = "Low - Some warning signs but economy appears stable"
    elif probability < 0.50:
        interpretation = "Moderate - Mixed signals, elevated risk but not imminent"
    elif probability < 0.70:
        interpretation = "High - Multiple indicators suggest significant recession risk"
    else:
        interpretation = "Very High - Strong indicators of imminent recession"
    
    print(f"  {interpretation}")
    
    print_separator()
    print("✓ Forecast complete!")
    print_separator()
    
    return True


def main():
    """Main entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run the US Recession 2025 forecast model',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run v1 model (default)
  python forecasts/us_recession_2025/run_forecast.py
  
  # Run v2 model with enhanced features
  python forecasts/us_recession_2025/run_forecast.py --version v2
  
  # Run without history
  python forecasts/us_recession_2025/run_forecast.py --no-history
  
  # Show more historical entries
  python forecasts/us_recession_2025/run_forecast.py --history-limit 20
  
  # Combine options
  python forecasts/us_recession_2025/run_forecast.py --version v2 --history-limit 5
        """
    )
    
    parser.add_argument(
        '--version',
        choices=['v1', 'v2'],
        default='v1',
        help='Model version to use (default: v1)'
    )
    
    parser.add_argument(
        '--no-history',
        action='store_true',
        help='Do not display historical forecasts'
    )
    
    parser.add_argument(
        '--history-limit',
        type=int,
        default=10,
        help='Number of historical entries to show (default: 10)'
    )
    
    args = parser.parse_args()
    
    success = run_forecast(
        show_history=not args.no_history,
        history_limit=args.history_limit,
        version=args.version
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
