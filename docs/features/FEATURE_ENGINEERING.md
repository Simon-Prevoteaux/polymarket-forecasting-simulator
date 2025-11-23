# Feature Engineering Guide

## Overview

Feature engineering transforms raw economic indicators into derived features that capture important patterns like trends, momentum, and volatility. The V2 model includes comprehensive feature engineering to improve forecast accuracy.

## Why Feature Engineering?

Raw economic indicators provide point-in-time values, but forecasting requires understanding:

1. **Trends**: Is the indicator improving or deteriorating?
2. **Momentum**: How fast is it changing?
3. **Volatility**: How stable or unstable is it?
4. **Context**: How does current value compare to recent history?

## Engineered Features

### 1. Rate of Change

**Definition**: Percentage change over different time windows

**Formula**:
```
ROC = (current_value - past_value) / past_value * 100
```

**Time Windows**:
- **30-day**: Short-term momentum
- **90-day**: Medium-term trend
- **180-day**: Long-term trend

**Example**:
```python
# Unemployment rate: 3.8% → 4.2% over 90 days
roc_90d = (4.2 - 3.8) / 3.8 * 100 = 10.5%
# Positive ROC indicates rising unemployment (recession signal)
```

**Interpretation**:
- Positive ROC: Indicator increasing
- Negative ROC: Indicator decreasing
- Larger magnitude: Faster change

### 2. Moving Averages

**Definition**: Average value over a rolling time window

**Formula**:
```
MA = mean(values over window)
```

**Time Windows**:
- **30-day**: Short-term average
- **90-day**: Medium-term average

**Purpose**:
- Smooth out noise and volatility
- Identify underlying trends
- Compare current value to recent average

**Example**:
```python
# GDP growth: current = 2.1%, 90-day MA = 2.5%
# Current below average suggests slowing growth
```

**Interpretation**:
- Current > MA: Above recent average (positive signal)
- Current < MA: Below recent average (negative signal)
- Distance from MA: Strength of signal

### 3. Volatility

**Definition**: Standard deviation of values over time window

**Formula**:
```
Volatility = std_dev(values over window)
```

**Time Windows**:
- **30-day**: Short-term volatility
- **90-day**: Medium-term volatility

**Purpose**:
- Measure uncertainty and instability
- High volatility often precedes recessions
- Identify regime changes

**Example**:
```python
# VIX volatility: 30-day std = 5.2
# High volatility indicates market uncertainty
```

**Interpretation**:
- Low volatility: Stable conditions
- High volatility: Uncertain conditions
- Increasing volatility: Potential regime change

## Feature Engineering Pipeline

### Data Flow

```
Raw Indicators
    ↓
Historical Data Fetch (lookback_days)
    ↓
Feature Calculation
    ├── Rate of Change (30d, 90d, 180d)
    ├── Moving Averages (30d, 90d)
    └── Volatility (30d, 90d)
    ↓
Feature Dictionary
    ↓
Model Input
```

### Implementation

**Location**: `forecasts/us_recession_2025/features.py`

**Key Functions**:

```python
def calculate_rate_of_change(series: pd.Series, window: int) -> float:
    """Calculate percentage change over window."""
    if len(series) < window:
        return 0.0
    current = series.iloc[-1]
    past = series.iloc[-window]
    if past == 0:
        return 0.0
    return ((current - past) / abs(past)) * 100

def calculate_moving_average(series: pd.Series, window: int) -> float:
    """Calculate moving average over window."""
    if len(series) < window:
        return series.mean()
    return series.iloc[-window:].mean()

def calculate_volatility(series: pd.Series, window: int) -> float:
    """Calculate standard deviation over window."""
    if len(series) < window:
        return series.std()
    return series.iloc[-window:].std()
```

### Feature Dictionary Structure

```python
features = {
    # Rate of change features
    'UNRATE_roc_30d': 2.5,
    'UNRATE_roc_90d': 5.2,
    'UNRATE_roc_180d': 8.1,
    'T10Y2Y_roc_30d': -15.3,
    # ... more ROC features
    
    # Moving average features
    'UNRATE_ma_30d': 3.9,
    'UNRATE_ma_90d': 3.8,
    'T10Y2Y_ma_30d': -0.45,
    # ... more MA features
    
    # Volatility features
    'UNRATE_vol_30d': 0.12,
    'UNRATE_vol_90d': 0.15,
    'VIX_vol_30d': 5.2,
    # ... more volatility features
}
```

## Using Features in Models

### Feature Integration

```python
from forecasts.us_recession_2025.features import engineer_features

# Get raw indicators
indicators = fetch_economic_indicators_v2()

# Engineer features
features = engineer_features(indicators, lookback_days=365)

# Use in model
def calculate_probability(indicators, features):
    # Combine raw indicators and engineered features
    signals = []
    
    # Raw indicator signals
    signals.append(indicators['UNRATE'] > 4.0)
    
    # Feature-based signals
    signals.append(features['UNRATE_roc_90d'] > 5.0)  # Rising unemployment
    signals.append(features['T10Y2Y_ma_30d'] < 0)     # Inverted yield curve
    signals.append(features['VIX_vol_30d'] > 3.0)     # High volatility
    
    # Combine signals
    probability = sum(signals) / len(signals)
    return probability
```

