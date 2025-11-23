# Design Document: US Recession Forecast v2

## Overview

The US Recession Forecast v2 represents a significant enhancement to the existing forecasting system, transforming it from a point-in-time prediction tool into a comprehensive, validated, and time-aware forecasting platform. The v2 design introduces four major capabilities:

1. **Historical Backtesting Engine**: Enables retrospective model evaluation by running forecasts on historical data
2. **Jupyter Notebook Analysis Suite**: Provides structured data exploration and model analysis workflows
3. **Enhanced Feature Engineering**: Incorporates additional economic indicators and derived features
4. **Temporal Decay Modeling**: Adjusts probabilities based on time-to-event using industry-standard approaches

The design maintains full backward compatibility with v1 while enabling side-by-side comparison of model versions. All enhancements follow the existing architectural patterns established in the polymarket-forecasting-simulator framework.

## Architecture

### System Components

```
forecasts/us_recession_2025/
├── model.py                    # v1 model (unchanged)
├── model_v2.py                 # v2 model with temporal decay
├── config.py                   # Shared configuration
├── config_v2.py                # v2-specific configuration
├── data.py                     # v1 data fetching (unchanged)
├── data_v2.py                  # Enhanced data fetching with new indicators
├── features.py                 # NEW: Feature engineering module
├── temporal.py                 # NEW: Temporal decay functions
├── backtesting.py              # NEW: Historical backtesting engine
├── run_forecast.py             # v1 standalone script
├── run_forecast_v2.py          # NEW: v2 standalone script
├── notebooks/                  # NEW: Jupyter notebook suite
│   ├── README.md
│   ├── 01_data_exploration.ipynb
│   ├── 02_indicator_analysis.ipynb
│   ├── 03_model_comparison.ipynb
│   ├── 04_backtesting_results.ipynb
│   └── 05_temporal_calibration.ipynb
└── tests/
    ├── test_recession_model_v2.py
    ├── test_features.py
    ├── test_temporal.py
    ├── test_backtesting.py
    └── test_recession_model_v2_properties.py
```

### Data Flow

```
Historical Data Request
    ↓
[Data Fetcher] → Fetch indicators for historical date
    ↓
[Feature Engineering] → Calculate derived features
    ↓
[Base Model] → Calculate base probability
    ↓
[Temporal Decay] → Apply time-to-event adjustment
    ↓
[Database] → Store with backtest flag
    ↓
[Analysis/Visualization]
```

## Components and Interfaces

### 1. Enhanced Data Fetcher (data_v2.py)

**Purpose**: Fetch additional economic indicators and support historical date queries

**Interface**:
```python
def fetch_economic_indicators_v2(
    lookback_days: int = 365,
    as_of_date: Optional[datetime] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch enhanced set of economic indicators.
    
    Args:
        lookback_days: Historical window for analysis
        as_of_date: Date to fetch data as of (for backtesting)
        api_key: FRED API key
    
    Returns:
        Dictionary with all indicators, timestamps, and raw data
    """
```

**New Indicators**:
- `BAA10Y`: Corporate bond spread (BAA-rated minus 10-year Treasury)
- `HOUST`: Housing starts
- `NAPM`: ISM Manufacturing PMI
- `RSXFS`: Retail sales excluding food services
- `DCOILWTICO`: WTI crude oil prices
- `VIXCLS`: VIX volatility index

### 2. Feature Engineering Module (features.py)

**Purpose**: Calculate derived features from raw indicators

**Interface**:
```python
class FeatureEngineer:
    """Calculate derived features from economic indicators."""
    
    def calculate_rate_of_change(
        self,
        values: List[float],
        periods: List[int] = [30, 90, 180]
    ) -> Dict[str, float]:
        """Calculate rate of change over multiple periods."""
    
    def calculate_moving_averages(
        self,
        values: List[float],
        windows: List[int] = [30, 90]
    ) -> Dict[str, float]:
        """Calculate simple moving averages."""
    
    def calculate_volatility(
        self,
        values: List[float],
        window: int = 30
    ) -> float:
        """Calculate rolling volatility (standard deviation)."""
    
    def engineer_features(
        self,
        indicators: Dict[str, Any],
        raw_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Generate all engineered features.
        
        Returns dictionary with features like:
        - unemployment_roc_30d: 30-day rate of change
        - gdp_ma_90d: 90-day moving average
        - yield_curve_volatility: Recent volatility
        """
```

**Feature Categories**:
1. **Rate of Change**: Momentum indicators (30d, 90d, 180d)
2. **Moving Averages**: Trend indicators (30d, 90d)
3. **Volatility**: Uncertainty measures (30d rolling std dev)
4. **Cross-Indicator**: Ratios and differences between indicators

### 3. Temporal Decay Module (temporal.py)

**Purpose**: Apply time-to-event adjustments to base probabilities

