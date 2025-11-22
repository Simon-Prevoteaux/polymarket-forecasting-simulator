#!/usr/bin/env python3
"""
Convenience script to run the US Recession 2025 V2 forecast model.

This is a wrapper around run_forecast.py that defaults to v2.

Usage:
    python forecasts/us_recession_2025/run_forecast_v2.py
    python forecasts/us_recession_2025/run_forecast_v2.py --no-history
    python forecasts/us_recession_2025/run_forecast_v2.py --history-limit 20
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from forecasts.us_recession_2025.run_forecast import run_forecast


def main():
    """Main entry point - runs v2 model by default."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run the US Recession 2025 V2 forecast model',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script runs the enhanced V2 model with:
  - Additional economic indicators (credit spreads, housing, manufacturing, etc.)
  - Feature engineering (rate of change, moving averages, volatility)
  - Temporal decay adjustment based on time remaining until deadline
  - Detailed probability breakdown

Examples:
  python forecasts/us_recession_2025/run_forecast_v2.py
  python forecasts/us_recession_2025/run_forecast_v2.py --no-history
  python forecasts/us_recession_2025/run_forecast_v2.py --history-limit 20
        """
    )
    
    parser.add_argument(
        '--no-history',
        action='store_true',
        help='Do not display historical forecasts'
    )
    
    parser.add_argument(
        '--history-limit',
        type=int,
        default=10,
        help='Number of historical entries to show (default: 10)'
    )
    
    args = parser.parse_args()
    
    # Always use v2
    success = run_forecast(
        show_history=not args.no_history,
        history_limit=args.history_limit,
        version='v2'
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
