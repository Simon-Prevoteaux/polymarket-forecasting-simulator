#!/usr/bin/env python3
"""
Demo script to show how temporal decay threshold affects the adjustment.
"""

from forecasts.us_recession_2025.temporal import exponential_decay_adjustment
from datetime import datetime

# Current situation
base_prob = 0.4882  # 48.82%
days_remaining = 38

print("="*70)
print("TEMPORAL DECAY THRESHOLD DEMONSTRATION")
print("="*70)
print(f"\nBase Probability: {base_prob*100:.2f}%")
print(f"Days Remaining: {days_remaining}")
print(f"Decay Rate: 0.015 (default)")
print("\n" + "-"*70)

# Test different thresholds
thresholds = [0.3, 0.4, 0.5, 0.6, 1.0]

print("\nThreshold | Adjusted Prob | Change    | Decay Applied?")
print("-"*70)

for threshold in thresholds:
    adjusted = exponential_decay_adjustment(
        base_prob, 
        days_remaining, 
        decay_rate=0.015, 
        threshold=threshold
    )
    change = (adjusted - base_prob) * 100
    applied = "YES" if adjusted != base_prob else "NO"
    
    print(f"{threshold:8.1f}  | {adjusted*100:12.2f}% | {change:+8.2f}% | {applied}")

print("\n" + "="*70)
print("RECOMMENDATION:")
print("="*70)
print(f"""
To apply temporal decay to your current probability of {base_prob*100:.2f}%:

Option 1: Increase threshold to 0.5 or higher
  - This will apply decay to probabilities below 50%
  - Run with: decay_threshold=0.5

Option 2: Set threshold to 1.0 to always apply decay
  - This will apply decay to ALL probabilities
  - Run with: decay_threshold=1.0

Option 3: Use sigmoid decay (no threshold)
  - Sigmoid method doesn't use a threshold
  - Run with: decay_method='sigmoid'
""")
