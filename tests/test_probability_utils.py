"""
Unit tests for probability calculation utilities.

Tests specific examples and edge cases for probability functions.
"""

import pytest
import math
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import probability


class TestNormalizeProbability:
    """Tests for normalize_probability function."""
    
    def test_valid_probability_unchanged(self):
        """Valid probabilities should pass through unchanged."""
        assert probability.normalize_probability(0.0) == 0.0
        assert probability.normalize_probability(0.5) == 0.5
        assert probability.normalize_probability(1.0) == 1.0
        assert probability.normalize_probability(0.123) == 0.123
    
    def test_negative_clamped_to_zero(self):
        """Negative values should be clamped to 0."""
        assert probability.normalize_probability(-0.1) == 0.0
        assert probability.normalize_probability(-1.0) == 0.0
        assert probability.normalize_probability(-100.0) == 0.0
    
    def test_above_one_clamped_to_one(self):
        """Values above 1 should be clamped to 1."""
        assert probability.normalize_probability(1.1) == 1.0
        assert probability.normalize_probability(2.0) == 1.0
        assert probability.normalize_probability(100.0) == 1.0


class TestCombineProbabilities:
    """Tests for combine_probabilities function."""
    
    def test_empty_list_raises_error(self):
        """Empty probability list should raise ValueError."""
        with pytest.raises(ValueError, match="Cannot combine empty list"):
            probability.combine_probabilities([])
    
    def test_single_probability_returned(self):
        """Single probability should be returned unchanged."""
        assert probability.combine_probabilities([0.7]) == 0.7
        assert probability.combine_probabilities([0.0]) == 0.0
        assert probability.combine_probabilities([1.0]) == 1.0
    
    def test_equal_weights_default(self):
        """Without weights, should use equal weighting (average)."""
        result = probability.combine_probabilities([0.2, 0.4, 0.6])
        expected = (0.2 + 0.4 + 0.6) / 3
        assert result == pytest.approx(expected)
        
        result = probability.combine_probabilities([0.0, 1.0])
        assert result == pytest.approx(0.5)
    
    def test_weighted_combination(self):
        """Should correctly apply weights."""
        # 80% weight on 0.3, 20% weight on 0.7
        result = probability.combine_probabilities([0.3, 0.7], weights=[0.8, 0.2])
        expected = 0.3 * 0.8 + 0.7 * 0.2
        assert result == pytest.approx(expected)
        
        # Weights that don't sum to 1 should be normalized
        result = probability.combine_probabilities([0.3, 0.7], weights=[4, 1])
        expected = 0.3 * 0.8 + 0.7 * 0.2  # 4/5 and 1/5
        assert result == pytest.approx(expected)
    
    def test_invalid_probability_raises_error(self):
        """Probabilities outside [0, 1] should raise ValueError."""
        with pytest.raises(ValueError, match="must be in"):
            probability.combine_probabilities([0.5, 1.5])
        
        with pytest.raises(ValueError, match="must be in"):
            probability.combine_probabilities([-0.1, 0.5])
    
    def test_mismatched_weights_length_raises_error(self):
        """Weights length must match probabilities length."""
        with pytest.raises(ValueError, match="must match"):
            probability.combine_probabilities([0.3, 0.5, 0.7], weights=[0.5, 0.5])
    
    def test_negative_weights_raise_error(self):
        """Negative weights should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            probability.combine_probabilities([0.3, 0.7], weights=[0.5, -0.5])
    
    def test_zero_sum_weights_raise_error(self):
        """Weights that sum to zero should raise ValueError."""
        with pytest.raises(ValueError, match="cannot sum to zero"):
            probability.combine_probabilities([0.3, 0.7], weights=[0.0, 0.0])
    
    def test_multiple_probabilities_equal_weights(self):
        """Test with multiple probabilities and equal weights."""
        probs = [0.1, 0.2, 0.3, 0.4, 0.5]
        result = probability.combine_probabilities(probs)
        expected = sum(probs) / len(probs)
        assert result == pytest.approx(expected)


class TestLogisticTransform:
    """Tests for logistic_transform function."""
    
    def test_zero_input_default_params(self):
        """Input of 0 with default params should give 0.5."""
        result = probability.logistic_transform(0)
        assert result == pytest.approx(0.5)
    
    def test_large_positive_approaches_one(self):
        """Large positive values should approach 1."""
        result = probability.logistic_transform(10)
        assert result > 0.99
        
        result = probability.logistic_transform(100)
        assert result > 0.999
    
    def test_large_negative_approaches_zero(self):
        """Large negative values should approach 0."""
        result = probability.logistic_transform(-10)
        assert result < 0.01
        
        result = probability.logistic_transform(-100)
        assert result < 0.001
    
    def test_center_parameter(self):
        """Center parameter should shift the curve."""
        # With center=5, input of 5 should give 0.5
        result = probability.logistic_transform(5, center=5)
        assert result == pytest.approx(0.5)
        
        # With center=-3, input of -3 should give 0.5
        result = probability.logistic_transform(-3, center=-3)
        assert result == pytest.approx(0.5)
    
    def test_scale_parameter(self):
        """Scale parameter should affect steepness."""
        # Larger scale makes the curve less steep
        result_small_scale = probability.logistic_transform(1, scale=0.5)
        result_large_scale = probability.logistic_transform(1, scale=2.0)
        
        # With smaller scale, positive values should be closer to 1
        assert result_small_scale > result_large_scale
    
    def test_zero_scale_raises_error(self):
        """Scale of zero should raise ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            probability.logistic_transform(0, scale=0)
    
    def test_negative_scale_raises_error(self):
        """Negative scale should raise ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            probability.logistic_transform(0, scale=-1)
    
    def test_extreme_values_handled(self):
        """Extreme values should not cause overflow."""
        # Very large positive
        result = probability.logistic_transform(1000)
        assert 0 <= result <= 1
        
        # Very large negative
        result = probability.logistic_transform(-1000)
        assert 0 <= result <= 1
    
    def test_symmetry(self):
        """Logistic function should be symmetric around center."""
        center = 0
        delta = 2
        
        result_plus = probability.logistic_transform(center + delta, center=center)
        result_minus = probability.logistic_transform(center - delta, center=center)
        
        # Should be symmetric: f(c+d) + f(c-d) = 1
        assert result_plus + result_minus == pytest.approx(1.0)


class TestBayesianUpdate:
    """Tests for bayesian_update function."""
    
    def test_strong_evidence_for_hypothesis(self):
        """Strong evidence for hypothesis should increase probability."""
        # Prior 50%, evidence is 90% likely if true, 10% likely if false
        result = probability.bayesian_update(0.5, 0.9, 0.1)
        assert result == pytest.approx(0.9)
        assert result > 0.5  # Should increase from prior
    
    def test_strong_evidence_against_hypothesis(self):
        """Strong evidence against hypothesis should decrease probability."""
        # Prior 50%, evidence is 10% likely if true, 90% likely if false
        result = probability.bayesian_update(0.5, 0.1, 0.9)
        assert result == pytest.approx(0.1)
        assert result < 0.5  # Should decrease from prior
    
    def test_no_discriminating_evidence(self):
        """Equal likelihoods should leave prior unchanged."""
        result = probability.bayesian_update(0.5, 0.5, 0.5)
        assert result == pytest.approx(0.5)
        
        result = probability.bayesian_update(0.3, 0.7, 0.7)
        assert result == pytest.approx(0.3)
    
    def test_prior_zero_stays_zero(self):
        """Prior of 0 should stay 0 regardless of evidence."""
        result = probability.bayesian_update(0.0, 0.9, 0.1)
        assert result == 0.0
    
    def test_prior_one_stays_one(self):
        """Prior of 1 should stay 1 regardless of evidence."""
        result = probability.bayesian_update(1.0, 0.1, 0.9)
        assert result == 1.0
    
    def test_invalid_prior_raises_error(self):
        """Prior outside [0, 1] should raise ValueError."""
        with pytest.raises(ValueError, match="Prior must be in"):
            probability.bayesian_update(-0.1, 0.5, 0.5)
        
        with pytest.raises(ValueError, match="Prior must be in"):
            probability.bayesian_update(1.5, 0.5, 0.5)
    
    def test_invalid_likelihood_positive_raises_error(self):
        """Likelihood positive outside [0, 1] should raise ValueError."""
        with pytest.raises(ValueError, match="Likelihood positive must be in"):
            probability.bayesian_update(0.5, -0.1, 0.5)
        
        with pytest.raises(ValueError, match="Likelihood positive must be in"):
            probability.bayesian_update(0.5, 1.5, 0.5)
    
    def test_invalid_likelihood_negative_raises_error(self):
        """Likelihood negative outside [0, 1] should raise ValueError."""
        with pytest.raises(ValueError, match="Likelihood negative must be in"):
            probability.bayesian_update(0.5, 0.5, -0.1)
        
        with pytest.raises(ValueError, match="Likelihood negative must be in"):
            probability.bayesian_update(0.5, 0.5, 1.5)
    
    def test_both_likelihoods_zero_returns_prior(self):
        """When both likelihoods are zero, should return prior."""
        result = probability.bayesian_update(0.7, 0.0, 0.0)
        assert result == pytest.approx(0.7)
    
    def test_realistic_scenario(self):
        """Test with realistic medical test scenario."""
        # Disease prevalence: 1%
        # Test sensitivity (true positive rate): 95%
        # Test specificity (true negative rate): 90%, so false positive rate: 10%
        prior = 0.01
        likelihood_positive = 0.95  # P(positive test | have disease)
        likelihood_negative = 0.10  # P(positive test | no disease)
        
        result = probability.bayesian_update(prior, likelihood_positive, likelihood_negative)
        
        # Expected: 0.95 * 0.01 / (0.95 * 0.01 + 0.10 * 0.99) ≈ 0.0876
        expected = (0.95 * 0.01) / (0.95 * 0.01 + 0.10 * 0.99)
        assert result == pytest.approx(expected, abs=0.001)
        assert result > prior  # Positive test should increase probability


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
