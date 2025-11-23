# Historical Backtesting Guide

## Overview

Historical backtesting allows you to evaluate how forecast models would have performed in the past. By running the model on historical dates with only data available at that time, you can assess accuracy, identify weaknesses, and compare model versions.

## Why Backtest?

### Benefits

1. **Validate Accuracy**: Measure how well the model predicts actual outcomes
2. **Compare Versions**: Evaluate v2 improvements over v1
3. **Identify Weaknesses**: Find periods where the model over/under-predicts
4. **Build Confidence**: Demonstrate model reliability to stakeholders
5. **Calibrate Parameters**: Tune model parameters using historical data
6. **Understand Behavior**: See how the model responds to different economic conditions

### What Backtesting Tests

- **Temporal Consistency**: Model only uses data available at backtest date
- **Probability Bounds**: All forecasts remain in [0, 1]
- **Storage Completeness**: All metadata is captured
- **Version Isolation**: V1 and v2 results are stored separately
- **Chronological Ordering**: Results can be analyzed over time

## Quick Start

### Basic Backtest

```python
from forecasts.us_recession_2025.backtesting import BacktestEngine
from datetime import datetime

# Create backtest engine for v2
engine = BacktestEngine(model_version='v2')

# Run weekly backtests for 2023
results = engine.run_backtest(
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 12, 31),
    frequency='weekly'
)

print(f"Completed {len(results)} backtests")
for result in results[:5]:  # Show first 5
    print(f"{result['backtest_date'].date()}: {result['adjusted_probability']:.2%}")
```

### Calculate Performance Metrics

```python
# Define actual recession periods (if any)
actual_recession_periods = [
    # (datetime(2020, 2, 1), datetime(2020, 4, 30)),  # COVID recession
]

# Calculate metrics
metrics = engine.calculate_performance_metrics(
    backtest_results=results,
    actual_recession_periods=actual_recession_periods
)

print(f"Brier Score: {metrics['brier_score']:.4f}")
print(f"Calibration Slope: {metrics['calibration']['slope']:.4f}")
print(f"Calibration Intercept: {metrics['calibration']['intercept']:.4f}")
```

### Compare V1 vs V2

```python
# Run backtests for both versions
engine_v1 = BacktestEngine(model_version='v1')
engine_v2 = BacktestEngine(model_version='v2')

v1_results = engine_v1.run_backtest(start_date, end_date, 'weekly')
v2_results = engine_v2.run_backtest(start_date, end_date, 'weekly')

# Compare performance
comparison = engine_v2.compare_models(
    v1_results=v1_results,
    v2_results=v2_results,
    actual_outcomes=[]  # Binary outcomes if available
)

print(f"V1 Brier Score: {comparison['v1_brier']:.4f}")
print(f"V2 Brier Score: {comparison['v2_brier']:.4f}")
print(f"Improvement: {comparison['brier_improvement']:.4f}")
```

## BacktestEngine API

### Constructor

```python
BacktestEngine(model_version='v2')
```

**Parameters**:
- `model_version` (str): Model version to test ('v1' or 'v2')

**Returns**: BacktestEngine instance

### run_backtest()

```python
engine.run_backtest(start_date, end_date, frequency='weekly')
```

**Parameters**:
- `start_date` (datetime): First date to backtest
- `end_date` (datetime): Last date to backtest
- `frequency` (str): 'daily', 'weekly', or 'monthly'

**Returns**: List of backtest result dictionaries

**Result Structure**:
```python
{
    'backtest_date': datetime,           # Date model was "run"
    'forecast_date': datetime,           # Forecast deadline (2025-12-31)
    'model_version': str,                # 'v1' or 'v2'
    'base_probability': float,           # Before temporal adjustment
    'adjusted_probability': float,       # After temporal adjustment
    'days_remaining': int,               # Days from backtest to deadline
    'parameters': dict,                  # Model parameters used
    'indicators': dict,                  # Indicator values
    'features': dict,                    # Engineered features (v2 only)
    'temporal_metadata': dict            # Decay details (v2 only)
}
```

### calculate_performance_metrics()

```python
engine.calculate_performance_metrics(backtest_results, actual_recession_periods)
```

**Parameters**:
- `backtest_results` (list): Results from run_backtest()
- `actual_recession_periods` (list): List of (start_date, end_date) tuples for actual recessions

**Returns**: Dictionary of performance metrics

