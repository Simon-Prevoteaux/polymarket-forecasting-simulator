"""
US Recession 2025 Forecast Model

Implements the RecessionModel class that predicts recession probability
based on multiple economic indicators using weighted logistic regression.
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from forecasts import ForecastModel
from lib.probability import normalize_probability, combine_probabilities, logistic_transform
from lib.database import create_forecast_table, save_forecast_result
from lib.utils import validate_parameters
from .config import (
    DEFAULT_PARAMS,
    PARAMETER_SCHEMAS,
    INDICATOR_THRESHOLDS
)
from .data import fetch_economic_indicators, IndicatorFetchError


logger = logging.getLogger(__name__)


class RecessionModel(ForecastModel):
    """
    Forecast model for US recession probability by end of 2025.
    
    Analyzes multiple economic indicators including yield curve, unemployment,
    GDP growth, consumer confidence, and leading indicators to predict
    recession probability using weighted logistic regression.
    """
    
    def __init__(self):
        """Initialize the recession model and create database table."""
        self.name = "us_recession_2025"
        self.display_name = "US Recession 2025"
        self.description = (
            "Predicts the probability of a US recession by end of 2025 based on "
            "economic indicators including yield curve, unemployment rate, GDP growth, "
            "consumer confidence, leading indicators, and jobless claims."
        )
        self._last_updated = None
        self._last_indicators = None
        
        # Create database table for this forecast
        self._initialize_database()
    
    def _initialize_database(self):
        """Create the database table for storing forecast results."""
        schema = {
            'yield_curve_value': 'REAL',
            'unemployment_rate': 'REAL',
            'gdp_growth': 'REAL',
            'consumer_confidence': 'REAL',
            'leading_indicators': 'REAL',
            'jobless_claims': 'REAL'
        }
        create_forecast_table(self.name, schema)
        logger.info(f"Initialized database table for {self.name}")
    
    def get_name(self) -> str:
        """Return human-readable forecast name."""
        return self.display_name
    
    def get_description(self) -> str:
        """Return forecast description."""
        return self.description
    
    def get_parameters(self) -> Dict:
        """
        Return adjustable parameters with metadata.
        
        Returns:
            Dictionary mapping parameter names to their schemas
        """
        return {
            name: {
                'name': schema.name,
                'type': schema.type,
                'default': schema.default,
                'min_value': schema.min_value,
                'max_value': schema.max_value,
                'description': schema.description
            }
            for name, schema in PARAMETER_SCHEMAS.items()
        }
    
    def get_last_updated(self) -> datetime:
        """Return timestamp of last data update."""
        if self._last_updated is None:
            return datetime.now()
        return self._last_updated
    
    def get_data_sources(self) -> list:
        """Return list of data sources used by this forecast."""
        return [
            'FRED (Federal Reserve Economic Data) - T10Y2Y (10-Year Treasury Constant Maturity Minus 2-Year)',
            'FRED - UNRATE (Unemployment Rate)',
            'FRED - A191RL1Q225SBEA (Real GDP Growth)',
            'FRED - UMCSENT (University of Michigan Consumer Sentiment)',
            'FRED - USSLIND (Leading Index for the United States)',
            'FRED - ICSA (Initial Jobless Claims)'
        ]
    
    def calculate_probability(self, params: Optional[Dict] = None) -> float:
        """
        Calculate recession probability based on economic indicators.
        
        Uses weighted logistic regression approach to combine signals from
        multiple economic indicators into a single probability estimate.
        
        Args:
            params: Optional dictionary of parameter overrides. If None, uses defaults.
        
        Returns:
            Probability of recession (0-1)
        
        Raises:
            ValueError: If parameters are invalid
            IndicatorFetchError: If economic data cannot be fetched
        """
        # Use default parameters if none provided
        if params is None:
            params = DEFAULT_PARAMS.copy()
        else:
            # Merge with defaults
            merged_params = DEFAULT_PARAMS.copy()
            merged_params.update(params)
            params = merged_params
        
        # Validate parameters
        errors = validate_parameters(params, PARAMETER_SCHEMAS)
        if errors:
            error_msg = "; ".join([f"{k}: {v}" for k, v in errors.items()])
            raise ValueError(f"Invalid parameters: {error_msg}")
        
        # Fetch economic indicators
        logger.info("Fetching economic indicators...")
        try:
            indicators = fetch_economic_indicators(
                lookback_days=params['lookback_days']
            )
        except IndicatorFetchError as e:
            logger.error(f"Failed to fetch indicators: {e}")
            raise
        
        self._last_indicators = indicators
        self._last_updated = datetime.now()
        
        # Calculate individual indicator signals
        signals = self._calculate_indicator_signals(indicators)
        
        # Combine signals using weighted average
        weights = [
            params['yield_curve_weight'],
            params['unemployment_weight'],
            params['gdp_weight'],
            params['confidence_weight'],
            params['leading_indicators_weight']
        ]
        
        probabilities = [
            signals['yield_curve'],
            signals['unemployment'],
            signals['gdp'],
            signals['consumer_confidence'],
            signals['leading_indicators']
        ]
        
        # Normalize weights to sum to 1
        weight_sum = sum(weights)
        if weight_sum > 0:
            normalized_weights = [w / weight_sum for w in weights]
        else:
            # If all weights are zero, use equal weighting
            normalized_weights = [0.2] * 5
        
        # Combine probabilities
        combined_probability = combine_probabilities(probabilities, normalized_weights)
        
        # Ensure result is in valid range
        final_probability = normalize_probability(combined_probability)
        
        # Save result to database
        self._save_result(final_probability, params, indicators)
        
        logger.info(f"Calculated recession probability: {final_probability:.4f}")
        
        return final_probability
    
    def _calculate_indicator_signals(self, indicators: Dict) -> Dict[str, float]:
        """
        Calculate individual probability signals from each indicator.
        
        Uses logistic transformation of z-scores to convert indicator values
        to probability space.
        
        Args:
            indicators: Dictionary of indicator values
        
        Returns:
            Dictionary mapping indicator names to probability signals (0-1)
        """
        signals = {}
        
        # Yield curve: inverted curve (negative) signals recession
        yield_curve_val = indicators['yield_curve']
        threshold = INDICATOR_THRESHOLDS['yield_curve']
        z_score = (yield_curve_val - threshold['mean']) / threshold['std']
        # Negative z-score (inverted curve) should give higher recession probability
        signals['yield_curve'] = logistic_transform(-z_score, center=0, scale=1.0)
        
        # Unemployment: rising unemployment signals recession
        unemployment_val = indicators['unemployment']
        threshold = INDICATOR_THRESHOLDS['unemployment']
        z_score = (unemployment_val - threshold['mean']) / threshold['std']
        # Positive z-score (high unemployment) should give higher recession probability
        signals['unemployment'] = logistic_transform(z_score, center=0, scale=1.0)
        
        # GDP: negative growth signals recession
        gdp_val = indicators['gdp']
        threshold = INDICATOR_THRESHOLDS['gdp']
        z_score = (gdp_val - threshold['mean']) / threshold['std']
        # Negative z-score (low/negative growth) should give higher recession probability
        signals['gdp'] = logistic_transform(-z_score, center=0, scale=1.0)
        
        # Consumer confidence: low confidence signals recession
        confidence_val = indicators['consumer_confidence']
        threshold = INDICATOR_THRESHOLDS['consumer_confidence']
        z_score = (confidence_val - threshold['mean']) / threshold['std']
        # Negative z-score (low confidence) should give higher recession probability
        signals['consumer_confidence'] = logistic_transform(-z_score, center=0, scale=1.0)
        
        # Leading indicators: declining indicators signal recession
        leading_val = indicators['leading_indicators']
        threshold = INDICATOR_THRESHOLDS['leading_indicators']
        z_score = (leading_val - threshold['mean']) / threshold['std']
        # Negative z-score (declining indicators) should give higher recession probability
        signals['leading_indicators'] = logistic_transform(-z_score, center=0, scale=1.0)
        
        logger.debug(f"Indicator signals: {signals}")
        
        return signals
    
    def _save_result(
        self,
        probability: float,
        params: Dict,
        indicators: Dict
    ) -> None:
        """
        Save forecast result to database.
        
        Args:
            probability: Calculated probability
            params: Parameters used in calculation
            indicators: Indicator values used
        """
        additional_data = {
            'yield_curve_value': indicators['yield_curve'],
            'unemployment_rate': indicators['unemployment'],
            'gdp_growth': indicators['gdp'],
            'consumer_confidence': indicators['consumer_confidence'],
            'leading_indicators': indicators['leading_indicators'],
            'jobless_claims': indicators['jobless_claims']
        }
        
        # Create data snapshot for storage
        data_snapshot = {
            'indicators': {
                'yield_curve': indicators['yield_curve'],
                'unemployment': indicators['unemployment'],
                'gdp': indicators['gdp'],
                'consumer_confidence': indicators['consumer_confidence'],
                'leading_indicators': indicators['leading_indicators'],
                'jobless_claims': indicators['jobless_claims']
            },
            'timestamps': indicators['timestamps']
        }
        
        try:
            save_forecast_result(
                forecast_name=self.name,
                probability=probability,
                parameters=params,
                data_snapshot=data_snapshot,
                additional_data=additional_data
            )
            logger.info("Saved forecast result to database")
        except Exception as e:
            logger.error(f"Failed to save forecast result: {e}")
            # Don't raise - calculation succeeded even if save failed
