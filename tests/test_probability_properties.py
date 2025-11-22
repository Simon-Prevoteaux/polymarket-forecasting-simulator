"""
Property-based tests for probability calculation utilities.

These tests verify universal properties that should hold across all inputs.
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import probability


# Feature: polymarket-forecasting-simulator, Property 1: Probability bounds enforcement
@given(
    value=st.floats(
        min_value=-1000.0,
        max_value=1000.0,
        allow_nan=False,
        allow_infinity=False
    )
)
@settings(max_examples=100)
def test_normalize_probability_bounds(value):
    """
    Property 1: Probability bounds enforcement (normalize_probability)
    
    For any input value, normalize_probability must return a value between 0 and 1 (inclusive).
    
    Validates: Requirements 2.1
    """
    result = probability.normalize_probability(value)
    assert 0.0 <= result <= 1.0, f"normalize_probability({value}) = {result}, which is outside [0, 1]"


# Feature: polymarket-forecasting-simulator, Property 1: Probability bounds enforcement
@given(
    probabilities=st.lists(
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=10
    ),
    weights=st.one_of(
        st.none(),
        st.lists(
            st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        )
    )
)
@settings(max_examples=100)
def test_combine_probabilities_bounds(probabilities, weights):
    """
    Property 1: Probability bounds enforcement (combine_probabilities)
    
    For any list of valid probabilities and optional weights, combine_probabilities 
    must return a value between 0 and 1 (inclusive).
    
    Validates: Requirements 2.1
    """
    # If weights provided, ensure length matches probabilities
    if weights is not None:
        if len(weights) != len(probabilities):
            # Adjust weights to match probabilities length
            if len(weights) < len(probabilities):
                weights = weights + [1.0] * (len(probabilities) - len(weights))
            else:
                weights = weights[:len(probabilities)]
        
        # Ensure at least one weight is non-zero
        if all(w == 0 for w in weights):
            weights[0] = 1.0
    
    result = probability.combine_probabilities(probabilities, weights)
    assert 0.0 <= result <= 1.0, f"combine_probabilities returned {result}, which is outside [0, 1]"


# Feature: polymarket-forecasting-simulator, Property 1: Probability bounds enforcement
@given(
    x=st.floats(
        min_value=-100.0,
        max_value=100.0,
        allow_nan=False,
        allow_infinity=False
    ),
    center=st.floats(
        min_value=-50.0,
        max_value=50.0,
        allow_nan=False,
        allow_infinity=False
    ),
    scale=st.floats(
        min_value=0.01,
        max_value=10.0,
        allow_nan=False,
        allow_infinity=False
    )
)
@settings(max_examples=100)
def test_logistic_transform_bounds(x, center, scale):
    """
    Property 1: Probability bounds enforcement (logistic_transform)
    
    For any input value x, center, and positive scale, logistic_transform 
    must return a value between 0 and 1 (inclusive).
    
    Validates: Requirements 2.1
    """
    result = probability.logistic_transform(x, center, scale)
    assert 0.0 <= result <= 1.0, f"logistic_transform({x}, {center}, {scale}) = {result}, which is outside [0, 1]"


# Feature: polymarket-forecasting-simulator, Property 1: Probability bounds enforcement
@given(
    prior=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    likelihood_positive=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    likelihood_negative=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_bayesian_update_bounds(prior, likelihood_positive, likelihood_negative):
    """
    Property 1: Probability bounds enforcement (bayesian_update)
    
    For any valid prior and likelihoods (all in [0, 1]), bayesian_update 
    must return a value between 0 and 1 (inclusive).
    
    Validates: Requirements 2.1
    """
    result = probability.bayesian_update(prior, likelihood_positive, likelihood_negative)
    assert 0.0 <= result <= 1.0, f"bayesian_update({prior}, {likelihood_positive}, {likelihood_negative}) = {result}, which is outside [0, 1]"


# Additional property: Idempotence of normalize_probability
@given(
    value=st.floats(
        min_value=-1000.0,
        max_value=1000.0,
        allow_nan=False,
        allow_infinity=False
    )
)
@settings(max_examples=100)
def test_normalize_probability_idempotent(value):
    """
    Property: Idempotence of normalize_probability
    
    Normalizing an already normalized probability should return the same value.
    This is a "the more things change, the more they stay the same" property.
    """
    normalized_once = probability.normalize_probability(value)
    normalized_twice = probability.normalize_probability(normalized_once)
    assert normalized_once == normalized_twice, "normalize_probability should be idempotent"


# Additional property: Weighted average bounds
@given(
    probabilities=st.lists(
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        min_size=2,
        max_size=5
    )
)
@settings(max_examples=100)
def test_combine_probabilities_within_range(probabilities):
    """
    Property: Combined probability is within the range of input probabilities
    
    The weighted average of probabilities should be between the minimum and maximum
    of the input probabilities.
    """
    result = probability.combine_probabilities(probabilities)
    min_prob = min(probabilities)
    max_prob = max(probabilities)
    
    # Use approximate comparison to handle floating point precision issues
    assert min_prob - 1e-10 <= result <= max_prob + 1e-10, \
        f"Combined probability {result} is outside range [{min_prob}, {max_prob}]"


# Additional property: Logistic transform symmetry
@given(
    delta=st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False),
    center=st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False),
    scale=st.floats(min_value=0.1, max_value=5.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_logistic_transform_symmetry(delta, center, scale):
    """
    Property: Logistic transform symmetry around center
    
    For any center and delta, f(center + delta) + f(center - delta) should equal 1.
    This tests the mathematical property of the logistic function.
    """
    result_plus = probability.logistic_transform(center + delta, center, scale)
    result_minus = probability.logistic_transform(center - delta, center, scale)
    
    assert result_plus + result_minus == pytest.approx(1.0, abs=1e-10), \
        f"Logistic symmetry violated: f({center + delta}) + f({center - delta}) = {result_plus + result_minus} ≠ 1"


# Additional property: Bayesian update with no evidence returns prior
@given(
    prior=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    likelihood=st.floats(min_value=1e-100, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_bayesian_update_no_discriminating_evidence(prior, likelihood):
    """
    Property: Bayesian update with equal likelihoods returns prior
    
    When evidence is equally likely under both hypotheses, the posterior should equal the prior.
    Excludes extremely small likelihoods that cause numerical instability.
    """
    result = probability.bayesian_update(prior, likelihood, likelihood)
    assert result == pytest.approx(prior, abs=1e-9), \
        f"With equal likelihoods, posterior {result} should equal prior {prior}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
