# US Recession 2025 Forecast V2 - Jupyter Notebooks

This directory contains Jupyter notebooks for data exploration, model analysis, and backtesting visualization for the US Recession 2025 Forecast V2.

## Notebooks Overview

### 01_data_exploration.ipynb
**Purpose**: Explore and visualize economic indicators

**Contents**:
- Load 5 years of historical economic data
- Time series plots for each indicator
- Statistical summaries (mean, std, min, max)
- Correlation analysis and heatmap
- Missing data analysis
- Historical recession period visualization

**When to use**: Initial data exploration, understanding indicator relationships, identifying data quality issues

---

### 02_indicator_analysis.ipynb
**Purpose**: Deep dive into individual indicators and their predictive power

**Contents**:
- Individual indicator analysis
- Indicator behavior during historical recessions
- Lead/lag relationship analysis
- Signal quality assessment (true positive/false positive rates)
- Optimal threshold identification

**When to use**: Understanding which indicators are most predictive, calibrating indicator thresholds

---

### 03_model_comparison.ipynb
**Purpose**: Compare v1 and v2 model predictions

**Contents**:
- Side-by-side v1 vs v2 probability comparison
- V2 probability breakdown visualization
- Parameter sensitivity analysis
- Feature importance visualization
- Weight optimization experiments

**When to use**: Evaluating v2 improvements over v1, understanding model behavior, parameter tuning

---

### 04_backtesting_results.ipynb
**Purpose**: Visualize historical model performance

**Contents**:
- Historical probability evolution over time
- V1 vs v2 performance comparison
- Brier score decomposition
- Calibration plots
- Forecast error analysis
- Performance metrics dashboard

**When to use**: Evaluating model accuracy, identifying periods of over/under-prediction, model validation

---

### 05_temporal_calibration.ipynb
**Purpose**: Calibrate and visualize temporal decay functions

**Contents**:
- Exponential decay curve visualization
- Sigmoid decay curve visualization
- Parameter sensitivity analysis
- Empirical calibration from historical data
- Brier score optimization
- Validation on held-out data

**When to use**: Calibrating temporal decay parameters, understanding time-to-event effects, optimizing decay functions

---

## Execution Order

For first-time analysis, execute notebooks in order:

1. **01_data_exploration.ipynb** - Understand the data
2. **02_indicator_analysis.ipynb** - Analyze individual indicators
3. **03_model_comparison.ipynb** - Compare model versions
4. **04_backtesting_results.ipynb** - Evaluate historical performance
5. **05_temporal_calibration.ipynb** - Calibrate temporal decay

## Setup

### Prerequisites

Ensure you have the following installed:
- Python 3.10+
- Jupyter Notebook or JupyterLab
- All project dependencies from `requirements.txt`

### Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Install Jupyter if not already installed
pip install jupyter

# Install additional notebook dependencies
pip install matplotlib seaborn
```

### Running Notebooks

```bash
# From project root
cd forecasts/us_recession_2025/notebooks

# Start Jupyter
jupyter notebook

# Or use JupyterLab
jupyter lab
```

## Common Patterns

### Data Loading

All notebooks use consistent data loading:

```python
import sys
sys.path.append('../../../')  # Add project root to path

from forecasts.us_recession_2025.data_v2 import fetch_economic_indicators_v2
from forecasts.us_recession_2025 import RecessionModel, RecessionModelV2

# Fetch 5 years of data
indicators = fetch_economic_indicators_v2(lookback_days=1825)
```

### Visualization Style

Consistent styling across all notebooks:

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)

# Color scheme
RECESSION_COLOR = '#ff6b6b'
V1_COLOR = '#4ecdc4'
V2_COLOR = '#45b7d1'
```

### Reproducibility

Set random seeds for reproducible results:

```python
import numpy as np
import random

np.random.seed(42)
random.seed(42)
```

## Data Sources

