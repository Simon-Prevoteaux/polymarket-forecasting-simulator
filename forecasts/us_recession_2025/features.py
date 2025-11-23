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
        
        # List of indicators to process
        indicator_names = [
            'unemployment', 'gdp', 'yield_curve', 'consumer_confidence',
            'leading_indicators', 'jobless_claims', 'credit_spread',
            'housing_starts', 'manufacturing_pmi', 'retail_sales',
            'oil_price', 'vix'
        ]
        
        # Process each indicator
        for indicator_name in indicator_names:
            # Extract time series from raw_data
            time_series = self._extract_time_series(raw_data, indicator_name)
            
            if time_series is None or len(time_series) == 0:
                # Skip this indicator if no data available
                # Features will not be added for this indicator
                continue
            
            # Calculate rate of change features
            # Returns None for periods with insufficient data
            roc_features = self.calculate_rate_of_change(time_series)
            for period, value in roc_features.items():
                features[f'{indicator_name}_{period}'] = value
            
            # Calculate moving average features
            # Returns None for windows with insufficient data
            ma_features = self.calculate_moving_averages(time_series)
            for window, value in ma_features.items():
                features[f'{indicator_name}_{window}'] = value
            
            # Calculate volatility feature
            # Returns None if insufficient data for volatility calculation
            volatility = self.calculate_volatility(time_series)
            features[f'{indicator_name}_volatility'] = volatility
        
        return features
    
    def _extract_time_series(
        self,
        raw_data: Dict[str, Any],
        indicator_name: str
    ) -> Optional[List[float]]:
        """
        Extract time series values from raw FRED API data.
        
        Args:
            raw_data: Dictionary of raw API responses
            indicator_name: Name of the indicator to extract
        
        Returns:
            List of float values (chronologically ordered, most recent last),
            or None if data not available
        """
        if indicator_name not in raw_data:
            return None
        
        indicator_data = raw_data[indicator_name]
        observations = indicator_data.get('observations', [])
        
        if not observations:
            return None
        
        # Extract values, filtering out missing data ('.')
        values = []
        for obs in observations:
            if obs['value'] != '.':
                try:
                    values.append(float(obs['value']))
                except (ValueError, KeyError):
                    continue
        
        if not values:
            return None
        
        # Apply forward-fill for any gaps
        # This handles missing data by carrying forward the last known value
        filled_values = self._forward_fill(values)
        
        return filled_values
    
    def _forward_fill(self, values: List[Optional[float]]) -> List[float]:
        """
        Forward-fill missing values in a time series.
        
        This method handles gaps in time series data by carrying forward the last
        known value. This is a common approach for handling missing economic data
        where the most recent observation is the best estimate.
        
        Args:
            values: List of values (may contain None for missing data)
        
        Returns:
            List with gaps filled by carrying forward last known value.
            If the first value is None, it will remain None.
        """
        if not values:
            return []
        
        filled = []
        last_valid = None
        
        for value in values:
            if value is not None:
                filled.append(value)
                last_valid = value
            elif last_valid is not None:
                # Forward-fill: use last known value
                filled.append(last_valid)
            else:
                # No previous value to fill with, keep as None
                # This will be filtered out later
                pass
        
        return filled
