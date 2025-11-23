# US Recession 2025 Forecast Model

## Overview

This forecast model predicts the probability of a US recession occurring by the end of 2025. The system includes two model versions:

- **V1 (Original)**: Analyzes 6 economic indicators using weighted logistic regression
- **V2 (Enhanced)**: Adds 6 more indicators, feature engineering, temporal decay modeling, and historical backtesting

Both versions are maintained for comparison and validation purposes. V2 represents a significant enhancement with time-aware probability adjustments, comprehensive backtesting infrastructure, and interactive Jupyter notebooks for analysis.

## Economic Indicators

### V1 Indicators

The original model uses six key economic indicators from the Federal Reserve Economic Data (FRED) API:

1. **Yield Curve (T10Y2Y)**: 10-Year Treasury Constant Maturity Minus 2-Year Treasury
   - An inverted yield curve (negative spread) is a strong historical predictor of recessions
   - Default weight: 35%

2. **Unemployment Rate (UNRATE)**: Civilian Unemployment Rate
   - Rising unemployment typically accompanies or precedes recessions
   - Default weight: 25%

3. **GDP Growth (A191RL1Q225SBEA)**: Real GDP Growth Rate (quarterly, annual rate)
   - Negative or declining GDP growth indicates economic contraction
   - Default weight: 20%

4. **Consumer Confidence (UMCSENT)**: University of Michigan Consumer Sentiment Index
   - Low consumer confidence can signal economic weakness
   - Default weight: 10%

5. **Leading Indicators (USSLIND)**: Leading Index for the United States
   - Composite index designed to predict economic turning points
   - Default weight: 10%

6. **Initial Jobless Claims (ICSA)**: Weekly initial unemployment insurance claims
   - Rising claims indicate labor market weakness
   - Currently tracked but not weighted in default model

### V2 Additional Indicators

The enhanced v2 model adds six additional indicators for more comprehensive analysis:

7. **Credit Spread (BAA10Y)**: BAA Corporate Bond Yield minus 10-Year Treasury
   - Widening spreads indicate increased credit risk and economic stress
   - Historical predictor of financial crises and recessions

8. **Housing Starts (HOUST)**: New Privately-Owned Housing Units Started
   - Declining housing starts signal weakening construction and consumer demand
   - Leading indicator of economic activity

9. **Manufacturing PMI (NAPM)**: ISM Manufacturing Purchasing Managers Index
   - Values below 50 indicate manufacturing contraction
   - Timely indicator of industrial sector health

10. **Retail Sales (RSXFS)**: Advance Retail Sales: Retail Trade and Food Services
    - Declining retail sales indicate weakening consumer spending
    - Major component of GDP

11. **Oil Prices (DCOILWTICO)**: Crude Oil Prices: West Texas Intermediate
    - Sharp price changes can signal economic shocks
    - Affects inflation and consumer spending

12. **VIX (VIXCLS)**: CBOE Volatility Index
    - Elevated VIX indicates market uncertainty and fear
    - "Fear gauge" for financial markets

## V2 Features

### Feature Engineering

V2 includes sophisticated feature engineering to extract more signal from raw indicators:

**Rate of Change Features**:
- 30-day rate of change: Short-term momentum
- 90-day rate of change: Medium-term trends
- 180-day rate of change: Long-term structural changes

**Moving Averages**:
- 30-day simple moving average: Smooth short-term noise
- 90-day simple moving average: Identify medium-term trends

**Volatility Measures**:
- 30-day rolling standard deviation: Capture recent uncertainty
- Applied to key indicators like yield curve and unemployment

### Temporal Decay Modeling

V2 introduces time-aware probability adjustments based on time remaining until December 31, 2025:

**Concept**: As time passes without recession signals, the probability should decrease. This reflects:
- Information accumulation: Each day without recession provides evidence against it
- Time constraints: Less time remaining means less opportunity for recession to occur
- Market behavior: Prediction markets like Polymarket show this pattern empirically

**Decay Functions**:

1. **Exponential Decay** (default):
   ```
   If base_prob < threshold and days_remaining < 365:
       adjustment_factor = exp(-decay_rate * (365 - days_remaining) / 365)
       adjusted_prob = base_prob * adjustment_factor
   ```
   - Default decay_rate: 0.01-0.03
   - Default threshold: 0.4 (only decay low probabilities)

