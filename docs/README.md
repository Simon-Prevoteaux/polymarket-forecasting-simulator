# Documentation Index

Welcome to the Polymarket Forecasting Simulator documentation. This guide will help you find the information you need quickly.

## 📚 Documentation Structure

### Getting Started
- **[Project Overview](../README.md)** - Main project README with installation and quick start
- **[Setup Guide](../SETUP.md)** - Detailed setup instructions

### Core Concepts
- **[Architecture Overview](architecture/OVERVIEW.md)** - System design and components
- **[Forecast Model Interface](architecture/FORECAST_INTERFACE.md)** - How to implement forecast models
- **[Database Schema](architecture/DATABASE_SCHEMA.md)** - Database structure and tables

### US Recession Forecast
- **[US Recession Overview](../forecasts/us_recession_2025/README.md)** - Complete model documentation
- **[Model Comparison: V1 vs V2](forecasts/US_RECESSION_V1_VS_V2.md)** - Differences between versions
- **[Jupyter Notebooks Guide](../forecasts/us_recession_2025/notebooks/README.md)** - Interactive analysis

### Advanced Features
- **[Temporal Decay](features/TEMPORAL_DECAY.md)** - Time-aware probability adjustments
- **[Historical Backtesting](features/BACKTESTING.md)** - Model validation and performance metrics
- **[Feature Engineering](features/FEATURE_ENGINEERING.md)** - Derived indicators and transformations

### Development
- **[Testing Guide](development/TESTING.md)** - How to write and run tests
- **[Adding New Forecasts](development/ADDING_FORECASTS.md)** - Step-by-step guide
- **[API Reference](development/API_REFERENCE.md)** - Python and REST API documentation

### Implementation History
- **[Task Summaries](implementation/)** - Detailed implementation notes by task
- **[Change Log](CHANGELOG.md)** - Version history and changes

## 🎯 Quick Navigation

### I want to...

**Understand the project**
→ Start with [Project Overview](../README.md)

**Set up the project**
→ Follow [Setup Guide](../SETUP.md)

**Run a forecast**
→ See [US Recession Overview](../forecasts/us_recession_2025/README.md)

**Understand temporal decay**
→ Read [Temporal Decay Guide](features/TEMPORAL_DECAY.md)

**Validate model performance**
→ Check [Backtesting Guide](features/BACKTESTING.md)

**Add a new forecast**
→ Follow [Adding Forecasts Guide](development/ADDING_FORECASTS.md)

**Run tests**
→ See [Testing Guide](development/TESTING.md)

**Understand the code**
→ Review [Architecture Overview](architecture/OVERVIEW.md)

**Use the API**
→ Check [API Reference](development/API_REFERENCE.md)

**Explore data interactively**
→ Use [Jupyter Notebooks](../forecasts/us_recession_2025/notebooks/README.md)

## 📖 Documentation by Role

### For Users
1. [Project Overview](../README.md)
2. [US Recession Forecast](../forecasts/us_recession_2025/README.md)
3. [Temporal Decay Explained](features/TEMPORAL_DECAY.md)
4. [Jupyter Notebooks](../forecasts/us_recession_2025/notebooks/README.md)

### For Developers
1. [Architecture Overview](architecture/OVERVIEW.md)
2. [Adding New Forecasts](development/ADDING_FORECASTS.md)
3. [Testing Guide](development/TESTING.md)
4. [API Reference](development/API_REFERENCE.md)

### For Data Scientists
1. [Feature Engineering](features/FEATURE_ENGINEERING.md)
2. [Backtesting Guide](features/BACKTESTING.md)
3. [Temporal Decay Methodology](features/TEMPORAL_DECAY.md)
4. [Jupyter Notebooks](../forecasts/us_recession_2025/notebooks/README.md)

### For Stakeholders
1. [Project Overview](../README.md)
2. [US Recession V1 vs V2](forecasts/US_RECESSION_V1_VS_V2.md)
3. [Model Performance](features/BACKTESTING.md#performance-metrics)

## 🔍 Search by Topic

### Temporal Decay
- [Temporal Decay Guide](features/TEMPORAL_DECAY.md) - Complete methodology
- [Temporal Adjustment Library](features/TEMPORAL_DECAY.md#temporal-adjustment-library) - Usage and API
- [Decay Methods Comparison](features/TEMPORAL_DECAY.md#available-methods) - All 6 methods explained

### Backtesting
- [Backtesting Guide](features/BACKTESTING.md) - Complete guide
- [Performance Metrics](features/BACKTESTING.md#performance-metrics-explained) - Brier score, calibration, etc.
- [Backtesting Workflows](features/BACKTESTING.md#backtesting-workflows) - Common use cases

### Testing
- [Testing Guide](development/TESTING.md) - Overview and organization
- [Property-Based Testing](development/TESTING.md#property-based-testing) - Using Hypothesis
- [Test Organization](development/TESTING.md#test-organization) - Where tests live

### Web Interface
- [Flask Application](architecture/OVERVIEW.md#web-interface) - Structure and routes
- [API Endpoints](development/API_REFERENCE.md#rest-api) - REST API documentation
- [Templates](architecture/OVERVIEW.md#templates) - HTML templates

## 📝 Recent Updates

See [CHANGELOG.md](CHANGELOG.md) for a complete version history.

### Latest (V2.0)
- Enhanced temporal decay with 6 methods
- Historical backtesting infrastructure
- Feature engineering pipeline
- 5 Jupyter notebooks for analysis
- Web interface temporal visualization
- Comprehensive documentation reorganization

## 🤝 Contributing

See [Contributing Guide](development/CONTRIBUTING.md) for guidelines on:
- Code style
- Pull request process
- Testing requirements
- Documentation standards

## 📧 Support

For questions or issues:
1. Check the relevant documentation section
2. Review [Troubleshooting](../README.md#troubleshooting)
3. Check logs in `logs/application.log`
4. Run tests to verify setup: `pytest tests/`
