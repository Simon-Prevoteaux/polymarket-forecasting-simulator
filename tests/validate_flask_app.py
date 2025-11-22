"""
Validation script for Flask web application structure.

This script verifies that the Flask application is properly configured
and can be started without errors.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))

from app import app


def validate_flask_app():
    """Validate Flask application structure and configuration."""
    print("Validating Flask web application structure...")
    print()
    
    # Check app exists
    print("✓ Flask app created successfully")
    
    # Check routes
    print("\nRegistered routes:")
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
            routes.append((rule.endpoint, rule.rule, methods))
            print(f"  ✓ {rule.endpoint}: {rule.rule} [{methods}]")
    
    # Verify expected routes exist
    expected_routes = [
        ('index', '/'),
        ('forecast_detail', '/forecast/<name>'),
        ('api_forecasts', '/api/forecasts'),
        ('api_simulate', '/api/forecast/<name>/simulate')
    ]
    
    print("\nVerifying expected routes:")
    for endpoint, path in expected_routes:
        found = any(r[0] == endpoint and r[1] == path for r in routes)
        if found:
            print(f"  ✓ {endpoint} ({path})")
        else:
            print(f"  ✗ {endpoint} ({path}) - MISSING")
            return False
    
    # Check templates directory
    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'web', 'templates')
    expected_templates = ['base.html', 'index.html', 'forecast.html', 'error.html']
    
    print("\nVerifying templates:")
    for template in expected_templates:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            print(f"  ✓ {template}")
        else:
            print(f"  ✗ {template} - MISSING")
            return False
    
    # Check static directories
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'web', 'static')
    
    print("\nVerifying static directories:")
    css_dir = os.path.join(static_dir, 'css')
    js_dir = os.path.join(static_dir, 'js')
    
    if os.path.exists(css_dir):
        print(f"  ✓ css/ directory")
        if os.path.exists(os.path.join(css_dir, 'style.css')):
            print(f"    ✓ style.css")
    else:
        print(f"  ✗ css/ directory - MISSING")
        return False
    
    if os.path.exists(js_dir):
        print(f"  ✓ js/ directory")
        if os.path.exists(os.path.join(js_dir, 'main.js')):
            print(f"    ✓ main.js")
    else:
        print(f"  ✗ js/ directory - MISSING")
        return False
    
    # Test app can create test client
    print("\nTesting Flask test client:")
    try:
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print(f"  ✓ Test client works (GET / returned 200)")
            else:
                print(f"  ✗ Test client failed (GET / returned {response.status_code})")
                return False
    except Exception as e:
        print(f"  ✗ Test client failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("✓ Flask web application structure validation PASSED")
    print("="*60)
    print("\nThe Flask app is ready for further development.")
    print("To start the development server, run:")
    print("  python web/app.py")
    print("\nNote: Forecast discovery and display functionality will be")
    print("implemented in subsequent tasks (10-12).")
    
    return True


if __name__ == '__main__':
    success = validate_flask_app()
    sys.exit(0 if success else 1)