**Interface**:
```python
def calculate_time_to_event(
    current_date: datetime,
    deadline: datetime = datetime(2025, 12, 31)
) -> int:
    """Calculate days remaining until deadline."""

def exponential_decay_adjustment(
    base_probability: float,
    days_remaining: int,
    decay_rate: float = 0.01,
    threshold: float = 0.4
) -> float:
    """
    Apply exponential decay to probability based on time remaining.
    
    Formula: If base_prob < threshold and days_remaining < 365:
        adjustment_factor = exp(-decay_rate * (365 - days_remaining) / 365)
        adjusted_prob = base_prob * adjustment_factor
    
    Args:
        base_probability: Initial probability from model
        days_remaining: Days until deadline
        decay_rate: Rate of exponential decay (higher = faster decay)
        threshold: Only apply decay if base_prob below this value
    
    Returns:
        Adjusted probability incorporating temporal information
    """

def sigmoid_decay_adjustment(
    base_probability: float,
    days_remaining: int,
    midpoint: int = 180,
    steepness: float = 0.02
) -> float:
    """
    Apply sigmoid-based decay adjustment.
    
    Uses sigmoid function centered at midpoint to create smooth
    transition in adjustment strength as deadline approaches.
    
    Formula: 
        time_factor = 1 / (1 + exp(-steepness * (midpoint - days_remaining)))
        adjusted_prob = base_prob * (1 - (1 - base_prob) * time_factor)
    """

class TemporalAdjuster:
    """Manages temporal decay adjustments with calibration."""
    
    def __init__(self, method: str = 'exponential', **params):
        """Initialize with decay method and parameters."""
    
    def adjust_probability(
        self,
        base_probability: float,
        current_date: datetime,
        deadline: datetime = datetime(2025, 12, 31)
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Apply temporal adjustment and return adjusted probability
        plus metadata about the adjustment.
        """
    
    def calibrate_from_historical_data(
        self,
        historical_forecasts: List[Dict],
        actual_outcomes: List[bool]
    ) -> Dict[str, float]:
        """
        Calibrate decay parameters using historical data.
        
        Fits parameters to minimize Brier score on historical forecasts.
        """
```

**Temporal Decay Rationale**:

The temporal decay approach is based on the principle that as time passes without recession signals, the probability should decrease. This reflects:

1. **Information Accumulation**: Each day without recession provides evidence against it
2. **Time Constraints**: Less time remaining means less opportunity for recession to occur
3. **Market Behavior**: Prediction markets like Polymarket show this pattern empirically

**Industry Standard Approaches**:
- **Exponential Decay**: Common in survival analysis and time-to-event modeling
- **Sigmoid Functions**: Used in logistic regression and neural networks for smooth transitions
- **Calibration**: Empirical Bayes approach to fit parameters from historical data

### 4. Backtesting Engine (backtesting.py)

**Purpose**: Run model on historical data to evaluate performance

**Interface**:
```python
class BacktestEngine:
    """Engine for running historical backtests."""
    
    def __init__(self, model_version: str = 'v2'):
        """Initialize with model version to test."""
    
    def run_backtest(
        self,
        start_date: datetime,
        end_date: datetime,
        frequency: str = 'weekly'
    ) -> List[Dict[str, Any]]:
        """
        Run model on historical dates.
        
        Args:
            start_date: First date to backtest
            end_date: Last date to backtest
            frequency: 'daily', 'weekly', or 'monthly'
        
        Returns:
            List of backtest results with probabilities and metadata
        """
    
    def calculate_performance_metrics(
        self,
        backtest_results: List[Dict],
        actual_recession_periods: List[Tuple[datetime, datetime]]
    ) -> Dict[str, float]:
        """
        Calculate performance metrics.
        
        Returns:
            - brier_score: Mean squared error of probability forecasts
            - calibration: Calibration slope and intercept
            - discrimination: AUC-ROC if binary outcomes available
            - sharpness: Standard deviation of forecasts
        """
    
    def compare_models(
        self,
        v1_results: List[Dict],
        v2_results: List[Dict],
        actual_outcomes: List[bool]
    ) -> Dict[str, Any]:
        """Compare performance of v1 vs v2 models."""
```

**Backtesting Database Schema**:
```sql
CREATE TABLE forecast_us_recession_2025_backtest (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backtest_date DATE NOT NULL,           -- Date model was "run" in past
    forecast_date DATE NOT NULL,           -- Date forecast was for (2025-12-31)
    model_version TEXT NOT NULL,           -- 'v1' or 'v2'
    base_probability REAL,                 -- Before temporal adjustment
    adjusted_probability REAL,             -- After temporal adjustment
    days_remaining INTEGER,                -- Days from backtest_date to forecast_date
    parameters TEXT,                       -- JSON of parameters used
    indicators TEXT,                       -- JSON of indicator values
    features TEXT,                         -- JSON of engineered features
    temporal_metadata TEXT,                -- JSON of temporal adjustment details
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(backtest_date, model_version)
);

CREATE INDEX idx_backtest_date ON forecast_us_recession_2025_backtest(backtest_date);
CREATE INDEX idx_model_version ON forecast_us_recession_2025_backtest(model_version);
```

