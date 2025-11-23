# Requirements Document

## Introduction

This specification defines enhancements to the US Recession 2025 forecast model (v2). The improvements focus on four key areas: (1) historical backtesting to evaluate model performance over time, (2) Jupyter notebook infrastructure for data exploration and model analysis, (3) enhanced data sources and feature engineering, and (4) temporal decay modeling to incorporate time-to-deadline effects into probability estimates. These enhancements will transform the forecast from a point-in-time prediction to a robust, validated, and time-aware forecasting system that better reflects real-world prediction market dynamics.

## Glossary

- **Forecast Model**: The computational system that generates recession probability predictions based on economic indicators
- **Historical Backtesting**: The process of running the forecast model on historical data to evaluate its performance over time
- **Temporal Decay**: The adjustment of probability estimates based on time remaining until the forecast deadline
- **Jupyter Notebook**: Interactive computational environment for data analysis and visualization
- **FRED**: Federal Reserve Economic Data, the primary data source for economic indicators
- **Property-Based Testing**: Testing methodology that verifies universal properties across many randomly generated inputs
- **Time-to-Event**: The remaining duration between the current date and the forecast deadline (December 31, 2025)

## Requirements

### Requirement 1: Historical Backtesting System

**User Story:** As a forecaster, I want to evaluate how my model would have performed in the past, so that I can understand its accuracy and identify areas for improvement.

#### Acceptance Criteria

1. WHEN the system performs historical backtesting THEN the system SHALL retrieve economic indicator data for specified historical dates
2. WHEN the system runs the model on historical data THEN the system SHALL calculate recession probabilities as if running on those past dates
3. WHEN historical forecasts are generated THEN the system SHALL store them in a dedicated backtesting database table with historical timestamps
4. WHEN backtesting results are displayed THEN the system SHALL show probability evolution over time with actual recession periods marked
5. WHEN comparing backtest predictions to actual outcomes THEN the system SHALL calculate accuracy metrics including Brier score and calibration statistics

### Requirement 2: Jupyter Notebook Analysis Infrastructure

**User Story:** As a data scientist, I want structured Jupyter notebooks for data exploration and model analysis, so that I can visualize patterns, test hypotheses, and improve the forecasting model.

#### Acceptance Criteria

1. WHEN the notebooks directory is created THEN the system SHALL organize notebooks into logical categories including data exploration, model analysis, and backtesting visualization
2. WHEN a data exploration notebook is executed THEN the system SHALL load all economic indicators and display statistical summaries, correlation matrices, and time series visualizations
3. WHEN a model analysis notebook is executed THEN the system SHALL visualize indicator signals, weight sensitivity, and probability decomposition
4. WHEN notebooks access data THEN the system SHALL use the existing data fetching utilities from the lib module
5. WHEN notebooks are documented THEN the system SHALL include markdown cells explaining methodology, findings, and recommendations

### Requirement 3: Enhanced Data Sources and Feature Engineering

**User Story:** As a forecaster, I want to incorporate additional relevant economic indicators and engineered features, so that my model captures more dimensions of recession risk.

#### Acceptance Criteria

1. WHEN new economic indicators are added THEN the system SHALL fetch data from FRED for indicators including credit spreads, housing starts, manufacturing PMI, and retail sales
2. WHEN feature engineering is performed THEN the system SHALL calculate rate-of-change features for all indicators over multiple time windows
3. WHEN feature engineering is performed THEN the system SHALL calculate moving averages and volatility measures for key indicators
4. WHEN new features are integrated THEN the system SHALL maintain backward compatibility with the v1 model interface
5. WHEN indicator data is missing THEN the system SHALL handle missing values gracefully using forward-fill or neutral defaults

### Requirement 4: Temporal Decay Modeling

**User Story:** As a forecaster, I want my probability estimates to reflect the time remaining until the deadline, so that predictions become more confident as the deadline approaches without contradictory signals.

#### Acceptance Criteria

