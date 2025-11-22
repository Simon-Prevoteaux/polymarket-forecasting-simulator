"""
Configuration for US Recession 2025 Forecast V2

Contains v2-specific parameters, indicator configurations, and temporal decay settings.
"""

from typing import Dict, Any
from datetime import datetime
from lib.utils import ParameterSchema


# New FRED indicator series IDs for v2
V2_INDICATOR_SERIES = {
    'credit_spread': 'BAA10Y',      # Corporate bond spread (BAA-rated minus 10-year Treasury)
    'housing_starts': 'HOUST',       # Housing starts
    'manufacturing_pmi': 'NAPM',     # ISM Manufacturing PMI (Note: NAPM is discontinued, but kept for historical data)
    'retail_sales': 'RSXFS',         # Retail sales excluding food services
    'oil_price': 'DCOILWTICO',       # WTI crude oil prices
    'vix': 'VIXCLS'                  # VIX volatility index
}

# Thresholds and statistics for new v2 indicators
# These are approximate values based on historical recession patterns
V2_INDICATOR_THRESHOLDS = {
    'credit_spread': {
        'recession_threshold': 2.0,   # Credit spread above 2% indicates stress
        'mean': 1.5,
        'std': 0.8,
        'description': 'BAA corporate bond spread over 10-year Treasury'
    },
    'housing_starts': {
        'recession_threshold': 1200,  # Housing starts below 1.2M (thousands) indicates weakness
        'mean': 1400,
        'std': 300,
        'description': 'New privately-owned housing units started (thousands)'
    },
    'manufacturing_pmi': {
        'recession_threshold': 50.0,  # PMI below 50 indicates contraction
        'mean': 52.0,
        'std': 3.0,
        'description': 'ISM Manufacturing PMI (50 = expansion/contraction threshold)'
    },
    'retail_sales': {
        'recession_threshold': 0.0,   # Negative growth indicates weakness
        'mean': 3.0,                  # Average annual growth rate
        'std': 5.0,
        'description': 'Retail sales excluding food services (year-over-year % change)'
    },
    'oil_price': {
        'recession_threshold': 100.0, # High oil prices (>$100/barrel) can indicate stress
        'mean': 65.0,
        'std': 25.0,
        'description': 'WTI crude oil price ($/barrel)'
    },
    'vix': {
        'recession_threshold': 25.0,  # VIX above 25 indicates elevated fear/uncertainty
        'mean': 18.0,
        'std': 8.0,
        'description': 'CBOE Volatility Index (market fear gauge)'
    }
}

# Temporal decay default parameters
# Based on empirical analysis of prediction market behavior and time-to-event modeling
TEMPORAL_DECAY_CONFIG = {
    'method': 'adaptive',            # 'adaptive' (RECOMMENDED), 'theta', 'simple_decay', 'threshold_decay', etc.
    'decay_rate': 0.015,             # Legacy: Rate of exponential decay (kept for backward compatibility)
    'threshold': 0.4,                # Legacy: Threshold for old exponential method
    'sigmoid_midpoint': 180,         # Legacy: Midpoint for sigmoid function
    'sigmoid_steepness': 0.02,       # Legacy: Steepness parameter for sigmoid
    'theta_total_days': 365,         # Total days in forecast window for theta decay
    'theta_decay_power': 1.5,        # Power for theta decay (1.5 = moderate, 2.0 = aggressive)
    'adaptive_lower_threshold': 0.4, # Adaptive: Below this, decay toward 0
    'adaptive_upper_threshold': 0.6, # Adaptive: Above this, amplify toward 1
    'enabled': True                  # Whether temporal decay is enabled by default
}

# Forecast deadline for temporal calculations
FORECAST_DEADLINE = datetime(2025, 12, 31)

# Feature engineering configuration
# Defines time windows for derived feature calculations
FEATURE_ENGINEERING_CONFIG = {
    'rate_of_change_periods': [30, 90, 180],  # Days for rate of change calculations
                                               # 30d = short-term momentum
                                               # 90d = medium-term trends
                                               # 180d = long-term structural changes
    'moving_average_windows': [30, 90],        # Days for moving averages
                                               # 30d = smooth short-term noise
                                               # 90d = identify medium-term trends
    'volatility_window': 30,                   # Days for volatility calculation (rolling std dev)
    'min_observations': 20                     # Minimum observations required for feature calculation
}

