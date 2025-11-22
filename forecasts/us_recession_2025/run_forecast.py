#!/usr/bin/env python3
"""
Standalone script to run the US Recession 2025 forecast model.

This script can be run directly without starting the web interface:
    python forecasts/us_recession_2025/run_forecast.py

Or as a module:
    python -m forecasts.us_recession_2025.run_forecast
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from forecasts.us_recession_2025.model import RecessionModel
from forecasts.us_recession_2025.config import DEFAULT_PARAMS, PARAMETER_SCHEMAS
from lib.database import get_forecast_history


def print_separator(char='=', length=70):
    """Print a separator line."""
    print(char * length)


def print_section(title):
    """Print a section header."""
    print(f"\n{title}")
    print("-" * len(title))


def run_forecast(show_history=True, history_limit=10):
    """
    Run the US Recession 2025 forecast and display results.
    
    Args:
        show_history: Whether to display historical forecasts
        history_limit: Number of historical entries to show
    """
    print_separator()
    print("US RECESSION 2025 FORECAST")
    print_separator()
    
    # Initialize model
    print("\nInitializing model...")
    try:
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
        print(f"    Default: {param_info['default']} (range: {param_info['min_value']} - {param_info['max_value']})")
    
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
    
    # Display indicator values
    if model._last_indicators:
        print_section("Economic Indicators")
        indicators = model._last_indicators
        
        print(f"  Yield Curve (10Y-2Y): {indicators['yield_curve']:.2f}")
        print(f"    Date: {indicators['timestamps']['yield_curve']}")
        
        print(f"\n  Unemployment Rate: {indicators['unemployment']:.2f}%")
        print(f"    Date: {indicators['timestamps']['unemployment']}")
        
        print(f"\n  GDP Growth: {indicators['gdp']:.2f}%")
        print(f"    Date: {indicators['timestamps']['gdp']}")
        
        print(f"\n  Consumer Confidence: {indicators['consumer_confidence']:.2f}")
        print(f"    Date: {indicators['timestamps']['consumer_confidence']}")
        
        print(f"\n  Leading Indicators: {indicators['leading_indicators']:.2f}")
        print(f"    Date: {indicators['timestamps']['leading_indicators']}")
        
        print(f"\n  Jobless Claims: {indicators['jobless_claims']:,.0f}")
        print(f"    Date: {indicators['timestamps']['jobless_claims']}")
    
    # Display historical data
    if show_history:
        print_section(f"Historical Forecasts (Last {history_limit})")
        try:
            history = get_forecast_history('us_recession_2025', limit=history_limit)
            
            if history and len(history) > 0:
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
  python forecasts/us_recession_2025/run_forecast.py
  python forecasts/us_recession_2025/run_forecast.py --no-history
  python forecasts/us_recession_2025/run_forecast.py --history-limit 20
        """
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
        history_limit=args.history_limit
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