2. **Sigmoid Decay** (alternative):
   ```
   time_factor = 1 / (1 + exp(-steepness * (midpoint - days_remaining)))
   adjusted_prob = base_prob * (1 - (1 - base_prob) * time_factor)
   ```
   - Default midpoint: 180 days (6 months)
   - Default steepness: 0.01-0.03

**Calibration**: Decay parameters are calibrated using historical recession data to minimize Brier score.

### Historical Backtesting

V2 includes a comprehensive backtesting engine to evaluate model performance:

**Features**:
- Run model on any historical date with data available at that time
- Store results in dedicated backtest database table
- Calculate performance metrics: Brier score, calibration, discrimination
- Compare v1 vs v2 performance side-by-side
- Visualize probability evolution over time

**Database Schema**:
```sql
CREATE TABLE forecast_us_recession_2025_backtest (
    id INTEGER PRIMARY KEY,
    backtest_date DATE NOT NULL,
    model_version TEXT NOT NULL,
    base_probability REAL,
    adjusted_probability REAL,
    days_remaining INTEGER,
    parameters TEXT,
    indicators TEXT,
    features TEXT,
    temporal_metadata TEXT,
    UNIQUE(backtest_date, model_version)
);
```

**Usage**:
```python
from forecasts.us_recession_2025.backtesting import BacktestEngine

engine = BacktestEngine(model_version='v2')
results = engine.run_backtest(
    start_date=datetime(2020, 1, 1),
    end_date=datetime(2024, 11, 1),
    frequency='weekly'
)

metrics = engine.calculate_performance_metrics(results, actual_recession_periods)
print(f"Brier Score: {metrics['brier_score']:.4f}")
```

### Jupyter Notebook Suite

V2 includes 5 interactive Jupyter notebooks for comprehensive analysis:

1. **01_data_exploration.ipynb**: Load and visualize all economic indicators, correlation analysis, missing data assessment
2. **02_indicator_analysis.ipynb**: Deep dive into individual indicators, lead/lag analysis, signal quality
3. **03_model_comparison.ipynb**: Side-by-side v1 vs v2 comparison, parameter sensitivity, feature importance
4. **04_backtesting_results.ipynb**: Historical performance visualization, Brier score decomposition, error analysis
5. **05_temporal_calibration.ipynb**: Decay parameter tuning, empirical calibration, sensitivity analysis

See `notebooks/README.md` for detailed documentation.

## Methodology

### V1 Signal Calculation

For each indicator, the v1 model:
1. Fetches the latest available data from FRED
2. Calculates a z-score relative to historical mean and standard deviation
3. Applies a logistic transformation to convert the z-score to a probability signal (0-1)
4. Adjusts the direction based on whether high or low values signal recession

### V2 Calculation Process

The v2 model follows a two-stage process:

**Stage 1: Base Probability Calculation**
1. Fetch all 12 economic indicators
2. Engineer features (rate of change, moving averages, volatility)
3. Calculate indicator signals using logistic transformation
4. Combine signals using weighted averaging
5. Result: Base probability (before temporal adjustment)

**Stage 2: Temporal Adjustment**
1. Calculate days remaining until December 31, 2025
2. Apply decay function if base probability < threshold
3. Validate adjusted probability is in [0, 1]
4. Result: Final adjusted probability

**Metadata Tracking**:
- Both base and adjusted probabilities stored
- Decay method, rate, and adjustment factor recorded
- Full indicator snapshot and engineered features saved
- Enables detailed analysis and debugging

### Probability Combination

Individual indicator signals are combined using weighted averaging:
- Each indicator contributes according to its assigned weight
- Weights are normalized to sum to 1.0
- The final probability is the weighted average of all signals

### Mathematical Approach

For each indicator i:
```
z_score_i = (value_i - mean_i) / std_i
signal_i = logistic_transform(±z_score_i)
```

Final probability:
```
P(recession) = Σ(weight_i × signal_i) / Σ(weight_i)
```

## Adjustable Parameters

Users can adjust the following parameters through the web interface:

