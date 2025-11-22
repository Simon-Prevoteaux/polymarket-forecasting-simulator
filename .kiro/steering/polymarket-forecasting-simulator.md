# Polymarket Forecasting Simulator - Project Guide

## Project Overview

The Polymarket Forecasting Simulator is a Python-based system for building and managing probabilistic forecasts for prediction markets. The system enables users to develop individual forecasting models for specific problems (e.g., "Will the US have a recession by end of 2025?"), visualize results through a simple web interface, and adjust parameters to simulate different scenarios.

**Philosophy:** Following Nate Silver's approach to real-world modeling with modular forecast components, statistical rigor, and a library of reusable utilities.

**Available Forecasts:**
- `us_recession_2025` - Predicts US recession probability using economic indicators (FRED data)
- `election_2028` - Predicts 2028 US Presidential Election outcome (DEMO: uses random data)

## Project Structure

```
polymarket-forecasting-simulator/
├── lib/                          # Shared utilities and reusable code
│   ├── __init__.py
│   ├── data_fetcher.py          # Data retrieval utilities
│   ├── probability.py            # Probability calculation helpers
│   ├── database.py               # SQLite operations
│   └── utils.py                  # General utilities
├── forecasts/                    # Individual forecast models (one folder per problem)
│   ├── __init__.py
│   ├── us_recession_2025/       # Example: US recession forecast
│   │   ├── __init__.py
│   │   ├── model.py             # Main forecast logic
│   │   ├── data.py              # Data collection specific to this forecast
│   │   ├── config.py            # Model parameters and configuration
│   │   ├── run_forecast.py      # Standalone execution script
│   │   └── README.md            # Documentation
│   └── election_2028/           # Example: Election forecast (DEMO)
│       ├── __init__.py
│       ├── model.py             # Main forecast logic
│       ├── data.py              # Data generation (dummy data)
│       ├── config.py            # Model parameters and configuration
│       ├── run_forecast.py      # Standalone execution script
│       └── README.md            # Documentation
├── web/                          # Flask web interface
│   ├── __init__.py
│   ├── app.py                   # Flask application
│   ├── templates/               # HTML templates
│   │   ├── base.html           # Base template with sidebar
│   │   ├── index.html          # Home page
│   │   ├── forecast.html       # Forecast detail page
│   │   └── error.html          # Error page (404/500)
│   └── static/                  # CSS and JavaScript
│       ├── css/
│       │   └── style.css       # Main stylesheet
│       └── js/
│           └── main.js         # JavaScript utilities
├── data/                         # Local data storage
│   └── forecasts.db             # SQLite database
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

## Core Design Principles

### 1. Modularity
- Each forecast problem lives in its own directory under `forecasts/`
- Forecasts are self-contained with dedicated scripts, data, and database tables
- Adding a new forecast doesn't require modifying existing code

### 2. Discoverability
- Web interface automatically detects forecast models by scanning `forecasts/` directory
- No manual registration required - just create a folder with the proper structure

### 3. Reusability
- Common functionality lives in `lib/` and is imported by forecast models
- Utilities include: data fetching, probability calculations, database operations

### 4. Simplicity
- Flask for lightweight web serving
- SQLite for local persistence (no external database)
- Minimal dependencies, easy setup

### 5. Extensibility
- Standard forecast model interface makes adding new forecasts straightforward
- Shared utilities can be extended without breaking existing forecasts

## Forecast Model Interface

Every forecast model must implement this standard interface:

```python
class ForecastModel:
    """Base interface for all forecast models"""
    
    def get_name(self) -> str:
        """Return human-readable forecast name"""
        pass
    
    def get_description(self) -> str:
        """Return forecast description"""
        pass
    
    def get_parameters(self) -> dict:
        """Return adjustable parameters with metadata"""
        pass
    
    def calculate_probability(self, params: dict = None) -> float:
        """Calculate and return probability (0-1)"""
        pass
    
    def get_last_updated(self) -> datetime:
        """Return timestamp of last data update"""
        pass
    
    def get_data_sources(self) -> list:
        """Return list of data sources used by this forecast"""
        pass
