# Implementation Plan

- [x] 1. Set up v2 project structure and configuration
  - Create new module files (model_v2.py, data_v2.py, config_v2.py, features.py, temporal.py, backtesting.py)
  - Create notebooks directory with README
  - Update __init__.py to export v2 classes
  - _Requirements: All_

- [x] 2. Implement enhanced data fetcher (data_v2.py)
  - [x] 2.1 Add new FRED indicator series IDs to configuration
    - Add BAA10Y (credit spread), HOUST (housing starts), NAPM (manufacturing PMI)
    - Add RSXFS (retail sales), DCOILWTICO (oil prices), VIXCLS (VIX)
    - _Requirements: 3.1_
  
  - [x] 2.2 Implement fetch_economic_indicators_v2 function
    - Add as_of_date parameter for historical data fetching
    - Fetch all v1 indicators plus new v2 indicators
    - Handle missing indicators with neutral defaults
    - Return enhanced data structure with all indicators
    - _Requirements: 1.1, 3.1, 3.5_
  
  - [x] 2.3 Write property test for historical data temporal consistency
    - **Property 1: Historical data retrieval preserves temporal consistency**
    - **Validates: Requirements 1.1**
  
  - [ ]* 2.4 Write unit tests for new indicator fetching
    - Test each new indicator individually
    - Test missing indicator handling
    - Mock FRED API responses
    - _Requirements: 3.1, 3.5_

- [x] 3. Implement feature engineering module (features.py)
  - [x] 3.1 Create FeatureEngineer class
    - Implement calculate_rate_of_change method (30d, 90d, 180d periods)
    - Implement calculate_moving_averages method (30d, 90d windows)
    - Implement calculate_volatility method (30d rolling std dev)
    - Implement engineer_features method to generate all features
    - _Requirements: 3.2, 3.3_
  
  - [x] 3.2 Add missing data handling in feature calculations
    - Forward-fill for gaps in time series
    - Skip features with insufficient data
    - Return None for uncalculable features
    - _Requirements: 3.5_
  
  - [ ]* 3.3 Write property test for feature engineering determinism
    - **Property 4: Feature engineering determinism**
    - **Validates: Requirements 3.2**
  
  - [ ]* 3.4 Write property test for rate of change correctness
    - **Property 5: Rate of change calculation correctness**
    - **Validates: Requirements 3.2**
  
  - [ ]* 3.5 Write property test for missing data handling
    - **Property 15: Feature engineering handles missing data**
    - **Validates: Requirements 3.5**
  
  - [ ]* 3.6 Write unit tests for feature calculations
    - Test rate of change with known values
    - Test moving averages with known values
    - Test volatility calculations
    - Test edge cases (single observation, all zeros)
    - _Requirements: 3.2, 3.3_

- [x] 4. Implement temporal decay module (temporal.py)
  - [x] 4.1 Implement time-to-event calculation
    - Create calculate_time_to_event function
    - Handle edge cases (past deadline, invalid dates)
    - _Requirements: 4.1_
  
  - [x] 4.2 Implement exponential decay function
    - Create exponential_decay_adjustment function
    - Apply decay only below threshold
    - Use exponential formula with configurable decay rate
    - _Requirements: 4.2, 4.4_
  
  - [x] 4.3 Implement sigmoid decay function
    - Create sigmoid_decay_adjustment function
    - Use sigmoid centered at midpoint
    - Configurable steepness parameter
    - _Requirements: 4.2, 4.4_
  
  - [x] 4.4 Create TemporalAdjuster class
    - Initialize with decay method and parameters
    - Implement adjust_probability method
    - Return adjusted probability and metadata
    - Validate all outputs in [0, 1]
    - _Requirements: 4.2, 4.6, 4.7_
  
  - [ ]* 4.5 Write property test for temporal decay monotonicity
    - **Property 6: Temporal decay monotonicity**
    - **Validates: Requirements 4.4**
  
  - [ ]* 4.6 Write property test for temporal decay boundary behavior
    - **Property 7: Temporal decay boundary behavior**
    - **Validates: Requirements 4.2, 4.4**
  
  - [ ]* 4.7 Write property test for temporal decay preserves high probabilities
    - **Property 8: Temporal decay preserves high probabilities**
    - **Validates: Requirements 4.4**
  
  - [ ]* 4.8 Write property test for parameter validity
    - **Property 13: Calibration parameter validity**
    - **Validates: Requirements 7.4**
  
  - [ ]* 4.9 Write unit tests for temporal decay functions
    - Test exponential decay with known parameters
    - Test sigmoid decay with known parameters
    - Test threshold behavior
    - Test parameter validation
    - _Requirements: 4.2, 4.4, 4.6, 4.7_