### Feature Importance

Different features have different predictive power:

**High Importance**:
- Yield curve rate of change (T10Y2Y_roc_*)
- Unemployment rate of change (UNRATE_roc_*)
- Credit spread moving averages (BAA10Y_ma_*)
- VIX volatility (VIX_vol_*)

**Medium Importance**:
- GDP growth rate of change (GDP_roc_*)
- Initial claims moving averages (ICSA_ma_*)
- Retail sales rate of change (RSXFS_roc_*)

**Lower Importance**:
- Housing starts features (HOUST_*)
- Oil price features (DCOILWTICO_*)
- Manufacturing PMI features (NAPM_*)

## Missing Data Handling

### Forward Fill Strategy

When historical data is insufficient for feature calculation:

1. **Insufficient History**: Use available data
   ```python
   if len(series) < window:
       return series.mean()  # Use all available data
   ```

2. **Missing Values**: Forward fill from last known value
   ```python
   series = series.fillna(method='ffill')
   ```

3. **Neutral Defaults**: Return 0 for rate of change if no data
   ```python
   if len(series) == 0:
       return 0.0
   ```

### Validation

```python
def validate_features(features: dict) -> dict:
    """Validate and clean feature dictionary."""
    validated = {}
    for key, value in features.items():
        if value is None or np.isnan(value):
            validated[key] = 0.0  # Neutral default
        elif np.isinf(value):
            validated[key] = 0.0  # Handle infinity
        else:
            validated[key] = float(value)
    return validated
```

## Feature Analysis

### Correlation Analysis

Understand relationships between features:

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Create feature matrix
feature_matrix = pd.DataFrame([
    features_at_date_1,
    features_at_date_2,
    # ... more dates
])

# Calculate correlations
correlations = feature_matrix.corr()

# Visualize
plt.figure(figsize=(12, 10))
sns.heatmap(correlations, annot=True, cmap='coolwarm', center=0)
plt.title('Feature Correlation Matrix')
plt.show()
```

### Feature Distribution

Analyze feature value distributions:

```python
import matplotlib.pyplot as plt

# Plot feature distributions
fig, axes = plt.subplots(3, 3, figsize=(15, 12))
for idx, (feature_name, values) in enumerate(feature_data.items()):
    ax = axes[idx // 3, idx % 3]
    ax.hist(values, bins=30, edgecolor='black')
    ax.set_title(feature_name)
    ax.set_xlabel('Value')
    ax.set_ylabel('Frequency')
plt.tight_layout()
plt.show()
```

## Best Practices

### 1. Consistent Time Windows

Use consistent time windows across indicators:
- 30 days: Short-term (1 month)
- 90 days: Medium-term (1 quarter)
- 180 days: Long-term (2 quarters)

### 2. Handle Missing Data Gracefully

Always provide fallback values:
```python
def safe_feature_calculation(series, window):
    try:
        return calculate_feature(series, window)
    except Exception as e:
        logger.warning(f"Feature calculation failed: {e}")
        return 0.0  # Neutral default
```

### 3. Validate Feature Values

Check for invalid values:
```python
def is_valid_feature(value):
    return (
        value is not None and
        not np.isnan(value) and
        not np.isinf(value)
    )
```

### 4. Document Feature Meanings

Always document what each feature represents:
```python
FEATURE_DESCRIPTIONS = {
    'UNRATE_roc_90d': 'Unemployment rate 90-day rate of change (%)',
    'T10Y2Y_ma_30d': '10Y-2Y yield spread 30-day moving average',
    'VIX_vol_30d': 'VIX 30-day volatility (std dev)'
}
```

### 5. Monitor Feature Drift

Track feature distributions over time to detect drift:
```python
def check_feature_drift(current_features, historical_features):
    """Check if current features are within historical range."""
    for feature_name, current_value in current_features.items():
        historical_values = historical_features[feature_name]
        mean = np.mean(historical_values)
        std = np.std(historical_values)
        
        # Check if current value is > 3 std devs from mean
        if abs(current_value - mean) > 3 * std:
            logger.warning(f"Feature drift detected: {feature_name}")
```

## Testing Features

### Unit Tests

```python
def test_rate_of_change_calculation():
    """Test ROC calculation."""
    series = pd.Series([100, 105, 110])
    roc = calculate_rate_of_change(series, window=2)
    assert abs(roc - 5.0) < 0.01  # 5% increase

def test_moving_average_calculation():
    """Test MA calculation."""
    series = pd.Series([10, 20, 30])
    ma = calculate_moving_average(series, window=3)
    assert abs(ma - 20.0) < 0.01  # Average of 10, 20, 30
```

### Property Tests

```python
from hypothesis import given, strategies as st

@given(st.lists(st.floats(min_value=0, max_value=100), min_size=10))
def test_volatility_non_negative(values):
    """Property: Volatility is always non-negative."""
    series = pd.Series(values)
    vol = calculate_volatility(series, window=5)
    assert vol >= 0
```

## See Also

- [US Recession Model](../../forecasts/us_recession_2025/README.md) - Model using features
- [Jupyter Notebooks](../../forecasts/us_recession_2025/notebooks/README.md) - Feature analysis
- [Features Source Code](../../forecasts/us_recession_2025/features.py) - Implementation