All notebooks use data from:
- Federal Reserve Economic Data (FRED)
- US Treasury
- Bureau of Labor Statistics
- Bureau of Economic Analysis
- University of Michigan
- ISM Manufacturing
- CBOE

## Notes

- Notebooks are designed to be self-contained with markdown explanations
- Each notebook includes error handling for missing data
- Visualizations are optimized for both screen and print
- All notebooks can be executed independently after initial data loading
- Historical recession periods are marked consistently across visualizations

## Expected Outputs

### 01_data_exploration.ipynb

**Outputs**:
- Time series plots for all 12 economic indicators
- Correlation heatmap showing indicator relationships
- Statistical summary tables (mean, std, min, max, quartiles)
- Missing data visualization
- Historical recession period markers

**Key Insights**:
- Which indicators are most correlated
- Data quality and availability issues
- Historical patterns during recessions
- Indicator volatility and trends

### 02_indicator_analysis.ipynb

**Outputs**:
- Individual indicator deep dives with recession overlays
- Lead/lag analysis showing predictive timing
- Signal quality metrics (true positive/false positive rates)
- Optimal threshold identification
- Indicator ranking by predictive power

**Key Insights**:
- Which indicators are most predictive
- How far in advance indicators signal recessions
- Optimal thresholds for each indicator
- False alarm rates

### 03_model_comparison.ipynb

**Outputs**:
- Side-by-side v1 vs v2 probability comparison
- Probability breakdown visualization (base vs adjusted)
- Parameter sensitivity heatmaps
- Feature importance bar charts
- Weight optimization results

**Key Insights**:
- How v2 improves over v1
- Which parameters have most impact
- Feature contribution to final probability
- Optimal parameter combinations

### 04_backtesting_results.ipynb

**Outputs**:
- Historical probability evolution line charts
- V1 vs v2 performance comparison
- Brier score decomposition
- Calibration plots
- Error analysis by time period

**Key Insights**:
- Model accuracy over time
- V2 performance improvements
- Calibration quality
- Periods of over/under-prediction

### 05_temporal_calibration.ipynb

**Outputs**:
- Decay curve visualizations (exponential and sigmoid)
- Parameter sensitivity analysis
- Brier score optimization results
- Validation on held-out data
- Recommended parameter values

**Key Insights**:
- Optimal decay parameters
- Robustness across parameter ranges
- Impact of temporal adjustment
- Calibration quality

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'forecasts'`

**Solution**: Ensure project root is in Python path
```python
import sys
sys.path.append('../../../')  # Add project root
```

### Missing Data

**Problem**: `DataFetchError: FRED API key is required`

**Solution**: Check FRED API key in `.env` file
```bash
# Check if .env exists
cat ../../../.env

# Should contain:
# FRED_API_KEY=your_api_key_here
```

### Slow Execution

**Problem**: Notebooks take too long to execute

**Solutions**:
1. Reduce `lookback_days` for faster iteration:
   ```python
   indicators = fetch_economic_indicators_v2(lookback_days=365)  # Instead of 1825
   ```

2. Use cached data when available:
   ```python
   from lib.data_fetcher import get_cached_data
   cached = get_cached_data('indicators_5y')
   if cached:
       indicators = cached
   else:
       indicators = fetch_economic_indicators_v2(lookback_days=1825)
   ```

3. Close other notebooks to free memory

### Memory Issues

**Problem**: Kernel crashes or runs out of memory

**Solutions**:
1. Close other notebooks
2. Restart kernel and clear outputs: `Kernel > Restart & Clear Output`
3. Reduce data size:
   ```python
   # Sample data instead of using all
   df_sample = df.sample(frac=0.5, random_state=42)
   ```

### Visualization Issues

**Problem**: Plots don't display or look incorrect

**Solutions**:
1. Ensure matplotlib backend is set:
   ```python
   %matplotlib inline
   import matplotlib.pyplot as plt
   ```

2. Increase figure size for better visibility:
   ```python
   plt.rcParams['figure.figsize'] = (14, 8)
   ```

3. Clear previous plots:
   ```python
   plt.clf()  # Clear current figure
   plt.close('all')  # Close all figures
   ```

### API Rate Limiting

**Problem**: `DataFetchError: FRED API rate limit exceeded`

**Solutions**:
1. Use cached data when available
2. Reduce frequency of API calls
3. Wait and retry (FRED limit: 120 requests/minute)
4. Use `time.sleep()` between requests:
   ```python
   import time
   time.sleep(1)  # Wait 1 second between requests
   ```

## Advanced Usage

### Custom Analysis

Add your own analysis cells to notebooks:

```python
# Example: Analyze specific indicator
import pandas as pd
import matplotlib.pyplot as plt

