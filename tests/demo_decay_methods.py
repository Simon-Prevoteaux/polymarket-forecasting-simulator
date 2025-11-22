#!/usr/bin/env python3
"""
Demo script comparing all three temporal decay methods.
"""

from forecasts.us_recession_2025.temporal import (
    exponential_decay_adjustment,
    sigmoid_decay_adjustment,
    theta_decay_adjustment
)

# Current situation
base_prob = 0.4882  # 48.82%
days_remaining = 38

print("="*80)
print("TEMPORAL DECAY METHOD COMPARISON")
print("="*80)
print(f"\nBase Probability: {base_prob*100:.2f}%")
print(f"Days Remaining: {days_remaining}")
print("\n" + "="*80)

# Method 1: Exponential (with threshold)
print("\n1. EXPONENTIAL DECAY (with threshold)")
print("-"*80)
print("Behavior: Only applies below threshold, exponential decay")
print("Use case: When you want to preserve high-risk signals\n")

for threshold in [0.4, 0.5, 1.0]:
    adjusted = exponential_decay_adjustment(base_prob, days_remaining, decay_rate=0.015, threshold=threshold)
    change = (adjusted - base_prob) * 100
    print(f"  Threshold {threshold:.1f}: {adjusted*100:6.2f}% (change: {change:+6.2f}%)")

# Method 2: Sigmoid
print("\n2. SIGMOID DECAY")
print("-"*80)
print("Behavior: Smooth S-curve transition, no threshold")
print("Use case: When you want gradual, smooth decay\n")

adjusted = sigmoid_decay_adjustment(base_prob, days_remaining, midpoint=180, steepness=0.02)
change = (adjusted - base_prob) * 100
print(f"  Adjusted: {adjusted*100:6.2f}% (change: {change:+6.2f}%)")

# Method 3: Theta (NEW - like options)
print("\n3. THETA DECAY (Options-style) ⭐ RECOMMENDED")
print("-"*80)
print("Behavior: Accelerating decay like options theta, no threshold")
print("Use case: When you want time decay that accelerates near expiration\n")

for power in [1.5, 2.0, 2.5, 3.0]:
    adjusted = theta_decay_adjustment(base_prob, days_remaining, total_days=365, decay_power=power)
    change = (adjusted - base_prob) * 100
    print(f"  Power {power:.1f}: {adjusted*100:6.2f}% (change: {change:+6.2f}%)")

# Show theta decay over time
print("\n" + "="*80)
print("THETA DECAY OVER TIME (power=2.0, like options)")
print("="*80)
print("\nDays Left | Probability | Decay %")
print("-"*40)

for days in [365, 180, 90, 60, 30, 14, 7, 1]:
    adjusted = theta_decay_adjustment(base_prob, days, total_days=365, decay_power=2.0)
    decay_pct = (1 - adjusted/base_prob) * 100
    print(f"{days:8d}  | {adjusted*100:10.2f}% | {decay_pct:6.1f}%")

print("\n" + "="*80)
print("RECOMMENDATION:")
print("="*80)
print("""
The THETA method (power=2.0) is recommended because:

✓ No arbitrary threshold - applies to all probabilities
✓ Accelerates as deadline approaches (like options theta decay)
✓ More intuitive - mirrors how prediction markets actually behave
✓ Quadratic decay (power=2.0) matches options pricing theory

With 38 days left and base probability of 48.82%:
- Theta decay reduces it to ~13.17% (73% decay)
- This reflects the time constraint: very little time for recession to occur

You can adjust decay_power to control aggressiveness:
- power=1.5: More gradual decay
- power=2.0: Standard (like options) ⭐
- power=2.5: More aggressive decay
- power=3.0: Very aggressive decay
""")