1. WHEN calculating temporal decay THEN the system SHALL compute the time-to-event as the number of days between the current date and December 31, 2025
2. WHEN applying temporal adjustment THEN the system SHALL use a two-stage process where base probability is calculated first, then adjusted based on time remaining
3. WHEN time remaining is large THEN the system SHALL apply minimal adjustment to the base probability
4. WHEN time remaining is small and base probability indicates low risk THEN the system SHALL adjust probability downward using a decay function
5. WHEN the temporal decay function is implemented THEN the system SHALL use industry-standard approaches such as exponential decay or sigmoid functions
6. WHEN temporal parameters are defined THEN the system SHALL make decay rate and threshold parameters adjustable through the configuration
7. WHEN temporal adjustment is applied THEN the system SHALL ensure the final probability remains within valid bounds of 0 to 1

### Requirement 5: Model Versioning and Comparison

**User Story:** As a forecaster, I want to maintain both v1 and v2 models simultaneously, so that I can compare their performance and ensure v2 improvements are genuine.

#### Acceptance Criteria

1. WHEN v2 model is implemented THEN the system SHALL preserve the existing v1 model code without modification
2. WHEN both models are available THEN the system SHALL store their results in separate database tables
3. WHEN displaying forecasts THEN the system SHALL show both v1 and v2 predictions side-by-side for comparison
4. WHEN running backtests THEN the system SHALL evaluate both model versions on the same historical data
5. WHEN comparing models THEN the system SHALL calculate relative performance metrics including accuracy differences and calibration improvements

### Requirement 6: Backtesting Database Schema

**User Story:** As a system architect, I want a well-designed database schema for backtesting results, so that historical model performance can be efficiently stored and queried.

#### Acceptance Criteria

1. WHEN the backtesting table is created THEN the system SHALL include columns for backtest date, forecast date, probability, model version, and parameters
2. WHEN backtesting results are stored THEN the system SHALL include the complete indicator snapshot for that historical date
3. WHEN querying backtesting results THEN the system SHALL support filtering by date range, model version, and probability threshold
4. WHEN storing backtesting data THEN the system SHALL prevent duplicate entries for the same backtest date and model version combination
5. WHEN backtesting data is retrieved THEN the system SHALL return results ordered chronologically for time series analysis

### Requirement 7: Temporal Decay Calibration

**User Story:** As a forecaster, I want to calibrate the temporal decay function using historical data, so that the time adjustment reflects empirically observed patterns.

#### Acceptance Criteria

1. WHEN calibrating temporal decay THEN the system SHALL analyze historical recession probabilities at various time distances from actual recessions
2. WHEN calibration is performed THEN the system SHALL fit decay parameters to minimize prediction error on historical data
3. WHEN decay parameters are determined THEN the system SHALL document the calibration methodology and resulting parameter values
4. WHEN temporal adjustment is applied THEN the system SHALL use the calibrated parameters as defaults
5. WHEN users adjust temporal parameters THEN the system SHALL validate that adjustments produce reasonable probability distributions

### Requirement 8: Notebook Execution and Reproducibility

**User Story:** As a data scientist, I want notebooks to be reproducible and well-documented, so that analysis can be verified and repeated by others.

#### Acceptance Criteria

1. WHEN notebooks are created THEN the system SHALL include a requirements cell that imports all necessary dependencies
2. WHEN notebooks access data THEN the system SHALL use relative paths and environment variables for configuration
3. WHEN notebooks generate visualizations THEN the system SHALL use consistent styling and color schemes
4. WHEN notebooks are documented THEN the system SHALL include a README explaining the purpose and execution order of each notebook
5. WHEN notebooks are executed THEN the system SHALL complete without errors on a fresh environment with proper dependencies installed

### Requirement 9: Web Interface Enhancements for V2 Features

**User Story:** As a user viewing forecasts in the web interface, I want to see v2-specific features including temporal decay visualization, so that I can understand how the model adjusts probabilities over time.

#### Acceptance Criteria

1. WHEN displaying the v2 forecast THEN the system SHALL show both base probability and temporally-adjusted probability with clear labels
2. WHEN the temporal decay is applied THEN the system SHALL display a visualization showing how probability would evolve as the deadline approaches
3. WHEN viewing v2 forecast details THEN the system SHALL show the number of days remaining until the forecast deadline
4. WHEN temporal adjustment metadata is available THEN the system SHALL display the decay method, decay rate, and whether the threshold was applied
5. WHEN the web interface renders v2 forecasts THEN the system SHALL maintain the generic forecast discovery mechanism without hardcoding v2-specific logic
