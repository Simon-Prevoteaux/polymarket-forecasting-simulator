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

### Setup

1. Clone or download this repository

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your FRED API key
# Get a free API key at https://fred.stlouisfed.org/docs/api/api_key.html
```

Your `.env` file should look like:
```
FRED_API_KEY=your_api_key_here
```

The application will automatically load environment variables from the `.env` file using python-dotenv.

## Usage

### Running the Web Interface

```bash
python -m web.app
```

Then open your browser to `http://localhost:5000`

### Adding a New Forecast Model

1. Create a new directory under `forecasts/`:
```bash
mkdir forecasts/your_forecast_name
```

2. Create the required files:
   - `__init__.py`
   - `model.py` - Implement the `ForecastModel` interface
   - `config.py` - Define model parameters
   - `data.py` - Implement data fetching logic
   - `README.md` - Document your model

3. Implement the `ForecastModel` interface in `model.py`:
```python
from forecasts import ForecastModel
from datetime import datetime

class YourModel(ForecastModel):
    def get_name(self) -> str:
        return "Your Forecast Name"
    
    def get_description(self) -> str:
        return "Description of what this forecast predicts"
    
    def get_parameters(self) -> dict:
        return {
            "param1": {
                "display_name": "Parameter 1",
                "type": "float",
                "default": 0.5,
                "min_value": 0.0,
                "max_value": 1.0
            }
        }
    
    def calculate_probability(self, params=None) -> float:
        # Your forecast logic here
        return 0.5  # Return probability between 0 and 1
    
    def get_last_updated(self) -> datetime:
        return datetime.now()
```

4. Restart the web interface - your forecast will appear automatically!

## Testing

Run unit tests:
```bash
pytest
```

Run property-based tests:
```bash
pytest -v
```

Run tests with coverage:
```bash
pytest --cov=lib --cov=forecasts --cov=web
```

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

## Contributing

When adding new features or forecast models:

1. Follow the existing project structure
2. Implement the `ForecastModel` interface for new forecasts
3. Add unit tests and property-based tests
4. Document your code with docstrings
5. Update this README if adding new capabilities

## License

This project is provided as-is for educational and research purposes.

## Acknowledgments

- Inspired by Nate Silver's approach to probabilistic forecasting
- Economic data provided by FRED (Federal Reserve Economic Data)