- `yield_curve_weight`: Weight for yield curve signal (0.0 - 1.0, default: 0.35)
- `unemployment_weight`: Weight for unemployment signal (0.0 - 1.0, default: 0.25)
- `gdp_weight`: Weight for GDP growth signal (0.0 - 1.0, default: 0.20)
- `confidence_weight`: Weight for consumer confidence signal (0.0 - 1.0, default: 0.10)
- `leading_indicators_weight`: Weight for leading indicators signal (0.0 - 1.0, default: 0.10)
- `lookback_days`: Historical window for data analysis (30 - 3650 days, default: 365)

## Data Sources

All economic data is sourced from the Federal Reserve Economic Data (FRED) API:
- Website: https://fred.stlouisfed.org/
- API Documentation: https://fred.stlouisfed.org/docs/api/
- API Key: Required (free registration)

## Setup

1. Obtain a FRED API key from https://fred.stlouisfed.org/docs/api/api_key.html
2. Set the `FRED_API_KEY` environment variable or add it to your `.env` file:
   ```
   FRED_API_KEY=your_api_key_here
   ```
3. The model will automatically create its database table on first run

## Usage

### V1 Programmatic Usage

```python
from forecasts.us_recession_2025 import RecessionModel

# Create v1 model instance
model = RecessionModel()

# Calculate probability with default parameters
probability = model.calculate_probability()
print(f"Recession probability: {probability:.2%}")

# Calculate with custom parameters
custom_params = {
    'yield_curve_weight': 0.40,
    'unemployment_weight': 0.30,
    'gdp_weight': 0.20,
    'confidence_weight': 0.05,
    'leading_indicators_weight': 0.05
}
probability = model.calculate_probability(custom_params)
print(f"Custom recession probability: {probability:.2%}")
```

### V2 Programmatic Usage

```python
from forecasts.us_recession_2025.model_v2 import RecessionModelV2
from datetime import datetime

# Create v2 model instance
model_v2 = RecessionModelV2()

# Calculate probability with temporal decay (default)
probability = model_v2.calculate_probability()
print(f"Adjusted recession probability: {probability:.2%}")

# Get detailed breakdown
breakdown = model_v2.get_probability_breakdown()
print(f"Base probability: {breakdown['base_probability']:.2%}")
print(f"Adjusted probability: {breakdown['adjusted_probability']:.2%}")
print(f"Days remaining: {breakdown['days_remaining']}")
print(f"Decay method: {breakdown['temporal_metadata']['decay_method']}")
print(f"Adjustment factor: {breakdown['temporal_metadata']['adjustment_factor']:.4f}")

# Calculate without temporal decay
probability_no_decay = model_v2.calculate_probability(apply_temporal_decay=False)
print(f"Base probability (no decay): {probability_no_decay:.2%}")

# Historical backtest
as_of_date = datetime(2024, 1, 1)
historical_prob = model_v2.calculate_probability(as_of_date=as_of_date)
print(f"Probability as of {as_of_date.date()}: {historical_prob:.2%}")

# Custom temporal decay parameters
custom_params = {
    'decay_method': 'exponential',
    'decay_rate': 0.02,
    'threshold': 0.35
}
probability_custom = model_v2.calculate_probability(params=custom_params)
print(f"Custom decay probability: {probability_custom:.2%}")
```

### Running Standalone Scripts

```bash
# Run v1 model
python forecasts/us_recession_2025/run_forecast.py

# Run v2 model with full breakdown
python forecasts/us_recession_2025/run_forecast_v2.py

# Run v2 with options
python forecasts/us_recession_2025/run_forecast_v2.py --no-history
python forecasts/us_recession_2025/run_forecast_v2.py --history-limit 20
```

### Running Backtests

```python
from forecasts.us_recession_2025.backtesting import BacktestEngine
from datetime import datetime

# Create backtest engine
engine = BacktestEngine(model_version='v2')

# Run weekly backtests for 2023
results = engine.run_backtest(
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 12, 31),
    frequency='weekly'
)

print(f"Completed {len(results)} backtests")

# Calculate performance metrics
metrics = engine.calculate_performance_metrics(results, actual_recession_periods=[])
print(f"Brier Score: {metrics['brier_score']:.4f}")
print(f"Calibration Slope: {metrics['calibration']['slope']:.4f}")

# Compare v1 vs v2
v1_results = engine.run_backtest(start_date, end_date, frequency='weekly')
comparison = engine.compare_models(v1_results, results, actual_outcomes=[])
print(f"V2 Brier Score Improvement: {comparison['brier_improvement']:.4f}")
```

