# Polymarket Forecasting Simulator

A modular Python application for building and managing probabilistic forecasts for prediction markets. Build individual forecasting models, visualize results through a web interface, and adjust parameters to simulate different scenarios.

## Overview

The Polymarket Forecasting Simulator follows Nate Silver's approach to real-world modeling with modular forecast components, statistical rigor, and a library of reusable utilities. Each forecast problem lives in its own directory with dedicated scripts, data, and database tables.

## Features

- **Modular Architecture**: Each forecast is self-contained in its own directory
- **Dynamic Discovery**: Web interface automatically detects and displays all forecast models
- **Parameter Simulation**: Adjust model parameters in real-time to explore scenarios
- **Local Persistence**: SQLite database stores historical forecasts and results
- **Reusable Utilities**: Shared library for data fetching, probability calculations, and database operations
- **Property-Based Testing**: Comprehensive testing using Hypothesis for correctness guarantees
- **Historical Backtesting**: Evaluate model performance on historical data with comprehensive metrics
- **Temporal Decay Modeling**: Time-aware probability adjustments as deadlines approach
- **Enhanced Feature Engineering**: Derived features including rate-of-change, moving averages, and volatility
- **Jupyter Notebook Suite**: Interactive data exploration and model analysis workflows
- **Model Versioning**: Side-by-side comparison of model versions (v1 vs v2)

## US Recession Forecast V2 Highlights

The US Recession 2025 forecast now includes a comprehensive v2 model with significant enhancements:

### Enhanced Data & Features
- **12 Economic Indicators**: Added credit spreads (BAA10Y), housing starts (HOUST), manufacturing PMI, retail sales (RSXFS), oil prices (DCOILWTICO), and VIX volatility
- **Feature Engineering**: Rate-of-change (30d, 90d, 180d), moving averages (30d, 90d), and volatility measures
- **Missing Data Handling**: Graceful handling with forward-fill and neutral defaults

### Temporal Decay Modeling
- **Time-Aware Adjustments**: Probabilities adjust based on time remaining until December 31, 2025
- **Multiple Decay Functions**: Exponential and sigmoid decay options
- **Calibrated Parameters**: Empirically tuned using historical recession data
- **Dual Probability Display**: Shows both base probability and temporally-adjusted probability

### Historical Backtesting
- **Performance Evaluation**: Run model on historical dates to assess accuracy
- **Comprehensive Metrics**: Brier score, calibration statistics, discrimination metrics
- **Model Comparison**: Side-by-side v1 vs v2 performance analysis
- **Dedicated Database**: Separate table for backtest results with full metadata

### Interactive Analysis
- **5 Jupyter Notebooks**: Data exploration, indicator analysis, model comparison, backtesting results, temporal calibration
- **Visualization Suite**: Time series plots, correlation heatmaps, calibration curves, decay projections
- **Parameter Tuning**: Interactive parameter sensitivity analysis and optimization

### Web Interface Enhancements
- **Temporal Decay Visualization**: Chart showing probability evolution as deadline approaches
- **Probability Breakdown**: Detailed view of base vs adjusted probabilities
- **Days Remaining Display**: Clear countdown to forecast deadline
- **Metadata Display**: Decay method, rate, and adjustment details

See `forecasts/us_recession_2025/README.md` for complete v2 documentation.

## Project Structure

```
polymarket-forecasting-simulator/
├── lib/                          # Shared utilities and reusable code
│   ├── __init__.py
│   ├── data_fetcher.py          # Data retrieval utilities
│   ├── probability.py            # Probability calculation helpers
│   ├── database.py               # SQLite operations
│   └── utils.py                  # General utilities
├── forecasts/                    # Individual forecast models
│   ├── __init__.py
│   └── us_recession_2025/       # Example: US recession forecast
│       ├── __init__.py
│       ├── model.py             # Main forecast logic
│       ├── data.py              # Data collection
│       ├── config.py            # Model parameters
│       └── README.md            # Documentation
├── web/                          # Flask web interface
│   ├── __init__.py
│   ├── app.py                   # Flask application
│   ├── templates/               # HTML templates
│   └── static/                  # CSS and JavaScript
├── data/                         # Local data storage
│   └── forecasts.db             # SQLite database
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- FRED API key (free registration at https://fred.stlouisfed.org/docs/api/api_key.html)

### Setup

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up FRED API key**:

The application requires a FRED API key to fetch economic data. You have two options:

**Option A: Using .env file (recommended)**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your FRED API key
# Get a free API key at https://fred.stlouisfed.org/docs/api/api_key.html
```

