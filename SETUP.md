# Setup Guide

This document provides detailed setup instructions for the Polymarket Forecasting Simulator.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Installation](#detailed-installation)
- [FRED API Setup](#fred-api-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Development Setup](#development-setup)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher** - Check with `python --version` or `python3 --version`
- **pip** - Python package manager (usually comes with Python)
- **Git** (optional) - For cloning the repository
- **FRED API Key** - Free registration at https://fred.stlouisfed.org/docs/api/api_key.html

### Checking Prerequisites

```bash
# Check Python version (should be 3.10+)
python --version

# Check pip
pip --version

# Check Git (optional)
git --version
```

## Quick Start

For experienced users, here's the quick setup:

```bash
# Clone or download the repository
git clone <repository-url>
cd polymarket-forecasting-simulator

# Create virtual environment and activate
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up FRED API key
cp .env.example .env
# Edit .env and add your FRED_API_KEY

# Run tests to verify
pytest

# Start the application
python -m web.app
```

Open http://localhost:5000 in your browser.

## Detailed Installation

### Step 1: Get the Code

**Option A: Clone with Git**
```bash
git clone <repository-url>
cd polymarket-forecasting-simulator
```

**Option B: Download ZIP**
1. Download the source code as a ZIP file
2. Extract to a directory
3. Open terminal/command prompt in that directory

### Step 2: Create Virtual Environment

A virtual environment isolates the project's dependencies from your system Python.

**On macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt
```

**On Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your prompt
```

**Troubleshooting Virtual Environment:**

If you get a "command not found" error on macOS/Linux:
```bash
# Try python3 instead of python
python3 -m venv venv
```

If you get an execution policy error on Windows:
```powershell
# Run PowerShell as Administrator and execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
venv\Scripts\activate
```

### Step 3: Install Dependencies

With the virtual environment activated:

```bash
# Upgrade pip first (recommended)
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- pandas (data manipulation)
- requests (HTTP client)
- hypothesis (property-based testing)
- pytest (testing framework)
- python-dotenv (environment variable management)

**Troubleshooting Dependencies:**

If installation fails, try installing packages individually:
```bash
pip install flask
pip install pandas
pip install requests
pip install hypothesis
pip install pytest
pip install python-dotenv
```

If you get SSL certificate errors:
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Step 4: Set Up FRED API Key

The application requires a FRED API key to fetch economic data.

#### 4.1: Get Your API Key

1. Go to https://fred.stlouisfed.org/
2. Click "My Account" → "API Keys"
3. Sign up for a free account if you don't have one
4. Request an API key (instant approval)
5. Copy your API key

#### 4.2: Configure the API Key

**Option A: Using .env file (Recommended)**

```bash
# Copy the example file
cp .env.example .env

# On Windows, use:
copy .env.example .env
```

Edit the `.env` file and add your API key:
```
FRED_API_KEY=your_actual_api_key_here
```

**Option B: Using Environment Variable**

**On macOS/Linux:**
```bash
export FRED_API_KEY=your_actual_api_key_here

# To make it permanent, add to ~/.bashrc or ~/.zshrc:
echo 'export FRED_API_KEY=your_actual_api_key_here' >> ~/.bashrc
source ~/.bashrc
```

**On Windows (Command Prompt):**
```cmd
set FRED_API_KEY=your_actual_api_key_here

# To make it permanent:
setx FRED_API_KEY "your_actual_api_key_here"
```

**On Windows (PowerShell):**
```powershell
$env:FRED_API_KEY="your_actual_api_key_here"

# To make it permanent:
[System.Environment]::SetEnvironmentVariable('FRED_API_KEY', 'your_actual_api_key_here', 'User')
```

#### 4.3: Verify API Key Setup

```bash
# Test that the API key is loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('FRED_API_KEY'))"
```

You should see your API key printed (not "None").

### Step 5: Initialize Database

The database will be created automatically on first run, but you can initialize it manually:

```bash
python -c "from lib.database import initialize_metadata_table; initialize_metadata_table()"
```

This creates:
- `data/` directory
- `data/forecasts.db` SQLite database
- `forecast_metadata` table

### Step 6: Verify Installation

Run the test suite to verify everything is working:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test categories
pytest tests/ -v                                    # Generic tests
pytest forecasts/us_recession_2025/tests/ -v       # Recession model tests
```

Expected output:
```
======================== test session starts ========================
collected XX items

tests/test_probability_utils.py ........                      [ XX%]
tests/test_database_validation.py ......                      [ XX%]
...

======================== XX passed in X.XXs =========================
```

### Step 7: Run the Application

Start the Flask web server:

```bash
python -m web.app
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

Open your browser to http://localhost:5000

You should see the Polymarket Forecasting Simulator home page with available forecasts.

## FRED API Setup

### Understanding FRED API

FRED (Federal Reserve Economic Data) provides free access to economic data:
- **Free tier**: 120 requests per minute
- **No credit card required**
- **Instant approval**
- **Thousands of economic indicators**

### API Key Best Practices

1. **Never commit API keys to version control** - Use .env file (already in .gitignore)
2. **Keep your key private** - Don't share in public forums
3. **Rotate keys periodically** - Generate new keys every few months
4. **Use environment variables** - Don't hardcode keys in source code

### Testing FRED API Connection

Test your FRED API connection:

```bash
python -c "
from lib.data_fetcher import fetch_fred_data
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('FRED_API_KEY')

if not api_key:
    print('ERROR: FRED_API_KEY not found')
else:
    print(f'API Key found: {api_key[:8]}...')
    try:
        data = fetch_fred_data('UNRATE', api_key=api_key)
        print('SUCCESS: FRED API connection working')
        print(f'Fetched {len(data.get(\"observations\", []))} observations')
    except Exception as e:
        print(f'ERROR: {e}')
"
```

## Verification

### Verify Installation Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed successfully
- [ ] FRED API key configured
- [ ] Database initialized
- [ ] Tests pass
- [ ] Web application starts
- [ ] Can access http://localhost:5000
- [ ] Forecasts appear in web interface

### Test Each Component

**Test Database:**
```bash
python -c "
from lib.database import get_connection
conn = get_connection()
cursor = conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
tables = cursor.fetchall()
print('Database tables:', [t[0] for t in tables])
conn.close()
"
```

**Test Data Fetcher:**
```bash
python -c "
from lib.data_fetcher import fetch_fred_data
data = fetch_fred_data('UNRATE')
print(f'Fetched {len(data[\"observations\"])} unemployment rate observations')
"
```

**Test Probability Functions:**
```bash
python -c "
from lib.probability import normalize_probability, combine_probabilities
print('normalize_probability(0.5):', normalize_probability(0.5))
print('combine_probabilities([0.3, 0.7]):', combine_probabilities([0.3, 0.7]))
"
```

**Test Recession Model:**
```bash
python forecasts/us_recession_2025/run_forecast.py
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: "python: command not found"

**Solution:** Use `python3` instead:
```bash
python3 -m venv venv
python3 -m web.app
```

#### Issue: "pip: command not found"

**Solution:** Install pip or use python -m pip:
```bash
# On macOS/Linux
sudo apt-get install python3-pip  # Ubuntu/Debian
brew install python3              # macOS with Homebrew

# Use python -m pip instead
python -m pip install -r requirements.txt
```

#### Issue: "FRED API key is required"

**Solution:** Verify API key setup:
```bash
# Check if .env file exists
cat .env

# Check if API key is loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('FRED_API_KEY'))"

# If None, recreate .env file
echo "FRED_API_KEY=your_key_here" > .env
```

#### Issue: "ModuleNotFoundError: No module named 'forecasts'"

**Solution:** Run from project root with virtual environment activated:
```bash
# Make sure you're in the project root
pwd  # Should show .../polymarket-forecasting-simulator

# Make sure virtual environment is activated
which python  # Should show .../venv/bin/python

# Run from project root
python -m web.app
```

#### Issue: "Database is locked"

**Solution:** Close other connections or recreate database:
```bash
# Find processes using the database
lsof data/forecasts.db  # macOS/Linux

# Kill the process or close the application

# Or recreate the database
rm data/forecasts.db
python -c "from lib.database import initialize_metadata_table; initialize_metadata_table()"
```

#### Issue: "Address already in use" (Port 5000)

**Solution:** Use a different port or kill the process:
```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill the process or use different port
# Edit web/app.py and change port number
```

#### Issue: Tests fail with "FRED API rate limit exceeded"

**Solution:** Wait a minute or clear cache:
```bash
# Clear cache
rm -rf data/cache/*

# Wait 60 seconds for rate limit to reset

# Run tests again
pytest
```

#### Issue: "SSL: CERTIFICATE_VERIFY_FAILED"

**Solution:** Update certificates or disable verification (not recommended for production):
```bash
# On macOS
/Applications/Python\ 3.10/Install\ Certificates.command

# Or install certifi
pip install --upgrade certifi

# Or temporarily disable SSL verification (development only)
export PYTHONHTTPSVERIFY=0
```

### Getting More Help

If you're still having issues:

1. **Check logs:** `cat logs/application.log`
2. **Run with debug:** `python -m web.app` (debug mode is on by default)
3. **Verify Python version:** `python --version` (must be 3.10+)
4. **Check dependencies:** `pip list`
5. **Try clean install:**
   ```bash
   deactivate
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Development Setup

For contributors and developers:

### Install Development Dependencies

```bash
# Install additional development tools
pip install pytest pytest-cov hypothesis black flake8 mypy

# Or use development requirements (if available)
pip install -r requirements-dev.txt
```

### Set Up Pre-Commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Code Quality Tools

**Format code with Black:**
```bash
black lib/ forecasts/ web/ tests/
```

**Check style with flake8:**
```bash
flake8 lib/ forecasts/ web/ tests/ --max-line-length=100
```

**Type checking with mypy:**
```bash
mypy lib/ forecasts/ web/
```

**Run tests with coverage:**
```bash
pytest --cov=lib --cov=forecasts --cov=web --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Development Workflow

1. Create a feature branch
2. Make changes
3. Run tests: `pytest`
4. Format code: `black .`
5. Check style: `flake8 .`
6. Commit changes
7. Push and create pull request

## Next Steps

After successful setup:

1. **Explore the web interface** - http://localhost:5000
2. **Run a forecast** - `python forecasts/us_recession_2025/run_forecast.py`
3. **Read the documentation** - See README.md
4. **Try parameter adjustment** - Use the web interface to modify parameters
5. **Review the code** - Explore lib/, forecasts/, and web/ directories
6. **Add your own forecast** - Follow the guide in README.md
7. **Run tests** - `pytest -v`
8. **Check logs** - `tail -f logs/application.log`

## Support

For additional help:
- Review README.md for usage documentation
- Check logs in `logs/application.log`
- Run tests to verify functionality
- Review code comments and docstrings
