# US Recession 2025 Forecast Model

## Overview

This forecast model predicts the probability of a US recession occurring by the end of 2025. It analyzes multiple economic indicators and combines them using a weighted logistic regression approach to generate a single probability estimate.

## Economic Indicators

The model uses six key economic indicators from the Federal Reserve Economic Data (FRED) API:

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

## Methodology

### Signal Calculation

For each indicator, the model:
1. Fetches the latest available data from FRED
2. Calculates a z-score relative to historical mean and standard deviation
3. Applies a logistic transformation to convert the z-score to a probability signal (0-1)
4. Adjusts the direction based on whether high or low values signal recession

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

### Programmatic Usage

```python
from forecasts.us_recession_2025 import RecessionModel

# Create model instance
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

The model includes comprehensive unit tests and property-based tests:

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

Run tests:
```bash
pytest forecasts/us_recession_2025/tests/ -v
```

## Validation

Validate the model against historical data:

```bash
python forecasts/us_recession_2025/tests/validate_recession_model.py
```

This script:
- Fetches current economic indicators
- Calculates recession probability
- Displays all indicator values
- Shows historical forecast trends

## Interpretation Guide

**Probability Ranges:**
- **0-20%**: Very low recession risk - economy appears healthy
- **20-40%**: Low to moderate risk - some warning signs present
- **40-60%**: Moderate risk - mixed signals, heightened uncertainty
- **60-80%**: High risk - multiple recession indicators present
- **80-100%**: Very high risk - strong recession signals

**Key Indicators to Watch:**
1. **Yield Curve**: Most reliable predictor - inversions (negative spread) have preceded most recessions
2. **Unemployment**: Rising unemployment is a strong recession signal
3. **GDP Growth**: Negative growth defines a recession
4. **Consumer Confidence**: Leading indicator of consumer spending
5. **Leading Indicators**: Composite index designed to predict turning points

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

## Future Enhancements

Potential improvements to consider:
- Add more indicators (housing starts, credit spreads, manufacturing PMI)
- Implement time-series analysis for trend detection
- Add confidence intervals using bootstrap methods
- Incorporate market-based recession probabilities
- Add regional recession forecasts
- Implement ensemble methods combining multiple approaches

## Version History

- **v1.0** (2024): Initial implementation with six economic indicators and weighted logistic regression approach