Your `.env` file should contain:
```
FRED_API_KEY=your_api_key_here
```

**Option B: Using environment variable**
```bash
export FRED_API_KEY=your_api_key_here  # On Windows: set FRED_API_KEY=your_api_key_here
```

The application will automatically load environment variables from the `.env` file using python-dotenv.

5. **Initialize the database** (optional - happens automatically on first run):
```bash
python -c "from lib.database import initialize_metadata_table; initialize_metadata_table()"
```

## Usage

### Running the Web Interface

Start the Flask web application to view and interact with forecasts:

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the web application
python -m web.app
```

Then open your browser to `http://localhost:5000`

The web interface provides:
- List of all available forecasts
- Current probability for each forecast
- Historical probability charts
- Parameter adjustment controls
- Data source information

### Running Forecasts Standalone

Each forecast can be run independently without the web interface:

```bash
# Run the US recession forecast
python forecasts/us_recession_2025/run_forecast.py

# Run the election forecast (demo)
python forecasts/election_2028/run_forecast.py
```

Standalone scripts display:
- Current probability calculation
- All indicator values with timestamps
- Historical forecast trends
- Interpretation of the probability

### Adding a New Forecast Model

Follow these steps to add a new forecast to the system:

#### 1. Create Directory Structure

```bash
mkdir -p forecasts/your_forecast_name/tests
cd forecasts/your_forecast_name
```

#### 2. Create Required Files

Create the following files in your forecast directory:

**`__init__.py`** - Package initialization:
```python
"""Your Forecast Name - Brief description."""

from .model import YourModel

__all__ = ['YourModel']
```

**`config.py`** - Model parameters and configuration:
```python
"""Configuration for Your Forecast model."""

from lib.utils import ParameterSchema

# Data sources (if using external APIs)
DATA_SOURCES = {
    'indicator1': 'API_SERIES_ID_1',
    'indicator2': 'API_SERIES_ID_2'
}

# Default parameter values
DEFAULT_PARAMS = {
    'weight1': 0.5,
    'weight2': 0.5,
    'lookback_days': 365
}

# Parameter schemas for validation
PARAMETER_SCHEMAS = {
    'weight1': ParameterSchema(
        name='weight1',
        type='float',
        default=0.5,
        min_value=0.0,
        max_value=1.0,
        description='Weight for first indicator'
    ),
    'weight2': ParameterSchema(
        name='weight2',
        type='float',
        default=0.5,
        min_value=0.0,
        max_value=1.0,
        description='Weight for second indicator'
    )
}
```

**`data.py`** - Data fetching logic:
```python
"""Data collection functions for Your Forecast model."""

import logging
from typing import Dict, Any
from lib.data_fetcher import fetch_fred_data, DataFetchError

logger = logging.getLogger(__name__)

def fetch_your_data() -> Dict[str, Any]:
    """
    Fetch data needed for your forecast.
    
    Returns:
        Dictionary containing indicator data
    
    Raises:
        Exception: If data cannot be fetched
    """
    # Implement your data fetching logic here
    data = {}
    # ... fetch data from APIs, files, etc.
    return data
```