```

## Database Schema Patterns

### Forecast Metadata Table
```sql
CREATE TABLE forecast_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP
);
```

### Individual Forecast Table Pattern
Each forecast gets its own table following this pattern:
```sql
CREATE TABLE forecast_{name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    probability REAL NOT NULL CHECK(probability >= 0 AND probability <= 1),
    parameters TEXT,           -- JSON string of parameters used
    data_snapshot TEXT,         -- JSON string of input data
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Technology Stack

- **Python 3.10+**: Core language
- **Flask**: Web framework (chosen for simplicity and flexibility)
- **SQLite3**: Database (built-in, no external dependencies)
- **Pandas**: Data manipulation and analysis
- **Requests**: HTTP client for data fetching
- **Hypothesis**: Property-based testing
- **Pytest**: Test runner
- **FRED API**: Economic data source (requires free API key)

## Key Requirements Summary

### Modular Structure (Req 1)
- `lib/` directory for reusable utilities
- Each forecast in dedicated problem-specific directory
- Unlimited forecasts can be added without modifying existing models

### Forecast Models (Req 2)
- Output probabilities between 0 and 1
- Collect and process relevant data sources
- Store results in dedicated SQLite tables

### Reusable Utilities (Req 3)
- Data fetching and processing utilities
- Probability calculation helpers
- Database operation utilities

### Web Interface (Req 4)
- Simple Flask/Gradio/Django interface
- Sidebar navigation listing all forecast models
- Clear display of probability predictions

### Parameter Simulation (Req 5)
- Adjustable parameters through web interface
- Real-time recalculation on parameter changes
- Input validation for parameter ranges
- Non-destructive simulations (preserve original state)

### Local Storage (Req 6)
- SQLite for relational data
- Local file system for non-relational data
- Dedicated table per forecast
- Historical tracking with timestamps

### Dynamic Discovery (Req 7)
- Web interface scans project directory for forecasts
- Navigation auto-updates when forecasts are added/removed
- No code changes needed to add new forecasts

### Modeling Principles (Req 8)
- Multiple data sources per forecast
- Statistical reasoning to combine evidence
- Document assumptions and limitations
- Update forecasts as new data becomes available

## Correctness Properties

The system implements 8 correctness properties verified through property-based testing:

1. **Probability bounds enforcement**: All outputs must be in [0, 1]
2. **Economic indicators collection**: Models must fetch all configured indicators
3. **Database persistence**: All calculations must be stored with timestamps
4. **Parameter modification triggers recalculation**: Changing parameters must recalculate probability
5. **Parameter validation**: Invalid inputs must be rejected, valid inputs accepted
6. **Simulation state preservation**: Simulations must not permanently alter model state
7. **Forecast table creation**: New models must create corresponding database tables
8. **Navigation reflects directory structure**: UI must show exactly the valid forecasts present

## Testing Strategy

### Test Organization Pattern

The project follows a clear test organization pattern to keep tests maintainable and co-located with their relevant code:

**Generic/Shared Tests** → `tests/` (root directory)
- Framework tests (Flask, database utilities, probability functions)
- Shared utility tests (data fetching, parameter validation)
- Integration tests across forecasts
- Forecast discovery tests
- Web interface tests

**Forecast-Specific Tests** → `forecasts/<forecast_name>/tests/`
- Model-specific unit tests
- Model-specific property-based tests
- Model-specific integration tests
- Model-specific validation scripts

**Example Structure:**
```
tests/                                    # Generic tests
├── test_flask_app.py                    # Flask routes and templates
├── test_database_properties.py          # Database utility properties
├── test_probability_utils.py            # Probability function tests
├── test_data_fetcher.py                 # Data fetching tests
└── test_forecast_discovery.py           # Forecast discovery tests

forecasts/us_recession_2025/tests/       # US recession-specific tests
├── __init__.py
├── README.md                            # Test documentation
├── test_recession_model.py              # Model unit tests
├── test_recession_model_properties.py   # Model property tests
├── test_recession_database_integration.py  # Database integration
├── validate_recession_model.py          # Manual validation
└── validate_recession_database.py       # Database validation
```

**Benefits of this organization:**
- Tests are co-located with the code they test
- Easy to understand what tests belong to which forecast
- Can run tests for a specific forecast in isolation
- Adding new forecasts doesn't clutter the root tests directory
- Clear separation between generic and forecast-specific tests

### Unit Tests
- Specific examples and edge cases
- Integration points between components
- Mock external dependencies (FRED API)
- Flask route and template rendering tests

**Flask Application Tests:**
- `tests/test_flask_app.py`: Unit tests for Flask routes, error handlers, and basic functionality
- `tests/validate_flask_app.py`: Validation script to verify complete Flask structure

### Property-Based Tests (Hypothesis)
- Minimum 100 iterations per property
- Tag format: `# Feature: polymarket-forecasting-simulator, Property {number}: {property_text}`
- Each correctness property has exactly one property-based test
- Realistic data generators (probabilities in [0,1], valid date ranges)

### Integration Tests
- End-to-end workflows
- Component interactions
- Database operations

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests (generic + all forecasts)
pytest tests/ forecasts/

# Run only generic tests
pytest tests/

# Run tests for a specific forecast
pytest forecasts/us_recession_2025/tests/

# Run specific test file
pytest tests/test_flask_app.py -v

# Run validation scripts
python tests/validate_flask_app.py
python forecasts/us_recession_2025/tests/validate_recession_model.py
```

## Running Forecasts

### Via Web Interface

Start the Flask application to view and interact with forecasts through the browser:

```bash
source venv/bin/activate
python web/app.py
```

Navigate to `http://localhost:5001` to see all forecasts.

### Standalone Execution

Each forecast should include a `run_forecast.py` script for standalone execution without the web interface:

```bash
# Run the US recession forecast
python forecasts/us_recession_2025/run_forecast.py

# Run the election forecast
python forecasts/election_2028/run_forecast.py

# With options
python forecasts/us_recession_2025/run_forecast.py --no-history
python forecasts/us_recession_2025/run_forecast.py --history-limit 20
```

**Standalone script features:**
- Display current probability calculation
- Show all economic indicators with values and dates
- Display historical forecasts with trend analysis
- Provide interpretation of the probability
- No web interface required
- Useful for automation, cron jobs, or quick checks

## Adding a New Forecast Model

### Required Files

1. Create directory: `forecasts/your_forecast_name/`
2. Create the following files:
   - `__init__.py` - Package initialization
   - `model.py` - Main forecast logic (implements `ForecastModel` interface)
   - `config.py` - Model parameters and configuration
   - `data.py` - Data collection specific to this forecast
   - `README.md` - Documentation for the forecast
   - `run_forecast.py` - Standalone execution script
3. Create test directory: `forecasts/your_forecast_name/tests/`
   - `__init__.py` - Test package initialization
   - `README.md` - Test documentation
   - `test_<forecast>_model.py` - Unit tests
   - `test_<forecast>_model_properties.py` - Property-based tests
   - `validate_<forecast>_model.py` - Validation scripts

### Implementation Steps

1. Implement `ForecastModel` interface in `model.py`
2. Define parameters in `config.py` with `ParameterSchema`
3. Implement data fetching in `data.py`
4. Create database table using `lib/database.py` utilities
5. Write unit tests and property-based tests
6. Create standalone `run_forecast.py` script
7. Document the forecast in `README.md`
8. Restart web interface - new forecast appears automatically

### Example Forecast Structure

```
forecasts/your_forecast_name/
├── __init__.py
├── README.md                    # Forecast documentation
├── model.py                     # ForecastModel implementation
├── config.py                    # Parameters and configuration
├── data.py                      # Data fetching logic
├── run_forecast.py              # Standalone execution script
└── tests/                       # Forecast-specific tests
    ├── __init__.py
    ├── README.md
    ├── test_your_forecast_model.py
    ├── test_your_forecast_properties.py
    └── validate_your_forecast.py
```

## Web Interface Conventions

### Flask Application Structure

The Flask application is located in `web/app.py` and provides the following:

**Core Routes:**
- `/`: Home page listing all forecasts
- `/forecast/<name>`: Display specific forecast with current probability
- `/api/forecasts`: JSON API endpoint listing all available forecasts
- `/api/forecast/<name>/simulate`: POST endpoint for parameter simulation

**Error Handlers:**
- 404 handler: Returns user-friendly "Forecast not found" page
- 500 handler: Returns generic "Internal server error" page

**Templates (web/templates/):**
- `base.html`: Base template with sidebar navigation and main content area
- `index.html`: Home page with forecast grid and project overview
- `forecast.html`: Individual forecast display page with probability, parameters, and charts
- `error.html`: Error page template for 404/500 errors

**Static Assets (web/static/):**
- `css/style.css`: Complete responsive stylesheet with sidebar, forecast cards, and mobile support
- `js/main.js`: JavaScript utilities for probability formatting and future interactive features

### UI Components
- Sidebar navigation with all discovered forecasts
- Main panel showing current probability as large percentage
- Historical probability chart (line graph)
- Parameter adjustment controls (sliders/inputs)
- Last updated timestamp
- Data source information

### Running the Flask Application

To start the development server:
```bash
# Activate virtual environment first
source venv/bin/activate

# Run the Flask app
python web/app.py
```

The app will start on `http://0.0.0.0:5000` by default with debug mode enabled in development.

## Error Handling Principles

- All errors logged with context (timestamp, forecast name, parameters, stack trace)
- User-facing errors must be clear and actionable
- System fails gracefully without corrupting data
- Critical errors prevent calculation rather than producing incorrect results
- Network failures: retry with exponential backoff, use cached data if available
- Database errors: use transactions, rollback on error

## Development Workflow

1. ✅ Implement core `lib/` utilities (tasks 2-5)
2. ✅ Build first forecast model (US recession) (tasks 6-8)
3. ✅ Create database layer (task 2)
4. ✅ Implement web interface structure (task 9)
5. 🚧 Implement forecast discovery (task 10)
6. 🚧 Complete web interface pages (tasks 11-12)
7. 🚧 Add parameter simulation (tasks 13-14)
8. 🚧 Add styling and polish (task 16)
9. 🚧 Add error handling and logging (task 17)
10. 🚧 Add additional forecast models as needed

### Current Implementation Status

**Completed:**
- Core utilities: data fetching, probability calculations, database operations, general utilities
- US recession forecast model with economic indicators
- Database layer with SQLite operations
- Flask web application structure with routes, templates, and static assets
- Comprehensive test suite with unit tests and property-based tests

**In Progress:**
- Forecast discovery mechanism (automatically detect forecast models)
- Web interface pages with actual forecast data
- Parameter simulation API and UI
- UI polish and responsive design enhancements

**Not Started:**
- Additional forecast models beyond US recession
- Historical probability charts
- Advanced error handling and logging

## Virtual Environment

This project uses a Python virtual environment located at `venv/` in the project root.

### Activating the Virtual Environment
- **macOS/Linux**: `source venv/bin/activate`
- **Windows**: `venv\Scripts\activate`

### Running Commands
All Python commands (pytest, pip, python scripts) should be run within the activated virtual environment:

```bash
# Activate the environment first
source venv/bin/activate

# Then run commands
pytest tests/
python -m forecasts.us_recession_2025.model
pip install -r requirements.txt
```

### Deactivating
When finished, deactivate the environment:
```bash
deactivate
```

### Important Notes
- The virtual environment must be activated before running any Python commands
- Dependencies are installed in the virtual environment, not globally
- If you see import errors, ensure the virtual environment is activated

## Configuration Requirements

### FRED API Setup
- Sign up for free API key at https://fred.stlouisfed.org/docs/api/api_key.html
- Store API key in environment variable or config file
- Implement rate limiting to respect API limits

### Database Initialization
- Database file created automatically on first run
- Tables created on-demand when forecasts are initialized
- No manual database setup required

## Best Practices

- **Probability outputs**: Always normalize to [0, 1] range
- **Data caching**: Cache external API data to reduce calls and improve performance
- **Parameter validation**: Validate before calculation, not during
- **Error logging**: Log all errors with sufficient context for debugging
- **Documentation**: Document assumptions and data sources for each forecast
- **Testing**: Write property tests for universal behaviors, unit tests for specific cases
- **State management**: Keep simulations stateless - don't modify original model configuration
