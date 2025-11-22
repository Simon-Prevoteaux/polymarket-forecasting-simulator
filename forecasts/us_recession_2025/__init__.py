"""
US Recession 2025 Forecast Model

Predicts the probability of a US recession by end of 2025 based on
economic indicators including yield curve, unemployment, GDP, consumer
confidence, leading indicators, and jobless claims.

V2 enhancements include:
- Additional economic indicators (credit spreads, housing, manufacturing, retail, oil, VIX)
- Feature engineering (rate of change, moving averages, volatility)
- Temporal decay modeling (time-to-event adjustments)
- Historical backtesting capabilities
- Jupyter notebook analysis suite
"""

from .model import RecessionModel
from .model_v2 import RecessionModelV2
from .features import FeatureEngineer
# Import from new generic library
from lib.temporal_adjustment import TemporalAdjuster, calculate_time_to_event

# Legacy imports for backward compatibility (deprecated)
# These are now in lib.temporal_adjustment
def exponential_decay_adjustment(*args, **kwargs):
    """DEPRECATED: Use lib.temporal_adjustment.threshold_decay instead."""
    import warnings
    warnings.warn(
        "exponential_decay_adjustment is deprecated. Use lib.temporal_adjustment with method='threshold_decay'",
        DeprecationWarning,
        stacklevel=2
    )
    from lib.temporal_adjustment import threshold_aware_decay
    return threshold_aware_decay(*args, **kwargs)

def sigmoid_decay_adjustment(*args, **kwargs):
    """DEPRECATED: Use lib.temporal_adjustment.trend_amplification instead."""
    import warnings
    warnings.warn(
        "sigmoid_decay_adjustment is deprecated. Use lib.temporal_adjustment with method='trend_amplification'",
        DeprecationWarning,
        stacklevel=2
    )
    from lib.temporal_adjustment import trend_amplification
    return trend_amplification(*args, **kwargs)
from .backtesting import BacktestEngine

__all__ = [
    'RecessionModel',
    'RecessionModelV2',
    'FeatureEngineer',
    'TemporalAdjuster',
    'BacktestEngine',
    'calculate_time_to_event',
    'exponential_decay_adjustment',
    'sigmoid_decay_adjustment'
]
