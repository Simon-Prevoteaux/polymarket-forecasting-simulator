# Temporal Adjustment Library - Complete Guide

## Overview

The `temporal_adjustment.py` library provides **context-aware** probability adjustments for time-sensitive forecasts. Unlike simple decay methods, these adjustments adapt based on signal strength and forecast type.

## Philosophy

Different forecasts need different temporal adjustments:

1. **Weak signals** (low probability) → Should decay as time passes without occurrence
2. **Strong signals** (high probability) → Should amplify/converge as deadline approaches
3. **Uncertain signals** (middle probability) → Should adjust gently or not at all

## Available Methods

### 1. No Adjustment (`none`)

**Returns base probability unchanged.**

**Best for:**
- Non-time-sensitive forecasts
- Continuous market predictions
- When you want pure model output

**Example:** Stock price predictions, long-term trends

```python
from lib.temporal_adjustment import TemporalAdjuster

adjuster = TemporalAdjuster(method='none')
adjusted, metadata = adjuster.adjust_probability(0.65, current_date, deadline)
# adjusted = 0.65 (unchanged)
```

---

### 2. Simple Decay (`simple_decay`)

**Always reduces probability as time passes.**

**Formula:** `adjusted = base * (days_remaining / total_days)^decay_power`

**Best for:**
- Events very unlikely to occur
- When any signal should decay over time

**Problem:** Reduces even strong signals inappropriately

**Parameters:**
- `decay_power` (default 1.5): Higher = faster decay

**Example:** Product launch that keeps getting delayed

```python
adjuster = TemporalAdjuster(method='simple_decay', total_days=365, decay_power=1.5)
adjusted, metadata = adjuster.adjust_probability(0.30, current_date, deadline)
# With 38 days left: 0.30 → 0.01 (strong decay)
```

---

### 3. Threshold Decay (`threshold_decay`)

**Decays only below a threshold, preserves high probabilities.**

**Logic:**
- If `base_prob >= threshold`: No adjustment
- If `base_prob < threshold`: Apply simple decay

**Best for:**
- When you want to protect strong signals
- Binary events with clear thresholds

**Problem:** Hard cutoff creates discontinuity

**Parameters:**
- `decay_power` (default 1.5): Decay rate
- `threshold` (default 0.5): Only decay below this

**Example:** Recession with strong vs weak signals

```python
adjuster = TemporalAdjuster(
    method='threshold_decay',
    total_days=365,
    decay_power=1.5,
    threshold=0.5
)

# Weak signal
adjusted, _ = adjuster.adjust_probability(0.35, current_date, deadline)
# 0.35 → 0.01 (decays)

# Strong signal
adjusted, _ = adjuster.adjust_probability(0.65, current_date, deadline)
# 0.65 → 0.65 (preserved)
```

---

### 4. Trend Amplification (`trend_amplification`)

**Amplifies trends as deadline approaches.**

**Logic:**
- If `base_prob > threshold`: Push toward 1.0
- If `base_prob < threshold`: Push toward 0.0
- If `base_prob ≈ threshold`: Minimal change

**Best for:**
- Events with strengthening evidence
- When signals should become more certain over time

**Problem:** Can over-amplify weak signals

**Parameters:**
- `amplification_power` (default 1.5): Amplification rate
- `threshold` (default 0.5): Neutral point

**Example:** Election with clear leader emerging

```python
adjuster = TemporalAdjuster(
    method='trend_amplification',
    total_days=365,
    amplification_power=1.5,
    threshold=0.5
)

# Strong signal amplifies
adjusted, _ = adjuster.adjust_probability(0.65, current_date, deadline)
# 0.65 → 0.80 (amplified toward 1.0)

# Weak signal decays
adjusted, _ = adjuster.adjust_probability(0.35, current_date, deadline)
# 0.35 → 0.21 (pushed toward 0.0)
```

---

### 5. Confidence Convergence (`confidence_convergence`)

**Converges toward 0 or 1 based on signal zones.**

**Logic:**
- Strong signals (`>upper_threshold`): Converge to 1.0
- Weak signals (`<lower_threshold`): Converge to 0.0
- Uncertain signals (between): Minimal adjustment

**Best for:**
- Binary events where uncertainty should decrease
- When you have clear confidence zones

**Problem:** Doesn't adjust uncertain signals

**Parameters:**
- `convergence_power` (default 2.0): Speed of convergence
- `lower_threshold` (default 0.3): Below this → 0
- `upper_threshold` (default 0.7): Above this → 1

**Example:** Merger approval with clear signals

```python
adjuster = TemporalAdjuster(
    method='confidence_convergence',
    total_days=365,
    convergence_power=2.0,
    lower_threshold=0.3,
    upper_threshold=0.7
)

# Very likely
adjusted, _ = adjuster.adjust_probability(0.85, current_date, deadline)
# 0.85 → 0.92 (converges to 1.0)

# Very unlikely
adjusted, _ = adjuster.adjust_probability(0.15, current_date, deadline)
# 0.15 → 0.08 (converges to 0.0)

# Uncertain (no change)
adjusted, _ = adjuster.adjust_probability(0.50, current_date, deadline)
# 0.50 → 0.50 (unchanged)
```

