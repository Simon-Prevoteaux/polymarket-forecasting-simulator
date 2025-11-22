# Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env
```

Edit `.env` and add your FRED API key:
```
FRED_API_KEY=your_api_key_here
```

Get a free API key at: https://fred.stlouisfed.org/docs/api/api_key.html

### 3. Verify Installation

Run the test suite to verify everything is working:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run only unit tests (no API calls)
pytest tests/test_data_fetcher.py -v

# Run real API tests (requires FRED_API_KEY in .env)
pytest tests/test_data_fetcher_real_api.py -v
```

### 4. Validate Data Fetching

Run the validation scripts:

```bash
# Offline validation (no API key needed)
python tests/validate_data_fetcher_offline.py

# Real API validation (requires FRED_API_KEY)
python tests/validate_data_fetcher.py
```

## Environment Variables

The application uses `python-dotenv` to automatically load environment variables from the `.env` file.

### Required Variables

- `FRED_API_KEY`: Your FRED API key for fetching economic data

### Optional Variables

You can add more environment variables as needed for future features.

## Testing

### Unit Tests (Mocked)
- **File**: `tests/test_data_fetcher.py`
- **Tests**: 17 tests covering cache, error handling, and API integration
- **No API key required**: Uses mocked responses

### Real API Tests
- **File**: `tests/test_data_fetcher_real_api.py`
- **Tests**: 8 tests with actual FRED API calls
- **Requires API key**: Set `FRED_API_KEY` in `.env`

### Validation Scripts
- **Offline**: `tests/validate_data_fetcher_offline.py` - No API key needed
- **Real API**: `tests/validate_data_fetcher.py` - Requires API key

## Troubleshooting

### "FRED_API_KEY not set" Error

Make sure you have:
1. Created a `.env` file in the project root
2. Added `FRED_API_KEY=your_key` to the file
3. The `.env` file is in the same directory as your Python scripts

### Import Errors

Make sure the virtual environment is activated:
```bash
source venv/bin/activate
```

### Test Failures

If tests fail, check:
1. Virtual environment is activated
2. All dependencies are installed: `pip install -r requirements.txt`
3. `.env` file exists with valid API key (for real API tests)

## What's Implemented

✅ **Data Fetching Utilities** (`lib/data_fetcher.py`)
- FRED API integration with retry logic
- Local caching with TTL expiration
- Error handling for network failures and rate limits
- Automatic API key loading from `.env`

✅ **Comprehensive Testing**
- 17 unit tests with mocked API responses
- 8 real API tests with actual FRED data
- Validation scripts for both offline and online testing

✅ **Documentation**
- README.md updated with .env setup instructions
- .env.example template for easy setup
- .gitignore to protect sensitive data

## Next Steps

Continue with the next task in the implementation plan:
- Task 5: Implement general utilities (utils.py)
- Task 6: Implement forecast model base interface
- Task 7: Implement US recession forecast model

See `tasks.md` for the complete implementation plan.