### Using Jupyter Notebooks

```bash
# Navigate to notebooks directory
cd forecasts/us_recession_2025/notebooks

# Start Jupyter
jupyter notebook

# Or use JupyterLab
jupyter lab
```

Execute notebooks in order:
1. `01_data_exploration.ipynb` - Understand the data
2. `02_indicator_analysis.ipynb` - Analyze indicators
3. `03_model_comparison.ipynb` - Compare v1 vs v2
4. `04_backtesting_results.ipynb` - Evaluate performance
5. `05_temporal_calibration.ipynb` - Calibrate decay parameters

### Web Interface

The model is automatically discovered by the web interface and appears in the forecast list. Users can:
- View the current recession probability
- See the latest values for all economic indicators
- Adjust parameter weights to simulate different scenarios
- View historical probability trends

## Assumptions and Limitations

### Assumptions
- Historical relationships between indicators and recessions remain valid
- Economic indicators are accurately measured and reported
- The weighted combination approach captures the complex dynamics of recession prediction
- FRED data is timely and reliable

### Limitations
- Model is based on historical patterns and may not capture unprecedented economic conditions
- Does not account for policy interventions (monetary policy, fiscal stimulus)
- Indicator weights are somewhat arbitrary and may need adjustment
- Quarterly GDP data has reporting lag
- Does not incorporate qualitative factors (geopolitical events, market sentiment)
- Binary recession definition may not capture economic nuances

## Model Performance

The model should be evaluated against:
- Historical recession periods (NBER recession dates)
- Leading indicators' historical accuracy
- Comparison with professional forecasts (Fed, IMF, private sector)

Regular backtesting and calibration is recommended to maintain accuracy.

## References

- National Bureau of Economic Research (NBER) recession dating: https://www.nber.org/cycles/
- Federal Reserve Economic Data (FRED): https://fred.stlouisfed.org/
- Yield curve as recession predictor: https://www.newyorkfed.org/research/capital_markets/ycfaq
- Nate Silver's forecasting methodology: "The Signal and the Noise" (2012)

## Testing

The model includes comprehensive unit tests and property-based tests for both v1 and v2:

### V1 Tests

**Unit Tests** (`tests/test_recession_model.py`):
- Test with known historical recession data
- Test with economic expansion data
- Test with default parameters
- Test handling of missing indicators

**Property-Based Tests** (`tests/test_recession_model_properties.py`):
- Probability bounds enforcement
- Economic indicators collection
- Database persistence
- Parameter validation

### V2 Tests

**Unit Tests**:
- `tests/test_features.py`: Feature engineering calculations
- `tests/test_temporal_new_library.py`: Temporal decay functions
- `tests/test_recession_model.py`: V2 model calculations
- `tests/test_data_v2_properties.py`: Enhanced data fetching

**Property-Based Tests** (`tests/test_recession_model_properties.py`):
- Historical data temporal consistency
- Backtest probability bounds
- Backtest storage completeness
- Feature engineering determinism
- Rate of change correctness
- Temporal decay monotonicity
- Temporal decay boundary behavior
- Temporal decay preserves high probabilities
- Model version isolation
- Backtest uniqueness constraint
- Missing indicator handling
- Calibration parameter validity
- Backtest chronological ordering
- Feature engineering missing data handling

**Integration Tests**:
- `tests/test_breakdown_with_v2_model.py`: Probability breakdown
- `tests/test_v2_breakdown_integration.py`: Web interface integration
- `tests/test_final_integration.py`: End-to-end v2 functionality

### Running Tests

```bash
# Run all tests
pytest forecasts/us_recession_2025/tests/ -v

# Run only v2 tests
pytest forecasts/us_recession_2025/tests/ -k "v2" -v

# Run property-based tests
pytest forecasts/us_recession_2025/tests/ -k "properties" -v

# Run with coverage
pytest forecasts/us_recession_2025/tests/ --cov=forecasts.us_recession_2025 --cov-report=html
```

## Validation

### V1 Validation

```bash
python forecasts/us_recession_2025/tests/validate_recession_model.py
```

This script:
- Fetches current economic indicators
- Calculates recession probability
- Displays all indicator values
- Shows historical forecast trends

### V2 Validation

