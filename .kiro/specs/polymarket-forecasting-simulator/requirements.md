# Requirements Document

## Introduction

The Polymarket Forecasting Simulator is a Python-based system for building and managing probabilistic forecasts for prediction markets. The system enables users to develop individual forecasting models for specific problems (e.g., "Will the US have a recession by end of 2025?"), visualize results through a simple web interface, and adjust parameters to simulate different scenarios. The architecture follows Nate Silver's approach to real-world modeling, with modular forecast components and a library of reusable utilities.

## Glossary

- **Forecasting System**: The complete Python application including models, utilities, and web interface
- **Forecast Model**: A Python script that generates probability predictions (0-1) for a specific problem
- **Problem**: A specific prediction question (e.g., recession forecast, election outcome)
- **Probability Output**: A numerical value between 0 and 1 representing the likelihood of an event
- **Web Interface**: The Flask/Gradio/Django frontend for visualizing and interacting with forecasts
- **Forecast Library**: The collection of all implemented forecast models organized by problem
- **Parameter Simulator**: Frontend functionality allowing users to adjust model inputs and observe output changes
- **Local Storage**: SQLite database and file system storage for data persistence
- **Forecast Table**: A dedicated SQLite table storing data and results for a specific forecast model

## Requirements

### Requirement 1

**User Story:** As a forecaster, I want to organize my forecasting code into a modular structure, so that I can scale to multiple prediction problems independently.

#### Acceptance Criteria

1. THE Forecasting System SHALL provide a lib directory containing reusable utilities and shared code
2. THE Forecasting System SHALL organize each forecast model in a dedicated problem-specific directory
3. WHEN a new forecast model is added THEN the Forecasting System SHALL maintain separation between problem-specific code and shared utilities
4. THE Forecasting System SHALL allow unlimited forecast models to be added without modifying existing models
5. WHEN accessing forecast models THEN the Forecasting System SHALL use a consistent directory structure across all problems

### Requirement 2

**User Story:** As a forecaster, I want to build a model that predicts US recession probability by end of 2025, so that I can make informed betting decisions on Polymarket.

#### Acceptance Criteria

1. THE Forecasting System SHALL implement a recession forecast model that outputs a probability between 0 and 1
2. WHEN the recession model executes THEN the Forecasting System SHALL collect and process relevant economic indicators
3. THE Forecasting System SHALL identify and incorporate appropriate data sources for recession prediction
4. WHEN calculating recession probability THEN the Forecasting System SHALL apply statistical or machine learning techniques to generate the forecast
5. THE Forecasting System SHALL store recession model data in a dedicated SQLite table

### Requirement 3

**User Story:** As a forecaster, I want a library of reusable utilities, so that I can avoid duplicating common functionality across different forecast models.

#### Acceptance Criteria

1. THE Forecasting System SHALL provide utility functions for data fetching and processing in the lib directory
2. THE Forecasting System SHALL provide utility functions for probability calculations in the lib directory
3. THE Forecasting System SHALL provide utility functions for database operations in the lib directory
4. WHEN a forecast model requires common functionality THEN the Forecasting System SHALL import utilities from the lib directory
5. THE Forecasting System SHALL maintain backward compatibility when updating shared utilities

### Requirement 4

**User Story:** As a forecaster, I want to visualize my forecasts through a simple web interface, so that I can easily review and compare predictions.

#### Acceptance Criteria

1. THE Forecasting System SHALL implement a web interface using Flask, Gradio, or Django
2. WHEN the Web Interface starts THEN the Forecasting System SHALL display all available forecast models
3. THE Web Interface SHALL provide a sidebar or navigation component listing all forecast models
4. WHEN a user selects a forecast model THEN the Web Interface SHALL display the current probability prediction
5. THE Web Interface SHALL present forecast results in a clear, readable format

### Requirement 5

**User Story:** As a forecaster, I want to adjust model parameters through the web interface, so that I can simulate different scenarios and understand model sensitivity.

#### Acceptance Criteria

1. WHEN viewing a forecast model THEN the Web Interface SHALL display adjustable parameters for that model
2. WHEN a user modifies a parameter value THEN the Web Interface SHALL recalculate the forecast probability
3. WHEN parameters are updated THEN the Web Interface SHALL display the new probability output immediately
4. THE Web Interface SHALL validate parameter inputs to ensure they are within acceptable ranges
5. WHEN parameter simulation completes THEN the Web Interface SHALL preserve the original model state for future runs

### Requirement 6

**User Story:** As a forecaster, I want to persist forecast data and results locally, so that I can track predictions over time without external dependencies.

#### Acceptance Criteria

1. THE Forecasting System SHALL use SQLite for relational data storage
2. THE Forecasting System SHALL use the local file system for non-relational data storage
3. WHEN a new forecast model is created THEN the Forecasting System SHALL create a dedicated SQLite table for that forecast
4. THE Forecasting System SHALL store historical probability outputs with timestamps
5. WHEN storing forecast data THEN the Forecasting System SHALL ensure data integrity and prevent corruption

### Requirement 7

**User Story:** As a forecaster, I want the web interface to reflect the project's folder structure, so that adding new forecasts automatically updates the interface.

#### Acceptance Criteria

1. WHEN the Web Interface initializes THEN the Forecasting System SHALL scan the project directory for forecast models
2. THE Web Interface SHALL dynamically generate navigation based on discovered forecast directories
3. WHEN a new forecast directory is added THEN the Web Interface SHALL include it in the navigation without code changes
4. THE Forecasting System SHALL identify forecast models by their directory structure and naming conventions
5. WHEN a forecast directory is removed THEN the Web Interface SHALL exclude it from navigation on next startup

### Requirement 8

**User Story:** As a forecaster, I want to follow Nate Silver's modeling principles, so that my forecasts are rigorous and well-reasoned.

#### Acceptance Criteria

1. THE Forecasting System SHALL incorporate multiple data sources when building forecast models
2. WHEN generating probabilities THEN the Forecasting System SHALL apply statistical reasoning to combine evidence
3. THE Forecasting System SHALL document assumptions and limitations for each forecast model
4. THE Forecasting System SHALL update forecasts as new data becomes available
5. WHEN presenting forecasts THEN the Forecasting System SHALL include uncertainty estimates or confidence intervals where applicable
