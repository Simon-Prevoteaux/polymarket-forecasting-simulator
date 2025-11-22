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
from .temporal import TemporalAdjuster, calculate_time_to_event, exponential_decay_adjustment, sigmoid_decay_adjustment
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
