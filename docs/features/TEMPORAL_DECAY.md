# Temporal Decay: Complete Guide

## Overview

Temporal decay is a time-aware probability adjustment technique that incorporates the time remaining until a forecast deadline. As time passes without the predicted event occurring, the probability adjusts to reflect the decreasing opportunity for the event to occur.

## Why Temporal Decay?

### Real-World Observation

Prediction markets like Polymarket exhibit a characteristic pattern: as deadlines approach without the predicted event occurring, probabilities tend to decrease. This reflects:

1. **Information Accumulation**: Each day without the event provides evidence against it
2. **Time Constraints**: Less time remaining means less opportunity for the event to occur
3. **Bayesian Updating**: Market participants update beliefs based on the passage of time

### Example

Consider a forecast for "US Recession by December 31, 2025":
- **January 1, 2025**: Base probability 35%, 365 days remaining → Adjusted: 35%
- **October 1, 2025**: Base probability 35%, 91 days remaining → Adjusted: 28%
- **December 1, 2025**: Base probability 35%, 30 days remaining → Adjusted: 22%

The base probability (economic signal strength) remains constant, but the adjusted probability decreases as the deadline approaches without a recession occurring.

## Temporal Adjustment Library

The `lib/temporal_adjustment.py` library provides **6 different methods** for context-aware probability adjustments.

### Available Methods

| Method | Weak Signal (20%) | Uncertain (50%) | Strong Signal (80%) | Best Use Case |
|--------|-------------------|-----------------|---------------------|---------------|
| **none** | 20% → 20% | 50% → 50% | 80% → 80% | No time effect |
| **simple_decay** | 20% → 1% | 50% → 2% | 80% → 3% | Always unlikely |
| **threshold_decay** | 20% → 1% | 50% → 50% | 80% → 80% | Protect strong signals |
| **trend_amplification** | 20% → 0% | 50% → 50% | 80% → 100% | Amplify trends |
| **confidence_convergence** | 20% → 10% | 50% → 50% | 80% → 92% | Clear zones |
| **adaptive** ⭐ | 20% → 1% | 50% → 9% | 80% → 84% | Context-aware (RECOMMENDED) |

*With 38 days remaining out of 365 total*

### Method Details

#### 1. None
**Returns base probability unchanged.**

Best for non-time-sensitive forecasts or when you want pure model output.

```python
from lib.temporal_adjustment import TemporalAdjuster

adjuster = TemporalAdjuster(method='none')
adjusted, metadata = adjuster.adjust_probability(0.65, current_date, deadline)
# adjusted = 0.65 (unchanged)
```

#### 2. Simple Decay
**Always reduces probability as time passes.**

Formula: `adjusted = base * (days_remaining / total_days)^decay_power`

Best for events very unlikely to occur. Problem: Reduces even strong signals inappropriately.

```python
adjuster = TemporalAdjuster(method='simple_decay', total_days=365, decay_power=1.5)
adjusted, metadata = adjuster.adjust_probability(0.30, current_date, deadline)
# With 38 days left: 0.30 → 0.01 (strong decay)
```

#### 3. Threshold Decay
**Decays only below a threshold, preserves high probabilities.**

Logic:
- If `base_prob >= threshold`: No adjustment
- If `base_prob < threshold`: Apply simple decay

Best for protecting strong signals. Problem: Hard cutoff creates discontinuity.

```python
adjuster = TemporalAdjuster(
    method='threshold_decay',
    total_days=365,
    decay_power=1.5,
    threshold=0.5
)

# Weak signal decays
adjusted, _ = adjuster.adjust_probability(0.35, current_date, deadline)
# 0.35 → 0.01

# Strong signal preserved
adjusted, _ = adjuster.adjust_probability(0.65, current_date, deadline)
# 0.65 → 0.65
```

#### 4. Trend Amplification
**Amplifies trends as deadline approaches.**

