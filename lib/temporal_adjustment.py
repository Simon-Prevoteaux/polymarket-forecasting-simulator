"""
Generic temporal adjustment library for probability forecasts.

This module provides reusable temporal adjustment methods that can be applied
to any forecast model. Different methods are appropriate for different types
of events and probability patterns.
"""

from datetime import datetime
from typing import Dict, Any, Tuple, Optional, Callable
import math


def calculate_time_to_event(
    current_date: datetime,
    deadline: datetime
) -> int:
    """
    Calculate days remaining until deadline.
    
    Args:
        current_date: Current date
        deadline: Forecast deadline
    
    Returns:
        Number of days remaining (can be negative if past deadline)
    """
    delta = deadline - current_date
    return delta.days


# ============================================================================
# DECAY METHODS (for events unlikely to occur)
# ============================================================================

def simple_decay(
    base_probability: float,
    days_remaining: int,
    total_days: int = 365,
    decay_power: float = 1.5
) -> float:
    """
    Simple time decay - reduces probability as deadline approaches.
    
    Best for: Events that become less likely as time passes without occurrence.
    Example: Recession, product launch, policy change
    
    Formula: adjusted = base * (days_remaining / total_days)^decay_power
    
    Args:
        base_probability: Initial probability
        days_remaining: Days until deadline
        total_days: Total forecast window
        decay_power: Acceleration factor (higher = faster decay)
    
    Returns:
        Adjusted probability
    """
    if base_probability < 0 or base_probability > 1:
        raise ValueError(f"base_probability must be in [0, 1], got {base_probability}")
    
    if days_remaining <= 0:
        return max(0.0, base_probability * 0.001)
    
    if days_remaining >= total_days:
        return base_probability
    
    time_ratio = days_remaining / total_days
    time_factor = math.pow(time_ratio, decay_power)
    
    return base_probability * time_factor


def theta_decay(
    base_probability: float,
    days_remaining: int,
    total_days: int = 365,
    decay_power: float = 1.5
) -> float:
    """
    Theta decay - inspired by options trading time decay.
    
    This is an alias for simple_decay with options-trading terminology.
    Like options theta, probability decays as time passes, with acceleration
    as the deadline approaches.
    
    Best for: Events that become less likely as time passes without occurrence.
    Example: Recession, product launch, policy change
    
    Formula: adjusted = base * (days_remaining / total_days)^decay_power
    
    Args:
        base_probability: Initial probability
        days_remaining: Days until deadline
        total_days: Total forecast window
        decay_power: Acceleration factor (1.5 = moderate, 2.0 = aggressive like options)
    
    Returns:
        Adjusted probability
    
    Note: This is the same as simple_decay but with options-trading naming.
          Use decay_power=2.0 for true quadratic theta decay like options.
    """
    return simple_decay(base_probability, days_remaining, total_days, decay_power)


def threshold_aware_decay(
    base_probability: float,
    days_remaining: int,
    total_days: int = 365,
    decay_power: float = 1.5,
    threshold: float = 0.5
) -> float:
    """
    Decay that only applies below a threshold.
    
    Best for: When you want to preserve high-confidence predictions.
    Example: Strong recession signals should not decay away.
    
    Logic:
    - If base_prob >= threshold: No decay (signal is strong)
    - If base_prob < threshold: Apply decay (signal is weak)
    
    Args:
        base_probability: Initial probability
        days_remaining: Days until deadline
        total_days: Total forecast window
        decay_power: Acceleration factor
        threshold: Only decay if below this value
    
    Returns:
        Adjusted probability
    """
    if base_probability >= threshold:
        return base_probability
    
    return simple_decay(base_probability, days_remaining, total_days, decay_power)


# ============================================================================
# CONVERGENCE METHODS (for events becoming more certain)
# ============================================================================

