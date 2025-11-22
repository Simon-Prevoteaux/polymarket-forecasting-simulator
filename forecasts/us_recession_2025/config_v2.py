"""
Configuration for US Recession 2025 Forecast V2

Contains v2-specific parameters, indicator configurations, and temporal decay settings.
"""

from typing import Dict, Any


# New FRED indicator series IDs for v2
V2_INDICATOR_SERIES = {
    'credit_spread': 'BAA10Y',      # Corporate bond spread (BAA-rated minus 10-year Treasury)
    'housing_starts': 'HOUST',       # Housing starts
    'manufacturing_pmi': 'NAPM',     # ISM Manufacturing PMI
    'retail_sales': 'RSXFS',         # Retail sales excluding food services
    'oil_price': 'DCOILWTICO',       # WTI crude oil prices
    'vix': 'VIXCLS'                  # VIX volatility index
}

# Temporal decay default parameters
TEMPORAL_DECAY_CONFIG = {
    'method': 'exponential',         # 'exponential' or 'sigmoid'
    'decay_rate': 0.015,             # Rate of exponential decay
    'threshold': 0.4,                # Only apply decay if base_prob below this
    'sigmoid_midpoint': 180,         # Midpoint for sigmoid function (days)
    'sigmoid_steepness': 0.02        # Steepness parameter for sigmoid
}

# Feature engineering configuration
FEATURE_ENGINEERING_CONFIG = {
    'rate_of_change_periods': [30, 90, 180],  # Days for rate of change calculations
    'moving_average_windows': [30, 90],        # Days for moving averages
    'volatility_window': 30                     # Days for volatility calculation
}

# V2-specific parameter schemas
V2_PARAMETER_SCHEMA = {
    'apply_temporal_decay': {
        'type': 'boolean',
        'default': True,
        'description': 'Apply temporal decay adjustment to base probability'
    },
    'decay_method': {
        'type': 'select',
        'options': ['exponential', 'sigmoid'],
        'default': 'exponential',
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
    }
}

# Forecast deadline
FORECAST_DEADLINE = '2025-12-31'


def get_v2_default_parameters() -> Dict[str, Any]:
    """Get default parameters for v2 model."""
    return {
        'apply_temporal_decay': True,
        'decay_method': 'exponential',
        'decay_rate': 0.015,
        'decay_threshold': 0.4
    }
