# Theta Decay Implementation Summary

## What Changed

Added a new **theta decay** method for temporal probability adjustment, inspired by options trading theta decay. This is now the **default method** for v2 forecasts.

## Why Theta Decay?

The previous exponential decay method had a hard threshold (default 0.4), which meant:
- Probabilities above 40% received NO temporal adjustment
- This felt arbitrary and didn't match intuition about how time should affect probabilities

Theta decay solves this by:
- ✅ **No threshold** - applies to ALL probabilities
- ✅ **Accelerates near expiration** - like options theta decay
- ✅ **More intuitive** - mirrors prediction market behavior
- ✅ **Configurable aggressiveness** - adjust decay_power parameter

## How It Works

Theta decay uses a power law formula:

```
time_ratio = days_remaining / total_days
time_value_remaining = time_ratio^decay_power
adjusted_prob = base_prob * time_value_remaining
```

### Decay Power Parameter

- **power = 1.0**: Linear decay (least aggressive)
- **power = 1.5**: Moderate decay ⭐ **DEFAULT**
- **power = 2.0**: Quadratic decay (like options)
- **power = 3.0**: Cubic decay (very aggressive)

## Example: Your Current Forecast

With 38 days remaining and base probability of 48.82%:

| Method | Power | Adjusted Probability | Change |
|--------|-------|---------------------|--------|
| Theta | 1.0 | 5.08% | -43.74% |
| **Theta** | **1.5** | **1.64%** | **-47.18%** ⭐ |
| Theta | 2.0 | 0.53% | -48.29% |
| Exponential (threshold=0.4) | N/A | 48.82% | 0% (no decay) |
| Exponential (threshold=0.5) | N/A | 48.17% | -0.65% |

## Configuration

### Default Settings (config_v2.py)

```python
TEMPORAL_DECAY_CONFIG = {
    'method': 'theta',           # NEW DEFAULT
    'theta_total_days': 365,
    'theta_decay_power': 1.5,    # Moderate aggressiveness
    'enabled': True
}
```

### Adjusting Parameters

You can customize theta decay in three ways:

1. **Change defaults in config_v2.py**
2. **Pass parameters when running:**
   ```python
   model.calculate_probability(params={
       'theta_decay_power': 2.0  # More aggressive
   })
   ```
3. **Switch methods:**
   ```python
   model.calculate_probability(params={
       'decay_method': 'exponential',  # Use old method
       'decay_threshold': 0.5
   })
   ```

## All Available Methods

### 1. Theta Decay (NEW, DEFAULT) ⭐
- **Pros**: No threshold, accelerates naturally, intuitive
- **Cons**: Can be aggressive with few days remaining
- **Best for**: Most use cases, especially when you want time to matter

### 2. Exponential Decay
- **Pros**: Preserves high-risk signals above threshold
- **Cons**: Arbitrary threshold, minimal effect near deadline
- **Best for**: When you want to protect high probabilities from decay

### 3. Sigmoid Decay
- **Pros**: Smooth S-curve transition
- **Cons**: Less intuitive parameters
- **Best for**: When you want gradual, smooth transitions

## Testing

Added comprehensive tests for theta decay:
- Basic functionality
- Boundary conditions (0 days, 365 days)
- Monotonic decrease verification
- No threshold behavior
- Parameter validation
- Integration with TemporalAdjuster class

All 38 temporal tests passing ✅

## Files Modified

1. `forecasts/us_recession_2025/temporal.py` - Added `theta_decay_adjustment()` function
2. `forecasts/us_recession_2025/config_v2.py` - Updated defaults and parameter schemas
3. `forecasts/us_recession_2025/model_v2.py` - Added theta method support
4. `forecasts/us_recession_2025/tests/test_temporal.py` - Added theta decay tests

## Migration Notes

Existing forecasts will automatically use theta decay with power=1.5. If you prefer the old behavior:

```python
# Revert to exponential with no threshold effect
params = {
    'decay_method': 'exponential',
    'decay_threshold': 1.0  # Always apply decay
}
```

## Recommendation

Keep the default theta decay with power=1.5. It provides:
- Reasonable time adjustment without being too aggressive
- No arbitrary thresholds
- Behavior that matches options trading intuition
- Easy to tune if needed (adjust decay_power)
