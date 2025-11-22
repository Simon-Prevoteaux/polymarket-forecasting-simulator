"""
Configuration for US Recession 2025 forecast model.

Defines model parameters, data sources, and default settings.
"""

from lib.utils import ParameterSchema


# FRED API series IDs for economic indicators
DATA_SOURCES = {
    'yield_curve': 'T10Y2Y',           # 10-Year Treasury Constant Maturity Minus 2-Year
    'unemployment': 'UNRATE',          # Unemployment Rate
    'gdp': 'A191RL1Q225SBEA',         # Real GDP growth rate (quarterly, annual rate)
    'consumer_confidence': 'UMCSENT',  # University of Michigan Consumer Sentiment
    'leading_indicators': 'USSLIND',   # Leading Index for the United States
    'jobless_claims': 'ICSA'           # Initial Jobless Claims
}


# Default parameter values
DEFAULT_PARAMS = {
    'yield_curve_weight': 0.35,
    'unemployment_weight': 0.25,
    'gdp_weight': 0.20,
    'confidence_weight': 0.10,
    'leading_indicators_weight': 0.10,
    'lookback_days': 365
}


# Parameter schemas for validation
PARAMETER_SCHEMAS = {
    'yield_curve_weight': ParameterSchema(
        name='yield_curve_weight',
        type='float',
        default=0.35,
        min_value=0.0,
        max_value=1.0,
        description='Weight for yield curve signal in recession probability calculation'
    ),
    'unemployment_weight': ParameterSchema(
        name='unemployment_weight',
        type='float',
        default=0.25,
        min_value=0.0,
        max_value=1.0,
        description='Weight for unemployment signal in recession probability calculation'
    ),
    'gdp_weight': ParameterSchema(
        name='gdp_weight',
        type='float',
        default=0.20,
        min_value=0.0,
        max_value=1.0,
        description='Weight for GDP growth signal in recession probability calculation'
    ),
    'confidence_weight': ParameterSchema(
        name='confidence_weight',
        type='float',
        default=0.10,
        min_value=0.0,
        max_value=1.0,
        description='Weight for consumer confidence signal in recession probability calculation'
    ),
    'leading_indicators_weight': ParameterSchema(
        name='leading_indicators_weight',
        type='float',
        default=0.10,
        min_value=0.0,
        max_value=1.0,
        description='Weight for leading economic indicators signal in recession probability calculation'
    ),
    'lookback_days': ParameterSchema(
        name='lookback_days',
        type='int',
        default=365,
        min_value=30,
        max_value=3650,
        description='Historical window in days for analysis'
    )
}


# Historical thresholds and statistics for indicators
# These are approximate values based on historical recession patterns
INDICATOR_THRESHOLDS = {
    'yield_curve': {
        'recession_threshold': -0.5,  # Inverted yield curve (negative spread)
        'mean': 0.8,
        'std': 1.2
    },
    'unemployment': {
        'recession_threshold': 6.0,  # Unemployment rate above 6%
        'mean': 5.5,
        'std': 1.5
    },
    'gdp': {
        'recession_threshold': 0.0,  # Negative GDP growth
        'mean': 2.5,
        'std': 2.0
    },
    'consumer_confidence': {
        'recession_threshold': 70.0,  # Low consumer confidence
        'mean': 85.0,
        'std': 10.0
    },
    'leading_indicators': {
        'recession_threshold': -1.0,  # Declining leading indicators
        'mean': 0.0,
        'std': 1.5
    }
}
