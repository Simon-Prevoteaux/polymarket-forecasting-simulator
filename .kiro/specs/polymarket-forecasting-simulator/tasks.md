# Implementation Plan

- [x] 1. Set up project structure and core utilities
  - Create directory structure: lib/, forecasts/, web/, data/
  - Create __init__.py files for Python packages
  - Set up requirements.txt with dependencies (Flask, pandas, requests, hypothesis, pytest)
  - Create README.md with project overview
  - _Requirements: 1.1, 1.2, 3.1, 3.2, 3.3_

- [x] 2. Implement database utilities
  - Create lib/database.py with SQLite connection management
  - Implement get_connection() function
  - Implement create_forecast_table() function
  - Implement save_forecast_result() function
  - Implement get_forecast_history() function
  - Create data/forecasts.db and forecast_metadata table
  - _Requirements: 6.1, 6.3, 6.4_

- [x] 2.1 Write property test for database persistence
  - **Property 3: Database persistence**
  - **Validates: Requirements 2.5, 6.4**

- [x] 2.2 Write property test for forecast table creation
  - **Property 7: Forecast table creation**
  - **Validates: Requirements 6.3**

- [x] 2.3 Validate database utilities
  - Write simple test script to create a test table and insert/retrieve data
  - Verify database file is created and tables exist
  - _Validation checkpoint_

- [x] 3. Implement probability calculation utilities
  - Create lib/probability.py with probability helper functions
  - Implement normalize_probability() function
  - Implement combine_probabilities() function
  - Implement logistic_transform() function
  - Implement bayesian_update() function
  - _Requirements: 3.2_

- [x] 3.1 Write unit tests for probability utilities
  - Test normalize_probability with edge cases (negative, >1, valid range)
  - Test combine_probabilities with empty, single, and multiple probabilities
  - Test logistic_transform with various inputs
  - _Requirements: 3.2_

- [x] 3.2 Write property test for probability bounds
  - **Property 1: Probability bounds enforcement**
  - **Validates: Requirements 2.1**

- [x] 3.3 Validate probability utilities
  - Run unit tests to verify all probability functions work correctly
  - Test with sample data to ensure outputs are in valid range
  - _Validation checkpoint_

- [x] 4. Implement data fetching utilities
  - Create lib/data_fetcher.py with data retrieval functions
  - Implement fetch_fred_data() function with API integration
  - Implement cache_data() and get_cached_data() functions
  - Implement error handling for network failures and rate limits
  - _Requirements: 3.1, 8.1_

- [x] 4.1 Write unit tests for data fetching
  - Test cache functionality with expiration
  - Test error handling for network failures
  - Mock FRED API responses for testing
  - _Requirements: 3.1_

- [x] 4.2 Validate data fetching utilities
  - Test fetching real data from FRED API (requires API key)
  - Verify caching works and reduces API calls
  - Test error handling with invalid series IDs
  - _Validation checkpoint_

- [x] 5. Implement general utilities
  - Create lib/utils.py with helper functions
  - Implement load_config() function
  - Implement setup_logging() function
  - Implement validate_parameters() function
  - _Requirements: 3.3_

- [x] 5.1 Write property test for parameter validation
  - **Property 5: Parameter validation**
  - **Validates: Requirements 5.4**

- [x] 5.2 Validate general utilities
  - Test parameter validation with valid and invalid inputs
  - Verify logging configuration works
  - _Validation checkpoint_

- [x] 6. Implement forecast model base interface
  - Create forecasts/__init__.py with ForecastModel base class
  - Define abstract methods: get_name(), get_description(), get_parameters(), calculate_probability()
  - Add get_last_updated() method
  - _Requirements: 1.2, 1.3_

- [x] 7. Implement US recession forecast model
  - Create forecasts/us_recession_2025/ directory structure
  - Create config.py with model parameters and data source configuration
  - Create data.py with functions to fetch economic indicators (yield curve, unemployment, GDP, consumer confidence, LEI, jobless claims)
  - Implement model.py with RecessionModel class extending ForecastModel
  - Implement calculate_probability() using weighted logistic regression approach
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 8.1, 8.2_

- [x] 7.1 Write property test for economic indicators collection
  - **Property 2: Economic indicators collection**
  - **Validates: Requirements 2.2**

- [x] 7.2 Write unit tests for recession model
  - Test with known historical recession data
  - Test with economic expansion data
  - Test with default parameters
  - Test handling of missing indicators
  - _Requirements: 2.1, 2.2_

- [x] 7.3 Validate recession model
  - Run model with current economic data
  - Verify probability output is between 0 and 1
  - Check that all indicators are fetched successfully
  - Verify result is stored in database
  - _Validation checkpoint_

- [x] 8. Create recession forecast database table
  - Use database utilities to create us_recession_2025 table
  - Define schema with probability, indicator values, parameters, timestamp
  - Test inserting and retrieving forecast results
  - _Requirements: 2.5, 6.3_

- [x] 8.1 Validate database integration
  - Run recession model and verify data is saved to database
  - Query historical results and verify timestamps
  - _Validation checkpoint_

- [x] 9. Implement Flask web application structure
  - Create web/app.py with Flask application initialization
  - Create web/templates/ directory with base.html template
  - Create web/static/ directories for CSS and JavaScript
  - Set up basic routing structure
  - _Requirements: 4.1_

