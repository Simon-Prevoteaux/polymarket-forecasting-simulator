"""
Flask web application for Polymarket Forecasting Simulator.

This module provides the web interface for viewing and interacting with
forecast models. It automatically discovers forecast models in the forecasts/
directory and provides routes for displaying forecasts and simulating
parameter changes.
"""

from flask import Flask, render_template, jsonify, request
import os
import sys
from datetime import datetime
import logging
import traceback

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forecasts import discover_forecasts, ForecastRegistry
from lib.logging_config import setup_application_logging, log_error_with_context

# Set up application-wide logging
setup_application_logging(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global registry for discovered forecasts
_forecast_registry: ForecastRegistry = None


def get_forecast_registry() -> ForecastRegistry:
    """
    Get or initialize the forecast registry.
    
    Returns:
        ForecastRegistry with all discovered models
    """
    global _forecast_registry
    if _forecast_registry is None:
        logger.info("Discovering forecast models...")
        _forecast_registry = discover_forecasts()
        logger.info(f"Discovered {len(_forecast_registry.list_names())} forecasts")
    return _forecast_registry


@app.route('/')
def index():
    """
    Home page listing all available forecast models.
    
    Returns:
        Rendered index.html template with list of forecasts
    """
    from werkzeug.exceptions import HTTPException
    
    try:
        logger.info("Rendering home page")
        registry = get_forecast_registry()
        forecasts = []
        
        for directory_name, model in registry.get_all().items():
            try:
                forecasts.append({
                    'directory_name': directory_name,
                    'name': directory_name,  # Used for URL routing
                    'display_name': model.get_name(),
                    'description': model.get_description(),
                    'last_updated': model.get_last_updated()
                })
            except Exception as e:
                log_error_with_context(
                    logger, e,
                    {'forecast': directory_name, 'action': 'get_forecast_metadata'}
                )
                # Continue with other forecasts
                continue
        
        logger.info(f"Successfully loaded {len(forecasts)} forecasts for home page")
        return render_template('index.html', forecasts=forecasts, active_forecast=None)
    
    except HTTPException:
        # Re-raise HTTP exceptions so they're handled by error handlers
        raise
    
    except Exception as e:
        log_error_with_context(logger, e, {'route': 'index'})
        # Return 500 error
        return internal_error(e)


@app.route('/forecast/<name>')
def forecast_detail(name):
    """
    Display detailed view of a specific forecast model.
    
    Args:
        name: The forecast model name (directory name)
        
    Returns:
        Rendered forecast.html template with forecast details
    """
    from werkzeug.exceptions import HTTPException
    
    try:
        logger.info(f"Rendering forecast detail page for: {name}")
        registry = get_forecast_registry()
        
        # Build forecasts list for sidebar
        forecasts = []
        for directory_name, model in registry.get_all().items():
            try:
                forecasts.append({
                    'directory_name': directory_name,
                    'name': directory_name,
                    'display_name': model.get_name(),
                    'description': model.get_description(),
                    'last_updated': model.get_last_updated()
                })
            except Exception as e:
                log_error_with_context(
                    logger, e,
                    {'forecast': directory_name, 'action': 'get_sidebar_metadata'}
                )
                continue
        
        # Get the specific forecast model
        model = registry.get(name)
        if model is None:
            logger.warning(f"Forecast not found: {name}")
            # Forecast not found - trigger 404
            from flask import abort
            abort(404)
        
        # Calculate current probability
        probability = None
        try:
            logger.info(f"Calculating probability for {name}")
            probability = model.calculate_probability()
            logger.info(f"Successfully calculated probability: {probability:.4f}")
        except Exception as e:
            log_error_with_context(
                logger, e,
                {'forecast': name, 'action': 'calculate_probability'}
            )
            # Try to get the last calculated probability from history
            from lib.database import get_forecast_history
            try:
                history_check = get_forecast_history(name, limit=1)
                if history_check and len(history_check) > 0:
                    probability = history_check[0]['probability']
                    logger.info(f"Using last calculated probability from history: {probability}")
            except Exception as hist_error:
                log_error_with_context(
                    logger, hist_error,
                    {'forecast': name, 'action': 'get_historical_probability'}
                )
        
        # Get historical data
        from lib.database import get_forecast_history
        history = []
        try:
            history = get_forecast_history(name, limit=100)
            logger.info(f"Retrieved {len(history)} historical records for {name}")
        except Exception as e:
            log_error_with_context(
                logger, e,
                {'forecast': name, 'action': 'get_forecast_history'}
            )
        
        # Extract indicator values from most recent history entry
        indicators = {}
        if history and len(history) > 0:
            latest = history[0]
            # Extract indicator values from additional columns
            for key in latest.keys():
                if key not in ['id', 'probability', 'parameters', 'data_snapshot', 'calculated_at']:
                    indicators[key] = latest[key]
        
        # Get model parameters
        try:
            parameters = model.get_parameters()
        except Exception as e:
            log_error_with_context(
                logger, e,
                {'forecast': name, 'action': 'get_parameters'}
            )
            parameters = {}
        
        # Get data sources
        try:
            data_sources = model.get_data_sources()
        except Exception as e:
            log_error_with_context(
                logger, e,
                {'forecast': name, 'action': 'get_data_sources'}
            )
            data_sources = []
        
        # Get probability breakdown if available
        breakdown = None
        show_temporal = False
        try:
            breakdown = model.get_probability_breakdown()
            if breakdown is not None:
                show_temporal = True
                logger.info(f"Breakdown data available for {name}")
        except Exception as e:
            log_error_with_context(
                logger, e,
                {'forecast': name, 'action': 'get_probability_breakdown'}
            )
        
        # Build forecast data for template
        forecast_data = {
            'name': name,
            'display_name': model.get_name(),
            'description': model.get_description(),
            'probability': probability if probability is not None else 0.0,
            'last_updated': model.get_last_updated(),
            'indicators': indicators,
            'history': history,
            'parameters': parameters,
            'data_sources': data_sources,
            'breakdown': breakdown
        }
        
        logger.info(f"Successfully rendered forecast detail page for {name}")
        return render_template('forecast.html', 
                             forecast=forecast_data,
                             forecasts=forecasts,
                             active_forecast=name,
                             show_temporal=show_temporal)
    
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) so they're handled by error handlers
        raise
    
    except Exception as e:
        log_error_with_context(logger, e, {'route': 'forecast_detail', 'forecast': name})
        return internal_error(e)