---

### 6. Adaptive ⭐ (RECOMMENDED)

**Smart, context-aware adjustment that handles all cases.**

**Logic:**
- **Strong signals** (`>upper_threshold`): Amplify toward 1.0
- **Weak signals** (`<lower_threshold`): Decay toward 0.0
- **Uncertain signals** (between): Gentle decay

**Best for:**
- Most real-world forecasts
- When behavior should depend on signal strength
- Binary events with varying confidence

**Why it's best:** Matches human intuition about how forecasts should evolve

**Parameters:**
- `decay_power` (default 1.5): Decay rate for weak signals
- `amplification_power` (default 1.5): Amplification rate for strong signals
- `lower_threshold` (default 0.4): Below this → decay
- `upper_threshold` (default 0.6): Above this → amplify

**Example:** US Recession forecast

```python
adjuster = TemporalAdjuster(
    method='adaptive',
    total_days=365,
    decay_power=1.5,
    amplification_power=1.5,
    lower_threshold=0.4,
    upper_threshold=0.6
)

# Strong signal (amplifies)
adjusted, _ = adjuster.adjust_probability(0.75, current_date, deadline)
# 0.75 → 0.79 (amplified)

# Weak signal (decays)
adjusted, _ = adjuster.adjust_probability(0.25, current_date, deadline)
# 0.25 → 0.01 (decayed)

# Uncertain signal (gentle decay)
adjusted, _ = adjuster.adjust_probability(0.49, current_date, deadline)
# 0.49 → 0.09 (gentle decay)
```

---

## Comparison Table

| Method | Weak Signal (20%) | Uncertain (50%) | Strong Signal (80%) | Best Use Case |
|--------|-------------------|-----------------|---------------------|---------------|
| **none** | 20% → 20% | 50% → 50% | 80% → 80% | No time effect |
| **simple_decay** | 20% → 1% | 50% → 2% | 80% → 3% | Always unlikely |
| **threshold_decay** | 20% → 1% | 50% → 50% | 80% → 80% | Protect strong signals |
| **trend_amplification** | 20% → 0% | 50% → 50% | 80% → 100% | Amplify trends |
| **confidence_convergence** | 20% → 10% | 50% → 50% | 80% → 92% | Clear zones |
| **adaptive** ⭐ | 20% → 1% | 50% → 9% | 80% → 84% | Context-aware |

*With 38 days remaining out of 365 total*

---

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

---

## Decision Guide

### Choose based on your forecast type:

**1. Binary event, weak signals (recession unlikely)**
→ Use `adaptive` or `simple_decay`

**2. Binary event, strong signals (recession likely)**
→ Use `adaptive` or `trend_amplification`

**3. Binary event, uncertain signals**
→ Use `adaptive` (gentle decay)

**4. Want to preserve high probabilities**
→ Use `threshold_decay`

**5. Want trends to strengthen**
→ Use `trend_amplification` or `adaptive`

**6. No time effect desired**
→ Use `none`

**7. Not sure / general purpose**
→ Use `adaptive` ⭐

---

## Integration with Forecast Models

### In your model class:

```python
from lib.temporal_adjustment import TemporalAdjuster

class MyForecastModel:
    def __init__(self):
        self.temporal_adjuster = TemporalAdjuster(
            method='adaptive',
            total_days=365,
            lower_threshold=0.4,
            upper_threshold=0.6
        )
    
    def calculate_probability(self, apply_temporal=True):
        # Calculate base probability
        base_prob = self._calculate_base_probability()
        
        if not apply_temporal:
            return base_prob
        
        # Apply temporal adjustment
        adjusted_prob, metadata = self.temporal_adjuster.adjust_probability(
            base_prob,
            datetime.now(),
            self.deadline
        )
        
        return adjusted_prob
```

---

## Advanced: Custom Adjustment Functions

You can create custom adjustment functions:

```python
def my_custom_adjustment(base_probability, days_remaining, **params):
    """Custom adjustment logic."""
    # Your logic here
    return adjusted_probability

# Use it
from lib.temporal_adjustment import TemporalAdjuster

# Add to available methods
TemporalAdjuster.METHODS['custom'] = my_custom_adjustment

# Use it
adjuster = TemporalAdjuster(method='custom', my_param=123)
```

---

## Testing

Run the demo script to see all methods in action:

```bash
python demo_temporal_adjustment_methods.py
```

This shows:
- How each method behaves with different probability levels
- Time evolution of probabilities
- Recommendations for your specific case

---

## Summary

**For most forecasts, use `adaptive` method** ⭐

It intelligently:
- Decays weak signals (unlikely events become more unlikely)
- Amplifies strong signals (likely events become more certain)
- Handles uncertain signals appropriately (gentle adjustment)

This matches human intuition and handles the full spectrum of forecast scenarios.