```bash
# Validate v2 model
python forecasts/us_recession_2025/tests/validate_recession_model_v2.py

# Validate feature engineering
python forecasts/us_recession_2025/tests/validate_features.py

# Validate temporal decay
python forecasts/us_recession_2025/tests/validate_temporal.py

# Validate backtesting
python forecasts/us_recession_2025/tests/validate_backtesting.py

# Validate data fetching
python forecasts/us_recession_2025/tests/validate_data_v2.py
```

### Web Interface Validation

```bash
# Validate breakdown endpoint
python tests/validate_breakdown_endpoint.py

# Validate temporal visualization
python tests/validate_temporal_template.py
python tests/validate_temporal_chart_js.py

# Validate complete integration
python tests/validate_final_integration.py
```

## Temporal Decay Methodology

### Rationale

The temporal decay approach is based on the principle that as time passes without recession signals, the probability should decrease. This reflects real-world prediction market behavior and incorporates time-to-event information.

### Industry Standard Approaches

V2 uses industry-standard time-to-event modeling techniques:

1. **Exponential Decay**: Common in survival analysis and reliability engineering
   - Simple, interpretable formula
   - Constant hazard rate assumption
   - Well-suited for economic forecasting

2. **Sigmoid Functions**: Used in logistic regression and neural networks
   - Smooth transitions
   - Flexible shape control
   - Natural S-curve behavior

3. **Empirical Calibration**: Bayesian approach to parameter fitting
   - Fit parameters to minimize prediction error on historical data
   - Validate on held-out periods
   - Update as new data becomes available

### When Decay is Applied

Temporal decay is only applied when:
- Base probability is below threshold (default: 0.4)
- Days remaining is less than 365
- Decay is enabled (default: true)

This ensures high-confidence predictions are not artificially reduced.

### Calibration Process

1. **Historical Data Collection**: Gather recession probabilities at various time distances from actual recessions
2. **Parameter Optimization**: Use scipy.optimize to minimize Brier score
3. **Cross-Validation**: Test on held-out historical periods
4. **Sensitivity Analysis**: Verify robustness across parameter ranges
5. **Documentation**: Record calibration methodology and results

See `notebooks/05_temporal_calibration.ipynb` for detailed calibration analysis.

## Interpretation Guide

### V1 Probability Ranges

- **0-20%**: Very low recession risk - economy appears healthy
- **20-40%**: Low to moderate risk - some warning signs present
- **40-60%**: Moderate risk - mixed signals, heightened uncertainty
- **60-80%**: High risk - multiple recession indicators present
- **80-100%**: Very high risk - strong recession signals

### V2 Dual Probability Interpretation

V2 provides two probabilities:

**Base Probability**: Economic signal strength without time adjustment
- Reflects current economic conditions
- Comparable to v1 probability
- Use for understanding economic health

**Adjusted Probability**: Time-aware probability incorporating deadline proximity
- Reflects both economic conditions and time remaining
- Decreases as deadline approaches without recession
- Use for prediction market comparison

**Example Interpretation**:
```
Base Probability: 35%
Adjusted Probability: 28%
Days Remaining: 120

Interpretation: Economic indicators show moderate recession risk (35%), 
but with only 120 days remaining and no recession yet, the time-adjusted 
probability is lower (28%). The 7 percentage point difference reflects 
the temporal decay adjustment.
```

### Key Indicators to Watch

**V1 Core Indicators**:
1. **Yield Curve**: Most reliable predictor - inversions (negative spread) have preceded most recessions
2. **Unemployment**: Rising unemployment is a strong recession signal
3. **GDP Growth**: Negative growth defines a recession
4. **Consumer Confidence**: Leading indicator of consumer spending
5. **Leading Indicators**: Composite index designed to predict turning points

**V2 Additional Indicators**:
6. **Credit Spread**: Widening spreads signal financial stress
7. **Housing Starts**: Leading indicator of construction activity
8. **Manufacturing PMI**: Timely indicator of industrial health
9. **Retail Sales**: Direct measure of consumer spending
10. **Oil Prices**: Affects inflation and economic activity
11. **VIX**: Market fear gauge and uncertainty measure

### Feature Importance

V2 engineered features provide additional signal:
- **Rate of Change**: Captures momentum and acceleration
- **Moving Averages**: Identifies trend direction
- **Volatility**: Measures uncertainty and instability