Logic:
- If `base_prob > threshold`: Push toward 1.0
- If `base_prob < threshold`: Push toward 0.0
- If `base_prob ≈ threshold`: Minimal change

Best for events with strengthening evidence. Problem: Can over-amplify weak signals.

```python
adjuster = TemporalAdjuster(
    method='trend_amplification',
    total_days=365,
    amplification_power=1.5,
    threshold=0.5
)

# Strong signal amplifies
adjusted, _ = adjuster.adjust_probability(0.65, current_date, deadline)
# 0.65 → 0.80

# Weak signal decays
adjusted, _ = adjuster.adjust_probability(0.35, current_date, deadline)
# 0.35 → 0.21
```

#### 5. Confidence Convergence
**Converges toward 0 or 1 based on signal zones.**

Logic:
- Strong signals (`>upper_threshold`): Converge to 1.0
- Weak signals (`<lower_threshold`): Converge to 0.0
- Uncertain signals (between): Minimal adjustment

Best for binary events where uncertainty should decrease. Problem: Doesn't adjust uncertain signals.

```python
adjuster = TemporalAdjuster(
    method='confidence_convergence',
    total_days=365,
    convergence_power=2.0,
    lower_threshold=0.3,
    upper_threshold=0.7
)

# Very likely converges to 1.0
adjusted, _ = adjuster.adjust_probability(0.85, current_date, deadline)
# 0.85 → 0.92

# Very unlikely converges to 0.0
adjusted, _ = adjuster.adjust_probability(0.15, current_date, deadline)
# 0.15 → 0.08

# Uncertain (no change)
adjusted, _ = adjuster.adjust_probability(0.50, current_date, deadline)
# 0.50 → 0.50
```

#### 6. Adaptive ⭐ (RECOMMENDED)
**Smart, context-aware adjustment that handles all cases.**

Logic:
- **Strong signals** (`>upper_threshold`): Amplify toward 1.0
- **Weak signals** (`<lower_threshold`): Decay toward 0.0
- **Uncertain signals** (between): Gentle decay

Best for most real-world forecasts. Matches human intuition about how forecasts should evolve.

```python
adjuster = TemporalAdjuster(
    method='adaptive',
    total_days=365,
    decay_power=1.5,
    amplification_power=1.5,
    lower_threshold=0.4,
    upper_threshold=0.6
)

# Strong signal amplifies
adjusted, _ = adjuster.adjust_probability(0.75, current_date, deadline)
# 0.75 → 0.79

# Weak signal decays
adjusted, _ = adjuster.adjust_probability(0.25, current_date, deadline)
# 0.25 → 0.01

# Uncertain signal (gentle decay)
adjusted, _ = adjuster.adjust_probability(0.49, current_date, deadline)
# 0.49 → 0.09
```

## Usage Examples

### Basic Usage

```python
from lib.temporal_adjustment import TemporalAdjuster
from datetime import datetime

# Create adjuster
adjuster = TemporalAdjuster(
    method='adaptive',
    total_days=365,
    decay_power=1.5,
    amplification_power=1.5,
    lower_threshold=0.4,
    upper_threshold=0.6
)

# Apply adjustment
base_probability = 0.48
current_date = datetime(2025, 11, 22)
deadline = datetime(2025, 12, 31)

adjusted_prob, metadata = adjuster.adjust_probability(
    base_probability,
    current_date,
    deadline
)

print(f"Base: {base_probability:.2%}")
print(f"Adjusted: {adjusted_prob:.2%}")
print(f"Method: {metadata['method']}")
print(f"Days remaining: {metadata['days_remaining']}")
```

### Comparing Methods

```python
from lib.temporal_adjustment import TemporalAdjuster

methods = ['none', 'simple_decay', 'threshold_decay', 'adaptive']
base_prob = 0.48

for method in methods:
    adjuster = TemporalAdjuster(method=method, total_days=365)
    adjusted, _ = adjuster.adjust_probability(base_prob, current_date, deadline)
    print(f"{method:20s}: {base_prob:.2%} → {adjusted:.2%}")
```