- [x] 5. Implement backtesting engine (backtesting.py)
  - [x] 5.1 Create backtesting database schema
    - Create forecast_us_recession_2025_backtest table
    - Add indexes for backtest_date and model_version
    - Add unique constraint on (backtest_date, model_version)
    - _Requirements: 6.1, 6.4_
  
  - [x] 5.2 Implement BacktestEngine class
    - Create __init__ with model_version parameter
    - Implement run_backtest method (daily/weekly/monthly frequency)
    - Fetch historical data for each backtest date
    - Run model and store results
    - _Requirements: 1.2, 1.3_
  
  - [x] 5.3 Implement performance metrics calculation
    - Create calculate_performance_metrics method
    - Calculate Brier score
    - Calculate calibration statistics
    - Calculate discrimination metrics (AUC-ROC if applicable)
    - _Requirements: 1.5_
  
  - [x] 5.4 Implement model comparison functionality
    - Create compare_models method
    - Compare v1 vs v2 performance
    - Calculate relative metrics
    - _Requirements: 5.4, 5.5_
  
  - [ ]* 5.5 Write property test for backtest probability bounds
    - **Property 2: Backtest probability bounds**
    - **Validates: Requirements 1.2**
  
  - [ ]* 5.6 Write property test for backtest storage completeness
    - **Property 3: Backtest storage completeness**
    - **Validates: Requirements 1.3**
  
  - [ ]* 5.7 Write property test for backtest uniqueness constraint
    - **Property 10: Backtest uniqueness constraint**
    - **Validates: Requirements 6.4**
  
  - [ ]* 5.8 Write property test for chronological ordering
    - **Property 14: Backtest chronological ordering**
    - **Validates: Requirements 6.3**
  
  - [ ]* 5.9 Write unit tests for backtesting
    - Test backtest result storage
    - Test performance metric calculations
    - Test model comparison logic
    - Mock historical data fetching
    - _Requirements: 1.2, 1.3, 1.5, 5.4_

- [x] 6. Implement RecessionModelV2 class (model_v2.py)
  - [x] 6.1 Create RecessionModelV2 class inheriting from ForecastModel
    - Initialize with v2 configuration
    - Create v2 database table
    - Set up feature engineer and temporal adjuster
    - _Requirements: 5.1_
  
  - [x] 6.2 Implement calculate_base_probability method
    - Fetch indicators using data_v2
    - Engineer features
    - Calculate indicator signals (reuse v1 logic)
    - Combine signals with weights
    - Return base probability before temporal adjustment
    - _Requirements: 4.2_
  
  - [x] 6.3 Implement calculate_probability method
    - Call calculate_base_probability
    - Apply temporal decay if enabled
    - Store result in v2 database table
    - Support as_of_date parameter for backtesting
    - _Requirements: 1.2, 4.2, 5.2_
  
  - [x] 6.4 Implement get_probability_breakdown method
    - Return base probability, adjusted probability
    - Return indicator signals and feature contributions
    - Return temporal metadata (decay method, rate, adjustment factor)
    - Return days remaining
    - _Requirements: 9.1, 9.3, 9.4_
  
  - [x] 6.5 Implement ForecastModel interface methods
    - get_name, get_description, get_parameters
    - get_last_updated, get_data_sources
    - Ensure backward compatibility with v1 interface
    - _Requirements: 3.4, 5.1_
  
  - [ ]* 6.6 Write property test for model version isolation
    - **Property 9: Model version isolation**
    - **Validates: Requirements 5.2**
  
  - [ ]* 6.7 Write property test for missing indicator handling
    - **Property 12: Missing indicator handling**
    - **Validates: Requirements 3.5**
  
  - [ ]* 6.8 Write unit tests for RecessionModelV2
    - Test probability calculation with default parameters
    - Test with custom parameters
    - Test temporal decay application
    - Test probability breakdown
    - Test backward compatibility
    - _Requirements: 4.2, 5.1, 9.1, 9.3, 9.4_

- [x] 7. Create v2 configuration (config_v2.py)
  - Add new indicator series IDs and thresholds
  - Add temporal decay default parameters
  - Add feature engineering configuration
  - Add v2-specific parameter schemas
  - _Requirements: 3.1, 4.6_

- [x] 8. Create standalone execution script (run_forecast_v2.py)
  - Import RecessionModelV2
  - Display base and adjusted probabilities
  - Show all indicators and features
  - Display temporal adjustment details
  - Show historical forecasts with trend analysis
  - _Requirements: 9.1, 9.3, 9.4_