@app.route('/api/forecasts')
def api_forecasts():
    """
    API endpoint returning list of all available forecasts.
    
    Returns:
        JSON response with forecast metadata
    """
    from werkzeug.exceptions import HTTPException
    
    try:
        logger.info("API request: list all forecasts")
        registry = get_forecast_registry()
        forecasts = []
        
        for directory_name, model in registry.get_all().items():
            try:
                forecasts.append({
                    'directory_name': directory_name,
                    'name': model.get_name(),
                    'description': model.get_description(),
                    'last_updated': model.get_last_updated().isoformat()
                })
            except Exception as e:
                log_error_with_context(
                    logger, e,
                    {'forecast': directory_name, 'action': 'serialize_forecast_metadata'}
                )
                continue
        
        logger.info(f"API response: {len(forecasts)} forecasts")
        return jsonify(forecasts)
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        log_error_with_context(logger, e, {'route': 'api_forecasts'})
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve forecast list'
        }), 500


@app.route('/api/forecast/<name>/breakdown')
def api_breakdown(name):
    """
    API endpoint for getting detailed probability breakdown.
    
    This endpoint returns detailed breakdown information if the model supports it,
    or falls back to basic probability information if not.
    
    Args:
        name: The forecast model name
        
    Returns:
        JSON response with probability breakdown or basic probability
    """
    from werkzeug.exceptions import HTTPException
    
    try:
        logger.info(f"API request: get breakdown for forecast {name}")
        registry = get_forecast_registry()
        
        # Get the forecast model
        model = registry.get(name)
        if model is None:
            logger.warning(f"Forecast not found for breakdown: {name}")
            return jsonify({
                'error': 'Forecast not found',
                'forecast': name,
                'message': f'No forecast model named "{name}" exists'
            }), 404
        
        # Check if model has get_probability_breakdown method
        # (All models have it from base class, but it may return None)
        try:
            breakdown = model.get_probability_breakdown()
            
            if breakdown is not None:
                # Model provides detailed breakdown
                logger.info(f"Breakdown available for {name}")
                return jsonify({
                    'success': True,
                    'forecast': name,
                    'has_breakdown': True,
                    'breakdown': breakdown
                }), 200
            else:
                # Model doesn't provide breakdown, return basic probability
                logger.info(f"No breakdown available for {name}, returning basic probability")
                probability = model.calculate_probability()
                return jsonify({
                    'success': True,
                    'forecast': name,
                    'has_breakdown': False,
                    'probability': probability
                }), 200
        
        except Exception as e:
            # Error getting breakdown or probability
            log_error_with_context(
                logger, e,
                {'forecast': name, 'action': 'get_breakdown'}
            )
            return jsonify({
                'error': 'Calculation failed',
                'message': str(e),
                'forecast': name
            }), 500
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        log_error_with_context(logger, e, {'route': 'api_breakdown', 'forecast': name})
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred while getting breakdown'
        }), 500