### 5. RecessionModelV2 Class (model_v2.py)

**Purpose**: Enhanced forecast model with all v2 features

**Interface**:
```python
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
        """Initialize v2 model."""
    
    def calculate_probability(
        self,
        params: Optional[Dict] = None,
        as_of_date: Optional[datetime] = None,
        apply_temporal_decay: bool = True
    ) -> float:
        """
        Calculate recession probability with optional temporal adjustment.
        
        Args:
            params: Model parameters
            as_of_date: Date to calculate as of (for backtesting)
            apply_temporal_decay: Whether to apply temporal adjustment
        
        Returns:
            Final adjusted probability
        """
    
    def calculate_base_probability(
        self,
        indicators: Dict,
        features: Dict,
        params: Dict
    ) -> float:
        """Calculate base probability before temporal adjustment."""
    
    def get_probability_breakdown(
        self,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Get detailed breakdown of probability calculation.
        
        Returns:
            - base_probability: Before temporal adjustment
            - adjusted_probability: After temporal adjustment
            - indicator_signals: Individual indicator contributions
            - feature_contributions: Feature importance
            - temporal_metadata: Decay adjustment details
        """
```

### 6. Jupyter Notebook Suite

**Purpose**: Interactive analysis and visualization

**Notebooks**:

1. **01_data_exploration.ipynb**
   - Load and visualize all economic indicators
   - Statistical summaries and distributions
   - Correlation analysis
   - Time series plots with recession periods marked
   - Missing data analysis

2. **02_indicator_analysis.ipynb**
   - Individual indicator deep dives
   - Relationship to historical recessions
   - Lead/lag analysis
   - Threshold identification
   - Signal quality assessment

3. **03_model_comparison.ipynb**
   - Side-by-side v1 vs v2 comparison
   - Parameter sensitivity analysis
   - Feature importance visualization
   - Weight optimization experiments

4. **04_backtesting_results.ipynb**
   - Historical performance visualization
   - Brier score decomposition
   - Calibration plots
   - Forecast evolution over time
   - Error analysis

5. **05_temporal_calibration.ipynb**
   - Temporal decay parameter tuning
   - Comparison of decay functions
   - Empirical calibration from historical data
   - Sensitivity analysis

**Notebook Structure**:
```python
# Standard notebook header
import sys
sys.path.append('../../../')  # Add project root to path

from forecasts.us_recession_2025 import RecessionModel, RecessionModelV2
from forecasts.us_recession_2025.backtesting import BacktestEngine
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set visualization style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
```

## Data Models

### Enhanced Indicator Data Structure

```python
{
    # Original v1 indicators
    'yield_curve': float,
    'unemployment': float,
    'gdp': float,
    'consumer_confidence': float,
    'leading_indicators': float,
    'jobless_claims': float,
    
    # New v2 indicators
    'credit_spread': float,          # BAA10Y
    'housing_starts': float,         # HOUST
    'manufacturing_pmi': float,      # NAPM
    'retail_sales': float,           # RSXFS
    'oil_price': float,              # DCOILWTICO
    'vix': float,                    # VIXCLS
    
    # Engineered features
    'features': {
        'unemployment_roc_30d': float,
        'unemployment_roc_90d': float,
        'gdp_ma_90d': float,
        'yield_curve_volatility': float,
        'credit_spread_roc_30d': float,
        # ... additional features
    },
    
    # Metadata
    'timestamps': Dict[str, str],
    'as_of_date': str,
    'raw_data': Dict[str, Any]
}
```

### Backtest Result Structure

```python
{
    'backtest_date': datetime,
    'forecast_date': datetime,
    'model_version': str,
    'base_probability': float,
    'adjusted_probability': float,
    'days_remaining': int,
    'parameters': Dict,
    'indicators': Dict,
    'features': Dict,
    'temporal_metadata': {
        'decay_method': str,
        'decay_rate': float,
        'adjustment_factor': float,
        'threshold_applied': bool
    }
}
```

## 

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Historical data retrieval preserves temporal consistency

*For any* historical date and economic indicator, fetching data as of that date should return only observations available on or before that date, never future data.

**Validates: Requirements 1.1**

### Property 2: Backtest probability bounds

*For any* historical backtest run, both base probability and adjusted probability must be within the valid range [0, 1].

**Validates: Requirements 1.2**

### Property 3: Backtest storage completeness

