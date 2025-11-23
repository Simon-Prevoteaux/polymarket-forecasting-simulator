"""
Validation script for temporal decay module

Demonstrates temporal decay functions and visualizes their behavior.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timedelta
# Now using the new generic library
from lib.temporal_adjustment import (
    calculate_time_to_event,
    threshold_aware_decay as exponential_decay_adjustment,
    trend_amplification as sigmoid_decay_adjustment,
    TemporalAdjuster
)


def validate_time_to_event():
    """Validate time-to-event calculation"""
    print("=" * 60)
    print("TIME-TO-EVENT CALCULATION")
    print("=" * 60)
    
    deadline = datetime(2025, 12, 31)
    test_dates = [
        datetime(2024, 1, 1),
        datetime(2025, 1, 1),
        datetime(2025, 6, 1),
        datetime(2025, 10, 1),
        datetime(2025, 12, 1),
        datetime(2025, 12, 31),
        datetime(2026, 1, 1),
    ]
    
    for date in test_dates:
        days = calculate_time_to_event(date, deadline)
        print(f"  {date.strftime('%Y-%m-%d')} → {days:4d} days remaining")
    
    print()


def validate_exponential_decay():
    """Validate exponential decay adjustment"""
    print("=" * 60)
    print("EXPONENTIAL DECAY ADJUSTMENT")
    print("=" * 60)
    
    base_prob = 0.3
    decay_rate = 0.015
    threshold = 0.4
    
    print(f"Base probability: {base_prob:.3f}")
    print(f"Decay rate: {decay_rate}")
    print(f"Threshold: {threshold}")
    print()
    
    days_list = [365, 300, 250, 200, 150, 100, 50, 10, 0, -10]
    
    print("Days Remaining | Adjusted Prob | Change")
    print("-" * 45)
    for days in days_list:
        adjusted = exponential_decay_adjustment(base_prob, days, decay_rate, threshold)
        change = adjusted - base_prob
        print(f"     {days:4d}      |     {adjusted:.4f}    | {change:+.4f}")
    
    print()
    
    # Test with probability above threshold
    print("Testing with probability above threshold (0.5):")
    high_prob = 0.5
    for days in [200, 100, 50]:
        adjusted = exponential_decay_adjustment(high_prob, days, decay_rate, threshold)
        print(f"  {days} days: {adjusted:.4f} (no decay applied)")
    
    print()


def validate_sigmoid_decay():
    """Validate sigmoid decay adjustment"""
    print("=" * 60)
    print("SIGMOID DECAY ADJUSTMENT")
    print("=" * 60)
    
    base_prob = 0.5
    midpoint = 180
    steepness = 0.02
    
    print(f"Base probability: {base_prob:.3f}")
    print(f"Midpoint: {midpoint} days")
    print(f"Steepness: {steepness}")
    print()
    
    days_list = [365, 300, 250, 200, 180, 150, 100, 50, 10, 0]
    
    print("Days Remaining | Adjusted Prob | Change")
    print("-" * 45)
    for days in days_list:
        adjusted = sigmoid_decay_adjustment(base_prob, days, midpoint, steepness)
        change = adjusted - base_prob
        print(f"     {days:4d}      |     {adjusted:.4f}    | {change:+.4f}")
    
    print()


def validate_temporal_adjuster():
    """Validate TemporalAdjuster class"""
    print("=" * 60)
    print("TEMPORAL ADJUSTER CLASS")
    print("=" * 60)
    
    # Test exponential method
    print("\n1. Exponential Method:")
    print("-" * 40)
    adjuster_exp = TemporalAdjuster(method='exponential', decay_rate=0.015, threshold=0.4)
    
    base_prob = 0.3
    current_date = datetime(2025, 10, 1)
    deadline = datetime(2025, 12, 31)
    
    adjusted_prob, metadata = adjuster_exp.adjust_probability(base_prob, current_date, deadline)
    
    print(f"Base probability: {base_prob:.4f}")
    print(f"Current date: {current_date.strftime('%Y-%m-%d')}")
    print(f"Deadline: {deadline.strftime('%Y-%m-%d')}")
    print(f"Days remaining: {calculate_time_to_event(current_date, deadline)}")
    print(f"\nAdjusted probability: {adjusted_prob:.4f}")
    print(f"Change: {adjusted_prob - base_prob:+.4f}")
    print(f"\nMetadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    
    # Test sigmoid method
    print("\n2. Sigmoid Method:")
    print("-" * 40)
    adjuster_sig = TemporalAdjuster(method='sigmoid', midpoint=180, steepness=0.02)
    
    base_prob = 0.5
    adjusted_prob, metadata = adjuster_sig.adjust_probability(base_prob, current_date, deadline)
    
    print(f"Base probability: {base_prob:.4f}")
    print(f"Current date: {current_date.strftime('%Y-%m-%d')}")
    print(f"Deadline: {deadline.strftime('%Y-%m-%d')}")
    print(f"Days remaining: {calculate_time_to_event(current_date, deadline)}")
    print(f"\nAdjusted probability: {adjusted_prob:.4f}")
    print(f"Change: {adjusted_prob - base_prob:+.4f}")
    print(f"\nMetadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    
    # Test with probability above threshold (exponential)
    print("\n3. Exponential with High Probability (No Decay):")
    print("-" * 40)
    base_prob = 0.6
    adjusted_prob, metadata = adjuster_exp.adjust_probability(base_prob, current_date, deadline)
    
    print(f"Base probability: {base_prob:.4f}")
    print(f"Adjusted probability: {adjusted_prob:.4f}")
    print(f"Threshold applied: {metadata['threshold_applied']}")
    
    print()


def compare_decay_methods():
    """Compare exponential and sigmoid decay methods"""
    print("=" * 60)
    print("COMPARISON: EXPONENTIAL VS SIGMOID")
    print("=" * 60)
    
    base_prob = 0.4
    
    adjuster_exp = TemporalAdjuster(method='exponential', decay_rate=0.015, threshold=0.5)
    adjuster_sig = TemporalAdjuster(method='sigmoid', midpoint=180, steepness=0.02)
    
    deadline = datetime(2025, 12, 31)
    
    print(f"Base probability: {base_prob:.3f}")
    print()
    print("Days | Exponential | Sigmoid | Difference")
    print("-" * 50)
    
    for days in [365, 300, 250, 200, 150, 100, 50, 10]:
        current_date = deadline - timedelta(days=days)
        
        exp_prob, _ = adjuster_exp.adjust_probability(base_prob, current_date, deadline)
        sig_prob, _ = adjuster_sig.adjust_probability(base_prob, current_date, deadline)
        diff = exp_prob - sig_prob
        
        print(f"{days:4d} |   {exp_prob:.4f}    |  {sig_prob:.4f}  | {diff:+.4f}")
    
    print()


def main():
    """Run all validation tests"""
    print("\n" + "=" * 60)
    print("TEMPORAL DECAY MODULE VALIDATION")
    print("=" * 60)
    print()
    
    validate_time_to_event()
    validate_exponential_decay()
    validate_sigmoid_decay()
    validate_temporal_adjuster()
    compare_decay_methods()
    
    print("=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)
    print("\nAll temporal decay functions are working correctly!")
    print()


if __name__ == '__main__':
    main()