**`model.py`** - Main forecast logic (implements `ForecastModel` interface):
```python
"""Your Forecast Model implementation."""

import logging
from datetime import datetime
from typing import Dict, Optional
from forecasts import ForecastModel
from lib.probability import normalize_probability, combine_probabilities
from lib.database import create_forecast_table, save_forecast_result
from lib.utils import validate_parameters
from .config import DEFAULT_PARAMS, PARAMETER_SCHEMAS
from .data import fetch_your_data

logger = logging.getLogger(__name__)

class YourModel(ForecastModel):
    """
    Forecast model for [describe what this predicts].
    
    [Detailed description of methodology]
    """
    
    def __init__(self):
        """Initialize the model and create database table."""
        self.name = "your_forecast_name"
        self.display_name = "Your Forecast Name"
        self.description = "Description of what this forecast predicts"
        self._last_updated = None
        
        # Create database table
        schema = {
            'indicator1_value': 'REAL',
            'indicator2_value': 'REAL'
        }
        create_forecast_table(self.name, schema)
    
    def get_name(self) -> str:
        """Return human-readable forecast name."""
        return self.display_name
    
    def get_description(self) -> str:
        """Return forecast description."""
        return self.description
    
    def get_parameters(self) -> Dict:
        """Return adjustable parameters with metadata."""
        return {
            name: {
                'name': schema.name,
                'type': schema.type,
                'default': schema.default,
                'min_value': schema.min_value,
                'max_value': schema.max_value,
                'description': schema.description
            }
            for name, schema in PARAMETER_SCHEMAS.items()
        }
    
    def get_last_updated(self) -> datetime:
        """Return timestamp of last data update."""
        return self._last_updated or datetime.now()
    
    def get_data_sources(self) -> list:
        """Return list of data sources used by this forecast."""
        return [
            'Source 1 - Description',
            'Source 2 - Description'
        ]
    
    def calculate_probability(self, params: Optional[Dict] = None) -> float:
        """
        Calculate forecast probability.
        
        Args:
            params: Optional parameter overrides
        
        Returns:
            Probability (0-1)
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Use defaults if no params provided
        if params is None:
            params = DEFAULT_PARAMS.copy()
        else:
            merged_params = DEFAULT_PARAMS.copy()
            merged_params.update(params)
            params = merged_params
        
        # Validate parameters
        errors = validate_parameters(params, PARAMETER_SCHEMAS)
        if errors:
            error_msg = "; ".join([f"{k}: {v}" for k, v in errors.items()])
            raise ValueError(f"Invalid parameters: {error_msg}")
        
        # Fetch data
        data = fetch_your_data()
        self._last_updated = datetime.now()
        
        # Calculate probability
        # ... your calculation logic here ...
        probability = 0.5  # Replace with actual calculation
        
        # Ensure valid range
        probability = normalize_probability(probability)
        
        # Save to database
        save_forecast_result(
            forecast_name=self.name,
            probability=probability,
            parameters=params,
            data_snapshot=data
        )
        
        return probability
```

**`run_forecast.py`** - Standalone execution script:
```python
"""Standalone script to run Your Forecast model."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from forecasts.your_forecast_name.model import YourModel
from lib.logging_config import setup_logging

def main():
    """Run the forecast and display results."""
    # Set up logging
    logger = setup_logging('your_forecast_name')
    
    logger.info("Starting Your Forecast calculation...")
    
    # Create model and calculate probability
    model = YourModel()
    probability = model.calculate_probability()
    
    # Display results
    print(f"\n{'='*60}")
    print(f"  {model.get_name()}")
    print(f"{'='*60}")
    print(f"\nCurrent Probability: {probability:.2%}")
    print(f"Last Updated: {model.get_last_updated()}")
    print(f"\n{'='*60}\n")

if __name__ == '__main__':
    main()
```

**`README.md`** - Documentation for your forecast:
```markdown
# Your Forecast Name

## Overview

[Describe what this forecast predicts and why it's useful]

## Methodology

[Explain your forecasting approach]

## Data Sources

[List and describe data sources]

## Parameters

[Document adjustable parameters]

## Usage

[Show how to use the forecast]

## Assumptions and Limitations

[Document assumptions and known limitations]
```

#### 3. Create Tests

Create test files in `forecasts/your_forecast_name/tests/`:

- `__init__.py` - Test package initialization
- `test_your_forecast_model.py` - Unit tests
- `test_your_forecast_properties.py` - Property-based tests
- `README.md` - Test documentation

#### 4. Verify Your Forecast

1. **Test the model**:
```bash
pytest forecasts/your_forecast_name/tests/ -v
```

2. **Run standalone**:
```bash
python forecasts/your_forecast_name/run_forecast.py
```

3. **Restart web interface**:
```bash
python -m web.app
```

Your forecast will appear automatically in the web interface!

### Best Practices for New Forecasts

1. **Always validate parameters** using `validate_parameters()` from `lib.utils`
2. **Normalize probabilities** using `normalize_probability()` from `lib.probability`
3. **Handle errors gracefully** - log errors and provide meaningful messages
4. **Cache external data** using functions from `lib.data_fetcher`
5. **Save results to database** using `save_forecast_result()` from `lib.database`
6. **Document thoroughly** - explain methodology, assumptions, and limitations
7. **Write tests** - both unit tests and property-based tests
8. **Use logging** - log important events and errors for debugging

## API Reference

### Web API Endpoints

