#!/usr/bin/env python3
"""
Demo script showing how different temporal adjustment methods behave
across different probability levels and time horizons.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.temporal_adjustment import TemporalAdjuster
from datetime import datetime, timedelta


def demo_method_behavior():
    """Demonstrate how each method behaves with different probabilities."""
    
    print("="*90)
    print("TEMPORAL ADJUSTMENT METHODS - BEHAVIOR DEMONSTRATION")
    print("="*90)
    
    # Test scenarios
    scenarios = [
        (0.15, "Very Low Signal", "Recession very unlikely"),
        (0.35, "Low Signal", "Weak recession indicators"),
        (0.50, "Uncertain Signal", "Mixed signals"),
        (0.65, "High Signal", "Strong recession indicators"),
        (0.85, "Very High Signal", "Recession very likely"),
    ]
    
    days_remaining = 38
    deadline = datetime(2025, 12, 31)
    current_date = deadline - timedelta(days=days_remaining)
    
    print(f"\nScenario: {days_remaining} days until deadline\n")
    
    # Methods to test
    methods = [
        ('none', {}, 'Baseline'),
        ('simple_decay', {'decay_power': 1.5}, 'Simple Decay'),
        ('threshold_decay', {'decay_power': 1.5, 'threshold': 0.5}, 'Threshold Decay'),
        ('trend_amplification', {'amplification_power': 1.5, 'threshold': 0.5}, 'Trend Amplify'),
        ('confidence_convergence', {'convergence_power': 2.0, 'lower_threshold': 0.3, 'upper_threshold': 0.7}, 'Convergence'),
        ('adaptive', {'decay_power': 1.5, 'amplification_power': 1.5, 'lower_threshold': 0.4, 'upper_threshold': 0.6}, 'Adaptive ⭐'),
    ]
    
    for base_prob, signal_name, description in scenarios:
        print(f"\n{signal_name}: {base_prob*100:.0f}% - {description}")
        print("-" * 90)
        print(f"{'Method':<20} | {'Adjusted':>10} | {'Change':>10} | {'Behavior'}")
        print("-" * 90)
        
        for method_name, params, display_name in methods:
            try:
                adjuster = TemporalAdjuster(method=method_name, total_days=365, **params)
                adjusted_prob, metadata = adjuster.adjust_probability(
                    base_prob,
                    current_date,
                    deadline
                )
                
                change = (adjusted_prob - base_prob) * 100
                
                # Determine behavior
                if abs(change) < 0.5:
                    behavior = "No change"
                elif change < -20:
                    behavior = "Strong decay"
                elif change < -5:
                    behavior = "Moderate decay"
                elif change < 0:
                    behavior = "Gentle decay"
                elif change > 20:
                    behavior = "Strong amplification"
                elif change > 5:
                    behavior = "Moderate amplification"
                else:
                    behavior = "Gentle amplification"
                
                print(f"{display_name:<20} | {adjusted_prob*100:>9.1f}% | {change:>+9.1f}% | {behavior}")
                
            except Exception as e:
                print(f"{display_name:<20} | ERROR: {e}")
    
    print("\n" + "="*90)
    print("KEY INSIGHTS")
    print("="*90)
    print("""
1. SIMPLE DECAY: Always reduces probability as time passes
   - Good for: Events unlikely to occur
   - Problem: Reduces even strong signals

2. THRESHOLD DECAY: Only decays below threshold (50%)
   - Good for: Preserving strong signals
   - Problem: Hard cutoff at threshold

3. TREND AMPLIFICATION: Amplifies signals above/below threshold
   - Good for: Events with strengthening evidence
   - Problem: Can over-amplify weak signals

4. CONFIDENCE CONVERGENCE: Pushes toward 0 or 1 based on zones
   - Good for: Binary events with clear signals
   - Problem: Doesn't adjust uncertain signals

5. ADAPTIVE ⭐ (RECOMMENDED): Context-aware adjustment
   - Decays weak signals (<40%)
   - Amplifies strong signals (>60%)
   - Gentle decay for uncertain signals (40-60%)
   - Best for: Most real-world forecasts
    """)


def demo_time_evolution():
    """Show how probabilities evolve over time with different methods."""
    
    print("\n" + "="*90)
    print("TIME EVOLUTION - How Probabilities Change as Deadline Approaches")
    print("="*90)
    
    base_prob = 0.48  # Uncertain signal
    deadline = datetime(2025, 12, 31)
    
    print(f"\nBase Probability: {base_prob*100:.0f}% (Uncertain signal)")
    print("\nDays Remaining | No Adjust | Simple Decay | Threshold | Adaptive ⭐")
    print("-" * 75)
    
    for days in [365, 180, 90, 60, 30, 14, 7, 1]:
        current_date = deadline - timedelta(days=days)
        
        # No adjustment
        none_adj = TemporalAdjuster(method='none')
        none_prob, _ = none_adj.adjust_probability(base_prob, current_date, deadline)
        
        # Simple decay
        simple_adj = TemporalAdjuster(method='simple_decay', total_days=365, decay_power=1.5)
        simple_prob, _ = simple_adj.adjust_probability(base_prob, current_date, deadline)
        
        # Threshold decay
        thresh_adj = TemporalAdjuster(method='threshold_decay', total_days=365, decay_power=1.5, threshold=0.5)
        thresh_prob, _ = thresh_adj.adjust_probability(base_prob, current_date, deadline)
        
        # Adaptive
        adaptive_adj = TemporalAdjuster(method='adaptive', total_days=365, decay_power=1.5, amplification_power=1.5, lower_threshold=0.4, upper_threshold=0.6)
        adaptive_prob, _ = adaptive_adj.adjust_probability(base_prob, current_date, deadline)
        
        print(f"{days:>14d} | {none_prob*100:>8.1f}% | {simple_prob*100:>11.1f}% | {thresh_prob*100:>8.1f}% | {adaptive_prob*100:>9.1f}%")
    
    print("\n💡 Notice:")
    print("   - Simple decay: Aggressive reduction regardless of signal strength")
    print("   - Threshold: Same as simple (below 50% threshold)")
    print("   - Adaptive: More moderate, context-aware decay")


if __name__ == '__main__':
    demo_method_behavior()
    demo_time_evolution()
    
    print("\n" + "="*90)
    print("RECOMMENDATION")
    print("="*90)
    print("""
For the US Recession forecast with current probability of ~49%:

✅ USE 'adaptive' method:
   - Your 49% signal is in the uncertain zone (40-60%)
   - Adaptive applies gentle decay (not aggressive)
   - If probability rises above 60%, it would amplify instead
   - If probability drops below 40%, it would decay more
   - This matches your intuition: weak signals decay, strong signals amplify

❌ AVOID 'simple_decay':
   - Too aggressive for uncertain signals
   - Would decay even if recession evidence strengthens

⚠️  'threshold_decay' is okay but has hard cutoff
   - Works for your case (below 50%)
   - But doesn't adapt if signal strengthens above threshold
    """)
