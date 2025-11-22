"""
Data collection functions for US Recession 2025 forecast model.

Fetches economic indicators from FRED API and processes them for analysis.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from lib.data_fetcher import fetch_fred_data, DataFetchError
from .config import DATA_SOURCES


logger = logging.getLogger(__name__)


class IndicatorFetchError(Exception):
    """Exception raised when fetching an economic indicator fails."""
    pass


def fetch_economic_indicators(
    lookback_days: int = 365,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch all economic indicators needed for recession forecast.
    
    Args:
        lookback_days: Number of days to look back for historical data
        api_key: Optional FRED API key (uses environment variable if not provided)
    
    Returns:
        Dictionary containing indicator data with keys:
        - yield_curve: Latest yield curve spread value
        - unemployment: Latest unemployment rate
        - gdp: Latest GDP growth rate
        - consumer_confidence: Latest consumer confidence index
        - leading_indicators: Latest leading indicators value
        - jobless_claims: Latest initial jobless claims
        - timestamps: Dict of timestamps for each indicator
        - raw_data: Dict of raw API responses for each indicator
    
    Raises:
        IndicatorFetchError: If any required indicator cannot be fetched
    """
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
    
    indicators = {}
    timestamps = {}
    raw_data = {}
    errors = []
    
    # Fetch each indicator
    for indicator_name, series_id in DATA_SOURCES.items():
        try:
            logger.info(f"Fetching {indicator_name} (series: {series_id})")
            data = fetch_fred_data(
                series_id=series_id,
                start_date=start_date,
                end_date=end_date,
                api_key=api_key
            )
            
            # Extract the most recent observation
            observations = data.get('observations', [])
            if not observations:
                raise IndicatorFetchError(
                    f"No observations returned for {indicator_name} (series: {series_id})"
                )
            
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
                raise IndicatorFetchError(
                    f"No valid observations found for {indicator_name} (series: {series_id})"
                )
            
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
    
    # Check if we have core required indicators (leading_indicators is optional)
    required_indicators = {'yield_curve', 'unemployment', 'gdp', 'consumer_confidence', 'jobless_claims'}
    missing_required = required_indicators - set(indicators.keys())
    
    if missing_required:
        error_msg = (
            f"Failed to fetch required indicators: {missing_required}. "
            f"Errors: {'; '.join(errors)}"
        )
        raise IndicatorFetchError(error_msg)
    
    # If leading_indicators is missing, use a default neutral value
    if 'leading_indicators' not in indicators:
        logger.warning("Leading indicators not available, using neutral default value of 0.0")
        indicators['leading_indicators'] = 0.0
        timestamps['leading_indicators'] = end_date
    
    return {
        'yield_curve': indicators['yield_curve'],
        'unemployment': indicators['unemployment'],
        'gdp': indicators['gdp'],
        'consumer_confidence': indicators['consumer_confidence'],
        'leading_indicators': indicators['leading_indicators'],
        'jobless_claims': indicators['jobless_claims'],
        'timestamps': timestamps,
        'raw_data': raw_data
    }


def get_indicator_value(indicator_name: str, api_key: Optional[str] = None) -> float:
    """
    Fetch a single economic indicator value.
    
    Args:
        indicator_name: Name of the indicator (must be in DATA_SOURCES)
        api_key: Optional FRED API key
    
    Returns:
        Latest value for the indicator
    
    Raises:
        ValueError: If indicator_name is not recognized
        IndicatorFetchError: If indicator cannot be fetched
    """
    if indicator_name not in DATA_SOURCES:
        raise ValueError(
            f"Unknown indicator: {indicator_name}. "
            f"Valid indicators: {list(DATA_SOURCES.keys())}"
        )
    
    series_id = DATA_SOURCES[indicator_name]
    
    try:
        # Fetch last 30 days of data
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
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
