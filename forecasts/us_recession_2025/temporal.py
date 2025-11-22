"""
Temporal decay module for US Recession 2025 Forecast V2

Applies time-to-event adjustments to base probabilities.
"""

from datetime import datetime
from typing import Dict, Any, Tuple, List
import math


def calculate_time_to_event(
    current_date: datetime,
    deadline: datetime = datetime(2025, 12, 31)
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


def exponential_decay_adjustment(
    base_probability: float,
    days_remaining: int,
    decay_rate: float = 0.01,
    threshold: float = 0.4
) -> float:
    """
    Apply exponential decay to probability based on time remaining.
    
    Formula: If base_prob < threshold and days_remaining < 365:
        adjustment_factor = exp(-decay_rate * (365 - days_remaining) / 365)
        adjusted_prob = base_prob * adjustment_factor
    
    Args:
        base_probability: Initial probability from model
        days_remaining: Days until deadline
        decay_rate: Rate of exponential decay (higher = faster decay)
        threshold: Only apply decay if base_prob below this value
    
    Returns:
        Adjusted probability incorporating temporal information
    """
    # Validate inputs
    if base_probability < 0 or base_probability > 1:
        raise ValueError(f"base_probability must be in [0, 1], got {base_probability}")
    
    if decay_rate <= 0:
        raise ValueError(f"decay_rate must be positive, got {decay_rate}")
    
    if threshold < 0 or threshold > 1:
        raise ValueError(f"threshold must be in [0, 1], got {threshold}")
    
    # Don't apply decay if probability is above threshold
    if base_probability >= threshold:
        return base_probability
    
    # Don't apply decay if we're far from deadline
    if days_remaining >= 365:
        return base_probability
    
    # Don't apply decay if deadline has passed
    if days_remaining <= 0:
        return base_probability
    
    # Calculate adjustment factor
    time_factor = (365 - days_remaining) / 365
    adjustment_factor = math.exp(-decay_rate * time_factor)
    
    # Apply adjustment
    adjusted_prob = base_probability * adjustment_factor
    
    # Ensure result is in valid range
    return max(0.0, min(1.0, adjusted_prob))


def sigmoid_decay_adjustment(
    base_probability: float,
    days_remaining: int,
    midpoint: int = 180,
    steepness: float = 0.02
) -> float:
    """
    Apply sigmoid-based decay adjustment.
    
    Uses sigmoid function centered at midpoint to create smooth
    transition in adjustment strength as deadline approaches.
    
    Formula: 
        time_factor = 1 / (1 + exp(-steepness * (midpoint - days_remaining)))
        adjusted_prob = base_prob * (1 - (1 - base_prob) * time_factor)
    
    Args:
        base_probability: Initial probability from model
        days_remaining: Days until deadline
        midpoint: Center point of sigmoid (days)
        steepness: Steepness of sigmoid curve
    
    Returns:
        Adjusted probability
    """
    # Validate inputs
    if base_probability < 0 or base_probability > 1:
        raise ValueError(f"base_probability must be in [0, 1], got {base_probability}")
    
    if steepness <= 0:
        raise ValueError(f"steepness must be positive, got {steepness}")
    
    # Calculate sigmoid time factor
    sigmoid_input = -steepness * (midpoint - days_remaining)
    time_factor = 1 / (1 + math.exp(sigmoid_input))
    
    # Apply adjustment
    adjusted_prob = base_probability * (1 - (1 - base_probability) * time_factor)
    
    # Ensure result is in valid range
    return max(0.0, min(1.0, adjusted_prob))


class TemporalAdjuster:
    """Manages temporal decay adjustments with calibration."""
    
    def __init__(self, method: str = 'exponential', **params):
        """
        Initialize with decay method and parameters.
        
        Args:
            method: 'exponential' or 'sigmoid'
            **params: Method-specific parameters
        """
        self.method = method
        self.params = params
        
        # Set defaults based on method
        if method == 'exponential':
            self.decay_rate = params.get('decay_rate', 0.015)
            self.threshold = params.get('threshold', 0.4)
        elif method == 'sigmoid':
            self.midpoint = params.get('midpoint', 180)
            self.steepness = params.get('steepness', 0.02)
        else:
            raise ValueError(f"Unknown decay method: {method}")
    
    def adjust_probability(
        self,
        base_probability: float,
        current_date: datetime,
        deadline: datetime = datetime(2025, 12, 31)
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Apply temporal adjustment and return adjusted probability
        plus metadata about the adjustment.
        
        Args:
            base_probability: Initial probability
            current_date: Current date
            deadline: Forecast deadline
        
        Returns:
            Tuple of (adjusted_probability, metadata_dict)
        """
        days_remaining = calculate_time_to_event(current_date, deadline)
        
        # Apply appropriate decay method
        if self.method == 'exponential':
            adjusted_prob = exponential_decay_adjustment(
                base_probability,
                days_remaining,
                self.decay_rate,
                self.threshold
            )
            threshold_applied = base_probability < self.threshold and days_remaining < 365
            adjustment_factor = adjusted_prob / base_probability if base_probability > 0 else 1.0
            
            metadata = {
                'decay_method': 'exponential',
                'decay_rate': self.decay_rate,
                'threshold': self.threshold,
                'threshold_applied': threshold_applied,
                'adjustment_factor': adjustment_factor
            }
        
        elif self.method == 'sigmoid':
            adjusted_prob = sigmoid_decay_adjustment(
                base_probability,
                days_remaining,
                self.midpoint,
                self.steepness
            )
            adjustment_factor = adjusted_prob / base_probability if base_probability > 0 else 1.0
            
            metadata = {
                'decay_method': 'sigmoid',
                'midpoint': self.midpoint,
                'steepness': self.steepness,
                'adjustment_factor': adjustment_factor
            }
        
        else:
            # Should never reach here due to __init__ validation
            adjusted_prob = base_probability
            metadata = {'decay_method': 'none'}
        
        return adjusted_prob, metadata
    
    def calibrate_from_historical_data(
        self,
        historical_forecasts: List[Dict],
        actual_outcomes: List[bool]
    ) -> Dict[str, float]:
        """
        Calibrate decay parameters using historical data.
        
        Fits parameters to minimize Brier score on historical forecasts.
        
        Args:
            historical_forecasts: List of historical forecast data
            actual_outcomes: List of actual outcomes (True/False)
        
        Returns:
            Dictionary of calibrated parameters
        """
        # Will be implemented in later tasks
        return {}