### List Available Methods

```python
from lib.temporal_adjustment import TemporalAdjuster

methods = TemporalAdjuster.list_methods()
for method, description in methods.items():
    print(f"{method}: {description}")
```

## Decision Guide

Choose based on your forecast type:

1. **Binary event, weak signals** → Use `adaptive` or `simple_decay`
2. **Binary event, strong signals** → Use `adaptive` or `trend_amplification`
3. **Binary event, uncertain signals** → Use `adaptive` (gentle decay)
4. **Want to preserve high probabilities** → Use `threshold_decay`
5. **Want trends to strengthen** → Use `trend_amplification` or `adaptive`
6. **No time effect desired** → Use `none`
7. **Not sure / general purpose** → Use `adaptive` ⭐

## Mathematical Framework

### Two-Stage Process

The V2 model uses a two-stage calculation:

**Stage 1: Base Probability**
```
P_base = f(economic_indicators, engineered_features, weights)
```
- Reflects current economic conditions
- Independent of time remaining
- Comparable to V1 probability

**Stage 2: Temporal Adjustment**
```
P_adjusted = g(P_base, days_remaining, decay_parameters)
```
- Incorporates time-to-event information
- Only applied when appropriate
- Produces final forecast probability

## Interpretation Guidelines

### Understanding Dual Probabilities

**Base Probability**: Economic signal strength
- Reflects current economic conditions
- Independent of time remaining
- Use for understanding economic health
- Comparable to V1 model

**Adjusted Probability**: Time-aware forecast
- Incorporates both economics and time
- Decreases as deadline approaches without event
- Use for prediction market comparison
- Final forecast output

### When Decay Matters Most

**High Impact Scenarios**:
1. **Low base probability + approaching deadline**: Large adjustment
   - Example: 30% base, 30 days remaining → 24% adjusted
2. **Moderate base probability + mid-range time**: Moderate adjustment
   - Example: 35% base, 180 days remaining → 32% adjusted

**Low Impact Scenarios**:
1. **High base probability**: No adjustment (above threshold)
   - Example: 75% base, any days remaining → 75% adjusted
2. **Far deadline**: Minimal adjustment
   - Example: 35% base, 365 days remaining → 35% adjusted

## Industry Standard Approaches

### Survival Analysis

Temporal decay draws from survival analysis, a statistical method for analyzing time-to-event data:

**Key Concepts**:
- **Hazard Function**: Instantaneous rate of event occurrence
- **Survival Function**: Probability of surviving past time t
- **Exponential Distribution**: Constant hazard rate (memoryless property)

### Bayesian Updating

Temporal decay can be viewed as Bayesian updating:

**Prior**: Base probability from economic indicators
**Evidence**: Passage of time without recession
**Posterior**: Adjusted probability incorporating time evidence

## Limitations and Considerations

### Assumptions

1. **Constant Hazard Rate** - Assumes event risk is constant per unit time
2. **Independence of Time and Economics** - Assumes time effect is independent of economic conditions
3. **Historical Patterns Hold** - Calibration assumes past relationships continue

### Known Limitations

1. **Black Swan Events**: Cannot predict unprecedented shocks
2. **Policy Interventions**: Does not account for aggressive policy responses
3. **Structural Changes**: Economic relationships evolve over time
4. **Data Quality**: Depends on accurate, timely indicator data

### When Not to Use Temporal Decay

1. **Very short-term forecasts** (< 30 days): Time effect may be too strong
2. **Very long-term forecasts** (> 2 years): Time effect may be too weak
3. **High-confidence predictions**: Decay may inappropriately reduce probability
4. **Rapidly changing conditions**: Base probability changes may dominate

## See Also

- [Backtesting Guide](BACKTESTING.md) - Validate temporal decay parameters
- [US Recession Model](../../forecasts/us_recession_2025/README.md) - Implementation example
- [Temporal Adjustment Library Source](../../lib/temporal_adjustment.py) - Code implementation
