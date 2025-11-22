"""
Probability calculation utilities for the Polymarket Forecasting Simulator.

Provides helper functions for probability calculations, transformations,
and combinations used across forecast models.
"""

import math
from typing import List, Optional, Tuple
import logging


logger = logging.getLogger(__name__)


def normalize_probability(value: float) -> float:
    """
    Ensure a value is a valid probability between 0 and 1.
    
    Clamps values outside the valid range to the nearest boundary.
    
    Args:
        value: Input value to normalize
    
    Returns:
        float: Normalized probability in range [0, 1]
    
    Examples:
        >>> normalize_probability(0.5)
        0.5
        >>> normalize_probability(-0.1)
        0.0
        >>> normalize_probability(1.5)
        1.0
    """
    if value < 0:
        logger.warning(f"Probability value {value} is negative, clamping to 0")
        return 0.0
    elif value > 1:
        logger.warning(f"Probability value {value} exceeds 1, clamping to 1")
        return 1.0
    return value


def combine_probabilities(
    probabilities: List[float],
    weights: Optional[List[float]] = None
) -> float:
    """
    Combine multiple probability estimates using weighted averaging.
    
    If no weights are provided, uses equal weighting. Weights are automatically
    normalized to sum to 1.
    
    Args:
        probabilities: List of probability values to combine
        weights: Optional list of weights (must match length of probabilities)
    
    Returns:
        float: Combined probability in range [0, 1]
    
    Raises:
        ValueError: If probabilities list is empty or weights length doesn't match
        ValueError: If any probability is outside [0, 1]
        ValueError: If weights sum to zero or contain negative values
    
    Examples:
        >>> combine_probabilities([0.3, 0.5, 0.7])
        0.5
        >>> combine_probabilities([0.3, 0.7], weights=[0.8, 0.2])
        0.38
    """
    if not probabilities:
        raise ValueError("Cannot combine empty list of probabilities")
    
    # Validate all probabilities are in valid range
    for i, p in enumerate(probabilities):
        if not 0 <= p <= 1:
            raise ValueError(f"Probability at index {i} is {p}, must be in [0, 1]")
    
    # Handle single probability
    if len(probabilities) == 1:
        return probabilities[0]
    
    # Set up weights
    if weights is None:
        # Equal weighting
        weights = [1.0 / len(probabilities)] * len(probabilities)
    else:
        if len(weights) != len(probabilities):
            raise ValueError(
                f"Weights length ({len(weights)}) must match probabilities length ({len(probabilities)})"
            )
        
        # Validate weights
        if any(w < 0 for w in weights):
            raise ValueError("Weights cannot be negative")
        
        weight_sum = sum(weights)
        if weight_sum == 0:
            raise ValueError("Weights cannot sum to zero")
        
        # Normalize weights to sum to 1
        weights = [w / weight_sum for w in weights]
    
    # Calculate weighted average
    combined = sum(p * w for p, w in zip(probabilities, weights))
    
    # Ensure result is in valid range (should be guaranteed by inputs, but be safe)
    return normalize_probability(combined)


def logistic_transform(
    x: float,
    center: float = 0.0,
    scale: float = 1.0
) -> float:
    """
    Apply logistic function to transform a value to probability space.
    
    The logistic function maps any real number to the range (0, 1).
    Useful for converting unbounded scores or z-scores to probabilities.
    
    Formula: 1 / (1 + exp(-(x - center) / scale))
    
    Args:
        x: Input value (can be any real number)
        center: Center point of the logistic curve (default: 0)
        scale: Scale parameter controlling steepness (default: 1)
    
    Returns:
        float: Probability in range (0, 1)
    
    Raises:
        ValueError: If scale is zero or negative
    
    Examples:
        >>> logistic_transform(0)
        0.5
        >>> logistic_transform(5)  # Large positive value
        0.9933...
        >>> logistic_transform(-5)  # Large negative value
        0.0066...
    """
    if scale <= 0:
        raise ValueError(f"Scale must be positive, got {scale}")
    
    try:
        # Calculate logistic function
        exponent = -(x - center) / scale
        
        # Handle extreme values to avoid overflow
        if exponent > 700:  # exp(700) would overflow
            return 0.0
        elif exponent < -700:  # exp(-700) is effectively 0
            return 1.0
        
        result = 1.0 / (1.0 + math.exp(exponent))
        return result
    
    except OverflowError:
        # Fallback for extreme values
        if x > center:
            return 1.0
        else:
            return 0.0


def bayesian_update(
    prior: float,
    likelihood_positive: float,
    likelihood_negative: float
) -> float:
    """
    Update a prior probability using Bayes' theorem.
    
    Given a prior probability and likelihoods of observing evidence under
    positive and negative hypotheses, calculates the posterior probability.
    
    Formula: P(H|E) = P(E|H) * P(H) / [P(E|H) * P(H) + P(E|¬H) * P(¬H)]
    
    Args:
        prior: Prior probability P(H) in range [0, 1]
        likelihood_positive: P(E|H) - likelihood of evidence given hypothesis is true
        likelihood_negative: P(E|¬H) - likelihood of evidence given hypothesis is false
    
    Returns:
        float: Posterior probability P(H|E) in range [0, 1]
    
    Raises:
        ValueError: If any input is outside [0, 1]
    
    Examples:
        >>> bayesian_update(0.5, 0.9, 0.1)  # Strong evidence for hypothesis
        0.9
        >>> bayesian_update(0.5, 0.1, 0.9)  # Strong evidence against hypothesis
        0.1
        >>> bayesian_update(0.5, 0.5, 0.5)  # No discriminating evidence
        0.5
    """
    # Validate inputs
    if not 0 <= prior <= 1:
        raise ValueError(f"Prior must be in [0, 1], got {prior}")
    if not 0 <= likelihood_positive <= 1:
        raise ValueError(f"Likelihood positive must be in [0, 1], got {likelihood_positive}")
    if not 0 <= likelihood_negative <= 1:
        raise ValueError(f"Likelihood negative must be in [0, 1], got {likelihood_negative}")
    
    # Handle edge cases
    if prior == 0:
        return 0.0
    if prior == 1:
        return 1.0
    
    # Calculate posterior using Bayes' theorem
    # P(H|E) = P(E|H) * P(H) / [P(E|H) * P(H) + P(E|¬H) * P(¬H)]
    
    numerator = likelihood_positive * prior
    denominator = likelihood_positive * prior + likelihood_negative * (1 - prior)
    
    # Handle case where denominator is zero or very close to zero (both likelihoods are zero)
    if denominator < 1e-300:  # Use a threshold for numerical stability
        logger.warning("Both likelihoods are effectively zero, returning prior")
        return prior
    
    posterior = numerator / denominator
    
    # Ensure result is in valid range
    return normalize_probability(posterior)
