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

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forecasts import discover_forecasts, ForecastRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    registry = get_forecast_registry()
    forecasts = []
    
    for directory_name, model in registry.get_all().items():
        forecasts.append({
            'directory_name': directory_name,
            'name': directory_name,  # Used for URL routing
            'display_name': model.get_name(),
            'description': model.get_description(),
            'last_updated': model.get_last_updated()
        })
    
    return render_template('index.html', forecasts=forecasts, active_forecast=None)


@app.route('/forecast/<name>')
def forecast_detail(name):
    """
    Display detailed view of a specific forecast model.
    
    Args:
        name: The forecast model name (directory name)
        
    Returns:
        Rendered forecast.html template with forecast details
    """
    registry = get_forecast_registry()
    
    # Build forecasts list for sidebar
    forecasts = []
    for directory_name, model in registry.get_all().items():
        forecasts.append({
            'directory_name': directory_name,
            'name': directory_name,
            'display_name': model.get_name(),
            'description': model.get_description(),
            'last_updated': model.get_last_updated()
        })
    
    # Get the specific forecast model
    model = registry.get(name)
    if model is None:
        # Forecast not found - trigger 404
        from flask import abort
        abort(404)
    
    # Calculate current probability
    try:
        probability = model.calculate_probability()
    except Exception as e:
        logger.error(f"Error calculating probability for {name}: {e}")
        probability = None
        # Try to get the last calculated probability from history
        from lib.database import get_forecast_history
        try:
            history_check = get_forecast_history(name, limit=1)
            if history_check and len(history_check) > 0:
                probability = history_check[0]['probability']
                logger.info(f"Using last calculated probability: {probability}")
        except Exception as hist_error:
            logger.error(f"Could not retrieve historical probability: {hist_error}")
    
    # Get historical data
    from lib.database import get_forecast_history
    try:
        history = get_forecast_history(name, limit=100)
    except Exception as e:
        logger.error(f"Error fetching history for {name}: {e}")
        history = []
    
    # Extract indicator values from most recent history entry
    indicators = {}
    if history and len(history) > 0:
        latest = history[0]
        # Extract indicator values from additional columns
        for key in latest.keys():
            if key not in ['id', 'probability', 'parameters', 'data_snapshot', 'calculated_at']:
                indicators[key] = latest[key]
    
    # Get model parameters
    parameters = model.get_parameters()
    
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
        'data_sources': model.get_data_sources()
    }
    
    return render_template('forecast.html', 
                         forecast=forecast_data,
                         forecasts=forecasts,
                         active_forecast=name)


@app.route('/api/forecasts')
def api_forecasts():
    """
    API endpoint returning list of all available forecasts.
    
    Returns:
        JSON response with forecast metadata
    """
    registry = get_forecast_registry()
    forecasts = []
    
    for directory_name, model in registry.get_all().items():
        forecasts.append({
            'directory_name': directory_name,
            'name': model.get_name(),
            'description': model.get_description(),
            'last_updated': model.get_last_updated().isoformat()
        })
    
    return jsonify(forecasts)


@app.route('/api/forecast/<name>/simulate', methods=['POST'])
def api_simulate(name):
    """
    API endpoint for simulating forecast with modified parameters.
    
    Args:
        name: The forecast model name
        
    Returns:
        JSON response with recalculated probability or validation errors
    """
    registry = get_forecast_registry()
    
    # Get the forecast model
    model = registry.get(name)
    if model is None:
        return jsonify({
            'error': 'Forecast not found',
            'forecast': name
        }), 404
    
    # Get parameters from request
    params = request.get_json()
    if params is None:
        return jsonify({
            'error': 'No parameters provided',
            'message': 'Request body must contain JSON with parameter values'
        }), 400
    
    # Calculate probability with modified parameters
    # The model handles parameter validation and defaults internally
    try:
        probability = model.calculate_probability(params if params else None)
        
        return jsonify({
            'success': True,
            'forecast': name,
            'probability': probability,
            'parameters': params
        }), 200
    
    except ValueError as e:
        # Parameter validation error
        logger.warning(f"Parameter validation error for {name}: {e}")
        return jsonify({
            'error': 'Invalid parameters',
            'message': str(e)
        }), 400
    
    except Exception as e:
        # Other calculation errors
        logger.error(f"Error calculating probability for {name}: {e}")
        return jsonify({
            'error': 'Calculation failed',
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with user-friendly message."""
    registry = get_forecast_registry()
    forecasts = []
    for directory_name, model in registry.get_all().items():
        forecasts.append({
            'directory_name': directory_name,
            'name': directory_name,
            'display_name': model.get_name(),
            'description': model.get_description(),
            'last_updated': model.get_last_updated()
        })
    
    return render_template('error.html', 
                         error_code=404,
                         error_message='Forecast not found',
                         forecasts=forecasts,
                         active_forecast=None), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with user-friendly message."""
    registry = get_forecast_registry()
    forecasts = []
    for directory_name, model in registry.get_all().items():
        forecasts.append({
            'directory_name': directory_name,
            'name': directory_name,
            'display_name': model.get_name(),
            'description': model.get_description(),
            'last_updated': model.get_last_updated()
        })
    
    return render_template('error.html',
                         error_code=500,
                         error_message='Internal server error',
                         forecasts=forecasts,
                         active_forecast=None), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
