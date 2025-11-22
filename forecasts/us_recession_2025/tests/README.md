# US Recession 2025 Forecast Tests

This directory contains tests specific to the US Recession 2025 forecast model.

## Test Files

### Unit Tests

- **test_recession_model.py** - Unit tests for the RecessionModel class
  - Tests with historical recession data
  - Tests with economic expansion data
  - Tests default parameters
  - Tests missing indicator handling
  - Tests model interface compliance

### Property-Based Tests

- **test_recession_model_properties.py** - Property-based tests using Hypothesis
  - Property 1: Probability bounds enforcement
  - Property 2: Economic indicators collection

### Integration Tests

- **test_recession_database_integration.py** - Database integration tests
  - Tests forecast result storage
  - Tests historical data retrieval
  - Tests database schema

### Validation Scripts

- **validate_recession_model.py** - Manual validation script for the model
- **validate_recession_database.py** - Manual validation script for database operations

## Running Tests

### Run all tests for this forecast:
```bash
python -m pytest forecasts/us_recession_2025/tests/ -v
```

### Run specific test file:
```bash
python -m pytest forecasts/us_recession_2025/tests/test_recession_model.py -v
```

### Run property-based tests:
```bash
python -m pytest forecasts/us_recession_2025/tests/test_recession_model_properties.py -v
```

### Run validation scripts:
```bash
python forecasts/us_recession_2025/tests/validate_recession_model.py
python forecasts/us_recession_2025/tests/validate_recession_database.py
```

## Test Organization

Following the project's test organization pattern:

- **Generic/shared tests** → `tests/` (root directory)
  - Framework tests (Flask, database utilities, probability functions)
  - Shared utility tests
  - Integration tests across forecasts

- **Forecast-specific tests** → `forecasts/<forecast_name>/tests/`
  - Model-specific unit tests
  - Model-specific property tests
  - Model-specific validation scripts

This organization keeps forecast tests co-located with their models, making it easier to:
- Understand what tests belong to which forecast
- Add new forecasts with their own test suites
- Run tests for a specific forecast in isolation
- Maintain and update forecast-specific tests

## Adding New Tests

When adding tests for this forecast:

1. **Unit tests** - Add to `test_recession_model.py` or create new test files
2. **Property tests** - Add to `test_recession_model_properties.py`
3. **Integration tests** - Add to `test_recession_database_integration.py`
4. **Validation scripts** - Create new `validate_*.py` files

Make sure all tests can be run from the project root using pytest.