# Get unemployment data
unemployment = indicators['unemployment']
dates = pd.to_datetime(indicators['timestamps']['unemployment'])

# Calculate 6-month change
df = pd.DataFrame({'date': dates, 'value': unemployment})
df = df.sort_values('date')
df['change_6m'] = df['value'].diff(periods=26)  # ~6 months of weekly data

# Plot
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['change_6m'])
plt.axhline(y=0, color='gray', linestyle='--')
plt.xlabel('Date')
plt.ylabel('6-Month Change in Unemployment Rate')
plt.title('Unemployment Rate 6-Month Change')
plt.grid(True, alpha=0.3)
plt.show()
```

### Exporting Results

Save analysis results for later use:

```python
import json
import pandas as pd

# Export to JSON
results = {
    'brier_score': 0.135,
    'calibration_slope': 1.02,
    'optimal_params': {'decay_rate': 0.02, 'threshold': 0.4}
}

with open('analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Export to CSV
df = pd.DataFrame(backtest_results)
df.to_csv('backtest_results.csv', index=False)

# Export plots
plt.savefig('probability_evolution.png', dpi=300, bbox_inches='tight')
```

### Automated Execution

Run notebooks programmatically:

```bash
# Install nbconvert
pip install nbconvert

# Execute notebook and save output
jupyter nbconvert --to notebook --execute 01_data_exploration.ipynb \
    --output 01_data_exploration_executed.ipynb

# Execute all notebooks
for notebook in *.ipynb; do
    jupyter nbconvert --to notebook --execute "$notebook" \
        --output "executed_${notebook}"
done
```

### Parameterized Notebooks

Use papermill for parameterized execution:

```bash
# Install papermill
pip install papermill

# Execute with parameters
papermill 03_model_comparison.ipynb output.ipynb \
    -p decay_rate 0.025 \
    -p threshold 0.35
```

## Best Practices

### Code Organization

1. **Import all libraries at the top**:
   ```python
   import sys
   sys.path.append('../../../')
   
   import pandas as pd
   import numpy as np
   import matplotlib.pyplot as plt
   import seaborn as sns
   
   from forecasts.us_recession_2025 import RecessionModel, RecessionModelV2
   ```

2. **Set random seeds for reproducibility**:
   ```python
   np.random.seed(42)
   random.seed(42)
   ```

3. **Use consistent styling**:
   ```python
   sns.set_style('whitegrid')
   plt.rcParams['figure.figsize'] = (12, 6)
   ```

### Documentation

1. **Add markdown cells explaining each section**
2. **Document assumptions and limitations**
3. **Include interpretation of results**
4. **Reference related notebooks and documentation**

### Version Control

1. **Clear outputs before committing**:
   ```bash
   jupyter nbconvert --clear-output --inplace *.ipynb
   ```

2. **Use .gitignore for large outputs**:
   ```
   *.ipynb_checkpoints
   *_executed.ipynb
   ```

3. **Document notebook versions in README**

## Contributing

When adding new notebooks:
1. Follow the naming convention: `##_descriptive_name.ipynb`
2. Include markdown cells explaining methodology
3. Use consistent styling and color schemes
4. Document all assumptions and limitations
5. Update this README with notebook description
