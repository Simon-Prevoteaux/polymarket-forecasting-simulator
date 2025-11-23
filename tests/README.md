# Generic Tests Directory

This directory contains tests for generic/shared functionality that applies across all forecasts.

## Directory Structure

```
tests/
├── core/                    # Core library tests
│   ├── test_database.py
│   ├── test_probability.py
│   ├── test_utils.py
│   └── test_data_fetcher.py
├── web/                     # Web interface tests
│   ├── test_flask_app.py
│   ├── test_forecast_discovery.py
│   └── test_forecast_interface.py
├── integration/             # Cross-component integration tests
│   └── test_final_integration.py
├── validation/              # Validation scripts
│   ├── validate_flask_app.py
│   ├── validate_forecast_discovery.py
│   └── validate_error_handling.py
└── README.md               # This file
```

## Test Organization Principles

### Generic Tests (tests/)
Tests that belong here:
- Framework tests (Flask routes, templates, error handlers)
- Shared utility tests (database, probability, data fetching)
- Forecast discovery and registration
- Generic forecast interface tests
- Integration tests across multiple forecasts

### Forecast-Specific Tests (forecasts/<name>/tests/)
Tests that belong in forecast directories:
- Model-specific unit tests
- Model-specific property-based tests
- Model-specific database integration
- Model-specific validation scripts
- Tests that import forecast-specific modules

## Running Tests

```bash
# Run all generic tests
pytest tests/

# Run specific test category
pytest tests/core/
pytest tests/web/
pytest tests/integration/

# Run all tests (generic + all forecasts)
pytest tests/ forecasts/

# Run with verbose output
pytest tests/ -v
```

## Test Categories

### Core Library Tests (tests/core/)
- `test_database.py` - Database operations and persistence
- `test_probability.py` - Probability calculation utilities
- `test_utils.py` - General utility functions
- `test_data_fetcher.py` - Data fetching and caching

### Web Interface Tests (tests/web/)
- `test_flask_app.py` - Flask routes and endpoints
- `test_forecast_discovery.py` - Forecast discovery mechanism
- `test_forecast_interface.py` - Generic forecast interface

### Integration Tests (tests/integration/)
- `test_final_integration.py` - End-to-end integration tests

### Validation Scripts (tests/validation/)
- Scripts to manually validate functionality
- Useful for debugging and verification
- Not run as part of automated test suite