*For any* backtest execution, the system should store all required fields including backtest_date, model_version, probabilities, indicators, and temporal metadata.

**Validates: Requirements 1.3**

### Property 4: Feature engineering determinism

*For any* set of indicator values, running feature engineering twice with the same inputs should produce identical feature values.

**Validates: Requirements 3.2**

### Property 5: Rate of change calculation correctness

*For any* time series with at least N+1 observations, the N-period rate of change should equal (latest_value - value_N_periods_ago) / value_N_periods_ago.

**Validates: Requirements 3.2**

### Property 6: Temporal decay monotonicity

*For any* base probability below the threshold, as days_remaining decreases (approaching deadline), the adjusted probability should be less than or equal to the base probability.

**Validates: Requirements 4.4**

### Property 7: Temporal decay boundary behavior

*For any* base probability, when days_remaining equals zero, the temporal adjustment should produce the minimum reasonable probability (approaching zero if base probability is low).

**Validates: Requirements 4.2, 4.4**

### Property 8: Temporal decay preserves high probabilities

*For any* base probability above the threshold, temporal decay should not be applied, and adjusted probability should equal base probability.

**Validates: Requirements 4.4**

### Property 9: Model version isolation

*For any* backtest date, running v1 and v2 models should store results in separate database records with distinct model_version values.

**Validates: Requirements 5.2**

### Property 10: Backtest uniqueness constraint

*For any* combination of backtest_date and model_version, attempting to store duplicate backtest results should either update the existing record or fail gracefully without creating duplicates.

**Validates: Requirements 6.4**

### Property 11: Notebook data access consistency

*For any* notebook execution, data fetched using lib utilities should match data fetched by the model for the same parameters and date.

**Validates: Requirements 2.4**

### Property 12: Missing indicator handling

*For any* indicator that fails to fetch, the system should either use a neutral default value or exclude it from calculation without crashing.

**Validates: Requirements 3.5**

### Property 13: Calibration parameter validity

*For any* calibrated temporal decay parameters, they should produce adjusted probabilities within [0, 1] for all reasonable base probabilities and days_remaining values.

**Validates: Requirements 7.4**

### Property 14: Backtest chronological ordering

*For any* query of backtest results, when ordered by backtest_date, the days_remaining values should decrease monotonically (more recent backtests have fewer days remaining).

**Validates: Requirements 6.3**

### Property 15: Feature engineering handles missing data

*For any* indicator with missing historical observations, feature engineering should handle gaps gracefully using forward-fill or skip that feature without failing.

**Validates: Requirements 3.5**

### Property 16: Web interface displays both probabilities

*For any* v2 forecast with temporal adjustment, the web interface response should contain both base_probability and adjusted_probability fields with distinct values when decay is applied.

**Validates: Requirements 9.1**

### Property 17: Temporal decay projection data generation

*For any* base probability and days remaining, the system should generate valid projection data points where each point has days_from_now in [0, days_remaining] and probability in [0, 1].

**Validates: Requirements 9.2**

### Property 18: Days remaining display

*For any* v2 forecast view, the response should include the days_remaining field with a non-negative integer value.

**Validates: Requirements 9.3**

### Property 19: Temporal metadata completeness

*For any* forecast with temporal adjustment applied, the metadata should include decay_method, decay_rate, threshold, and threshold_applied fields.

**Validates: Requirements 9.4**

## Error Handling

### Data Fetching Errors

**Historical Data Unavailability**:
- If historical data for a specific date is not available, use the most recent prior observation
- Log warning with the date gap
- Include metadata about data staleness in backtest results

**API Rate Limiting**:
- Implement exponential backoff with jitter
- Use cached data when available
- Fail gracefully with informative error message if all retries exhausted

**Missing Indicators**:
- For v2 indicators, use neutral default values if unavailable
- Log which indicators are missing
- Include indicator availability metadata in results

### Feature Engineering Errors

**Insufficient Historical Data**:
- If not enough observations for rate-of-change calculation, return None for that feature
- Skip features that cannot be calculated
- Log which features were skipped

**Division by Zero**:
- When calculating rate of change, if denominator is zero, return None
- Handle gracefully in model by excluding that feature

### Temporal Decay Errors

**Invalid Parameters**:
- Validate decay_rate > 0
- Validate threshold in [0, 1]
- Raise ValueError with clear message if invalid

**Date Errors**:
- If current_date > deadline, log warning and return base probability unchanged
- If dates are invalid, raise ValueError

### Backtesting Errors

**Database Errors**:
- Wrap all database operations in try-except
- Roll back transaction on error
- Log full error with context
- Continue with next backtest date if one fails

**Model Calculation Errors**:
- Catch exceptions during probability calculation
- Log error with backtest date and parameters
- Skip that backtest date and continue
- Report summary of failed backtests at end

## Testing Strategy