# Default weights for v2 indicators
# These weights determine how much each indicator contributes to the base probability
# Weights should sum to approximately 1.0 for interpretability
V2_DEFAULT_WEIGHTS = {
    # V1 indicators (inherited)
    'yield_curve_weight': 0.25,
    'unemployment_weight': 0.20,
    'gdp_weight': 0.15,
    'confidence_weight': 0.08,
    'leading_indicators_weight': 0.08,
    
    # New V2 indicators
    'credit_spread_weight': 0.10,
    'housing_starts_weight': 0.05,
    'manufacturing_pmi_weight': 0.04,
    'retail_sales_weight': 0.03,
    'vix_weight': 0.02,
    
    # Feature weights (for engineered features)
    'feature_weight_multiplier': 0.5  # Multiplier for feature contributions
}

# V2-specific parameter schemas (using ParameterSchema for validation)
V2_PARAMETER_SCHEMAS = {
    'apply_temporal_decay': ParameterSchema(
        name='apply_temporal_decay',
        type='bool',
        default=True,
        min_value=None,
        max_value=None,
        description='Apply temporal decay adjustment to base probability'
    ),
    'decay_method': ParameterSchema(
        name='decay_method',
        type='str',
        default='theta',
        min_value=None,
        max_value=None,
        description='Method for temporal decay calculation (exponential, sigmoid, or theta)'
    ),
    'decay_rate': ParameterSchema(
        name='decay_rate',
        type='float',
        default=0.015,
        min_value=0.001,
        max_value=0.1,
        description='Rate of exponential decay (higher = faster decay)'
    ),
    'decay_threshold': ParameterSchema(
        name='decay_threshold',
        type='float',
        default=0.4,
        min_value=0.0,
        max_value=1.0,
        description='Only apply decay if base probability below this threshold'
    ),
    'sigmoid_midpoint': ParameterSchema(
        name='sigmoid_midpoint',
        type='int',
        default=180,
        min_value=30,
        max_value=365,
        description='Midpoint for sigmoid decay function (days from deadline)'
    ),
    'sigmoid_steepness': ParameterSchema(
        name='sigmoid_steepness',
        type='float',
        default=0.02,
        min_value=0.001,
        max_value=0.1,
        description='Steepness parameter for sigmoid decay function'
    ),
    'theta_total_days': ParameterSchema(
        name='theta_total_days',
        type='int',
        default=365,
        min_value=30,
        max_value=730,
        description='Total days in forecast window for theta decay'
    ),
    'theta_decay_power': ParameterSchema(
        name='theta_decay_power',
        type='float',
        default=1.5,
        min_value=1.0,
        max_value=5.0,
        description='Power for theta decay acceleration (1.5 = moderate, 2.0 = aggressive like options theta)'
    ),
    'lookback_days': ParameterSchema(
        name='lookback_days',
        type='int',
        default=365,
        min_value=90,
        max_value=1825,  # 5 years
        description='Historical window in days for data analysis'
    )
}

# V2-specific parameter schemas for web interface (simplified format)
# This format is used by the Flask web interface for rendering parameter controls
V2_PARAMETER_SCHEMA = {
    'apply_temporal_decay': {
        'type': 'boolean',
        'default': True,
        'description': 'Apply temporal decay adjustment to base probability'
    },
    'decay_method': {
        'type': 'select',
        'options': ['theta', 'exponential', 'sigmoid'],
        'default': 'theta',
        'description': 'Method for temporal decay calculation'
    },
    'decay_rate': {
        'type': 'float',
        'min': 0.001,
        'max': 0.1,
        'default': 0.015,
        'step': 0.001,
        'description': 'Rate of exponential decay (higher = faster decay)'
    },
    'decay_threshold': {
        'type': 'float',
        'min': 0.0,
        'max': 1.0,
        'default': 0.4,
        'step': 0.05,
        'description': 'Only apply decay if base probability below this threshold'
    },
    'sigmoid_midpoint': {
        'type': 'int',
        'min': 30,
        'max': 365,
        'default': 180,
        'step': 10,
        'description': 'Midpoint for sigmoid decay (days from deadline)'
    },
    'sigmoid_steepness': {
        'type': 'float',
        'min': 0.001,
        'max': 0.1,
        'default': 0.02,
        'step': 0.001,
        'description': 'Steepness of sigmoid decay curve'
    },
    'theta_total_days': {
        'type': 'int',
        'min': 30,
        'max': 730,
        'default': 365,
        'step': 30,
        'description': 'Total days in forecast window for theta decay'
    },
    'theta_decay_power': {
        'type': 'float',
        'min': 1.0,
        'max': 5.0,
        'default': 1.5,
        'step': 0.1,
        'description': 'Power for theta decay (1.5 = moderate, 2.0 = aggressive like options)'
    },
    'lookback_days': {
        'type': 'int',
        'min': 90,
        'max': 1825,
        'default': 365,
        'step': 30,
        'description': 'Historical data window (days)'
    }
}