def trend_amplification(
    base_probability: float,
    days_remaining: int,
    total_days: int = 365,
    amplification_power: float = 1.5,
    threshold: float = 0.5
) -> float:
    """
    Amplifies probability trends as deadline approaches.
    
    Best for: Events where signals strengthen over time.
    Example: Recession with mounting evidence, election with clear leader
    
    Logic:
    - If base_prob > threshold: Amplify toward 1.0 (trend up)
    - If base_prob < threshold: Amplify toward 0.0 (trend down)
    - If base_prob ≈ threshold: Minimal change (uncertain)
    
    Formula:
        time_pressure = 1 - (days_remaining / total_days)^amplification_power
        distance_from_threshold = base_prob - threshold
        adjustment = distance_from_threshold * time_pressure
        adjusted = base_prob + adjustment
    
    Args:
        base_probability: Initial probability
        days_remaining: Days until deadline
        total_days: Total forecast window
        amplification_power: How aggressively to amplify
        threshold: Neutral point (typically 0.5)
    
    Returns:
        Adjusted probability
    """
    if base_probability < 0 or base_probability > 1:
        raise ValueError(f"base_probability must be in [0, 1], got {base_probability}")
    
    if days_remaining <= 0:
        # At deadline, push strongly toward 0 or 1
        return 0.99 if base_probability > threshold else 0.01
    
    if days_remaining >= total_days:
        return base_probability
    
    # Calculate time pressure (0 at start, 1 at deadline)
    time_ratio = days_remaining / total_days
    time_pressure = 1 - math.pow(time_ratio, amplification_power)
    
    # Calculate distance from threshold
    distance_from_threshold = base_probability - threshold
    
    # Apply amplification
    adjustment = distance_from_threshold * time_pressure
    adjusted = base_probability + adjustment
    
    return max(0.0, min(1.0, adjusted))


def confidence_convergence(
    base_probability: float,
    days_remaining: int,
    total_days: int = 365,
    convergence_power: float = 2.0,
    lower_threshold: float = 0.3,
    upper_threshold: float = 0.7
) -> float:
    """
    Converges toward 0 or 1 based on signal strength.
    
    Best for: Binary events where uncertainty should decrease over time.
    Example: Election outcome, merger approval, policy passage
    
    Logic:
    - Strong signals (>upper_threshold): Converge toward 1.0
    - Weak signals (<lower_threshold): Converge toward 0.0
    - Uncertain signals (between thresholds): Minimal change
    
    Args:
        base_probability: Initial probability
        days_remaining: Days until deadline
        total_days: Total forecast window
        convergence_power: Speed of convergence
        lower_threshold: Below this, converge to 0
        upper_threshold: Above this, converge to 1
    
    Returns:
        Adjusted probability
    """
    if base_probability < 0 or base_probability > 1:
        raise ValueError(f"base_probability must be in [0, 1], got {base_probability}")
    
    if days_remaining <= 0:
        # At deadline, push to extremes
        if base_probability > upper_threshold:
            return 0.95
        elif base_probability < lower_threshold:
            return 0.05
        else:
            return base_probability
    
    if days_remaining >= total_days:
        return base_probability
    
    # Calculate time pressure
    time_ratio = days_remaining / total_days
    time_pressure = 1 - math.pow(time_ratio, convergence_power)
    
    # Determine target and strength
    if base_probability > upper_threshold:
        # Converge toward 1.0
        target = 1.0
        strength = (base_probability - upper_threshold) / (1.0 - upper_threshold)
    elif base_probability < lower_threshold:
        # Converge toward 0.0
        target = 0.0
        strength = (lower_threshold - base_probability) / lower_threshold
    else:
        # In uncertain zone, minimal adjustment
        return base_probability
    
    # Apply convergence
    adjustment = (target - base_probability) * strength * time_pressure
    adjusted = base_probability + adjustment
    
    return max(0.0, min(1.0, adjusted))


# ============================================================================
# ADAPTIVE METHODS (context-aware)
# ============================================================================

def adaptive_adjustment(
    base_probability: float,
    days_remaining: int,
    total_days: int = 365,
    decay_power: float = 1.5,
    amplification_power: float = 1.5,
    lower_threshold: float = 0.4,
    upper_threshold: float = 0.6
) -> float:
    """
    Adaptive method that decays weak signals and amplifies strong signals.
    
    Best for: Most real-world forecasts where behavior should depend on signal strength.
    Example: Any binary event where you want smart time adjustment
    
    Logic:
    - Strong positive signals (>upper_threshold): Amplify toward 1.0
    - Weak signals (<lower_threshold): Decay toward 0.0
    - Uncertain signals (between thresholds): Gentle decay
    
    This is the "smart" method that handles both cases appropriately.
    
    Args:
        base_probability: Initial probability
        days_remaining: Days until deadline
        total_days: Total forecast window
        decay_power: Power for decay (weak signals)
        amplification_power: Power for amplification (strong signals)
        lower_threshold: Below this, apply decay
        upper_threshold: Above this, apply amplification
    
    Returns:
        Adjusted probability
    """
    if base_probability < 0 or base_probability > 1:
        raise ValueError(f"base_probability must be in [0, 1], got {base_probability}")
    
    if days_remaining <= 0:
        # At deadline, push to extremes based on signal
        if base_probability > upper_threshold:
            return min(0.95, base_probability * 1.2)
        elif base_probability < lower_threshold:
            return max(0.01, base_probability * 0.1)
        else:
            return base_probability * 0.5
    
    if days_remaining >= total_days:
        return base_probability
    
    # Calculate time pressure
    time_ratio = days_remaining / total_days
    
    if base_probability > upper_threshold:
        # Strong signal - amplify toward 1.0
        time_pressure = 1 - math.pow(time_ratio, amplification_power)
        distance_from_threshold = base_probability - upper_threshold
        max_distance = 1.0 - upper_threshold
        strength = distance_from_threshold / max_distance
        
        target = 1.0
        adjustment = (target - base_probability) * strength * time_pressure * 0.5
        adjusted = base_probability + adjustment
        
    elif base_probability < lower_threshold:
        # Weak signal - decay toward 0.0
        time_factor = math.pow(time_ratio, decay_power)
        adjusted = base_probability * time_factor
        
    else:
        # Uncertain zone - gentle decay
        time_factor = math.pow(time_ratio, decay_power * 0.5)
        adjusted = base_probability * time_factor
    
    return max(0.0, min(1.0, adjusted))


