"""
Election 2028 Forecast Model

Implements the ElectionModel class that predicts the probability of
Democratic victory in the 2028 US Presidential Election.

This is a DUMMY implementation for demonstration purposes.
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
from .data import fetch_election_indicators, ElectionDataFetchError


logger = logging.getLogger(__name__)


class ElectionModel(ForecastModel):
    """
    Forecast model for 2028 US Presidential Election.
    
    Predicts the probability of Democratic victory based on polling data,
    economic indicators, approval ratings, fundraising, and historical patterns.
    
    NOTE: This is a DUMMY implementation using random data for demonstration.
    """
    
    def __init__(self):
        """Initialize the election model and create database table."""
        self.name = "election_2028"
        self.display_name = "US Presidential Election 2028"
        self.description = (
            "Predicts the probability of Democratic victory in the 2028 US Presidential "
            "Election based on polling averages, economic indicators, presidential approval "
            "ratings, campaign fundraising, and historical election patterns. "
            "(DEMO: Uses randomly generated data)"
        )
        self._last_updated = None
        self._last_indicators = None
        
        # Create database table for this forecast
        self._initialize_database()
    
    def _initialize_database(self):
        """Create the database table for storing forecast results."""
        schema = {
            'polling': 'REAL',
            'economic_index': 'REAL',
            'approval': 'REAL',
            'fundraising': 'REAL',
            'historical_advantage': 'REAL'
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
            'RealClearPolitics - National polling averages (DEMO: Random data)',
            'FiveThirtyEight - Polling aggregation (DEMO: Random data)',
            'Bureau of Economic Analysis - Economic indicators (DEMO: Random data)',
            'Gallup - Presidential approval ratings (DEMO: Random data)',
            'Federal Election Commission - Campaign fundraising data (DEMO: Random data)',
            'Historical election database - Past election patterns (DEMO: Random data)'
        ]
    
    def calculate_probability(self, params: Optional[Dict] = None) -> float:
        """
        Calculate probability of Democratic victory.
        
        Uses weighted combination of polling, economic indicators, approval ratings,
        fundraising, and historical patterns.
        
        Args:
            params: Optional dictionary of parameter overrides. If None, uses defaults.
        
        Returns:
            Probability of Democratic victory (0-1)
        
        Raises:
            ValueError: If parameters are invalid
            ElectionDataFetchError: If election data cannot be fetched
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
        
        # Fetch election indicators
        logger.info("Fetching election indicators...")
        try:
            indicators = fetch_election_indicators()
        except ElectionDataFetchError as e:
            logger.error(f"Failed to fetch indicators: {e}")
            raise
        
        self._last_indicators = indicators
        self._last_updated = datetime.now()
        
        # Calculate individual indicator signals
        signals = self._calculate_indicator_signals(indicators)
        
        # Combine signals using weighted average
        weights = [
            params['polling_weight'],
            params['economic_weight'],
            params['approval_weight'],
            params['fundraising_weight'],
            params['historical_weight']
        ]
        
        probabilities = [
            signals['polling'],
            signals['economic'],
            signals['approval'],
            signals['fundraising'],
            signals['historical']
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
        
        logger.info(f"Calculated Democratic victory probability: {final_probability:.4f}")
        
        return final_probability
    
    def _calculate_indicator_signals(self, indicators: Dict) -> Dict[str, float]:
        """
        Calculate individual probability signals from each indicator.
        
        Uses logistic transformation to convert indicator values to probability space.
        
        Args:
            indicators: Dictionary of indicator values
        
        Returns:
            Dictionary mapping indicator names to probability signals (0-1)
        """
        signals = {}
        
        # Polling: Higher polling = higher probability
        polling_val = indicators['polling']
        threshold = INDICATOR_THRESHOLDS['polling']
        z_score = (polling_val - threshold['mean']) / threshold['std']
        signals['polling'] = logistic_transform(z_score, center=0, scale=1.0)
        
        # Economic index: Better economy helps incumbent party
        economic_val = indicators['economic_index']
        threshold = INDICATOR_THRESHOLDS['economic_index']
        z_score = (economic_val - threshold['mean']) / threshold['std']
        signals['economic'] = logistic_transform(z_score, center=0, scale=1.0)
        
        # Approval: Higher approval helps incumbent party
        approval_val = indicators['approval']
        threshold = INDICATOR_THRESHOLDS['approval']
        z_score = (approval_val - threshold['mean']) / threshold['std']
        signals['approval'] = logistic_transform(z_score, center=0, scale=1.0)
        
        # Fundraising: More money = higher probability
        fundraising_val = indicators['fundraising']
        threshold = INDICATOR_THRESHOLDS['fundraising']
        z_score = (fundraising_val - threshold['mean']) / threshold['std']
        signals['fundraising'] = logistic_transform(z_score, center=0, scale=1.0)
        
        # Historical advantage: Positive = helps Democrats
        historical_val = indicators['historical_advantage']
        threshold = INDICATOR_THRESHOLDS['historical_advantage']
        z_score = (historical_val - threshold['mean']) / threshold['std']
        signals['historical'] = logistic_transform(z_score, center=0, scale=1.0)
        
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
            'polling': indicators['polling'],
            'economic_index': indicators['economic_index'],
            'approval': indicators['approval'],
            'fundraising': indicators['fundraising'],
            'historical_advantage': indicators['historical_advantage']
        }
        
        # Create data snapshot for storage
        data_snapshot = {
            'indicators': {
                'polling': indicators['polling'],
                'economic_index': indicators['economic_index'],
                'approval': indicators['approval'],
                'fundraising': indicators['fundraising'],
                'historical_advantage': indicators['historical_advantage']
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
