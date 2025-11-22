#!/usr/bin/env python3
"""
Standalone script to run the Election 2028 forecast model.

This script can be run directly without starting the web interface:
    python forecasts/election_2028/run_forecast.py

Or as a module:
    python -m forecasts.election_2028.run_forecast

NOTE: This is a DEMO forecast using randomly generated data.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from forecasts.election_2028.model import ElectionModel
from forecasts.election_2028.config import DEFAULT_PARAMS, PARAMETER_SCHEMAS
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
    Run the Election 2028 forecast and display results.
    
    Args:
        show_history: Whether to display historical forecasts
        history_limit: Number of historical entries to show
    """
    print_separator()
    print("US PRESIDENTIAL ELECTION 2028 FORECAST")
    print_separator()
    print("\n⚠️  NOTE: This is a DEMO forecast using randomly generated data.")
    print("    It is NOT a real election forecast.\n")
    
    # Initialize model
    print("Initializing model...")
    try:
        model = ElectionModel()
        print(f"✓ Model: {model.get_name()}")
        print(f"  Description: {model.get_description()[:80]}...")
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
    print("Generating election indicators and calculating probability...")
    print("(Using randomly generated demo data)")
    
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
    print(f"\n  DEMOCRATIC VICTORY PROBABILITY: {probability * 100:.2f}%")
    print(f"  Republican Victory Probability: {(1 - probability) * 100:.2f}%")
    print(f"  Last Updated: {model.get_last_updated().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display indicator values
    if model._last_indicators:
        print_section("Election Indicators (DEMO DATA)")
        indicators = model._last_indicators
        
        print(f"  Polling Average: {indicators['polling']:.1f}%")
        print(f"    (Democratic candidate polling)")
        
        print(f"\n  Economic Index: {indicators['economic_index']:.1f}")
        print(f"    (Composite economic indicator, baseline: 100)")
        
        print(f"\n  Presidential Approval: {indicators['approval']:.1f}%")
        print(f"    (Current administration approval rating)")
        
        print(f"\n  Campaign Fundraising: ${indicators['fundraising']:.1f}M")
        print(f"    (Democratic campaign funds)")
        
        print(f"\n  Historical Advantage: {indicators['historical_advantage']:+.1f} points")
        print(f"    (Based on historical election patterns)")
    
    # Display historical data
    if show_history:
        print_section(f"Historical Forecasts (Last {history_limit})")
        try:
            history = get_forecast_history('election_2028', limit=history_limit)
            
            if history and len(history) > 0:
                print(f"\n  {'Date':<20} {'Dem Prob':<15} {'Rep Prob':<15} {'Trend'}")
                print("  " + "-" * 65)
                
                prev_prob = None
                for entry in history:
                    date_str = entry['calculated_at'][:19]  # Remove microseconds
                    prob = entry['probability']
                    dem_prob_str = f"{prob * 100:.2f}%"
                    rep_prob_str = f"{(1 - prob) * 100:.2f}%"
                    
                    # Calculate trend
                    if prev_prob is not None:
                        diff = prob - prev_prob
                        if abs(diff) < 0.001:
                            trend = "→ (no change)"
                        elif diff > 0:
                            trend = f"↑ Dem (+{diff * 100:.2f}%)"
                        else:
                            trend = f"↓ Dem ({diff * 100:.2f}%)"
                    else:
                        trend = ""
                    
                    print(f"  {date_str:<20} {dem_prob_str:<15} {rep_prob_str:<15} {trend}")
                    prev_prob = prob
            else:
                print("  No historical data available yet.")
        except Exception as e:
            print(f"  Error fetching history: {e}")
    
    # Summary
    print_section("Interpretation")
    if probability < 0.35:
        interpretation = "Strong Republican Advantage - Multiple indicators favor Republican victory"
        winner = "Republican"
        confidence = "High"
    elif probability < 0.45:
        interpretation = "Lean Republican - Indicators slightly favor Republican victory"
        winner = "Republican"
        confidence = "Moderate"
    elif probability < 0.55:
        interpretation = "Toss-Up - Race is too close to call, could go either way"
        winner = "Toss-Up"
        confidence = "Low"
    elif probability < 0.65:
        interpretation = "Lean Democratic - Indicators slightly favor Democratic victory"
        winner = "Democratic"
        confidence = "Moderate"
    else:
        interpretation = "Strong Democratic Advantage - Multiple indicators favor Democratic victory"
        winner = "Democratic"
        confidence = "High"
    
    print(f"  {interpretation}")
    print(f"\n  Predicted Winner: {winner}")
    print(f"  Confidence Level: {confidence}")
    
    print_separator()
    print("✓ Forecast complete!")
    print("\n⚠️  REMINDER: This forecast uses randomly generated demo data.")
    print("    Do not use for actual election predictions!")
    print_separator()
    
    return True


def main():
    """Main entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run the Election 2028 forecast model (DEMO)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python forecasts/election_2028/run_forecast.py
  python forecasts/election_2028/run_forecast.py --no-history
  python forecasts/election_2028/run_forecast.py --history-limit 20

NOTE: This is a DEMO forecast using randomly generated data.
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