def get_v2_default_parameters() -> Dict[str, Any]:
    """
    Get default parameters for v2 model.
    
    Returns:
        Dictionary of default parameter values for v2 model including
        temporal decay settings and data fetching configuration.
    """
    return {
        'apply_temporal_decay': TEMPORAL_DECAY_CONFIG['enabled'],
        'decay_method': TEMPORAL_DECAY_CONFIG['method'],
        'decay_rate': TEMPORAL_DECAY_CONFIG['decay_rate'],
        'decay_threshold': TEMPORAL_DECAY_CONFIG['threshold'],
        'sigmoid_midpoint': TEMPORAL_DECAY_CONFIG['sigmoid_midpoint'],
        'sigmoid_steepness': TEMPORAL_DECAY_CONFIG['sigmoid_steepness'],
        'theta_total_days': TEMPORAL_DECAY_CONFIG['theta_total_days'],
        'theta_decay_power': TEMPORAL_DECAY_CONFIG['theta_decay_power'],
        'lookback_days': 365,
        **V2_DEFAULT_WEIGHTS
    }


def get_all_indicator_thresholds() -> Dict[str, Dict[str, Any]]:
    """
    Get combined thresholds for all indicators (v1 + v2).
    
    Returns:
        Dictionary mapping indicator names to their threshold configurations.
    """
    from .config import INDICATOR_THRESHOLDS
    return {**INDICATOR_THRESHOLDS, **V2_INDICATOR_THRESHOLDS}


def validate_v2_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate v2 model parameters against schemas.
    
    Args:
        params: Dictionary of parameters to validate
    
    Returns:
        Validated parameters with defaults filled in for missing values
    
    Raises:
        ValueError: If parameters are invalid
    """
    validated = get_v2_default_parameters()
    
    for param_name, param_value in params.items():
        if param_name in V2_PARAMETER_SCHEMAS:
            schema = V2_PARAMETER_SCHEMAS[param_name]
            
            # Type validation
            if schema.type == 'float':
                try:
                    param_value = float(param_value)
                except (TypeError, ValueError):
                    raise ValueError(f"Parameter {param_name} must be a float")
                
                if schema.min_value is not None and param_value < schema.min_value:
                    raise ValueError(
                        f"Parameter {param_name} must be >= {schema.min_value}"
                    )
                if schema.max_value is not None and param_value > schema.max_value:
                    raise ValueError(
                        f"Parameter {param_name} must be <= {schema.max_value}"
                    )
            
            elif schema.type == 'int':
                try:
                    param_value = int(param_value)
                except (TypeError, ValueError):
                    raise ValueError(f"Parameter {param_name} must be an integer")
                
                if schema.min_value is not None and param_value < schema.min_value:
                    raise ValueError(
                        f"Parameter {param_name} must be >= {schema.min_value}"
                    )
                if schema.max_value is not None and param_value > schema.max_value:
                    raise ValueError(
                        f"Parameter {param_name} must be <= {schema.max_value}"
                    )
            
            elif schema.type == 'bool':
                if not isinstance(param_value, bool):
                    raise ValueError(f"Parameter {param_name} must be a boolean")
            
            elif schema.type == 'str':
                if not isinstance(param_value, str):
                    raise ValueError(f"Parameter {param_name} must be a string")
            
            validated[param_name] = param_value
        else:
            # Allow additional parameters (like weights) without validation
            validated[param_name] = param_value
    
    return validated