### Unit Tests

**Data Fetching** (`test_data_v2.py`):
- Test fetching each new indicator individually
- Test as_of_date parameter with known historical dates
- Test handling of missing data
- Mock FRED API responses

**Feature Engineering** (`test_features.py`):
- Test rate of change calculations with known values
- Test moving average calculations
- Test volatility calculations
- Test handling of missing data in time series
- Test edge cases (single observation, all zeros)

**Temporal Decay** (`test_temporal.py`):
- Test exponential decay with known parameters
- Test sigmoid decay with known parameters
- Test boundary conditions (0 days, 1000 days)
- Test threshold behavior
- Test parameter validation

**Backtesting** (`test_backtesting.py`):
- Test backtest result storage
- Test uniqueness constraint
- Test chronological ordering
- Test performance metric calculations
- Test model comparison logic

**Model V2** (`test_recession_model_v2.py`):
- Test probability calculation with default parameters
- Test with custom parameters
- Test temporal decay application
- Test probability breakdown
- Test backward compatibility with v1 interface

### Property-Based Tests (Hypothesis)

All property-based tests will run a minimum of 100 iterations and be tagged with the format:
`# Feature: us-recession-forecast-v2, Property {number}: {property_text}`

**Property Tests** (`test_recession_model_v2_properties.py`):

1. **Property 1: Historical data temporal consistency**
   - Generate random historical dates
   - Fetch data as of those dates
   - Verify no future data is included
   - **Validates: Requirements 1.1**

2. **Property 2: Backtest probability bounds**
   - Generate random backtest parameters
   - Run backtests
   - Verify all probabilities in [0, 1]
   - **Validates: Requirements 1.2**

3. **Property 3: Backtest storage completeness**
   - Generate random backtest runs
   - Store results
   - Verify all required fields present
   - **Validates: Requirements 1.3**

4. **Property 4: Feature engineering determinism**
   - Generate random indicator values
   - Run feature engineering twice
   - Verify identical results
   - **Validates: Requirements 3.2**

5. **Property 5: Rate of change correctness**
   - Generate random time series
   - Calculate rate of change
   - Verify formula correctness
   - **Validates: Requirements 3.2**

6. **Property 6: Temporal decay monotonicity**
   - Generate random base probabilities below threshold
   - Generate decreasing days_remaining sequences
   - Verify adjusted probability decreases or stays same
   - **Validates: Requirements 4.4**

7. **Property 7: Temporal decay boundary behavior**
   - Generate random base probabilities
   - Test with days_remaining = 0
   - Verify appropriate decay applied
   - **Validates: Requirements 4.2, 4.4**

8. **Property 8: Temporal decay preserves high probabilities**
   - Generate random base probabilities above threshold
   - Apply temporal decay
   - Verify adjusted equals base
   - **Validates: Requirements 4.4**

9. **Property 9: Model version isolation**
   - Generate random backtest dates
   - Run both v1 and v2
   - Verify separate storage with correct version tags
   - **Validates: Requirements 5.2**

10. **Property 10: Backtest uniqueness**
    - Generate random backtest dates
    - Attempt duplicate storage
    - Verify no duplicates created
    - **Validates: Requirements 6.4**

11. **Property 11: Notebook data consistency**
    - Generate random parameters
    - Fetch data via notebook utilities and model
    - Verify identical results
    - **Validates: Requirements 2.4**

12. **Property 12: Missing indicator handling**
    - Simulate missing indicators
    - Run model
    - Verify graceful handling without crash
    - **Validates: Requirements 3.5**

13. **Property 13: Calibration parameter validity**
    - Generate random calibrated parameters
    - Test across range of inputs
    - Verify all outputs in [0, 1]
    - **Validates: Requirements 7.4**

14. **Property 14: Backtest chronological ordering**
    - Generate random backtest dates
    - Query with chronological order
    - Verify days_remaining decreases monotonically
    - **Validates: Requirements 6.3**

15. **Property 15: Feature engineering missing data**
    - Generate time series with gaps
    - Run feature engineering
    - Verify graceful handling
    - **Validates: Requirements 3.5**

16. **Property 16: Web interface probability display**
    - Generate random v2 forecasts with temporal adjustment
    - Get breakdown data
    - Verify both base and adjusted probabilities present
    - **Validates: Requirements 9.1**

17. **Property 17: Temporal projection data**
    - Generate random base probabilities and days remaining
    - Generate projection data
    - Verify all points have valid coordinates
    - **Validates: Requirements 9.2**

18. **Property 18: Days remaining display**
    - Generate random v2 forecast requests
    - Get breakdown data
    - Verify days_remaining field present and non-negative
    - **Validates: Requirements 9.3**

19. **Property 19: Temporal metadata completeness**
    - Generate random forecasts with temporal adjustment
    - Get breakdown data
    - Verify all metadata fields present
    - **Validates: Requirements 9.4**