High volatility combined with negative rate of change is particularly concerning.

## Maintenance

**Regular Updates:**
- Review indicator weights quarterly based on recent economic patterns
- Update thresholds in `config.py` as economic conditions change
- Backtest against new recession data when available
- Monitor FRED API for data availability and changes

**Calibration:**
- Compare forecasts with professional predictions (Fed, IMF, private sector)
- Adjust weights based on indicator performance
- Consider adding new indicators as they become available
- Document all changes and rationale

## Known Issues

1. **GDP Data Lag**: GDP data is reported quarterly with a lag, so recent changes may not be reflected
2. **Indicator Correlation**: Some indicators are correlated, which may overweight certain signals
3. **Structural Changes**: Economic relationships change over time, requiring periodic recalibration
4. **Black Swan Events**: Model cannot predict unprecedented events (pandemics, wars, etc.)

## V2 Architecture

### Module Structure

```
forecasts/us_recession_2025/
├── model.py                    # V1 model (unchanged)
├── model_v2.py                 # V2 model with temporal decay
├── config.py                   # Shared configuration
├── config_v2.py                # V2-specific configuration
├── data.py                     # V1 data fetching (unchanged)
├── data_v2.py                  # Enhanced data fetching
├── features.py                 # Feature engineering module
├── temporal.py                 # Temporal decay functions (DEPRECATED - see lib/temporal_adjustment.py)
├── backtesting.py              # Historical backtesting engine
├── run_forecast.py             # V1 standalone script
├── run_forecast_v2.py          # V2 standalone script
├── notebooks/                  # Jupyter notebook suite
│   ├── 01_data_exploration.ipynb
│   ├── 02_indicator_analysis.ipynb
│   ├── 03_model_comparison.ipynb
│   ├── 04_backtesting_results.ipynb
│   ├── 05_temporal_calibration.ipynb
│   └── README.md
└── tests/                      # Comprehensive test suite
    ├── test_recession_model.py
    ├── test_recession_model_properties.py
    ├── test_features.py
    ├── test_temporal_new_library.py
    ├── test_data_v2_properties.py
    └── validate_*.py
```

### Data Flow

```
Historical Data Request
    ↓
[Data Fetcher V2] → Fetch 12 indicators for historical date
    ↓
[Feature Engineering] → Calculate derived features
    ↓
[Base Model] → Calculate base probability
    ↓
[Temporal Decay] → Apply time-to-event adjustment
    ↓
[Database] → Store with full metadata
    ↓
[Web Interface / Analysis]
```

### Database Schema

**V1 Table**: `forecast_us_recession_2025`
- Stores v1 model results
- Simple schema with probability and parameters

**V2 Table**: `forecast_us_recession_2025_v2`
- Stores v2 model results
- Includes base and adjusted probabilities
- Full indicator and feature snapshots

**Backtest Table**: `forecast_us_recession_2025_backtest`
- Stores historical backtest results
- Separate records for v1 and v2
- Enables performance comparison

## Future Enhancements

### Completed in V2
- ✅ Add more indicators (housing starts, credit spreads, manufacturing PMI, retail sales, oil, VIX)
- ✅ Implement time-series analysis (rate of change, moving averages, volatility)
- ✅ Incorporate market-based recession probabilities (temporal decay modeling)
- ✅ Implement ensemble methods (feature engineering combines multiple signals)

### Potential Future Improvements
- Add confidence intervals using bootstrap methods
- Add regional recession forecasts (state-level analysis)
- Implement machine learning models (random forest, gradient boosting)
- Add real-time data streaming for intraday updates
- Incorporate alternative data sources (satellite imagery, credit card data)
- Add scenario analysis (what-if simulations)
- Implement automated parameter optimization
- Add explainability features (SHAP values, feature attribution)

## Version History

- **v1.0** (2024): Initial implementation with six economic indicators and weighted logistic regression approach
- **v2.0** (2024): Major enhancement with:
  - 12 economic indicators (6 new)
  - Feature engineering (rate of change, moving averages, volatility)
  - Temporal decay modeling (exponential and sigmoid functions)
  - Historical backtesting engine
  - Jupyter notebook analysis suite
  - Enhanced web interface with temporal visualization
  - Comprehensive property-based testing
  - Model versioning and comparison infrastructure
