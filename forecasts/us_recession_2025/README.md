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

## Version History

- v1.0 (2024): Initial implementation with six economic indicators and weighted logistic regression approach
