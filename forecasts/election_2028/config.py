"""
Configuration for Election 2028 forecast model.

Defines parameters, thresholds, and configuration for the election forecast.
"""

from lib.utils import ParameterSchema


# Default parameter values
DEFAULT_PARAMS = {
    'polling_weight': 0.40,
    'economic_weight': 0.25,
    'approval_weight': 0.20,
    'fundraising_weight': 0.10,
    'historical_weight': 0.05,
}


# Parameter schemas with validation rules
PARAMETER_SCHEMAS = {
    'polling_weight': ParameterSchema(
        name='polling_weight',
        type='float',
        default=0.40,
        min_value=0.0,
        max_value=1.0,
        description='Weight for polling data (0-1)'
    ),
    'economic_weight': ParameterSchema(
        name='economic_weight',
        type='float',
        default=0.25,
        min_value=0.0,
        max_value=1.0,
        description='Weight for economic indicators (0-1)'
    ),
    'approval_weight': ParameterSchema(
        name='approval_weight',
        type='float',
        default=0.20,
        min_value=0.0,
        max_value=1.0,
        description='Weight for presidential approval rating (0-1)'
    ),
    'fundraising_weight': ParameterSchema(
        name='fundraising_weight',
        type='float',
        default=0.10,
        min_value=0.0,
        max_value=1.0,
        description='Weight for campaign fundraising (0-1)'
    ),
    'historical_weight': ParameterSchema(
        name='historical_weight',
        type='float',
        default=0.05,
        min_value=0.0,
        max_value=1.0,
        description='Weight for historical patterns (0-1)'
    ),
}


# Dummy thresholds for indicator interpretation
INDICATOR_THRESHOLDS = {
    'polling': {
        'mean': 50.0,  # 50% polling average
        'std': 5.0
    },
    'economic_index': {
        'mean': 100.0,  # Economic index baseline
        'std': 10.0
    },
    'approval': {
        'mean': 45.0,  # Presidential approval baseline
        'std': 8.0
    },
    'fundraising': {
        'mean': 500.0,  # Millions of dollars
        'std': 100.0
    },
    'historical_advantage': {
        'mean': 0.0,  # No inherent advantage
        'std': 5.0
    }
}