The Flask application provides the following REST API endpoints:

#### GET `/api/forecasts`

List all available forecasts.

**Response:**
```json
{
  "forecasts": [
    {
      "name": "us_recession_2025",
      "display_name": "US Recession 2025",
      "description": "Predicts the probability of a US recession...",
      "last_updated": "2024-11-22T10:30:00"
    }
  ]
}
```

#### GET `/api/forecast/<name>`

Get current forecast data.

**Response:**
```json
{
  "name": "us_recession_2025",
  "display_name": "US Recession 2025",
  "probability": 0.35,
  "last_updated": "2024-11-22T10:30:00",
  "parameters": {
    "yield_curve_weight": 0.35,
    "unemployment_weight": 0.25
  }
}
```

#### POST `/api/forecast/<name>/simulate`

Simulate forecast with custom parameters.

**Request Body:**
```json
{
  "yield_curve_weight": 0.40,
  "unemployment_weight": 0.30,
  "gdp_weight": 0.20
}
```

**Response:**
```json
{
  "probability": 0.38,
  "parameters": {
    "yield_curve_weight": 0.40,
    "unemployment_weight": 0.30,
    "gdp_weight": 0.20
  }
}
```

### Python API

#### ForecastModel Interface

All forecast models must implement this interface:

```python
from forecasts import ForecastModel
from datetime import datetime
from typing import Dict, Optional

class YourModel(ForecastModel):
    def get_name(self) -> str:
        """Return human-readable forecast name."""
        pass
    
    def get_description(self) -> str:
        """Return forecast description."""
        pass
    
    def get_parameters(self) -> Dict:
        """Return adjustable parameters with metadata."""
        pass
    
    def calculate_probability(self, params: Optional[Dict] = None) -> float:
        """Calculate and return probability (0-1)."""
        pass
    
    def get_last_updated(self) -> datetime:
        """Return timestamp of last data update."""
        pass
    
    def get_data_sources(self) -> list:
        """Return list of data sources used."""
        pass
```

#### Library Functions

**lib.probability**
- `normalize_probability(value: float) -> float` - Clamp value to [0, 1]
- `combine_probabilities(probs: List[float], weights: List[float]) -> float` - Weighted average
- `logistic_transform(x: float, center: float, scale: float) -> float` - Logistic function
- `bayesian_update(prior: float, likelihood_pos: float, likelihood_neg: float) -> float` - Bayesian update

**lib.data_fetcher**
- `fetch_fred_data(series_id: str, start_date: str, end_date: str) -> Dict` - Fetch FRED data
- `cache_data(key: str, data: Any, ttl: int) -> None` - Cache data locally
- `get_cached_data(key: str) -> Optional[Any]` - Retrieve cached data
- `clear_cache(key: Optional[str]) -> None` - Clear cache

**lib.database**
- `get_connection() -> sqlite3.Connection` - Get database connection
- `create_forecast_table(name: str, schema: Dict) -> None` - Create forecast table
- `save_forecast_result(name: str, probability: float, ...) -> int` - Save result
- `get_forecast_history(name: str, limit: int) -> List[Dict]` - Get history

**lib.utils**
- `validate_parameters(params: Dict, schema: Dict) -> Dict[str, str]` - Validate parameters
- `setup_logging(name: str, level: int, log_file: str) -> logging.Logger` - Configure logging
- `load_config(forecast_name: str, config_file: str) -> Dict` - Load configuration

## Testing

The project includes comprehensive unit tests and property-based tests.

### Running Tests

**Run all tests:**
```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_probability_utils.py -v

# Run tests for specific forecast
pytest forecasts/us_recession_2025/tests/ -v
```

**Run with coverage:**
```bash
pytest --cov=lib --cov=forecasts --cov=web --cov-report=html
```

View coverage report by opening `htmlcov/index.html` in your browser.

**Run only property-based tests:**
```bash
pytest -k "properties" -v
```

**Run only unit tests:**
```bash
pytest -k "not properties" -v
```

### Test Organization

Tests are organized into two categories:

**Generic Tests** (`tests/` directory):
- Framework tests (Flask, database, probability functions)
- Shared utility tests
- Integration tests across forecasts
- Forecast discovery tests

**Forecast-Specific Tests** (`forecasts/<name>/tests/` directory):
- Model-specific unit tests
- Model-specific property-based tests
- Model-specific integration tests
- Validation scripts

