"""
Sample data validation for probability utilities.

Tests probability functions with realistic sample data to ensure outputs are in valid range.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import probability


def test_sample_data():
    """Test probability functions with sample data."""
    print("=" * 70)
    print("PROBABILITY UTILITIES SAMPLE DATA VALIDATION")
    print("=" * 70)
    
    # Test normalize_probability
    print("\n1. Testing normalize_probability:")
    test_values = [-0.5, 0.0, 0.25, 0.5, 0.75, 1.0, 1.5]
    for val in test_values:
        result = probability.normalize_probability(val)
        print(f"   normalize_probability({val:5.2f}) = {result:.2f}")
        assert 0 <= result <= 1, f"Result {result} is outside [0, 1]"
    print("   ✓ All results in valid range [0, 1]")
    
    # Test combine_probabilities
    print("\n2. Testing combine_probabilities:")
    
    # Equal weights
    probs1 = [0.2, 0.5, 0.8]
    result1 = probability.combine_probabilities(probs1)
    print(f"   Equal weights: {probs1} → {result1:.3f}")
    assert 0 <= result1 <= 1
    
    # Custom weights
    probs2 = [0.3, 0.7]
    weights2 = [0.8, 0.2]
    result2 = probability.combine_probabilities(probs2, weights2)
    print(f"   Weighted: {probs2} with weights {weights2} → {result2:.3f}")
    assert 0 <= result2 <= 1
    
    # Multiple probabilities
    probs3 = [0.1, 0.2, 0.3, 0.4, 0.5]
    result3 = probability.combine_probabilities(probs3)
    print(f"   Multiple: {probs3} → {result3:.3f}")
    assert 0 <= result3 <= 1
    
    print("   ✓ All results in valid range [0, 1]")
    
    # Test logistic_transform
    print("\n3. Testing logistic_transform:")
    test_inputs = [-5, -2, -1, 0, 1, 2, 5]
    for x in test_inputs:
        result = probability.logistic_transform(x)
        print(f"   logistic_transform({x:3d}) = {result:.4f}")
        assert 0 <= result <= 1
    
    # Test with different parameters
    result_centered = probability.logistic_transform(3, center=3, scale=1)
    print(f"   logistic_transform(3, center=3, scale=1) = {result_centered:.4f}")
    assert 0 <= result_centered <= 1
    
    print("   ✓ All results in valid range [0, 1]")
    
    # Test bayesian_update
    print("\n4. Testing bayesian_update:")
    
    # Strong evidence for hypothesis
    result1 = probability.bayesian_update(0.5, 0.9, 0.1)
    print(f"   Prior=0.5, L+=0.9, L-=0.1 → Posterior={result1:.3f} (strong evidence FOR)")
    assert 0 <= result1 <= 1
    assert result1 > 0.5, "Should increase from prior"
    
    # Strong evidence against hypothesis
    result2 = probability.bayesian_update(0.5, 0.1, 0.9)
    print(f"   Prior=0.5, L+=0.1, L-=0.9 → Posterior={result2:.3f} (strong evidence AGAINST)")
    assert 0 <= result2 <= 1
    assert result2 < 0.5, "Should decrease from prior"
    
    # No discriminating evidence
    result3 = probability.bayesian_update(0.5, 0.5, 0.5)
    print(f"   Prior=0.5, L+=0.5, L-=0.5 → Posterior={result3:.3f} (no change)")
    assert 0 <= result3 <= 1
    assert abs(result3 - 0.5) < 0.01, "Should stay near prior"
    
    # Medical test scenario
    result4 = probability.bayesian_update(0.01, 0.95, 0.10)
    print(f"   Medical test: Prior=0.01, Sensitivity=0.95, FPR=0.10 → Posterior={result4:.4f}")
    assert 0 <= result4 <= 1
    
    print("   ✓ All results in valid range [0, 1]")
    
    # Test realistic forecasting scenario
    print("\n5. Testing realistic forecasting scenario:")
    
    # Combine multiple indicator signals
    indicator_probs = [0.35, 0.42, 0.55, 0.48, 0.51]
    indicator_weights = [0.3, 0.25, 0.2, 0.15, 0.1]
    
    combined = probability.combine_probabilities(indicator_probs, indicator_weights)
    print(f"   Combined indicators: {combined:.3f}")
    assert 0 <= combined <= 1
    
    # Apply logistic transform to z-score
    z_score = 1.5  # Standard deviations from mean
    transformed = probability.logistic_transform(z_score)
    print(f"   Z-score {z_score} → Probability: {transformed:.3f}")
    assert 0 <= transformed <= 1
    
    # Update with new evidence
    prior = combined
    updated = probability.bayesian_update(prior, 0.7, 0.3)
    print(f"   Bayesian update: {prior:.3f} → {updated:.3f}")
    assert 0 <= updated <= 1
    
    # Normalize final result
    final = probability.normalize_probability(updated)
    print(f"   Final probability: {final:.3f}")
    assert 0 <= final <= 1
    
    print("   ✓ All results in valid range [0, 1]")
    
    print("\n" + "=" * 70)
    print("ALL SAMPLE DATA VALIDATION PASSED ✓")
    print("=" * 70)
    return True


if __name__ == "__main__":
    try:
        success = test_sample_data()
        sys.exit(0 if success else 1)
    except AssertionError as e:
        print(f"\n✗ Validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