- [x] 9. Checkpoint - Ensure all core v2 model tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Create Jupyter notebook: Data Exploration (notebooks/01_data_exploration.ipynb)
  - [x] 10.1 Set up notebook structure and imports
    - Add project root to path
    - Import data fetching utilities
    - Import pandas, matplotlib, seaborn
    - Set visualization style
    - _Requirements: 8.1, 8.2_
  
  - [x] 10.2 Load and visualize all economic indicators
    - Fetch 5 years of historical data
    - Create time series plots for each indicator
    - Mark historical recession periods
    - _Requirements: 2.2_
  
  - [x] 10.3 Generate statistical summaries
    - Calculate mean, std, min, max for each indicator
    - Create distribution plots
    - Identify outliers
    - _Requirements: 2.2_
  
  - [x] 10.4 Create correlation analysis
    - Calculate correlation matrix
    - Create heatmap visualization
    - Identify highly correlated indicators
    - _Requirements: 2.2_
  
  - [x] 10.5 Analyze missing data
    - Identify gaps in time series
    - Visualize data availability
    - Document data quality issues
    - _Requirements: 2.2_

- [x] 11. Create Jupyter notebook: Indicator Analysis (notebooks/02_indicator_analysis.ipynb)
  - [x] 11.1 Set up notebook structure
    - Import necessary libraries
    - Load historical data
    - Define recession periods
    - _Requirements: 8.1, 8.2_
  
  - [x] 11.2 Analyze individual indicators
    - Deep dive into each indicator
    - Plot indicator vs recession periods
    - Calculate lead/lag relationships
    - _Requirements: 2.2_
  
  - [x] 11.3 Assess signal quality
    - Calculate true positive/false positive rates
    - Identify optimal thresholds
    - Evaluate predictive power
    - _Requirements: 2.2_

- [x] 12. Create Jupyter notebook: Model Comparison (notebooks/03_model_comparison.ipynb)
  - [x] 12.1 Set up notebook structure
    - Import v1 and v2 models
    - Load current data
    - _Requirements: 8.1, 8.2_
  
  - [x] 12.2 Compare v1 and v2 predictions
    - Run both models on same data
    - Display side-by-side probabilities
    - Show probability breakdown for v2
    - _Requirements: 2.3, 5.3_
  
  - [x] 12.3 Analyze parameter sensitivity
    - Test different weight combinations
    - Visualize impact on probability
    - Identify most influential parameters
    - _Requirements: 2.3_
  
  - [x] 12.4 Visualize feature importance
    - Show contribution of each feature
    - Compare v1 indicators vs v2 features
    - _Requirements: 2.3_
  
  - [x] 12.5 Write property test for notebook data consistency
    - **Property 11: Notebook data access consistency**
    - **Validates: Requirements 2.4**

- [ ] 13. Create Jupyter notebook: Backtesting Results (notebooks/04_backtesting_results.ipynb)
  - [ ] 13.1 Set up notebook structure
    - Import backtesting engine
    - Load historical backtest results
    - _Requirements: 8.1, 8.2_
  
  - [ ] 13.2 Visualize historical performance
    - Plot probability evolution over time
    - Mark actual recession periods
    - Show v1 vs v2 comparison
    - _Requirements: 1.4, 2.3_
  
  - [ ] 13.3 Calculate and display performance metrics
    - Show Brier score decomposition
    - Create calibration plots
    - Display discrimination metrics
    - _Requirements: 1.5_
  
  - [ ] 13.4 Analyze forecast errors
    - Identify periods of over/under-prediction
    - Analyze error patterns
    - Suggest improvements
    - _Requirements: 2.3_

- [ ] 14. Create Jupyter notebook: Temporal Calibration (notebooks/05_temporal_calibration.ipynb)
  - [ ] 14.1 Set up notebook structure
    - Import temporal decay functions
    - Load historical data
    - _Requirements: 8.1, 8.2_
  
  - [ ] 14.2 Visualize decay functions
    - Plot exponential decay curves
    - Plot sigmoid decay curves
    - Compare different parameter values
    - _Requirements: 2.3_
  
  - [ ] 14.3 Calibrate decay parameters
    - Fit parameters to historical data
    - Minimize Brier score
    - Validate on held-out data
    - _Requirements: 7.2, 7.4_
  
  - [ ] 14.4 Analyze sensitivity to parameters
    - Test range of decay rates
    - Test range of thresholds
    - Visualize impact on forecasts
    - _Requirements: 2.3, 7.5_

- [ ] 15. Create notebooks README
  - Document purpose of each notebook
  - Explain execution order
  - List dependencies
  - Provide usage examples
  - _Requirements: 8.4_