### Property-Based Testing

The project uses [Hypothesis](https://hypothesis.readthedocs.io/) for property-based testing to verify correctness properties:

1. **Probability bounds enforcement** - All outputs in [0, 1]
2. **Economic indicators collection** - Models fetch all configured indicators
3. **Database persistence** - All calculations stored with timestamps
4. **Parameter modification triggers recalculation** - Changing parameters recalculates
5. **Parameter validation** - Invalid inputs rejected, valid inputs accepted
6. **Simulation state preservation** - Simulations don't alter model state
7. **Forecast table creation** - New models create database tables
8. **Navigation reflects directory structure** - UI shows valid forecasts

Each property test runs 100+ iterations with randomly generated inputs to verify correctness across a wide range of scenarios.

### Writing Tests

When adding new functionality, write both unit tests and property tests:

**Unit Test Example:**
```python
def test_normalize_probability_clamps_negative():
    """Test that negative values are clamped to 0."""
    assert normalize_probability(-0.5) == 0.0

def test_normalize_probability_clamps_above_one():
    """Test that values above 1 are clamped to 1."""
    assert normalize_probability(1.5) == 1.0
```

**Property Test Example:**
```python
from hypothesis import given, strategies as st

@given(st.floats(min_value=0, max_value=1))
def test_probability_always_in_range(prob):
    """Property: normalized probability is always in [0, 1]."""
    result = normalize_probability(prob)
    assert 0 <= result <= 1
```

## Error Handling and Logging

The application includes comprehensive error handling and logging:

### Logging

All application events, errors, and warnings are logged to the `logs/` directory:

- **application.log**: Main application log with all events
- **Rotating logs**: Automatically rotated at 10MB, keeping 5 backup files
- **Structured format**: `YYYY-MM-DD HH:MM:SS - module - LEVEL - message`

View logs:
```bash
# View recent entries
tail -f logs/application.log

# Search for errors
grep ERROR logs/application.log
```

### Error Handling

The application handles errors gracefully:

- **404 Errors**: User-friendly page with list of available forecasts
- **500 Errors**: Generic error page with helpful message
- **API Errors**: Structured JSON responses with error details
- **Validation Errors**: Clear messages for invalid parameters
- **Network Errors**: Automatic retry with exponential backoff
- **Data Errors**: Fallback to cached data when available

All errors are logged with full context and stack traces for debugging.

## Technology Stack

- **Python 3.10+**: Core language
- **Flask**: Web framework
- **SQLite3**: Database (built-in, no external dependencies)
- **Pandas**: Data manipulation and analysis
- **Requests**: HTTP client for data fetching
- **Hypothesis**: Property-based testing
- **Pytest**: Test runner

## Design Principles

1. **Modularity**: Each forecast is self-contained with its own directory, configuration, and database table
2. **Discoverability**: The web interface automatically detects forecast models by scanning the forecasts/ directory
3. **Reusability**: Common functionality lives in lib/ and is imported by forecast models
4. **Simplicity**: Use Flask for lightweight web serving, SQLite for local persistence, minimal dependencies
5. **Extensibility**: Adding a new forecast requires only creating a new directory with standard structure

## Forecast Model Interface

Every forecast model must implement these methods:

- `get_name()`: Return human-readable forecast name
- `get_description()`: Return forecast description
- `get_parameters()`: Return adjustable parameters with metadata
- `calculate_probability(params)`: Calculate and return probability (0-1)
- `get_last_updated()`: Return timestamp of last data update

## Database Schema

Each forecast gets its own table in the SQLite database:

```sql
CREATE TABLE forecast_{name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    probability REAL NOT NULL CHECK(probability >= 0 AND probability <= 1),
    parameters TEXT,           -- JSON string of parameters used
    data_snapshot TEXT,         -- JSON string of input data
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Troubleshooting

### Common Issues

**Issue: "FRED API key is required" error**

Solution: Make sure you've set up your FRED API key:
```bash
# Check if .env file exists
cat .env

# If not, create it
echo "FRED_API_KEY=your_api_key_here" > .env

# Or set environment variable
export FRED_API_KEY=your_api_key_here
```

**Issue: "No module named 'forecasts'" error**

Solution: Make sure you're running commands from the project root directory and the virtual environment is activated:
```bash
# Activate virtual environment
source venv/bin/activate

# Run from project root
python -m web.app
```

**Issue: Database locked error**

Solution: Close any other connections to the database:
```bash
# Check for processes using the database
lsof data/forecasts.db

# If needed, remove the database and let it recreate
rm data/forecasts.db
```

**Issue: Import errors when running tests**

Solution: Install the package in development mode:
```bash
pip install -e .
```

**Issue: Cached data is stale**

Solution: Clear the cache:
```bash
# Clear all cache
rm -rf data/cache/*

# Or clear specific series
python -c "from lib.data_fetcher import clear_cache; clear_cache()"
```

**Issue: Web interface doesn't show new forecast**

Solution: Restart the Flask application and check for errors:
```bash
# Stop the app (Ctrl+C)
# Restart with debug output
python -m web.app
```

### Getting Help

If you encounter issues:

1. Check the logs in `logs/application.log`
2. Run tests to verify installation: `pytest tests/`
3. Verify FRED API key is valid: `python -c "import os; print(os.getenv('FRED_API_KEY'))"`
4. Check Python version: `python --version` (should be 3.10+)

## FAQ

**Q: How often should I run forecasts?**

A: Economic data is typically updated daily or weekly. Running forecasts once per day is usually sufficient. You can set up a cron job for automated updates.

**Q: Can I use data sources other than FRED?**

A: Yes! The `lib.data_fetcher` module can be extended to support other APIs. Just add new fetch functions and use them in your forecast's `data.py` file.

**Q: How do I export forecast results?**

A: Query the database directly:
```python
from lib.database import get_forecast_history
import json

history = get_forecast_history('us_recession_2025', limit=100)
with open('forecast_history.json', 'w') as f:
    json.dump(history, f, indent=2, default=str)
```

**Q: Can I deploy this to a server?**

A: Yes! For production deployment:
1. Use a production WSGI server (gunicorn, uWSGI)
2. Set `debug=False` in `web/app.py`
3. Use environment variables for sensitive data
4. Consider using PostgreSQL instead of SQLite for better concurrency
5. Set up proper logging and monitoring

**Q: How accurate are the forecasts?**

A: Forecast accuracy depends on the model, data quality, and economic conditions. Always:
- Backtest against historical data
- Compare with professional forecasts
- Document assumptions and limitations
- Update models as new information becomes available

**Q: Can I use this for actual trading?**

A: This is an educational tool. For actual trading:
- Thoroughly validate and backtest models
- Understand the risks and limitations
- Consider professional financial advice
- Never risk more than you can afford to lose

**Q: How do I add more economic indicators?**

A: Edit `forecasts/us_recession_2025/config.py`:
1. Add the FRED series ID to `DATA_SOURCES`
2. Add parameter schema for the indicator weight
3. Update `model.py` to incorporate the new indicator
4. Update thresholds in `INDICATOR_THRESHOLDS`

**Q: Can I create forecasts for non-economic events?**

A: Absolutely! The framework is general-purpose. You can create forecasts for:
- Sports outcomes
- Election results
- Weather events
- Technology adoption
- Any event with quantifiable data

## Contributing

We welcome contributions! When adding new features or forecast models:

1. **Follow the existing project structure** - Keep forecasts modular and self-contained
2. **Implement the `ForecastModel` interface** - Ensure compatibility with the web interface
3. **Add comprehensive tests** - Both unit tests and property-based tests
4. **Document your code** - Add docstrings to all functions and classes
5. **Update documentation** - Update README.md and create forecast-specific README
6. **Follow Python best practices** - PEP 8 style guide, type hints where appropriate
7. **Test thoroughly** - Run all tests before submitting changes

### Code Style

- Follow PEP 8 style guide
- Use type hints for function signatures
- Write descriptive docstrings (Google style)
- Keep functions focused and modular
- Use meaningful variable names

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -am 'Add new feature'`)
6. Push to the branch (`git push origin feature/your-feature`)
7. Create a Pull Request

## License

This project is provided as-is for educational and research purposes.

## Acknowledgments

- Inspired by Nate Silver's approach to probabilistic forecasting
- Economic data provided by FRED (Federal Reserve Economic Data)
- Property-based testing powered by Hypothesis
- Web framework by Flask

## Resources

- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Nate Silver's "The Signal and the Noise"](https://www.penguinrandomhouse.com/books/305826/the-signal-and-the-noise-by-nate-silver/)
- [NBER Recession Dating](https://www.nber.org/cycles/)
