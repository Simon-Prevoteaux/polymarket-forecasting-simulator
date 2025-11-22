"""
Feature engineering module for US Recession 2025 Forecast V2

Calculates derived features from raw economic indicators.
"""

from typing import Dict, List, Any, Optional
import statistics


class FeatureEngineer:
    """Calculate derived features from economic indicators."""
    
    def calculate_rate_of_change(
        self,
        values: List[float],
        periods: List[int] = [30, 90, 180]
    ) -> Dict[str, Optional[float]]:
        """
        Calculate rate of change over multiple periods.
        
        Args:
            values: Time series values (most recent last)
            periods: List of periods to calculate rate of change for
        
        Returns:
            Dictionary with rate of change for each period
        """
        results = {}
        
        for period in periods:
            if len(values) < period + 1:
                results[f'roc_{period}d'] = None
                continue
            
            current_value = values[-1]
            past_value = values[-(period + 1)]
            
            if past_value == 0:
                results[f'roc_{period}d'] = None
            else:
                roc = (current_value - past_value) / past_value
                results[f'roc_{period}d'] = roc
        
        return results
    
    def calculate_moving_averages(
        self,
        values: List[float],
        windows: List[int] = [30, 90]
    ) -> Dict[str, Optional[float]]:
        """
        Calculate simple moving averages.
        
        Args:
            values: Time series values (most recent last)
            windows: List of window sizes for moving averages
        
        Returns:
            Dictionary with moving average for each window
        """
        results = {}
        
        for window in windows:
            if len(values) < window:
                results[f'ma_{window}d'] = None
                continue
            
            window_values = values[-window:]
            results[f'ma_{window}d'] = statistics.mean(window_values)
        
        return results
    
    def calculate_volatility(
        self,
        values: List[float],
        window: int = 30
    ) -> Optional[float]:
        """
        Calculate rolling volatility (standard deviation).
        
        Args:
            values: Time series values (most recent last)
            window: Window size for volatility calculation
        
        Returns:
            Standard deviation of values in window, or None if insufficient data
        """
        if len(values) < window:
            return None
        
        window_values = values[-window:]
        
        if len(window_values) < 2:
            return None
        
        return statistics.stdev(window_values)
    
    def engineer_features(
        self,
        indicators: Dict[str, Any],
        raw_data: Dict[str, Any]
    ) -> Dict[str, Optional[float]]:
        """
        Generate all engineered features.
        
        Args:
            indicators: Current indicator values
            raw_data: Historical time series data for each indicator
        
        Returns:
            Dictionary with features like:
            - unemployment_roc_30d: 30-day rate of change
            - gdp_ma_90d: 90-day moving average
            - yield_curve_volatility: Recent volatility
        """
        features = {}
        
        # Will be fully implemented in later tasks
        # For now, return empty features structure
        
        return features