**Metrics Structure**:
```python
{
    'brier_score': float,                # Mean squared error (lower is better)
    'calibration': {
        'slope': float,                  # Should be close to 1.0
        'intercept': float,              # Should be close to 0.0
        'r_squared': float               # Goodness of fit
    },
    'discrimination': {
        'auc_roc': float,                # Area under ROC curve (if binary outcomes)
        'separation': float              # Difference in mean forecasts
    },
    'sharpness': float,                  # Standard deviation of forecasts
    'mean_forecast': float,              # Average probability
    'forecast_range': tuple              # (min, max) probabilities
}
```

## Performance Metrics Explained

### Brier Score

**Definition**: Mean squared error of probability forecasts

**Formula**:
```
BS = (1/N) * Σ(forecast_i - outcome_i)²
```

**Interpretation**:
- Range: [0, 1]
- Lower is better (0 = perfect forecast)
- Penalizes both over and under-confidence
- Standard metric for probabilistic forecasts

**Good Brier Scores**:
- < 0.10: Excellent
- 0.10 - 0.15: Good
- 0.15 - 0.20: Fair
- \> 0.20: Poor

### Calibration

**Definition**: Agreement between forecast probabilities and observed frequencies

**Metrics**:
- **Slope**: Should be close to 1.0 (perfect calibration)
  - < 1.0: Over-confident (forecasts too extreme)
  - \> 1.0: Under-confident (forecasts too moderate)
- **Intercept**: Should be close to 0.0
  - < 0: Systematic over-prediction
  - \> 0: Systematic under-prediction

**Calibration Plot**: Plot forecast probabilities vs observed frequencies
- Perfect calibration: Points lie on 45-degree line
- Above line: Under-prediction
- Below line: Over-prediction

### Discrimination

**Definition**: Ability to distinguish between positive and negative outcomes

**Metrics**:
- **AUC-ROC**: Area under Receiver Operating Characteristic curve
  - Range: [0, 1]
  - 0.5: Random guessing
  - 1.0: Perfect discrimination
  - \> 0.7: Good discrimination
- **Separation**: Difference in mean forecasts for positive vs negative outcomes
  - Larger is better
  - Indicates model can distinguish outcomes

### Sharpness

**Definition**: Concentration of forecast probabilities

**Metric**: Standard deviation of forecasts
- Higher sharpness: More decisive forecasts (closer to 0 or 1)
- Lower sharpness: More uncertain forecasts (closer to 0.5)

**Trade-off**: Sharpness should be balanced with calibration
- Too sharp: Over-confident, poor calibration
- Too diffuse: Under-confident, less informative

## Backtesting Workflows

### Workflow 1: Initial Model Validation

**Goal**: Validate model on historical data before deployment

**Steps**:
1. Run backtests for past 3-5 years
2. Calculate Brier score and calibration
3. Identify periods of poor performance
4. Adjust parameters if needed
5. Re-run backtests to verify improvement

**Code**:
```python
from forecasts.us_recession_2025.backtesting import BacktestEngine
from datetime import datetime

engine = BacktestEngine(model_version='v2')

# Run backtests
results = engine.run_backtest(
    start_date=datetime(2020, 1, 1),
    end_date=datetime(2024, 11, 1),
    frequency='monthly'
)

# Calculate metrics
metrics = engine.calculate_performance_metrics(results, [])

# Evaluate
if metrics['brier_score'] < 0.15:
    print("✓ Model validation passed")
else:
    print("✗ Model needs improvement")
    print(f"  Brier Score: {metrics['brier_score']:.4f}")
    print(f"  Calibration Slope: {metrics['calibration']['slope']:.4f}")
```

### Workflow 2: V1 vs V2 Comparison

**Goal**: Demonstrate v2 improvements over v1

**Steps**:
1. Run backtests for both versions on same dates
2. Calculate performance metrics for each
3. Compare Brier scores and calibration
4. Visualize probability evolution over time
5. Document improvements

**Code**:
```python
from forecasts.us_recession_2025.backtesting import BacktestEngine
from datetime import datetime
import matplotlib.pyplot as plt

# Run backtests
engine_v1 = BacktestEngine(model_version='v1')
engine_v2 = BacktestEngine(model_version='v2')

start = datetime(2023, 1, 1)
end = datetime(2024, 11, 1)

v1_results = engine_v1.run_backtest(start, end, 'weekly')
v2_results = engine_v2.run_backtest(start, end, 'weekly')

# Compare
comparison = engine_v2.compare_models(v1_results, v2_results, [])

print(f"V1 Brier Score: {comparison['v1_brier']:.4f}")
print(f"V2 Brier Score: {comparison['v2_brier']:.4f}")
print(f"Improvement: {comparison['brier_improvement']:.4f}")

# Visualize
dates = [r['backtest_date'] for r in v1_results]
v1_probs = [r['adjusted_probability'] for r in v1_results]
v2_probs = [r['adjusted_probability'] for r in v2_results]

plt.figure(figsize=(12, 6))
plt.plot(dates, v1_probs, label='V1', linewidth=2)
plt.plot(dates, v2_probs, label='V2', linewidth=2)
plt.xlabel('Date')
plt.ylabel('Recession Probability')
plt.title('V1 vs V2 Historical Forecasts')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

### Workflow 3: Parameter Optimization

**Goal**: Find optimal model parameters using historical data

**Steps**:
1. Define parameter ranges to test
2. Run backtests for each parameter combination
3. Calculate Brier score for each
4. Select parameters with lowest Brier score
5. Validate on held-out data

**Code**:
```python
from forecasts.us_recession_2025.backtesting import BacktestEngine
from datetime import datetime

