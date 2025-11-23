# Run Forecast V2 - Decay Method Comparison Feature

## What's New

The `run_forecast_v2.py` script now automatically compares all three temporal decay methods side-by-side!

## Usage

### Default Behavior (with comparison)
```bash
python forecasts/us_recession_2025/run_forecast_v2.py
```

This will show:
1. Your forecast with the default theta decay method
2. **NEW:** A comparison table showing all three methods

### Skip the Comparison
```bash
python forecasts/us_recession_2025/run_forecast_v2.py --no-compare
```

### Other Options
```bash
# No history, no comparison
python forecasts/us_recession_2025/run_forecast_v2.py --no-history --no-compare

# Show more history
python forecasts/us_recession_2025/run_forecast_v2.py --history-limit 20
```

## Example Output

```
TEMPORAL DECAY METHOD COMPARISON
--------------------------------

Comparing all three decay methods with 38 days remaining:

  Method          | Adjusted Prob | Change      | % Change  | Notes
  ---------------------------------------------------------------------------
  Theta (1.5) ⭐  |         1.64% |     -47.18% |    -96.6% | DEFAULT, no threshold
  Exponential     |        48.82% |      +0.00% |     +0.0% | threshold=0.4, NO DECAY
  Sigmoid         |        25.21% |     -23.61% |    -48.4% | smooth S-curve

  Base Probability (no decay): 48.82%

  💡 Interpretation:
     - Theta decay is most aggressive with 38 days left
     - Exponential only applies below threshold (40%)
     - Sigmoid provides moderate, smooth decay
     - All methods reflect time constraint: less time = lower probability
```

## What It Shows

For each decay method, you see:
- **Adjusted Probability**: Final probability after temporal adjustment
- **Change**: Absolute change from base probability (in percentage points)
- **% Change**: Relative change from base probability
- **Notes**: Key characteristics of each method

## Why This Is Useful

1. **Understand the impact**: See exactly how much each method affects your forecast
2. **Make informed choices**: Compare methods to decide which fits your use case
3. **Validate behavior**: Ensure the decay is working as expected
4. **Educational**: Learn how different decay approaches behave

## The Three Methods

### 1. Theta (DEFAULT) ⭐
- **No threshold** - applies to all probabilities
- **Accelerates** as deadline approaches (power law)
- **Most aggressive** with few days remaining
- **Best for**: Most use cases, especially when time matters

### 2. Exponential
- **Has threshold** (default 0.4 = 40%)
- Only applies below threshold
- **Minimal effect** near deadline
- **Best for**: Preserving high-risk signals

### 3. Sigmoid
- **No threshold** - smooth S-curve
- **Moderate decay** across all probabilities
- **Best for**: Gradual, smooth transitions

## Technical Details

The comparison function:
- Runs the model three times with different decay methods
- Uses the same base probability for fair comparison
- Calculates both absolute and relative changes
- Handles errors gracefully if any method fails

## Performance Note

Running the comparison adds ~2-3 seconds to execution time since it calculates the forecast three times. Use `--no-compare` if you need faster execution.
