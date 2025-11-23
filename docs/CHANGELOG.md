# Changelog

All notable changes to the Polymarket Forecasting Simulator project.

## [2.0.0] - 2025-11-23

### US Recession Forecast V2 - Major Release

#### Added

**Enhanced Data & Features**
- 6 new economic indicators: Credit spreads (BAA10Y), housing starts (HOUST), manufacturing PMI (NAPM), retail sales (RSXFS), oil prices (DCOILWTICO), VIX volatility
- Feature engineering pipeline with rate-of-change (30d, 90d, 180d), moving averages (30d, 90d), and volatility measures
- Graceful missing data handling with forward-fill and neutral defaults

**Temporal Decay Modeling**
- Generic temporal adjustment library (`lib/temporal_adjustment.py`) with 6 methods
- Time-aware probability adjustments based on days remaining until deadline
- Dual probability display: base probability and temporally-adjusted probability
- Methods: none, simple_decay, threshold_decay, trend_amplification, confidence_convergence, adaptive
- Adaptive method as recommended default for context-aware adjustments

**Historical Backtesting**
- Complete backtesting infrastructure (`forecasts/us_recession_2025/backtesting.py`)
- BacktestEngine API for running historical simulations
- Performance metrics: Brier score, calibration statistics, discrimination metrics
- Model comparison: Side-by-side v1 vs v2 performance analysis
- Dedicated database table for backtest results with full metadata

**Interactive Analysis**
- 5 Jupyter notebooks for comprehensive analysis:
  1. Data Exploration - Indicator time series and distributions
  2. Indicator Analysis - Correlation and feature importance
  3. Model Comparison - V1 vs V2 side-by-side
  4. Backtesting Results - Historical performance analysis
  5. Temporal Calibration - Parameter tuning (planned)
- Visualization suite: time series plots, correlation heatmaps, calibration curves
- Parameter sensitivity analysis and optimization tools

**Web Interface Enhancements**
- Temporal decay visualization with Chart.js
- Probability breakdown showing base vs adjusted probabilities
- Days remaining countdown display
- Temporal metadata display (decay method, rate, adjustment details)
- Enhanced forecast detail page with temporal section

**Documentation**
- Reorganized documentation structure with clear navigation
- Comprehensive temporal decay guide with all 6 methods explained
- Complete backtesting guide with workflows and examples
- Feature engineering guide with implementation details
- Documentation index with role-based navigation
- Implementation history preserved in `docs/implementation/`

#### Changed

- US Recession model now has v1 and v2 versions side-by-side
- V2 uses two-stage calculation: base probability + temporal adjustment
- Enhanced model interface with optional `get_probability_breakdown()` method
- Improved test organization: generic tests in `tests/`, forecast-specific in `forecasts/<name>/tests/`
- Updated Flask routes to support probability breakdown API

#### Fixed

- Temporal adjustment now handles all probability ranges (no hard thresholds in adaptive mode)
- Missing data handling improved with forward-fill strategy
- Database schema supports both v1 and v2 models
- Test suite reorganized for better maintainability (250 tests passing)

### Technical Details

**New Modules**
- `lib/temporal_adjustment.py` - Generic temporal adjustment library
- `forecasts/us_recession_2025/model_v2.py` - V2 model implementation
- `forecasts/us_recession_2025/features.py` - Feature engineering
- `forecasts/us_recession_2025/data_v2.py` - Enhanced data fetching
- `forecasts/us_recession_2025/config_v2.py` - V2 configuration
- `forecasts/us_recession_2025/backtesting.py` - Backtesting engine

**Database Changes**
- Added `forecast_us_recession_2025_v2` table for v2 results
- Added `forecast_us_recession_2025_backtest` table for backtest results
- Enhanced schema with features, temporal_metadata columns

**API Changes**
- New endpoint: `GET /api/forecast/<name>/breakdown` - Get probability breakdown
- Enhanced endpoint: `GET /forecast/<name>` - Now includes breakdown data
- Backward compatible: V1 models continue to work without breakdown

**Testing**
- 250 total tests passing (91 forecast-specific, 159 generic)
- Property-based tests for temporal decay, feature engineering, backtesting
- Integration tests for v1/v2 compatibility
- Validation scripts for all major features

## [1.0.0] - 2024-11-01

### Initial Release

#### Added