### Integration Tests

**End-to-End Backtesting**:
- Run complete backtest from 2020-2024
- Verify all results stored correctly
- Calculate performance metrics
- Compare v1 vs v2

**Notebook Execution**:
- Execute each notebook in order
- Verify no errors
- Verify outputs are generated
- Verify visualizations render

**Model Comparison**:
- Run v1 and v2 on same current data
- Verify both produce valid probabilities
- Verify v2 includes temporal adjustment
- Verify results stored in separate tables

### Validation Scripts

**validate_backtesting.py**:
- Run sample backtest
- Display results
- Show performance metrics
- Visualize probability evolution

**validate_temporal_decay.py**:
- Test temporal decay functions
- Visualize decay curves
- Show adjustment examples
- Validate parameter ranges

**validate_features.py**:
- Fetch current data
- Calculate all features
- Display feature values
- Show feature correlations

## Implementation Notes

### Temporal Decay Calibration Methodology

The temporal decay function will be calibrated using historical recession data:

1. **Data Collection**: Gather historical recession probabilities from prediction markets or expert forecasts at various time distances from actual recessions

2. **Parameter Fitting**: Use optimization (scipy.optimize) to fit decay parameters that minimize Brier score on historical data

3. **Validation**: Test calibrated parameters on held-out historical periods

4. **Default Parameters**: Based on empirical analysis, suggested defaults:
   - Exponential decay_rate: 0.01-0.03
   - Sigmoid midpoint: 180 days (6 months)
   - Sigmoid steepness: 0.01-0.03
   - Threshold: 0.4 (only decay low probabilities)

### Feature Engineering Best Practices

**Rate of Change Periods**:
- 30 days: Short-term momentum
- 90 days: Medium-term trends
- 180 days: Long-term structural changes

**Moving Average Windows**:
- 30 days: Smooth short-term noise
- 90 days: Identify medium-term trends

**Volatility Measures**:
- 30-day rolling standard deviation
- Captures recent uncertainty

### Notebook Best Practices

**Data Loading**:
```python
# Use consistent data loading pattern
from forecasts.us_recession_2025.data_v2 import fetch_economic_indicators_v2

indicators = fetch_economic_indicators_v2(lookback_days=1825)  # 5 years
```

**Visualization Style**:
```python
# Consistent color scheme
RECESSION_COLOR = '#ff6b6b'
V1_COLOR = '#4ecdc4'
V2_COLOR = '#45b7d1'

# Mark recession periods
def mark_recessions(ax, recession_periods):
    for start, end in recession_periods:
        ax.axvspan(start, end, alpha=0.2, color=RECESSION_COLOR)
```

**Reproducibility**:
```python
# Set random seeds
import numpy as np
import random

np.random.seed(42)
random.seed(42)
```

### Database Migration

Since this is an enhancement to existing forecast, we need to:

1. Create new backtest table (doesn't affect existing tables)
2. Add v2 model as separate forecast in discovery system
3. Maintain v1 table for comparison
4. Create views for easy v1 vs v2 comparison

```sql
-- View for comparing v1 and v2 latest forecasts
CREATE VIEW IF NOT EXISTS recession_forecast_comparison AS
SELECT 
    v1.calculated_at,
    v1.probability as v1_probability,
    v2.base_probability as v2_base_probability,
    v2.adjusted_probability as v2_adjusted_probability,
    v2.days_remaining
FROM forecast_us_recession_2025 v1
LEFT JOIN forecast_us_recession_2025_v2 v2 
    ON DATE(v1.calculated_at) = DATE(v2.calculated_at)
ORDER BY v1.calculated_at DESC;
```

### Performance Considerations

**Backtesting Performance**:
- Batch fetch historical data where possible
- Use caching aggressively for historical data
- Parallelize backtest runs if needed (multiprocessing)
- Limit backtest frequency (weekly is sufficient)

**Feature Engineering Performance**:
- Calculate features once per forecast run
- Cache intermediate calculations
- Use vectorized operations (numpy/pandas)

**Notebook Performance**:
- Load data once at notebook start
- Cache expensive calculations
- Use sampling for exploratory analysis
- Full data for final analysis

## Future Enhancements

### Phase 2 Improvements

1. **Machine Learning Models**: Train ML models (Random Forest, XGBoost) on engineered features
2. **Ensemble Methods**: Combine multiple model approaches
3. **Real-time Updates**: Automatic daily backtesting and model updates
4. **Confidence Intervals**: Bootstrap methods for uncertainty quantification
5. **Regional Forecasts**: State-level recession probabilities
6. **Sector Analysis**: Industry-specific recession indicators

### Phase 3 Improvements

1. **Alternative Data**: Incorporate non-traditional data sources (Google Trends, credit card data)
2. **Sentiment Analysis**: News and social media sentiment
3. **International Indicators**: Global economic indicators
4. **Policy Modeling**: Incorporate Fed policy expectations
5. **Market-Based Indicators**: Options-implied volatility, credit default swaps

## References

### Temporal Decay Modeling

- **Survival Analysis**: Kaplan-Meier estimators and Cox proportional hazards models
- **Time-to-Event Modeling**: Standard approach in medical statistics and reliability engineering
- **Prediction Markets**: Empirical studies of how market probabilities evolve over time

### Feature Engineering

- **Economic Indicators**: FRED documentation and research papers
- **Technical Analysis**: Rate of change and moving average methodologies
- **Financial Econometrics**: Volatility modeling (GARCH, rolling windows)

### Backtesting

- **Forecast Evaluation**: Brier score, calibration plots, discrimination metrics
- **Time Series Cross-Validation**: Walk-forward analysis
- **Model Comparison**: Diebold-Mariano test for forecast accuracy

### Industry Standards

- **Nate Silver's FiveThirtyEight**: Methodology for election and economic forecasting
- **Federal Reserve**: Economic forecasting approaches (Greenbook, Tealbook)
- **IMF/World Bank**: Recession probability models
- **Academic Research**: Papers on recession prediction using economic indicators

### Python Libraries

- **Hypothesis**: Property-based testing framework
- **Pandas**: Time series manipulation
- **NumPy**: Numerical computations
- **SciPy**: Optimization and statistical functions
- **Matplotlib/Seaborn**: Visualization
- **Jupyter**: Interactive analysis
- **SQLite**: Database operations

## Web Interface Enhancements

### Overview

The web interface will be enhanced to display v2-specific features while maintaining the generic forecast discovery mechanism. The key addition is visualization of temporal decay and its effect on probability estimates.

### Enhanced Forecast Display

**Additional Data in API Response**:

The v2 model's `get_probability_breakdown()` method will return extended metadata that the web interface can display:

```python
{
    'base_probability': 0.45,
    'adjusted_probability': 0.38,
    'days_remaining': 245,
    'temporal_metadata': {
        'decay_method': 'exponential',
        'decay_rate': 0.015,
        'threshold': 0.4,
        'threshold_applied': True,
        'adjustment_factor': 0.844
    },
    'indicator_signals': {...},
    'feature_contributions': {...}
}
```

### Temporal Decay Visualization

**Interactive Chart Component**:

A new chart will show how the probability would evolve from now until the deadline, assuming no change in base probability:

```javascript
// Temporal decay projection chart
function renderTemporalDecayChart(baseProb, adjustedProb, daysRemaining, decayParams) {
    // Generate projection: what would happen if base prob stays constant
    // X-axis: Days from now to deadline
    // Y-axis: Adjusted probability
    // Show current position on the curve
    // Show base probability as horizontal reference line
}
```

**Visual Elements**:
- Line chart showing probability decay curve
- Current position marked with a dot
- Base probability shown as dashed horizontal line
- Shaded area showing the adjustment range
- Tooltip showing days remaining and probability at each point

### Generic Implementation Approach

**Model Interface Extension**:

The `ForecastModel` base interface will be extended with an optional method:

```python
class ForecastModel:
    # ... existing methods ...
    
    def get_probability_breakdown(self) -> Optional[Dict[str, Any]]:
        """
        Optional method for models that provide detailed breakdowns.
        
        Returns:
            Dictionary with detailed probability components, or None
            if model doesn't support breakdowns.
        """
        return None
```

**Frontend Detection**:

The web interface will check if `get_probability_breakdown()` returns data:

```python
# In Flask route
breakdown = model.get_probability_breakdown()
if breakdown and 'temporal_metadata' in breakdown:
    # Render temporal decay visualization
    return render_template('forecast.html', 
                         forecast=forecast,
                         breakdown=breakdown,
                         show_temporal=True)
else:
    # Standard forecast display
    return render_template('forecast.html',
                         forecast=forecast,
                         show_temporal=False)
```

**Template Conditional Rendering**:

```html
<!-- In forecast.html -->
{% if show_temporal %}
<div class="temporal-decay-section">
    <h3>Temporal Adjustment</h3>
    <div class="probability-comparison">
        <div class="prob-item">
            <span class="label">Base Probability:</span>
            <span class="value">{{ "%.1f"|format(breakdown.base_probability * 100) }}%</span>
        </div>
        <div class="prob-item">
            <span class="label">Adjusted Probability:</span>
            <span class="value">{{ "%.1f"|format(breakdown.adjusted_probability * 100) }}%</span>
        </div>
        <div class="prob-item">
            <span class="label">Days Remaining:</span>
            <span class="value">{{ breakdown.days_remaining }}</span>
        </div>
    </div>
    
    <div class="decay-chart-container">
        <canvas id="temporalDecayChart"></canvas>
    </div>
    
    <div class="decay-metadata">
        <p><strong>Decay Method:</strong> {{ breakdown.temporal_metadata.decay_method }}</p>
        <p><strong>Decay Rate:</strong> {{ "%.3f"|format(breakdown.temporal_metadata.decay_rate) }}</p>
        <p><strong>Adjustment Applied:</strong> {{ "Yes" if breakdown.temporal_metadata.threshold_applied else "No" }}</p>
    </div>
</div>
{% endif %}
```

### CSS Styling

```css
.temporal-decay-section {
    margin-top: 2rem;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.probability-comparison {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.prob-item {
    display: flex;
    flex-direction: column;
    padding: 1rem;
    background: white;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.prob-item .label {
    font-size: 0.875rem;
    color: #6c757d;
    margin-bottom: 0.5rem;
}

.prob-item .value {
    font-size: 1.5rem;
    font-weight: 600;
    color: #212529;
}

.decay-chart-container {
    margin: 1.5rem 0;
    background: white;
    padding: 1rem;
    border-radius: 4px;
}

.decay-metadata {
    font-size: 0.875rem;
    color: #6c757d;
}

.decay-metadata p {
    margin: 0.5rem 0;
}
```

### JavaScript Chart Implementation

```javascript
// In web/static/js/main.js

function renderTemporalDecayChart(canvasId, breakdown) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const daysRemaining = breakdown.days_remaining;
    const baseProb = breakdown.base_probability;
    const currentAdjusted = breakdown.adjusted_probability;
    const decayRate = breakdown.temporal_metadata.decay_rate;
    
    // Generate projection data
    const projectionData = [];
    for (let days = daysRemaining; days >= 0; days -= Math.max(1, Math.floor(daysRemaining / 50))) {
        const adjustedProb = calculateDecayedProbability(baseProb, days, decayRate);
        projectionData.push({
            x: daysRemaining - days,  // Days from now
            y: adjustedProb * 100     // Percentage
        });
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [
                {
                    label: 'Projected Adjusted Probability',
                    data: projectionData,
                    borderColor: '#45b7d1',
                    backgroundColor: 'rgba(69, 183, 209, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Base Probability',
                    data: [
                        {x: 0, y: baseProb * 100},
                        {x: daysRemaining, y: baseProb * 100}
                    ],
                    borderColor: '#4ecdc4',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                },
                {
                    label: 'Current Position',
                    data: [{x: 0, y: currentAdjusted * 100}],
                    pointRadius: 8,
                    pointBackgroundColor: '#ff6b6b',
                    showLine: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'linear',
                    title: {
                        display: true,
                        text: 'Days from Now'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Probability (%)'
                    },
                    min: 0,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + 
                                   context.parsed.y.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
}

function calculateDecayedProbability(baseProb, daysRemaining, decayRate) {
    // Implement exponential decay formula
    if (baseProb >= 0.4) return baseProb;  // No decay above threshold
    const adjustmentFactor = Math.exp(-decayRate * (365 - daysRemaining) / 365);
    return baseProb * adjustmentFactor;
}
```

### API Endpoint Enhancement

**New Endpoint for Breakdown Data**:

```python
@app.route('/api/forecast/<name>/breakdown')
def get_forecast_breakdown(name):
    """Get detailed probability breakdown for a forecast."""
    try:
        model = discover_forecast_model(name)
        if model is None:
            return jsonify({'error': 'Forecast not found'}), 404
        
        # Check if model supports breakdown
        if hasattr(model, 'get_probability_breakdown'):
            breakdown = model.get_probability_breakdown()
            if breakdown:
                return jsonify(breakdown)
        
        # Fallback for models without breakdown
        return jsonify({
            'probability': model.calculate_probability(),
            'breakdown_available': False
        })
    
    except Exception as e:
        logger.error(f"Error getting breakdown for {name}: {e}")
        return jsonify({'error': str(e)}), 500
```

### Backward Compatibility

**Ensuring Generic Behavior**:

1. **Optional Feature**: Temporal decay visualization only appears if model provides breakdown data
2. **Graceful Degradation**: Models without `get_probability_breakdown()` display normally
3. **No Hardcoding**: No forecast-specific logic in web interface code
4. **Reusable Components**: Temporal decay chart can be used by any future forecast with similar features

**Testing Compatibility**:

- Verify v1 model displays without temporal section
- Verify v2 model displays with temporal section
- Verify election_2028 model (no temporal decay) displays normally
- Verify new forecasts can opt-in to temporal visualization by implementing the interface

## Version History

- **v2.0** (2024): Enhanced model with historical backtesting, feature engineering, temporal decay, Jupyter notebook analysis suite, and web interface enhancements for temporal decay visualization
