"""
Data collection functions for US Recession 2025 Forecast V2.

Fetches enhanced set of economic indicators from FRED API with support for
historical data retrieval (as_of_date parameter for backtesting).
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from lib.data_fetcher import fetch_fred_data, DataFetchError
from .config import DATA_SOURCES
from .config_v2 import V2_INDICATOR_SERIES


logger = logging.getLogger(__name__)


class IndicatorFetchError(Exception):
    """Exception raised when fetching an economic indicator fails."""
    pass


def fetch_economic_indicators_v2(
    lookback_days: int = 365,
    as_of_date: Optional[datetime] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch enhanced set of economic indicators for v2 model.
    
    This function fetches all v1 indicators plus new v2 indicators (credit spreads,
    housing starts, manufacturing PMI, retail sales, oil prices, VIX). It supports
    historical data fetching via the as_of_date parameter for backtesting.
    
    Args:
        lookback_days: Number of days to look back for historical data
        as_of_date: Date to fetch data as of (for backtesting). If None, uses current date.
                   This ensures no future data leakage in historical analysis.
        api_key: Optional FRED API key (uses environment variable if not provided)
    
    Returns:
        Dictionary containing indicator data with keys:
        - All v1 indicators: yield_curve, unemployment, gdp, consumer_confidence,
          leading_indicators, jobless_claims
        - New v2 indicators: credit_spread, housing_starts, manufacturing_pmi,
          retail_sales, oil_price, vix
        - timestamps: Dict of timestamps for each indicator
        - as_of_date: The date data was fetched as of (for temporal consistency)
        - raw_data: Dict of raw API responses for each indicator
    
    Raises:
        IndicatorFetchError: If required indicators cannot be fetched
    
    Examples:
        >>> # Fetch current data
        >>> indicators = fetch_economic_indicators_v2()
        >>> print(indicators['yield_curve'])
        
        >>> # Fetch historical data for backtesting
        >>> historical_date = datetime(2023, 6, 15)
        >>> indicators = fetch_economic_indicators_v2(as_of_date=historical_date)
        >>> # Returns only data available on or before 2023-06-15
    """
    # Determine the effective end date (as_of_date or now)
    if as_of_date is None:
        end_date_dt = datetime.now()
    else:
        end_date_dt = as_of_date
    
    end_date = end_date_dt.strftime('%Y-%m-%d')
    start_date = (end_date_dt - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
    
    indicators = {}
    timestamps = {}
    raw_data = {}
    errors = []
    
    # Combine v1 and v2 indicator sources
    all_indicators = {**DATA_SOURCES, **V2_INDICATOR_SERIES}
    
    # Fetch each indicator
    for indicator_name, series_id in all_indicators.items():
        try:
            logger.info(f"Fetching {indicator_name} (series: {series_id}) as of {end_date}")
            data = fetch_fred_data(
                series_id=series_id,
                start_date=start_date,
                end_date=end_date,
                api_key=api_key
            )
            
            # Extract the most recent observation (on or before as_of_date)
            observations = data.get('observations', [])
            if not observations:
                logger.warning(
                    f"No observations returned for {indicator_name} (series: {series_id})"
                )
                errors.append(f"No observations for {indicator_name}")
                continue
            
            # Find the most recent non-missing value
            latest_value = None
            latest_date = None
            
            for obs in reversed(observations):
                if obs['value'] != '.':  # FRED uses '.' for missing values
                    try:
                        latest_value = float(obs['value'])
                        latest_date = obs['date']
                        break
                    except (ValueError, KeyError):
                        continue
            
            if latest_value is None:
                logger.warning(
                    f"No valid observations found for {indicator_name} (series: {series_id})"
                )
                errors.append(f"No valid observations for {indicator_name}")
                continue
            
            indicators[indicator_name] = latest_value
            timestamps[indicator_name] = latest_date
            raw_data[indicator_name] = data
            
            logger.info(
                f"Successfully fetched {indicator_name}: {latest_value} (date: {latest_date})"
            )
            
        except DataFetchError as e:
            error_msg = f"Failed to fetch {indicator_name}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error fetching {indicator_name}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
    
    # Check if we have core required indicators (v1 indicators)
    # V2 indicators are optional and will use neutral defaults if missing
    required_indicators = {'yield_curve', 'unemployment', 'gdp', 'consumer_confidence'}
    missing_required = required_indicators - set(indicators.keys())
    
    if missing_required:
        error_msg = (
            f"Failed to fetch required indicators: {missing_required}. "
            f"Errors: {'; '.join(errors)}"
        )
        raise IndicatorFetchError(error_msg)
    
    # Handle missing optional indicators with neutral defaults
    # These defaults represent "no signal" values
    optional_defaults = {
        'leading_indicators': 0.0,      # Neutral leading indicators
        'jobless_claims': 300000.0,     # Historical average
        'credit_spread': 2.0,            # Historical average spread
        'housing_starts': 1400.0,        # Historical average (thousands)
        'manufacturing_pmi': 50.0,       # Neutral PMI (50 = no change)
        'retail_sales': 0.0,             # Neutral growth rate
        'oil_price': 70.0,               # Historical average
        'vix': 15.0                      # Historical average volatility
    }
    
    for indicator_name, default_value in optional_defaults.items():
        if indicator_name not in indicators:
            logger.warning(
                f"{indicator_name} not available, using neutral default value of {default_value}"
            )
            indicators[indicator_name] = default_value
            timestamps[indicator_name] = end_date
    
    # Build the result dictionary with all indicators
    result = {
        # V1 indicators
        'yield_curve': indicators['yield_curve'],
        'unemployment': indicators['unemployment'],
        'gdp': indicators['gdp'],
        'consumer_confidence': indicators['consumer_confidence'],
        'leading_indicators': indicators['leading_indicators'],
        'jobless_claims': indicators['jobless_claims'],
        
        # V2 indicators
        'credit_spread': indicators['credit_spread'],
        'housing_starts': indicators['housing_starts'],
        'manufacturing_pmi': indicators['manufacturing_pmi'],
        'retail_sales': indicators['retail_sales'],
        'oil_price': indicators['oil_price'],
        'vix': indicators['vix'],
        
        # Metadata
        'timestamps': timestamps,
        'as_of_date': end_date,
        'raw_data': raw_data
    }
    
    return result


def get_indicator_value_v2(
    indicator_name: str,
    as_of_date: Optional[datetime] = None,
    api_key: Optional[str] = None
) -> float:
    """
    Fetch a single economic indicator value (v2 version with as_of_date support).
    
    Args:
        indicator_name: Name of the indicator (must be in DATA_SOURCES or V2_INDICATOR_SERIES)
        as_of_date: Date to fetch data as of (for backtesting)
        api_key: Optional FRED API key
    
    Returns:
        Latest value for the indicator (on or before as_of_date)
    
    Raises:
        ValueError: If indicator_name is not recognized
        IndicatorFetchError: If indicator cannot be fetched
    """
    all_indicators = {**DATA_SOURCES, **V2_INDICATOR_SERIES}
    
    if indicator_name not in all_indicators:
        raise ValueError(
            f"Unknown indicator: {indicator_name}. "
            f"Valid indicators: {list(all_indicators.keys())}"
        )
    
    series_id = all_indicators[indicator_name]
    
    try:
        # Determine end date
        if as_of_date is None:
            end_date_dt = datetime.now()
        else:
            end_date_dt = as_of_date
        
        # Fetch last 30 days of data (or up to as_of_date)
        end_date = end_date_dt.strftime('%Y-%m-%d')
        start_date = (end_date_dt - timedelta(days=30)).strftime('%Y-%m-%d')
        
        data = fetch_fred_data(
            series_id=series_id,
            start_date=start_date,
            end_date=end_date,
            api_key=api_key
        )
        
        observations = data.get('observations', [])
        if not observations:
            raise IndicatorFetchError(f"No observations for {indicator_name}")
        
        # Get most recent non-missing value
        for obs in reversed(observations):
            if obs['value'] != '.':
                return float(obs['value'])
        
        raise IndicatorFetchError(f"No valid observations for {indicator_name}")
        
    except DataFetchError as e:
        raise IndicatorFetchError(f"Failed to fetch {indicator_name}: {str(e)}")