**Core Framework**
- Modular forecast architecture with self-contained forecast directories
- Dynamic forecast discovery - web interface automatically detects models
- Flask web interface with forecast listing and detail pages
- SQLite database for local persistence
- Reusable utility library (`lib/`) for data fetching, probability calculations, database operations

**US Recession 2025 Forecast (V1)**
- 6 economic indicators: Unemployment rate, yield curve, GDP growth, initial claims, consumer sentiment, industrial production
- Weighted probability calculation based on indicator thresholds
- Historical forecast tracking
- Standalone execution script

**Election 2028 Forecast (Demo)**
- Demo forecast using random data
- Example of forecast model structure

**Testing Infrastructure**
- Comprehensive unit tests
- Property-based testing with Hypothesis
- 8 correctness properties verified
- Test coverage for core utilities and forecast models

**Documentation**
- Project README with installation and usage instructions
- Forecast-specific documentation
- API reference for Python and REST endpoints
- Contributing guidelines

#### Technical Details

**Core Modules**
- `lib/data_fetcher.py` - FRED API integration with caching
- `lib/probability.py` - Probability calculation utilities
- `lib/database.py` - SQLite operations
- `lib/utils.py` - Parameter validation and general utilities
- `lib/logging_config.py` - Logging configuration

**Web Interface**
- Flask application with routes for home, forecast detail, API endpoints
- HTML templates with responsive design
- CSS styling and basic JavaScript
- Error handling (404, 500 pages)

**Database Schema**
- `forecast_metadata` table for forecast registration
- Per-forecast tables with probability, parameters, data_snapshot, timestamps
- Automatic table creation on model initialization

**Testing**
- 179 tests covering core utilities, web interface, forecast models
- Property-based tests for probability bounds, parameter validation, database persistence
- Integration tests for end-to-end workflows

## Version History

- **2.0.0** (2025-11-23) - US Recession V2 with temporal decay, backtesting, feature engineering
- **1.0.0** (2024-11-01) - Initial release with core framework and US Recession V1

## Upgrade Guide

### From 1.0.0 to 2.0.0

**No Breaking Changes** - V2 is fully backward compatible with V1.

**To Use V2 Features**:

1. **Update dependencies** (if needed):
   ```bash
   pip install -r requirements.txt
   ```

2. **Use V2 model directly**:
   ```python
   from forecasts.us_recession_2025.model_v2 import RecessionModelV2
   model = RecessionModelV2()
   breakdown = model.get_probability_breakdown()
   ```

3. **Run V2 standalone script**:
   ```bash
   python forecasts/us_recession_2025/run_forecast_v2.py
   ```

4. **Explore Jupyter notebooks**:
   ```bash
   cd forecasts/us_recession_2025/notebooks
   jupyter notebook
   ```

5. **Run backtests**:
   ```python
   from forecasts.us_recession_2025.backtesting import BacktestEngine
   engine = BacktestEngine(model_version='v2')
   results = engine.run_backtest(start_date, end_date, 'weekly')
   ```

**V1 Model Still Available**:
- V1 model continues to work: `from forecasts.us_recession_2025.model import RecessionModel`
- Web interface shows V1 by default (v2 not auto-discovered by design)
- All V1 tests continue to pass

## Future Plans

### Planned Features

- [ ] Additional forecast models (stock market, elections, etc.)
- [ ] Real-time data updates and notifications
- [ ] Advanced visualization dashboard
- [ ] Model ensemble methods
- [ ] API authentication and rate limiting
- [ ] Export functionality (CSV, JSON, PDF reports)
- [ ] Mobile-responsive web interface improvements
- [ ] Automated parameter optimization
- [ ] Forecast accuracy tracking over time
- [ ] User-configurable alerts and thresholds

### Under Consideration

- [ ] PostgreSQL support for production deployments
- [ ] Docker containerization
- [ ] Cloud deployment guides (AWS, GCP, Azure)
- [ ] GraphQL API
- [ ] WebSocket support for real-time updates
- [ ] Machine learning model integration
- [ ] Multi-user support with authentication
- [ ] Forecast sharing and collaboration features

## Contributing

See [Contributing Guide](development/CONTRIBUTING.md) for details on:
- How to report bugs
- How to suggest features
- How to submit pull requests
- Code style guidelines
- Testing requirements

## License

This project is provided as-is for educational and research purposes.