- [ ] 16. Checkpoint - Ensure all notebooks execute successfully
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Extend ForecastModel base interface (forecasts/__init__.py)
  - [ ] 17.1 Add optional get_probability_breakdown method
    - Add method signature to base class
    - Return None by default
    - Document expected return structure
    - _Requirements: 9.5_
  
  - [ ]* 17.2 Write unit test for interface extension
    - Test that v1 model works without breakdown
    - Test that v2 model provides breakdown
    - Test backward compatibility
    - _Requirements: 3.4, 9.5_

- [ ] 18. Enhance Flask API endpoints (web/app.py)
  - [ ] 18.1 Create /api/forecast/<name>/breakdown endpoint
    - Check if model has get_probability_breakdown method
    - Return breakdown data if available
    - Return basic probability if not available
    - _Requirements: 9.1, 9.3, 9.4_
  
  - [ ] 18.2 Update /forecast/<name> route
    - Get breakdown data if available
    - Pass breakdown to template
    - Set show_temporal flag
    - _Requirements: 9.1, 9.5_
  
  - [ ]* 18.3 Write property test for web interface probability display
    - **Property 16: Web interface displays both probabilities**
    - **Validates: Requirements 9.1**
  
  - [ ]* 18.4 Write property test for days remaining display
    - **Property 18: Days remaining display**
    - **Validates: Requirements 9.3**
  
  - [ ]* 18.5 Write property test for temporal metadata completeness
    - **Property 19: Temporal metadata completeness**
    - **Validates: Requirements 9.4**
  
  - [ ]* 18.6 Write unit tests for new API endpoints
    - Test breakdown endpoint with v1 model
    - Test breakdown endpoint with v2 model
    - Test error handling
    - _Requirements: 9.1, 9.3, 9.4, 9.5_

- [ ] 19. Update forecast.html template (web/templates/forecast.html)
  - [ ] 19.1 Add conditional temporal decay section
    - Check show_temporal flag
    - Display base and adjusted probabilities
    - Display days remaining
    - Display temporal metadata
    - _Requirements: 9.1, 9.3, 9.4_
  
  - [ ] 19.2 Add temporal decay chart container
    - Add canvas element for Chart.js
    - Add chart container styling
    - _Requirements: 9.2_

- [ ] 20. Add temporal decay visualization CSS (web/static/css/style.css)
  - Add .temporal-decay-section styles
  - Add .probability-comparison grid styles
  - Add .prob-item card styles
  - Add .decay-chart-container styles
  - Add .decay-metadata styles
  - Ensure responsive design
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [ ] 21. Implement temporal decay chart JavaScript (web/static/js/main.js)
  - [ ] 21.1 Implement calculateDecayedProbability function
    - Apply exponential decay formula
    - Handle threshold logic
    - _Requirements: 9.2_
  
  - [ ] 21.2 Implement renderTemporalDecayChart function
    - Generate projection data points
    - Create Chart.js line chart
    - Add base probability reference line
    - Mark current position
    - Configure tooltips and legend
    - _Requirements: 9.2_
  
  - [ ] 21.3 Add chart initialization on page load
    - Check if breakdown data exists
    - Initialize chart with data
    - Handle errors gracefully
    - _Requirements: 9.2_
  
  - [ ]* 21.4 Write property test for temporal projection data
    - **Property 17: Temporal decay projection data generation**
    - **Validates: Requirements 9.2**
  
  - [ ]* 21.5 Write unit tests for chart functions
    - Test calculateDecayedProbability with known inputs
    - Test projection data generation
    - Test edge cases (0 days, large days)
    - _Requirements: 9.2_

- [ ] 22. Add Chart.js library to base template (web/templates/base.html)
  - Add Chart.js CDN link
  - Ensure loaded before main.js
  - _Requirements: 9.2_

- [ ] 23. Final integration testing
  - [ ]* 23.1 Test v1 model display (no temporal section)
    - Verify v1 forecast displays normally
    - Verify no temporal section shown
    - _Requirements: 3.4, 9.5_
  
  - [ ]* 23.2 Test v2 model display (with temporal section)
    - Verify both probabilities displayed
    - Verify temporal chart renders
    - Verify metadata displayed
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [ ]* 23.3 Test other forecasts (election_2028)
    - Verify election forecast displays normally
    - Verify no temporal section shown
    - _Requirements: 9.5_
  
  - [ ]* 23.4 Test responsive design
    - Test on mobile viewport
    - Test on tablet viewport
    - Test on desktop viewport
    - _Requirements: 9.1, 9.2_

- [ ] 24. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 25. Documentation and cleanup
  - Update main README with v2 features
  - Update us_recession_2025 README with v2 documentation
  - Document temporal decay methodology
  - Document backtesting usage
  - Document notebook usage
  - Add examples and screenshots
  - _Requirements: All_
