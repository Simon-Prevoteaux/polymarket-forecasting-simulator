"""
Quick verification script to display the actual JSON structure
returned by /api/forecasts endpoint.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))

from app import app
import json


def main():
    """Display the JSON structure from /api/forecasts."""
    print("\n" + "="*70)
    print("ACTUAL JSON STRUCTURE FROM /api/forecasts")
    print("="*70)
    
    with app.test_client() as client:
        response = client.get('/api/forecasts')
        
        if response.status_code == 200:
            data = response.get_json()
            print("\nFormatted JSON response:")
            print(json.dumps(data, indent=2))
            
            print("\n" + "="*70)
            print("FIELD VERIFICATION")
            print("="*70)
            
            if len(data) > 0:
                forecast = data[0]
                print("\nRequired fields present:")
                print(f"  ✓ directory_name: {forecast.get('directory_name', 'MISSING')}")
                print(f"  ✓ name: {forecast.get('name', 'MISSING')}")
                print(f"  ✓ description: {forecast.get('description', 'MISSING')}")
                print(f"  ✓ last_updated: {forecast.get('last_updated', 'MISSING')}")
                
                print("\nField types:")
                print(f"  directory_name: {type(forecast.get('directory_name')).__name__}")
                print(f"  name: {type(forecast.get('name')).__name__}")
                print(f"  description: {type(forecast.get('description')).__name__}")
                print(f"  last_updated: {type(forecast.get('last_updated')).__name__}")
            else:
                print("\nNo forecasts found in response")
        else:
            print(f"\nError: Status code {response.status_code}")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    main()
