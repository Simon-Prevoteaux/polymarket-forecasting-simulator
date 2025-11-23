"""
US Recession 2025 Forecast Model V2

Enhanced recession forecast model with:
- Additional economic indicators
- Feature engineering
- Temporal decay adjustment
- Backtesting support
"""

import logging
from datetime import datetime
from typing import Dict, Optional, Any, List
from forecasts import ForecastModel
from lib.database import get_connection
from lib.probability import normalize_probability, combine_probabilities, logistic_transform
from lib.utils import validate_parameters, ParameterSchema
import json

from .data_v2 import fetch_economic_indicators_v2, IndicatorFetchError
from .features import FeatureEngineer
from lib.temporal_adjustment import TemporalAdjuster, calculate_time_to_event
from .config import INDICATOR_THRESHOLDS, DEFAULT_PARAMS, PARAMETER_SCHEMAS
from .config_v2 import (
    get_v2_default_parameters,
    V2_PARAMETER_SCHEMA,
    V2_PARAMETER_SCHEMAS,
    TEMPORAL_DECAY_CONFIG,
    FORECAST_DEADLINE
)


logger = logging.getLogger(__name__)


class RecessionModelV2(ForecastModel):
    """
    Enhanced recession forecast model with temporal decay.
    
    Extends v1 model with:
    - Additional economic indicators
    - Feature engineering
    - Temporal decay adjustment
    - Backtesting support
    """
    
    def __init__(self):
        """Initialize v2 model with configuration, feature engineer, and temporal adjuster."""
        self.name = "us_recession_2025_v2"
        self.display_name = "US Recession 2025 V2"
        self.description = (
            "Enhanced US Recession 2025 forecast with temporal decay modeling, "
            "additional economic indicators (credit spreads, housing starts, PMI, "
            "retail sales, oil prices, VIX), and feature engineering."
        )
        self.table_name = 'forecast_us_recession_2025_v2'
        
        # Initialize feature engineer
        self.feature_engineer = FeatureEngineer()
        
        # Initialize temporal adjuster with default config using new library
        method = TEMPORAL_DECAY_CONFIG.get('method', 'adaptive')
        
        # Map old method names to new library methods
        if method == 'exponential':
            # Old exponential with threshold -> threshold_decay in new library
            self.temporal_adjuster = TemporalAdjuster(
                method='threshold_decay',
                total_days=365,
                decay_power=TEMPORAL_DECAY_CONFIG.get('decay_rate', 0.015) * 100,  # Convert rate to power
                threshold=TEMPORAL_DECAY_CONFIG.get('threshold', 0.4)
            )
        elif method == 'sigmoid':
            # Sigmoid not in new library, use trend_amplification as closest
            self.temporal_adjuster = TemporalAdjuster(
                method='trend_amplification',
                total_days=365,
                amplification_power=1.5,
                threshold=0.5
            )
        elif method == 'theta':
            # Theta is now in new library
            self.temporal_adjuster = TemporalAdjuster(
                method='theta',
                total_days=TEMPORAL_DECAY_CONFIG.get('theta_total_days', 365),
                decay_power=TEMPORAL_DECAY_CONFIG.get('theta_decay_power', 1.5)
            )
        elif method == 'adaptive':
            # New adaptive method (recommended)
            self.temporal_adjuster = TemporalAdjuster(
                method='adaptive',
                total_days=365,
                decay_power=1.5,
                amplification_power=1.5,
                lower_threshold=0.4,
                upper_threshold=0.6
            )
        else:
            # Default to adaptive (smart method)
            self.temporal_adjuster = TemporalAdjuster(
                method='adaptive',
                total_days=365,
                decay_power=1.5,
                amplification_power=1.5,
                lower_threshold=0.4,
                upper_threshold=0.6
            )
        
        # Set forecast deadline
        self.deadline = FORECAST_DEADLINE
        
        # Create database table
        self._create_table()
        
        logger.info(f"Initialized {self.name} model")
    
    def _create_table(self):
        """Create v2 forecast table if it doesn't exist."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                base_probability REAL NOT NULL CHECK(base_probability >= 0 AND base_probability <= 1),
                adjusted_probability REAL NOT NULL CHECK(adjusted_probability >= 0 AND adjusted_probability <= 1),
                days_remaining INTEGER,
                parameters TEXT,
                indicators TEXT,
                features TEXT,
                temporal_metadata TEXT,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created/verified table: {self.table_name}")
    
    def get_name(self) -> str:
        """Return human-readable forecast name."""
        return self.display_name
    
    def get_description(self) -> str:
        """Return forecast description."""
        return self.description
    
    def get_parameters(self) -> Dict:
        """
        Return adjustable parameters with metadata.
        
        Combines v1 parameters (weights, lookback_days) with v2 parameters
        (temporal decay settings).
        
        Returns:
            Dictionary mapping parameter names to their schemas
        """
        # Start with v1 parameters
        params = {
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
        
        # Add v2-specific parameters
        for name, schema in V2_PARAMETER_SCHEMA.items():
            params[name] = schema
        
        return params
    
    def calculate_probability(
        self,
        params: Optional[Dict] = None,
        as_of_date: Optional[datetime] = None,
        apply_temporal_decay: bool = True
    ) -> float:
        """
        Calculate recession probability with optional temporal adjustment.
        
        This is the main entry point for probability calculation. It:
        1. Fetches economic indicators (with historical support via as_of_date)
        2. Engineers features from raw indicators
        3. Calculates base probability using indicator signals
        4. Applies temporal decay adjustment if enabled
        5. Stores result in database
        
        Args:
            params: Model parameters (uses defaults if None)
            as_of_date: Date to calculate as of (for backtesting)
            apply_temporal_decay: Whether to apply temporal adjustment
        
        Returns:
            Final adjusted probability (0-1)
        
        Raises:
            ValueError: If parameters are invalid
            IndicatorFetchError: If economic data cannot be fetched
        """
        # Merge parameters with defaults
        if params is None:
            params = {}
        
        # Combine v1 and v2 defaults
        merged_params = DEFAULT_PARAMS.copy()
        merged_params.update(get_v2_default_parameters())
        merged_params.update(params)
        params = merged_params
        
        # Validate parameters (only validate parameters that have schemas)
        # V2 weights are internal and don't need validation
        all_schemas = {**PARAMETER_SCHEMAS, **V2_PARAMETER_SCHEMAS}
        params_to_validate = {k: v for k, v in params.items() if k in all_schemas}
        errors = validate_parameters(params_to_validate, all_schemas)
        if errors:
            error_msg = "; ".join([f"{k}: {v}" for k, v in errors.items()])
            raise ValueError(f"Invalid parameters: {error_msg}")
        
        # Determine effective date for calculation
        effective_date = as_of_date if as_of_date is not None else datetime.now()
        
        logger.info(f"Calculating probability as of {effective_date}")
        
        # Fetch economic indicators
        try:
            indicators = fetch_economic_indicators_v2(
                lookback_days=params['lookback_days'],
                as_of_date=as_of_date
            )
        except IndicatorFetchError as e:
            logger.error(f"Failed to fetch indicators: {e}")
            raise
        
        # Engineer features
        features = self.feature_engineer.engineer_features(
            indicators,
            indicators['raw_data']
        )
        
        logger.info(f"Engineered {len(features)} features")
        
        # Calculate base probability
        base_probability = self.calculate_base_probability(indicators, features, params)
        
        logger.info(f"Base probability: {base_probability:.4f}")
        
        # Apply temporal decay if enabled
        adjusted_probability = base_probability
        temporal_metadata = {}
        days_remaining = calculate_time_to_event(effective_date, self.deadline)
        
        if apply_temporal_decay and params.get('apply_temporal_decay', True):
            # Update temporal adjuster with current parameters
            decay_method = params.get('decay_method', TEMPORAL_DECAY_CONFIG['method'])
            
            if decay_method == 'exponential':
                self.temporal_adjuster = TemporalAdjuster(
                    method='exponential',
                    decay_rate=params.get('decay_rate', TEMPORAL_DECAY_CONFIG['decay_rate']),
                    threshold=params.get('decay_threshold', TEMPORAL_DECAY_CONFIG['threshold'])
                )
            elif decay_method == 'sigmoid':
                self.temporal_adjuster = TemporalAdjuster(
                    method='sigmoid',
                    midpoint=params.get('sigmoid_midpoint', TEMPORAL_DECAY_CONFIG['sigmoid_midpoint']),
                    steepness=params.get('sigmoid_steepness', TEMPORAL_DECAY_CONFIG['sigmoid_steepness'])
                )
            elif decay_method == 'theta':
                self.temporal_adjuster = TemporalAdjuster(
                    method='theta',
                    total_days=params.get('theta_total_days', TEMPORAL_DECAY_CONFIG['theta_total_days']),
                    decay_power=params.get('theta_decay_power', TEMPORAL_DECAY_CONFIG['theta_decay_power'])
                )
            
            adjusted_probability, temporal_metadata = self.temporal_adjuster.adjust_probability(
                base_probability,
                effective_date,
                self.deadline
            )
            
            logger.info(f"Adjusted probability: {adjusted_probability:.4f}")
        
        # Store result in database
        self._save_result(
            base_probability,
            adjusted_probability,
            days_remaining,
            params,
            indicators,
            features,
            temporal_metadata
        )
        
        return adjusted_probability
    
    def calculate_base_probability(
        self,
        indicators: Dict,
        features: Dict,
        params: Dict
    ) -> float:
        """
        Calculate base probability before temporal adjustment.
        
        Uses the same weighted logistic regression approach as v1, combining
        signals from multiple economic indicators. The v2 model has access to
        additional indicators and engineered features, but uses the same core
        v1 indicators for the base calculation to maintain comparability.
        
        Args:
            indicators: Dictionary of indicator values
            features: Dictionary of engineered features
            params: Model parameters
        
        Returns:
            Base probability (0-1) before temporal adjustment
        """
        # Calculate individual indicator signals using v1 logic
        signals = self._calculate_indicator_signals(indicators)
        
        # Combine signals using weighted average (v1 approach)
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
        base_probability = normalize_probability(combined_probability)
        
        logger.debug(f"Indicator signals: {signals}")
        logger.debug(f"Base probability: {base_probability:.4f}")
        
        return base_probability
    
    def _calculate_indicator_signals(self, indicators: Dict) -> Dict[str, float]:
        """
        Calculate individual probability signals from each indicator.
        
        Uses logistic transformation of z-scores to convert indicator values
        to probability space. This is the same logic as v1 model.
        
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
        signals['yield_curve'] = logistic_transform(-z_score, center=0, scale=1.0)
        
        # Unemployment: rising unemployment signals recession
        unemployment_val = indicators['unemployment']
        threshold = INDICATOR_THRESHOLDS['unemployment']
        z_score = (unemployment_val - threshold['mean']) / threshold['std']
        signals['unemployment'] = logistic_transform(z_score, center=0, scale=1.0)
        
        # GDP: negative growth signals recession
        gdp_val = indicators['gdp']
        threshold = INDICATOR_THRESHOLDS['gdp']
        z_score = (gdp_val - threshold['mean']) / threshold['std']
        signals['gdp'] = logistic_transform(-z_score, center=0, scale=1.0)
        
        # Consumer confidence: low confidence signals recession
        confidence_val = indicators['consumer_confidence']
        threshold = INDICATOR_THRESHOLDS['consumer_confidence']
        z_score = (confidence_val - threshold['mean']) / threshold['std']
        signals['consumer_confidence'] = logistic_transform(-z_score, center=0, scale=1.0)
        
        # Leading indicators: declining indicators signal recession
        leading_val = indicators['leading_indicators']
        threshold = INDICATOR_THRESHOLDS['leading_indicators']
        z_score = (leading_val - threshold['mean']) / threshold['std']
        signals['leading_indicators'] = logistic_transform(-z_score, center=0, scale=1.0)
        
        return signals
    
    def get_probability_breakdown(
        self,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Get detailed breakdown of probability calculation.
        
        This method provides transparency into the model's calculation by
        returning all intermediate values and metadata. It's used by the
        web interface to display detailed information about the forecast.
        
        Args:
            params: Optional parameter overrides
        
        Returns:
            Dictionary containing:
            - base_probability: Before temporal adjustment
            - adjusted_probability: After temporal adjustment
            - days_remaining: Days until forecast deadline
            - indicator_signals: Individual indicator contributions
            - indicators: Raw indicator values
            - features: Engineered feature values
            - temporal_metadata: Decay adjustment details
            - timestamps: Data timestamps
        """
        # Calculate probability to get all values
        adjusted_probability = self.calculate_probability(params)
        
        # Fetch the most recent result from database
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            SELECT base_probability, adjusted_probability, days_remaining,
                   parameters, indicators, features, temporal_metadata
            FROM {self.table_name}
            ORDER BY calculated_at DESC LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            # No results in database, return minimal breakdown
            return {
                'base_probability': adjusted_probability,
                'adjusted_probability': adjusted_probability,
                'days_remaining': calculate_time_to_event(datetime.now(), self.deadline),
                'indicator_signals': {},
                'indicators': {},
                'features': {},
                'temporal_metadata': {},
                'timestamps': {}
            }
        
        # Parse stored data
        base_probability = result[0]
        adjusted_probability = result[1]
        days_remaining = result[2]
        parameters = json.loads(result[3]) if result[3] else {}
        indicators = json.loads(result[4]) if result[4] else {}
        features = json.loads(result[5]) if result[5] else {}
        temporal_metadata = json.loads(result[6]) if result[6] else {}
        
        # Calculate indicator signals for breakdown
        indicator_signals = self._calculate_indicator_signals(indicators)
        
        # Extract timestamps
        timestamps = indicators.get('timestamps', {})
        
        return {
            'base_probability': base_probability,
            'adjusted_probability': adjusted_probability,
            'days_remaining': days_remaining,
            'indicator_signals': indicator_signals,
            'indicators': {
                k: v for k, v in indicators.items()
                if k not in ['timestamps', 'as_of_date', 'raw_data']
            },
            'features': features,
            'temporal_metadata': temporal_metadata,
            'timestamps': timestamps
        }
    
    def _save_result(
        self,
        base_probability: float,
        adjusted_probability: float,
        days_remaining: int,
        params: Dict,
        indicators: Dict,
        features: Dict,
        temporal_metadata: Dict
    ) -> None:
        """
        Save forecast result to database.
        
        Args:
            base_probability: Probability before temporal adjustment
            adjusted_probability: Probability after temporal adjustment
            days_remaining: Days until deadline
            params: Parameters used in calculation
            indicators: Indicator values used
            features: Engineered features
            temporal_metadata: Temporal adjustment metadata
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Prepare data for storage
        # Remove raw_data from indicators to reduce storage size
        indicators_for_storage = {
            k: v for k, v in indicators.items()
            if k != 'raw_data'
        }
        
        cursor.execute(f'''
            INSERT INTO {self.table_name}
            (base_probability, adjusted_probability, days_remaining,
             parameters, indicators, features, temporal_metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            base_probability,
            adjusted_probability,
            days_remaining,
            json.dumps(params),
            json.dumps(indicators_for_storage),
            json.dumps(features),
            json.dumps(temporal_metadata)
        ))
        
        conn.commit()
        conn.close()
        
        logger.info("Saved v2 forecast result to database")
    
    def get_last_updated(self) -> datetime:
        """Return timestamp of last data update."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            SELECT calculated_at FROM {self.table_name}
            ORDER BY calculated_at DESC LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return datetime.fromisoformat(result[0])
        return datetime.now()
    
    def get_data_sources(self) -> List[str]:
        """Return list of data sources used by this forecast."""
        return [
            'FRED (Federal Reserve Economic Data) - T10Y2Y (10-Year Treasury Constant Maturity Minus 2-Year)',
            'FRED - UNRATE (Unemployment Rate)',
            'FRED - A191RL1Q225SBEA (Real GDP Growth)',
            'FRED - UMCSENT (University of Michigan Consumer Sentiment)',
            'FRED - USSLIND (Leading Index for the United States)',
            'FRED - ICSA (Initial Jobless Claims)',
            'FRED - BAA10Y (Corporate Bond Spread)',
            'FRED - HOUST (Housing Starts)',
            'FRED - NAPM (ISM Manufacturing PMI)',
            'FRED - RSXFS (Retail Sales Excluding Food Services)',
            'FRED - DCOILWTICO (WTI Crude Oil Prices)',
            'FRED - VIXCLS (CBOE Volatility Index)'
        ]
