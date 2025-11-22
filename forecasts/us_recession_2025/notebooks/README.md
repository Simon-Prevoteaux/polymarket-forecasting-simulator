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

## Troubleshooting

**Import Errors**: Ensure virtual environment is activated and project root is in Python path

**Missing Data**: Check FRED API key in `.env` file

**Slow Execution**: Consider reducing `lookback_days` for faster iteration during development

**Memory Issues**: Close other notebooks when running memory-intensive analyses

## Contributing

When adding new notebooks:
1. Follow the naming convention: `##_descriptive_name.ipynb`
2. Include markdown cells explaining methodology
3. Use consistent styling and color schemes
4. Document all assumptions and limitations
5. Update this README with notebook description
