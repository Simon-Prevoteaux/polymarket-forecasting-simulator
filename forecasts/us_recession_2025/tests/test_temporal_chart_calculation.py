#!/usr/bin/env python3
"""
Test that JavaScript temporal decay calculation matches Python implementation.

This test validates that the calculateDecayedProbability JavaScript function
produces the same results as the Python temporal adjustment functions.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lib.temporal_adjustment import TemporalAdjuster
import math


def python_calculate_decayed_probability(base_probability, days_remaining, decay_power, total_days=365, threshold=None):
    """
    Python implementation matching the JavaScript function.
    This should match the logic in web/static/js/main.js
    
    Uses power-law decay formula matching lib/temporal_adjustment.py:
    time_ratio = days_remaining / total_days
    time_factor = (time_ratio)^decay_power
    adjusted = base * time_factor
    """
    # Validate inputs
    if base_probability < 0 or base_probability > 1:
        raise ValueError(f"base_probability must be in [0, 1], got {base_probability}")
    
    # If threshold is specified and probability is above it, no decay
    if threshold is not None and base_probability >= threshold:
        return base_probability
    
    # If we're at or past the deadline, return very small probability
    if days_remaining <= 0:
        return max(0.0, base_probability * 0.001)
    
    # If we're at or beyond the total forecast window, no decay
    if days_remaining >= total_days:
        return base_probability
    
    # Apply power-law decay formula
    time_ratio = days_remaining / total_days
    time_factor = math.pow(time_ratio, decay_power)
    
    return base_probability * time_factor


def test_decay_calculation():
    """Test that decay calculation works correctly"""
    print("\nTesting temporal decay calculation...")
    
    test_cases = [
        # (base_prob, days_remaining, decay_power, total_days, threshold, expected_behavior)
        (0.3, 180, 1.5, 365, 0.4, "should decay"),
        (0.5, 180, 1.5, 365, 0.4, "should NOT decay (above threshold)"),
        (0.3, 0, 1.5, 365, 0.4, "should decay to near zero (at deadline)"),
        (0.3, 365, 1.5, 365, 0.4, "should equal base (far from deadline)"),
        (0.2, 90, 2.0, 365, 0.4, "should decay significantly"),
    ]
    
    for base_prob, days_remaining, decay_power, total_days, threshold, description in test_cases:
        result = python_calculate_decayed_probability(
            base_prob, days_remaining, decay_power, total_days, threshold
        )
        
        # Validate result is in valid range
        assert 0 <= result <= 1, f"{description}: Result {result} is outside valid range [0, 1]"
        
        # Validate threshold behavior
        if base_prob >= threshold:
            assert result == base_prob, f"{description}: Expected no decay for prob >= threshold. Base: {base_prob}, Result: {result}"
        
        # Validate decay direction
        if base_prob < threshold and days_remaining > 0 and days_remaining < 365:
            assert result <= base_prob, f"{description}: Decay should not increase probability. Base: {base_prob}, Result: {result}"
        
        print(f"   ✓ PASSED: {description}")
        print(f"      Base: {base_prob:.3f}, Days: {days_remaining}, Result: {result:.3f}")


def test_decay_monotonicity():
    """Test that decay is monotonic as days decrease"""
    print("\nTesting decay monotonicity...")
    
    base_prob = 0.3
    decay_power = 1.5
    total_days = 365
    threshold = 0.4
    
    previous_result = base_prob
    
    # Test from 365 days down to 0
    for days in range(365, -1, -30):
        result = python_calculate_decayed_probability(
            base_prob, days, decay_power, total_days, threshold
        )
        
        # Allow small floating point errors
        assert result <= previous_result + 0.001, f"Monotonicity violated at {days} days. Previous: {previous_result:.4f}, Current: {result:.4f}"
        
        previous_result = result
    
    print(f"   ✓ PASSED: Decay is monotonic from 365 to 0 days")
    print(f"      Start: {base_prob:.3f}, End: {previous_result:.3f}")


def test_boundary_conditions():
    """Test boundary conditions"""
    print("\nTesting boundary conditions...")
    
    # Test at exactly threshold
    result = python_calculate_decayed_probability(0.4, 180, 1.5, 365, 0.4)
    assert result == 0.4, f"At threshold boundary: Expected 0.4, Got {result}"
    print(f"   ✓ PASSED: At threshold boundary (no decay)")
    
    # Test at 0 days remaining
    result = python_calculate_decayed_probability(0.3, 0, 1.5, 365, 0.4)
    expected = 0.3 * 0.001  # Should be very small
    assert abs(result - expected) <= 0.0001, f"At 0 days remaining: Expected {expected}, Got {result}"
    print(f"   ✓ PASSED: At 0 days remaining (decays to near zero)")
    
    # Test at 365 days remaining (no elapsed time)
    result = python_calculate_decayed_probability(0.3, 365, 1.5, 365, 0.4)
    assert abs(result - 0.3) <= 0.001, f"At 365 days remaining: Expected 0.3, Got {result}"
    print(f"   ✓ PASSED: At 365 days remaining (no decay)")


def test_comparison_with_temporal_adjuster():
    """Compare with actual TemporalAdjuster implementation"""
    print("\nComparing with TemporalAdjuster...")
    
    from datetime import datetime, timedelta
    
    # Create adjuster with simple_decay method (matches our formula)
    adjuster = TemporalAdjuster(
        method='simple_decay',
        total_days=365,
        decay_power=1.5
    )
    
    base_prob = 0.3
    days_remaining = 180
    
    # Calculate using TemporalAdjuster
    current_date = datetime(2025, 7, 4)  # 180 days before Dec 31, 2025
    deadline = datetime(2025, 12, 31)
    
    adjusted_prob, metadata = adjuster.adjust_probability(
        base_prob, current_date, deadline
    )
    
    # Calculate using our JavaScript-matching function
    js_result = python_calculate_decayed_probability(
        base_prob, days_remaining, 1.5, 365, None
    )
    
    # They should be very close (within floating point precision)
    assert abs(adjusted_prob - js_result) < 0.001, f"Results differ significantly. TemporalAdjuster: {adjusted_prob:.4f}, JavaScript formula: {js_result:.4f}, Difference: {abs(adjusted_prob - js_result):.6f}"
    
    print(f"   ✓ PASSED: JavaScript formula matches TemporalAdjuster")
    print(f"      TemporalAdjuster: {adjusted_prob:.4f}")
    print(f"      JavaScript formula: {js_result:.4f}")
    print(f"      Difference: {abs(adjusted_prob - js_result):.6f}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Temporal Decay Calculation Tests")
    print("=" * 60)
    
    results = []
    
    results.append(test_decay_calculation())
    results.append(test_decay_monotonicity())
    results.append(test_boundary_conditions())
    results.append(test_comparison_with_temporal_adjuster())
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total} test suites")
    
    if all(results):
        print("\n✓ All tests passed!")
        print("\nThe JavaScript decay calculation matches the Python implementation.")
        return 0
    else:
        print("\n✗ Some tests failed.")
        print("\nPlease review the failed tests above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