# ============================================================================
# NO ADJUSTMENT (baseline)
# ============================================================================

def no_adjustment(
    base_probability: float,
    days_remaining: int,
    **kwargs
) -> float:
    """
    No temporal adjustment - returns base probability unchanged.
    
    Best for: Non-time-sensitive forecasts, continuous probabilities,
              or when you want pure model output.
    Example: Election polling (not time-dependent), market predictions
    
    Args:
        base_probability: Initial probability
        days_remaining: Days until deadline (ignored)
        **kwargs: Additional parameters (ignored)
    
    Returns:
        Base probability unchanged
    """
    return base_probability


# ============================================================================
# TEMPORAL ADJUSTER CLASS
# ============================================================================

class TemporalAdjuster:
    """
    Flexible temporal adjustment manager supporting multiple methods.
    
    This class provides a unified interface for applying different temporal
    adjustment strategies to probability forecasts.
    """
    
    # Map method names to functions
    METHODS = {
        'none': no_adjustment,
        'simple_decay': simple_decay,
        'theta': theta_decay,  # Alias for simple_decay with options terminology
        'threshold_decay': threshold_aware_decay,
        'trend_amplification': trend_amplification,
        'confidence_convergence': confidence_convergence,
        'adaptive': adaptive_adjustment,
    }
    
    def __init__(self, method: str = 'adaptive', **params):
        """
        Initialize temporal adjuster.
        
        Args:
            method: Adjustment method name
            **params: Method-specific parameters
        """
        if method not in self.METHODS:
            raise ValueError(
                f"Unknown method: {method}. "
                f"Available: {', '.join(self.METHODS.keys())}"
            )
        
        self.method = method
        self.params = params
        self.adjustment_function = self.METHODS[method]
    
    def adjust_probability(
        self,
        base_probability: float,
        current_date: datetime,
        deadline: datetime,
        **override_params
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Apply temporal adjustment to probability.
        
        Args:
            base_probability: Initial probability
            current_date: Current date
            deadline: Forecast deadline
            **override_params: Override default parameters
        
        Returns:
            Tuple of (adjusted_probability, metadata)
        """
        days_remaining = calculate_time_to_event(current_date, deadline)
        
        # Merge parameters
        params = {**self.params, **override_params}
        
        # Apply adjustment
        adjusted_prob = self.adjustment_function(
            base_probability,
            days_remaining,
            **params
        )
        
        # Calculate metadata
        adjustment_factor = adjusted_prob / base_probability if base_probability > 0 else 1.0
        
        metadata = {
            'method': self.method,
            'days_remaining': days_remaining,
            'adjustment_factor': adjustment_factor,
            'parameters': params
        }
        
        return adjusted_prob, metadata
    
    @classmethod
    def get_method_info(cls, method: str) -> str:
        """Get description of a method."""
        descriptions = {
            'none': 'No adjustment - returns base probability',
            'simple_decay': 'Simple time decay for unlikely events',
            'theta': 'Theta decay (options-style) - same as simple_decay',
            'threshold_decay': 'Decay only below threshold',
            'trend_amplification': 'Amplifies trends as deadline approaches',
            'confidence_convergence': 'Converges to 0 or 1 based on signal strength',
            'adaptive': 'Smart method: decays weak signals, amplifies strong signals',
        }
        return descriptions.get(method, 'Unknown method')
    
    @classmethod
    def list_methods(cls) -> Dict[str, str]:
        """List all available methods with descriptions."""
        return {
            method: cls.get_method_info(method)
            for method in cls.METHODS.keys()
        }
