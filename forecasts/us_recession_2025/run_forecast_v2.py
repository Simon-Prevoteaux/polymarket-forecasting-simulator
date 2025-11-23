#!/usr/bin/env python3
"""
Standalone script to run the US Recession 2025 V2 forecast model.

This script demonstrates the enhanced V2 features including:
- Base and adjusted probabilities
- Additional economic indicators
- Engineered features
- Temporal decay adjustment details
- Historical trend analysis

Usage:
    python forecasts/us_recession_2025/run_forecast_v2.py
    python forecasts/us_recession_2025/run_forecast_v2.py --no-history
    python forecasts/us_recession_2025/run_forecast_v2.py --history-limit 20
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from forecasts.us_recession_2025.model_v2 import RecessionModelV2
from lib.database import get_forecast_history


def print_separator(char='=', length=80):
    """Print a separator line."""
    print(char * length)


def print_section(title):
    """Print a section header."""
    print(f"\n{title}")
    print("-" * len(title))


def format_percentage(value, decimals=2):
    """Format a probability as a percentage."""
    if value is None:
        return "N/A"
    return f"{value * 100:.{decimals}f}%"


def format_number(value, decimals=2):
    """Format a number with specified decimals."""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def run_forecast_v2(show_history=True, history_limit=10, compare_methods=True):
    """
    Run the US Recession 2025 V2 forecast and display enhanced results.
    
    Args:
        show_history: Whether to display historical forecasts
        history_limit: Number of historical entries to show
        compare_methods: Whether to compare all three decay methods
    """
    print_separator()
    print("US RECESSION 2025 FORECAST - VERSION 2")
    print("Enhanced Model with Temporal Decay & Feature Engineering")
    print_separator()
    
    # Initialize model
    print("\nInitializing V2 model...")
    try:
        model = RecessionModelV2()
        print(f"✓ Model: {model.get_name()}")
        print(f"  {model.get_description()}")
    except Exception as e:
        print(f"✗ Failed to initialize model: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Calculate probability and get breakdown
    print_section("Calculating Enhanced Forecast")
    print("Fetching economic indicators, engineering features, and applying temporal decay...")
    
    try:
        probability = model.calculate_probability()
        breakdown = model.get_probability_breakdown()
        print(f"\n✓ Calculation successful!")
    except Exception as e:
        print(f"\n✗ Calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Display main results
    print_section("FORECAST RESULTS")
    
    base_prob = breakdown.get('base_probability', probability)
    adjusted_prob = breakdown.get('adjusted_probability', probability)
    days_remaining = breakdown.get('days_remaining', 0)
    
    print(f"\n  BASE PROBABILITY (Economic Indicators):  {format_percentage(base_prob)}")
    print(f"  ADJUSTED PROBABILITY (With Time Decay):  {format_percentage(adjusted_prob)}")
    print(f"\n  Days Until Deadline (Dec 31, 2025):      {days_remaining} days")
    print(f"  Last Updated:                             {model.get_last_updated().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show adjustment impact
    if base_prob != adjusted_prob:
        adjustment = adjusted_prob - base_prob
        adjustment_pct = (adjustment / base_prob * 100) if base_prob > 0 else 0
        print(f"\n  Temporal Adjustment:                      {adjustment:+.4f} ({adjustment_pct:+.2f}%)")
    
    # Display temporal decay details
    temporal_metadata = breakdown.get('temporal_metadata', {})
    if temporal_metadata:
        print_section("Temporal Decay Details")
        
        decay_method = temporal_metadata.get('decay_method', 'N/A')
        decay_rate = temporal_metadata.get('decay_rate', 'N/A')
        threshold = temporal_metadata.get('threshold', 'N/A')
        threshold_applied = temporal_metadata.get('threshold_applied', False)
        adjustment_factor = temporal_metadata.get('adjustment_factor', 1.0)
        
        print(f"\n  Decay Method:        {decay_method}")
        print(f"  Decay Rate:          {decay_rate}")
        print(f"  Threshold:           {threshold}")
        print(f"  Threshold Applied:   {'Yes' if threshold_applied else 'No'}")
        print(f"  Adjustment Factor:   {format_number(adjustment_factor, 4)}")
        
        if threshold_applied and threshold != 'N/A':
            print(f"\n  Note: Base probability ({format_percentage(base_prob)}) is below threshold")
            print(f"        ({format_percentage(threshold)}), so temporal decay was applied.")
        elif threshold != 'N/A':
            print(f"\n  Note: Base probability ({format_percentage(base_prob)}) is above threshold")
            print(f"        ({format_percentage(threshold)}), so no temporal decay was applied.")
        else:
            print(f"\n  Note: {decay_method.capitalize()} decay method does not use a threshold.")
    
    # Compare all temporal adjustment methods (if enabled)
    if compare_methods:
        print("\n")
        compare_all_adjustment_methods(base_prob, days_remaining, model.deadline)
    
    # Display core economic indicators
    indicators = breakdown.get('indicators', {})
    timestamps = breakdown.get('timestamps', {})
    
    if indicators:
        print_section("Core Economic Indicators (V1)")
        
        # Yield Curve
        if 'yield_curve' in indicators:
            val = indicators['yield_curve']
            date = timestamps.get('yield_curve', 'N/A')
            print(f"\n  Yield Curve (10Y-2Y):        {format_number(val)} bps")
            print(f"    Date: {date}")
            if val < 0:
                print(f"    ⚠️  INVERTED - Strong recession signal")
            elif val < 0.5:
                print(f"    ⚠️  FLAT - Moderate recession signal")
        
        # Unemployment
        if 'unemployment' in indicators:
            val = indicators['unemployment']
            date = timestamps.get('unemployment', 'N/A')
            print(f"\n  Unemployment Rate:           {format_number(val)}%")
            print(f"    Date: {date}")
            if val > 5.0:
                print(f"    ⚠️  ELEVATED - Potential recession signal")
        
        # GDP Growth
        if 'gdp' in indicators:
            val = indicators['gdp']
            date = timestamps.get('gdp', 'N/A')
            print(f"\n  GDP Growth (Annual):         {format_number(val)}%")
            print(f"    Date: {date}")
            if val < 0:
                print(f"    ⚠️  NEGATIVE - Strong recession signal")
            elif val < 1.0:
                print(f"    ⚠️  WEAK - Moderate recession signal")
        
        # Consumer Confidence
        if 'consumer_confidence' in indicators:
            val = indicators['consumer_confidence']
            date = timestamps.get('consumer_confidence', 'N/A')
            print(f"\n  Consumer Confidence:         {format_number(val)}")
            print(f"    Date: {date}")
            if val < 70:
                print(f"    ⚠️  LOW - Recession signal")
        
        # Leading Indicators
        if 'leading_indicators' in indicators:
            val = indicators['leading_indicators']
            date = timestamps.get('leading_indicators', 'N/A')
            print(f"\n  Leading Indicators Index:    {format_number(val)}")
            print(f"    Date: {date}")
            if val < 0:
                print(f"    ⚠️  DECLINING - Recession signal")
        
        # Jobless Claims
        if 'jobless_claims' in indicators:
            val = indicators['jobless_claims']
            date = timestamps.get('jobless_claims', 'N/A')
            print(f"\n  Initial Jobless Claims:      {val:,.0f}")
            print(f"    Date: {date}")
            if val > 300000:
                print(f"    ⚠️  ELEVATED - Potential recession signal")
        
        # V2-specific indicators
        print_section("Additional Economic Indicators (V2)")
        
        # Credit Spread
        if 'credit_spread' in indicators:
            val = indicators['credit_spread']
            date = timestamps.get('credit_spread', 'N/A')
            print(f"\n  Credit Spread (BAA-10Y):     {format_number(val)} bps")
            print(f"    Date: {date}")
            if val > 2.0:
                print(f"    ⚠️  WIDENING - Credit stress signal")
        
        # Housing Starts
        if 'housing_starts' in indicators:
            val = indicators['housing_starts']
            date = timestamps.get('housing_starts', 'N/A')
            print(f"\n  Housing Starts:              {val:,.0f} units")
            print(f"    Date: {date}")
            if val < 1200000:
                print(f"    ⚠️  WEAK - Housing market slowdown")
        
        # Manufacturing PMI
        if 'manufacturing_pmi' in indicators:
            val = indicators['manufacturing_pmi']
            date = timestamps.get('manufacturing_pmi', 'N/A')
            print(f"\n  Manufacturing PMI:           {format_number(val)}")
            print(f"    Date: {date}")
            if val < 50:
                print(f"    ⚠️  CONTRACTION - Manufacturing declining")
        
        # Retail Sales
        if 'retail_sales' in indicators:
            val = indicators['retail_sales']
            date = timestamps.get('retail_sales', 'N/A')
            print(f"\n  Retail Sales:                {format_number(val)} (millions)")
            print(f"    Date: {date}")
        
        # Oil Price
        if 'oil_price' in indicators:
            val = indicators['oil_price']
            date = timestamps.get('oil_price', 'N/A')
            print(f"\n  Oil Price (WTI):             ${format_number(val)}/barrel")
            print(f"    Date: {date}")
        
        # VIX
        if 'vix' in indicators:
            val = indicators['vix']
            date = timestamps.get('vix', 'N/A')
            print(f"\n  VIX (Volatility Index):      {format_number(val)}")
            print(f"    Date: {date}")
            if val > 30:
                print(f"    ⚠️  HIGH - Market fear elevated")
            elif val > 20:
                print(f"    ⚠️  ELEVATED - Increased uncertainty")
    
    # Display engineered features
    features = breakdown.get('features', {})
    if features:
        print_section("Engineered Features")
        
        # Group features by type
        roc_features = {k: v for k, v in features.items() if 'roc' in k.lower()}
        ma_features = {k: v for k, v in features.items() if 'ma' in k.lower()}
        vol_features = {k: v for k, v in features.items() if 'volatility' in k.lower() or 'vol' in k.lower()}
        
        if roc_features:
            print("\n  Rate of Change Features:")
            for name, value in sorted(roc_features.items()):
                if value is not None:
                    print(f"    {name:40s} {format_number(value, 4)}")
        
        if ma_features:
            print("\n  Moving Average Features:")
            for name, value in sorted(ma_features.items()):
                if value is not None:
                    print(f"    {name:40s} {format_number(value, 4)}")
        
        if vol_features:
            print("\n  Volatility Features:")
            for name, value in sorted(vol_features.items()):
                if value is not None:
                    print(f"    {name:40s} {format_number(value, 4)}")
    
    # Display indicator signals
    indicator_signals = breakdown.get('indicator_signals', {})
    if indicator_signals:
        print_section("Indicator Signal Strengths")
        print("\n  (Individual probability contributions from each indicator)")
        print()
        
        for name, signal in sorted(indicator_signals.items()):
            signal_pct = format_percentage(signal)
            bar_length = int(signal * 40)
            bar = '█' * bar_length + '░' * (40 - bar_length)
            print(f"  {name:25s} {signal_pct:>8s}  {bar}")
    
    # Display historical forecasts
    if show_history:
        print_section(f"Historical Forecasts (Last {history_limit})")
        try:
            # Use the table name without 'forecast_' prefix since get_forecast_history adds it
            history = get_forecast_history('us_recession_2025_v2', limit=history_limit)
            
            if history and len(history) > 0:
                print(f"\n  {'Date':<20} {'Base':<10} {'Adjusted':<10} {'Days':<6} {'Trend'}")
                print("  " + "-" * 70)
                
                prev_adjusted = None
                for entry in history:
                    date_str = entry['calculated_at'][:19]
                    base_prob = entry.get('base_probability', 0)
                    adj_prob = entry.get('adjusted_probability', base_prob)
                    days = entry.get('days_remaining', 0)
                    
                    base_str = format_percentage(base_prob, 1)
                    adj_str = format_percentage(adj_prob, 1)
                    days_str = str(days)
                    
                    # Calculate trend
                    if prev_adjusted is not None:
                        diff = adj_prob - prev_adjusted
                        if abs(diff) < 0.001:
                            trend = "→"
                        elif diff > 0:
                            trend = f"↑ +{diff * 100:.1f}%"
                        else:
                            trend = f"↓ {diff * 100:.1f}%"
                    else:
                        trend = ""
                    
                    print(f"  {date_str:<20} {base_str:<10} {adj_str:<10} {days_str:<6} {trend}")
                    prev_adjusted = adj_prob
                
                # Trend analysis
                if len(history) >= 2:
                    print("\n  Trend Analysis:")
                    first_prob = history[-1].get('adjusted_probability', 0)
                    last_prob = history[0].get('adjusted_probability', 0)
                    change = last_prob - first_prob
                    change_pct = (change / first_prob * 100) if first_prob > 0 else 0
                    
                    if abs(change) < 0.01:
                        trend_desc = "STABLE - Probability relatively unchanged"
                    elif change > 0:
                        trend_desc = f"INCREASING - Up {format_percentage(change)} ({change_pct:+.1f}%)"
                    else:
                        trend_desc = f"DECREASING - Down {format_percentage(abs(change))} ({change_pct:.1f}%)"
                    
                    print(f"    {trend_desc}")
            else:
                print("  No historical data available yet.")
        except Exception as e:
            print(f"  Error fetching history: {e}")
    
    # Interpretation
    print_section("Interpretation")
    
    if adjusted_prob < 0.15:
        interpretation = "VERY LOW RISK"
        description = "Economic indicators suggest minimal recession risk. The economy appears stable."
    elif adjusted_prob < 0.30:
        interpretation = "LOW RISK"
        description = "Some warning signs present, but the economy appears generally stable."
    elif adjusted_prob < 0.50:
        interpretation = "MODERATE RISK"
        description = "Mixed signals present. Elevated risk but recession not imminent."
    elif adjusted_prob < 0.70:
        interpretation = "HIGH RISK"
        description = "Multiple indicators suggest significant recession risk. Close monitoring warranted."
    else:
        interpretation = "VERY HIGH RISK"
        description = "Strong indicators of imminent recession. Multiple warning signals present."
    
    print(f"\n  Risk Level: {interpretation}")
    print(f"  {description}")
    
    # V2-specific interpretation
    if base_prob != adjusted_prob:
        print(f"\n  Temporal Context:")
        if adjusted_prob < base_prob:
            print(f"    The temporal decay adjustment has REDUCED the probability by")
            print(f"    {format_percentage(abs(adjusted_prob - base_prob))} as time passes without recession.")
        else:
            print(f"    The temporal decay adjustment has INCREASED the probability by")
            print(f"    {format_percentage(adjusted_prob - base_prob)}.")
    
    print_separator()
    print("✓ V2 Forecast complete!")
    print_separator()
    
    return True


def compare_all_adjustment_methods(base_prob, days_remaining, deadline):
    """
    Compare all temporal adjustment methods from lib.temporal_adjustment.
    
    Args:
        base_prob: Base probability before temporal adjustment
        days_remaining: Days until deadline
        deadline: Deadline date
    """
    from lib.temporal_adjustment import TemporalAdjuster
    from datetime import datetime, timedelta
    
    print_section("TEMPORAL ADJUSTMENT METHOD COMPARISON")
    print(f"\nComparing all adjustment methods with {days_remaining} days remaining")
    print(f"Base Probability: {format_percentage(base_prob)}\n")
    
    current_date = deadline - timedelta(days=days_remaining)
    
    # Define methods to test
    methods_to_test = [
        ('none', {}, 'No adjustment'),
        ('theta', {'decay_power': 1.5}, 'Theta decay (options-style)'),
        ('simple_decay', {'decay_power': 1.5}, 'Simple decay'),
        ('threshold_decay', {'decay_power': 1.5, 'threshold': 0.5}, 'Decay below 50% only'),
        ('trend_amplification', {'amplification_power': 1.5, 'threshold': 0.5}, 'Amplify trends'),
        ('confidence_convergence', {'convergence_power': 2.0, 'lower_threshold': 0.3, 'upper_threshold': 0.7}, 'Converge to 0 or 1'),
        ('adaptive', {'decay_power': 1.5, 'amplification_power': 1.5, 'lower_threshold': 0.4, 'upper_threshold': 0.6}, 'SMART: decay weak, amplify strong ⭐'),
    ]
    
    results = []
    
    for method_name, params, description in methods_to_test:
        try:
            adjuster = TemporalAdjuster(method=method_name, total_days=365, **params)
            adjusted_prob, metadata = adjuster.adjust_probability(
                base_prob,
                current_date,
                deadline
            )
            
            change = (adjusted_prob - base_prob) * 100
            pct_change = (change / (base_prob * 100)) * 100 if base_prob > 0 else 0
            
            results.append({
                'name': method_name,
                'description': description,
                'adjusted': adjusted_prob,
                'change': change,
                'pct_change': pct_change
            })
        except Exception as e:
            print(f"  ⚠️  {method_name} failed: {e}")
    
    # Display comparison table
    print("  Method                  | Adjusted Prob | Change      | % Change  | Description")
    print("  " + "-" * 95)
    
    for result in results:
        name = result['name']
        desc = result['description']
        adj = result['adjusted']
        change = result['change']
        pct = result['pct_change']
        
        # Highlight the adaptive method
        marker = " ⭐" if "SMART" in desc else "   "
        
        print(f"{marker}{name:22s} | {format_percentage(adj):>13s} | {change:>+10.2f}% | {pct:>+8.1f}% | {desc}")
    
    print(f"\n  💡 Interpretation for base probability of {format_percentage(base_prob)}:")
    
    if base_prob > 0.6:
        print(f"     - Signal is STRONG (>{format_percentage(0.6)})")
        print(f"     - 'adaptive' and 'trend_amplification' amplify toward 1.0")
        print(f"     - 'confidence_convergence' also pushes toward certainty")
        print(f"     - Simple decay methods reduce probability (may not be appropriate)")
    elif base_prob < 0.4:
        print(f"     - Signal is WEAK (<{format_percentage(0.4)})")
        print(f"     - Most methods apply decay toward 0.0")
        print(f"     - 'adaptive' intelligently decays weak signals")
        print(f"     - This reflects low likelihood with little time remaining")
    else:
        print(f"     - Signal is UNCERTAIN ({format_percentage(0.4)}-{format_percentage(0.6)})")
        print(f"     - 'adaptive' applies gentle decay")
        print(f"     - 'threshold_decay' may or may not apply")
        print(f"     - 'confidence_convergence' makes minimal adjustment")
    
    print(f"\n  🎯 Recommended: 'adaptive' method")
    print(f"     - Decays weak signals (like your {format_percentage(base_prob)})")
    print(f"     - Would amplify strong signals (>60%)")
    print(f"     - Context-aware and handles both cases appropriately")


def main():
    """Main entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run the US Recession 2025 V2 forecast model with enhanced features',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run V2 model with all features
  python forecasts/us_recession_2025/run_forecast_v2.py
  
  # Run without historical data
  python forecasts/us_recession_2025/run_forecast_v2.py --no-history
  
  # Show more historical entries
  python forecasts/us_recession_2025/run_forecast_v2.py --history-limit 20
  
  # Skip the decay method comparison
  python forecasts/us_recession_2025/run_forecast_v2.py --no-compare

V2 Features:
  - Base and adjusted probabilities
  - Temporal decay modeling
  - Additional economic indicators (credit spreads, housing, PMI, retail, oil, VIX)
  - Engineered features (rate of change, moving averages, volatility)
  - Enhanced historical trend analysis
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
    
    parser.add_argument(
        '--no-compare',
        action='store_true',
        help='Do not compare all three decay methods'
    )
    
    args = parser.parse_args()
    
    success = run_forecast_v2(
        show_history=not args.no_history,
        history_limit=args.history_limit,
        compare_methods=not args.no_compare
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