@app.route('/api/forecast/<name>/simulate', methods=['POST'])
def api_simulate(name):
    """
    API endpoint for simulating forecast with modified parameters.
    
    Args:
        name: The forecast model name
        
    Returns:
        JSON response with recalculated probability or validation errors
    """
    from werkzeug.exceptions import HTTPException
    
    try:
        logger.info(f"API request: simulate forecast {name}")
        registry = get_forecast_registry()
        
        # Get the forecast model
        model = registry.get(name)
        if model is None:
            logger.warning(f"Forecast not found for simulation: {name}")
            return jsonify({
                'error': 'Forecast not found',
                'forecast': name,
                'message': f'No forecast model named "{name}" exists'
            }), 404
        
        # Get parameters from request
        params = request.get_json()
        if params is None:
            logger.warning(f"No parameters provided for simulation: {name}")
            return jsonify({
                'error': 'No parameters provided',
                'message': 'Request body must contain JSON with parameter values'
            }), 400
        
        logger.info(f"Simulating {name} with parameters: {params}")
        
        # Calculate probability with modified parameters
        # The model handles parameter validation and defaults internally
        try:
            probability = model.calculate_probability(params if params else None)
            
            logger.info(f"Simulation successful for {name}: probability={probability:.4f}")
            return jsonify({
                'success': True,
                'forecast': name,
                'probability': probability,
                'parameters': params
            }), 200
        
        except ValueError as e:
            # Parameter validation error
            log_error_with_context(
                logger, e,
                {'forecast': name, 'action': 'validate_parameters', 'params': params}
            )
            return jsonify({
                'error': 'Invalid parameters',
                'message': str(e),
                'forecast': name
            }), 400
        
        except Exception as e:
            # Other calculation errors
            log_error_with_context(
                logger, e,
                {'forecast': name, 'action': 'calculate_probability', 'params': params}
            )
            return jsonify({
                'error': 'Calculation failed',
                'message': str(e),
                'forecast': name
            }), 500
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        log_error_with_context(logger, e, {'route': 'api_simulate', 'forecast': name})
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred during simulation'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with user-friendly message."""
    logger.warning(f"404 error: {request.url}")
    
    try:
        registry = get_forecast_registry()
        forecasts = []
        for directory_name, model in registry.get_all().items():
            try:
                forecasts.append({
                    'directory_name': directory_name,
                    'name': directory_name,
                    'display_name': model.get_name(),
                    'description': model.get_description(),
                    'last_updated': model.get_last_updated()
                })
            except Exception as e:
                log_error_with_context(
                    logger, e,
                    {'forecast': directory_name, 'action': 'get_error_page_metadata'}
                )
                continue
        
        # Extract forecast name from URL if present
        forecast_name = None
        if '/forecast/' in request.url:
            parts = request.url.split('/forecast/')
            if len(parts) > 1:
                forecast_name = parts[1].split('/')[0].split('?')[0]
        
        error_details = {
            'error_code': 404,
            'error_message': 'Page not found',
            'error_description': 'The page you are looking for does not exist.',
            'forecasts': forecasts,
            'active_forecast': None
        }
        
        if forecast_name:
            error_details['error_description'] = (
                f'The forecast "{forecast_name}" does not exist. '
                'Please select a forecast from the sidebar.'
            )
        
        return render_template('error.html', **error_details), 404
    
    except Exception as e:
        log_error_with_context(logger, e, {'handler': '404_error_handler'})
        # Fallback to simple error page
        return render_template('error.html',
                             error_code=404,
                             error_message='Page not found',
                             error_description='The page you are looking for does not exist.',
                             forecasts=[],
                             active_forecast=None), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with user-friendly message."""
    log_error_with_context(logger, error, {'handler': '500_error_handler', 'url': request.url})
    
    try:
        registry = get_forecast_registry()
        forecasts = []
        for directory_name, model in registry.get_all().items():
            try:
                forecasts.append({
                    'directory_name': directory_name,
                    'name': directory_name,
                    'display_name': model.get_name(),
                    'description': model.get_description(),
                    'last_updated': model.get_last_updated()
                })
            except Exception as e:
                log_error_with_context(
                    logger, e,
                    {'forecast': directory_name, 'action': 'get_error_page_metadata'}
                )
                continue
        
        return render_template('error.html',
                             error_code=500,
                             error_message='Internal server error',
                             error_description='An unexpected error occurred. Please try again later.',
                             forecasts=forecasts,
                             active_forecast=None), 500
    
    except Exception as e:
        log_error_with_context(logger, e, {'handler': '500_error_handler_fallback'})
        # Fallback to simple error page
        return render_template('error.html',
                             error_code=500,
                             error_message='Internal server error',
                             error_description='An unexpected error occurred. Please try again later.',
                             forecasts=[],
                             active_forecast=None), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
