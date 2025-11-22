"""
Demonstration script for the backtesting engine.

Shows how to use the BacktestEngine to evaluate model performance
on historical data.

Note: This is a demonstration only. Actual backtesting requires
a fully implemented v2 model with as_of_date support.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timedelta
from forecasts.us_recession_2025.backtesting import BacktestEngine
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demonstrate_backtest_workflow():
    """Demonstrate a complete backtesting workflow."""
    
    print("\n" + "="*70)
    print("BACKTESTING ENGINE DEMONSTRATION")
    print("="*70)
    
    # Initialize the backtesting engine
    print("\n1. Initializing BacktestEngine...")
    engine = BacktestEngine(model_version='v2')
    print("   ✓ Engine initialized with v2 model")
    
    # Define backtest parameters
    print("\n2. Setting up backtest parameters...")
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    frequency = 'monthly'
    
    print(f"   - Start Date: {start_date.date()}")
    print(f"   - End Date: {end_date.date()}")
    print(f"   - Frequency: {frequency}")
    
    # Generate backtest dates
    print("\n3. Generating backtest dates...")
    dates = engine._generate_backtest_dates(start_date, end_date, frequency)
    print(f"   ✓ Generated {len(dates)} backtest dates")
    print(f"   - First date: {dates[0].date()}")
    print(f"   - Last date: {dates[-1].date()}")
    
    # Note about running backtests
    print("\n4. Running backtests...")
    print("   Note: Actual backtesting requires a fully implemented v2 model")
    print("   with as_of_date support. This demo shows the workflow only.")
    print("   ")
    print("   To run actual backtests, you would:")
    print("   ")
    print("   from forecasts.us_recession_2025.model_v2 import RecessionModelV2")
    print("   model = RecessionModelV2()")
    print("   results = engine.run_backtest(")
    print("       start_date=start_date,")
    print("       end_date=end_date,")
    print("       frequency=frequency,")
    print("       model_instance=model")
    print("   )")
    
    # Demonstrate performance metrics with sample data
    print("\n5. Calculating performance metrics (with sample data)...")
    
    # Create sample backtest results
    sample_results = []
    for i, date in enumerate(dates):
        sample_results.append({
            'backtest_date': date,
            'forecast_date': datetime(2025, 12, 31),
            'model_version': 'v2',
            'base_probability': 0.25 + (i * 0.02),
            'adjusted_probability': 0.20 + (i * 0.02),
            'days_remaining': (datetime(2025, 12, 31) - date).days,
            'parameters': {},
            'indicators': {},
            'features': {},
            'temporal_metadata': {}
        })
    
    # Define sample recession periods (none in 2023)
    recession_periods = []
    
    # Calculate metrics
    metrics = engine.calculate_performance_metrics(sample_results, recession_periods)
    
    print(f"   ✓ Brier Score: {metrics['brier_score']:.4f}")
    print(f"   ✓ Mean Probability: {metrics['mean_probability']:.4f}")
    print(f"   ✓ Sharpness: {metrics['sharpness']:.4f}")
    print(f"   ✓ Number of Forecasts: {metrics['num_forecasts']}")
    
    if metrics['calibration_slope'] is not None:
        print(f"   ✓ Calibration Slope: {metrics['calibration_slope']:.4f}")
        print(f"   ✓ Calibration Intercept: {metrics['calibration_intercept']:.4f}")
    
    # Demonstrate model comparison
    print("\n6. Comparing models (with sample data)...")
    
    # Create sample v1 results (slightly different probabilities)
    v1_results = []
    for i, date in enumerate(dates):
        v1_results.append({
            'backtest_date': date,
            'base_probability': 0.30 + (i * 0.02),
            'adjusted_probability': 0.30 + (i * 0.02)  # v1 has no temporal adjustment
        })
    
    comparison = engine.compare_models(v1_results, sample_results, recession_periods)
    
    print(f"   ✓ V1 Brier Score: {comparison['v1_metrics']['brier_score']:.4f}")
    print(f"   ✓ V2 Brier Score: {comparison['v2_metrics']['brier_score']:.4f}")
    
    if comparison['brier_score_improvement'] is not None:
        print(f"   ✓ Improvement: {comparison['brier_score_improvement']:.4f}")
        print(f"   ✓ Relative Improvement: {comparison['relative_improvement_pct']:.2f}%")
        
        if comparison['v2_is_better']:
            print("   ✓ V2 model performs better!")
        else:
            print("   ✓ V1 model performs better")
    
    # Demonstrate result storage and retrieval
    print("\n7. Storing and retrieving results...")
    
    # Store one sample result
    test_result = sample_results[0]
    test_result['model_version'] = 'demo'
    engine._save_backtest_result(test_result)
    print("   ✓ Saved sample backtest result")
    
    # Retrieve it
    retrieved = engine.get_backtest_results(
        start_date=test_result['backtest_date'] - timedelta(days=1),
        end_date=test_result['backtest_date'] + timedelta(days=1),
        model_version='demo'
    )
    
    if retrieved:
        print(f"   ✓ Retrieved {len(retrieved)} result(s)")
        result = retrieved[0]
        print(f"     - Date: {result['backtest_date'].date()}")
        print(f"     - Base Probability: {result['base_probability']:.4f}")
        print(f"     - Adjusted Probability: {result['adjusted_probability']:.4f}")
    
    # Summary
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nThe backtesting engine provides:")
    print("  ✓ Historical model evaluation")
    print("  ✓ Performance metrics calculation")
    print("  ✓ Model comparison capabilities")
    print("  ✓ Result storage and retrieval")
    print("\nNext steps:")
    print("  1. Complete v2 model implementation with as_of_date support")
    print("  2. Run actual backtests on historical data")
    print("  3. Analyze results in Jupyter notebooks")
    print("  4. Use insights to improve model calibration")


def demonstrate_recession_detection():
    """Demonstrate recession period detection."""
    
    print("\n" + "="*70)
    print("RECESSION DETECTION DEMONSTRATION")
    print("="*70)
    
    engine = BacktestEngine(model_version='v2')
    
    # Define historical recession periods
    recession_periods = [
        (datetime(2007, 12, 1), datetime(2009, 6, 30)),  # Great Recession
        (datetime(2020, 2, 1), datetime(2020, 4, 30))    # COVID Recession
    ]
    
    print("\nHistorical US Recession Periods:")
    for i, (start, end) in enumerate(recession_periods, 1):
        duration = (end - start).days
        print(f"  {i}. {start.date()} to {end.date()} ({duration} days)")
    
    # Test various dates
    test_dates = [
        datetime(2008, 6, 15),   # During Great Recession
        datetime(2020, 3, 15),   # During COVID Recession
        datetime(2019, 6, 15),   # Not in recession
        datetime(2023, 6, 15)    # Not in recession
    ]
    
    print("\nTesting dates:")
    for date in test_dates:
        in_recession = engine._is_in_recession(date, recession_periods)
        status = "IN RECESSION" if in_recession else "Not in recession"
        print(f"  {date.date()}: {status}")


if __name__ == '__main__':
    demonstrate_backtest_workflow()
    print("\n")
    demonstrate_recession_detection()