engine = BacktestEngine(model_version='v2')

# Parameter grid
decay_rates = [0.01, 0.015, 0.02, 0.025, 0.03]
thresholds = [0.35, 0.40, 0.45]

best_brier = float('inf')
best_params = None

# Grid search
for decay_rate in decay_rates:
    for threshold in thresholds:
        params = {
            'decay_method': 'exponential',
            'decay_rate': decay_rate,
            'threshold': threshold
        }
        
        results = engine.run_backtest(
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2024, 11, 1),
            frequency='monthly',
            custom_params=params
        )
        
        metrics = engine.calculate_performance_metrics(results, [])
        brier = metrics['brier_score']
        
        print(f"decay_rate={decay_rate}, threshold={threshold}: Brier={brier:.4f}")
        
        if brier < best_brier:
            best_brier = brier
            best_params = params

print(f"\nOptimal parameters: {best_params}")
print(f"Best Brier Score: {best_brier:.4f}")
```

## Best Practices

### Frequency Selection

**Daily Backtests**:
- Pros: Maximum temporal resolution, captures day-to-day changes
- Cons: Computationally expensive, data may not change daily
- Use when: Analyzing short-term model behavior

**Weekly Backtests** (Recommended):
- Pros: Good balance of resolution and efficiency
- Cons: May miss intra-week changes
- Use when: Standard model evaluation

**Monthly Backtests**:
- Pros: Fast, focuses on longer-term trends
- Cons: Lower temporal resolution
- Use when: Long-term performance analysis

### Date Range Selection

**Training Period**: Use for parameter optimization
- Typical: 3-5 years of historical data
- Should include various economic conditions
- Should include at least one recession if possible

**Validation Period**: Use for final evaluation
- Typical: Most recent 1-2 years
- Should be held out from training
- Simulates real-world deployment

**Example Split**:
```python
# Training: 2018-2022
training_results = engine.run_backtest(
    datetime(2018, 1, 1),
    datetime(2022, 12, 31),
    'weekly'
)

# Validation: 2023-2024
validation_results = engine.run_backtest(
    datetime(2023, 1, 1),
    datetime(2024, 11, 1),
    'weekly'
)
```

## Database Schema

### Backtest Table

```sql
CREATE TABLE forecast_us_recession_2025_backtest (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backtest_date DATE NOT NULL,
    forecast_date DATE NOT NULL,
    model_version TEXT NOT NULL,
    base_probability REAL,
    adjusted_probability REAL,
    days_remaining INTEGER,
    parameters TEXT,                     -- JSON
    indicators TEXT,                     -- JSON
    features TEXT,                       -- JSON (v2 only)
    temporal_metadata TEXT,              -- JSON (v2 only)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(backtest_date, model_version)
);

CREATE INDEX idx_backtest_date ON forecast_us_recession_2025_backtest(backtest_date);
CREATE INDEX idx_model_version ON forecast_us_recession_2025_backtest(model_version);
```

### Querying Backtest Results

```python
from lib.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# Get all v2 backtests from 2023
cursor.execute("""
    SELECT backtest_date, adjusted_probability, days_remaining
    FROM forecast_us_recession_2025_backtest
    WHERE model_version = 'v2'
      AND backtest_date >= '2023-01-01'
      AND backtest_date < '2024-01-01'
    ORDER BY backtest_date
""")

results = cursor.fetchall()
for date, prob, days in results:
    print(f"{date}: {prob:.2%} ({days} days remaining)")
```

## See Also

- [Temporal Decay Guide](TEMPORAL_DECAY.md) - Understand temporal adjustments
- [US Recession Model](../../forecasts/us_recession_2025/README.md) - Model documentation
- [Jupyter Notebooks](../../forecasts/us_recession_2025/notebooks/README.md) - Interactive analysis
