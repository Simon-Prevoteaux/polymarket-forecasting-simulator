# Running the Jupyter Notebooks

## Quick Start

### 1. Activate Virtual Environment

```bash
# From project root
source venv/bin/activate
```

### 2. Start Jupyter Notebook

```bash
# Navigate to notebooks directory
cd forecasts/us_recession_2025/notebooks

# Start Jupyter Notebook
jupyter notebook
```

This will open Jupyter in your browser at `http://localhost:8888`

### 3. Open and Run the Notebook

1. Click on `01_data_exploration.ipynb` in the Jupyter file browser
2. Run cells one by one using `Shift + Enter`
3. Or run all cells: `Cell` → `Run All` from the menu

## Alternative: JupyterLab

For a more modern interface:

```bash
cd forecasts/us_recession_2025/notebooks
jupyter lab
```

## Important Notes

### FRED API Key Required

The notebook fetches data from FRED (Federal Reserve Economic Data). You need a free API key:

1. Sign up at: https://fred.stlouisfed.org/docs/api/api_key.html
2. Add your key to `.env` file in project root:
   ```
   FRED_API_KEY=your_key_here
   ```

### First Run May Take Time

The first execution will:
- Fetch 5 years of data for 12 economic indicators
- This may take 1-2 minutes depending on your connection
- Subsequent runs will be faster if data is cached

### Expected Output

The notebook will generate:
- Time series plots for all indicators
- Statistical summary tables
- Correlation heatmap
- Distribution plots
- Missing data visualizations
- Data quality reports

## Troubleshooting

### ModuleNotFoundError

If you see import errors:
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Verify packages are installed
pip list | grep -E "jupyter|matplotlib|seaborn"
```

### FRED API Errors

If you see "API key not found" or rate limit errors:
- Check your `.env` file has `FRED_API_KEY=...`
- Verify the key is valid at https://fred.stlouisfed.org/
- Wait a few minutes if you hit rate limits

### Path Issues

If imports fail with "No module named 'forecasts'":
- The notebook automatically adds project root to path
- Verify you're running from the notebooks directory
- Check that the path calculation in cell 2 is correct

## Running from Command Line

You can also execute notebooks from command line:

```bash
# Install nbconvert if needed
pip install nbconvert

# Execute notebook
jupyter nbconvert --to notebook --execute 01_data_exploration.ipynb
```

## Next Steps

After running `01_data_exploration.ipynb`, you can proceed to:
- `02_indicator_analysis.ipynb` - Deep dive into indicators (coming soon)
- `03_model_comparison.ipynb` - Compare v1 vs v2 models (coming soon)
- `04_backtesting_results.ipynb` - Historical performance (coming soon)
- `05_temporal_calibration.ipynb` - Calibrate decay parameters (coming soon)