- [x] 10. Implement forecast discovery mechanism
  - Create function to scan forecasts/ directory for valid models
  - Implement model loading and instantiation
  - Create registry of discovered forecasts
  - _Requirements: 7.1, 7.4_

- [x] 10.1 Write property test for navigation reflecting directory structure
  - **Property 8: Navigation reflects directory structure**
  - **Validates: Requirements 7.2, 7.3, 7.5**

- [x] 10.2 Write unit tests for forecast discovery
  - Test discovery of valid forecast models
  - Test that invalid directories are ignored
  - _Requirements: 7.1, 7.2_

- [x] 10.3 Validate forecast discovery
  - Create test forecast directory and verify it's discovered
  - Remove directory and verify it's no longer listed
  - _Validation checkpoint_

- [x] 11. Implement web interface home page
  - Create templates/index.html with forecast list
  - Implement route for home page (/)
  - Display all discovered forecasts with names and descriptions
  - Add sidebar navigation component
  - _Requirements: 4.2, 4.3, 7.2_

- [x] 11.1 Validate home page
  - Start Flask app and navigate to home page
  - Verify all forecasts are listed
  - Verify sidebar navigation is present
  - _Validation checkpoint_

- [x] 12. Implement individual forecast display page
  - Create templates/forecast.html for displaying forecast details
  - Implement route for /forecast/<name>
  - Display current probability as large percentage
  - Show last updated timestamp
  - Display data sources and indicator values
  - Add historical probability chart (simple line graph)
  - _Requirements: 4.4, 4.5, 8.5_

- [x] 12.1 Write unit tests for forecast page
  - Test that forecast page displays probability
  - Test handling of non-existent forecast (404)
  - _Requirements: 4.4_

- [x] 12.2 Validate forecast display page
  - Navigate to recession forecast page
  - Verify probability is displayed correctly
  - Verify chart shows historical data
  - _Validation checkpoint_

- [x] 13. Implement parameter adjustment interface
  - Add parameter input controls to forecast.html (sliders, number inputs)
  - Display current parameter values and defaults
  - Add "Reset to Defaults" button
  - Implement client-side JavaScript for parameter updates
  - _Requirements: 5.1_

- [x] 14. Implement parameter simulation API
  - Create API route /api/forecast/<name>/simulate
  - Accept POST request with parameter values
  - Validate parameters using lib/utils.validate_parameters()
  - Calculate new probability with modified parameters
  - Return JSON response with new probability
  - _Requirements: 5.2, 5.4_

- [x] 14.1 Write property test for parameter modification triggers recalculation
  - **Property 4: Parameter modification triggers recalculation**
  - **Validates: Requirements 5.2**

- [x] 14.2 Write property test for simulation state preservation
  - **Property 6: Simulation state preservation**
  - **Validates: Requirements 5.5**

- [x] 14.3 Validate parameter simulation
  - Adjust parameters in web interface
  - Verify probability recalculates
  - Reset to defaults and verify original probability returns
  - Test with invalid parameter values and verify validation errors
  - _Validation checkpoint_

- [x] 15. Implement forecast list API endpoint
  - Create API route /api/forecasts
  - Return JSON list of all available forecasts with metadata
  - Include name, description, last updated timestamp
  - _Requirements: 7.2_

- [x] 15.1 Validate API endpoints
  - Test /api/forecasts returns correct JSON structure
  - Test /api/forecast/<name>/simulate with valid and invalid parameters
  - _Validation checkpoint_

- [x] 16. Add styling and UI polish
  - Create web/static/css/style.css with clean, minimal styling
  - Style sidebar navigation
  - Style forecast display with emphasis on probability percentage
  - Add responsive design for mobile viewing
  - Style parameter controls and buttons
  - _Requirements: 4.5_

- [x] 16.1 Validate UI appearance
  - Review web interface in browser
  - Test responsive design on different screen sizes
  - Verify all elements are styled consistently
  - _Validation checkpoint_

- [x] 17. Add error handling and logging
  - Implement error handlers for 404, 500 errors in Flask app
  - Add logging throughout application (data fetching, calculations, errors)
  - Create logs/ directory for log files
  - Add user-friendly error messages in web interface
  - _Requirements: Error Handling section_

- [x] 17.1 Validate error handling
  - Test accessing non-existent forecast (should show 404)
  - Test with invalid parameters (should show validation error)
  - Simulate data fetching error and verify graceful handling
  - _Validation checkpoint_

- [x] 18. Create project documentation
  - Write comprehensive README.md with setup instructions
  - Document how to add new forecast models
  - Add docstrings to all functions and classes
  - Create forecasts/us_recession_2025/README.md explaining the model
  - Document FRED API key setup
  - _Requirements: 8.3_

- [x] 19. Final integration testing and validation
  - Run complete end-to-end workflow: start app → view forecasts → adjust parameters → verify database storage
  - Test adding a second simple forecast model to verify extensibility
  - Run all unit tests and property tests
  - Verify all requirements are met
  - _Final validation checkpoint_

- [x] 20. Create steering document
  - Document project structure and organization principles
  - Document forecast model interface requirements
  - Document database schema patterns
  - Document web interface conventions
  - Save to .kiro/steering/polymarket-forecasting-simulator.md
  - _Requirements: User request for steering doc_
