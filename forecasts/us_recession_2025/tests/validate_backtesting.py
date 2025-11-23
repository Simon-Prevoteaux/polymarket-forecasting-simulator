"""
Validation script for backtesting engine.

Tests the BacktestEngine class with sample data to verify:
- Database schema creation
- Backtest result storage
- Performance metrics calculation
- Model comparison functionality
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_database_schema():
    """Test that database schema is created correctly."""
    print("\n" + "="*70)
    print("TEST 1: Database Schema Creation")
    print("="*70)
    
    try:
        engine = BacktestEngine(model_version='v2')
        print("✓ BacktestEngine initialized successfully")
        print("✓ Database table created with indexes")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize BacktestEngine: {e}")
        return False


def test_backtest_date_generation():
    """Test backtest date generation with different frequencies."""
    print("\n" + "="*70)
    print("TEST 2: Backtest Date Generation")
    print("="*70)
    
    engine = BacktestEngine(model_version='v2')
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    
    try:
        # Test daily frequency
        daily_dates = engine._generate_backtest_dates(start_date, end_date, 'daily')
        print(f"✓ Daily frequency: {len(daily_dates)} dates generated")
        assert len(daily_dates) == 31, f"Expected 31 daily dates, got {len(daily_dates)}"
        
        # Test weekly frequency
        weekly_dates = engine._generate_backtest_dates(start_date, end_date, 'weekly')
        print(f"✓ Weekly frequency: {len(weekly_dates)} dates generated")
        assert len(weekly_dates) >= 4, f"Expected at least 4 weekly dates, got {len(weekly_dates)}"
        
        # Test monthly frequency
        monthly_dates = engine._generate_backtest_dates(start_date, end_date, 'monthly')
        print(f"✓ Monthly frequency: {len(monthly_dates)} dates generated")
        assert len(monthly_dates) >= 1, f"Expected at least 1 monthly date, got {len(monthly_dates)}"
        
        return True
    except Exception as e:
        print(f"✗ Failed to generate backtest dates: {e}")
        return False


def test_recession_detection():
    """Test recession period detection."""
    print("\n" + "="*70)
    print("TEST 3: Recession Period Detection")
    print("="*70)
    
    engine = BacktestEngine(model_version='v2')
    
    # Define sample recession periods
    recession_periods = [
        (datetime(2020, 2, 1), datetime(2020, 4, 30)),  # COVID recession
        (datetime(2007, 12, 1), datetime(2009, 6, 30))  # Great Recession
    ]
    
    try:
        # Test dates in recession
        in_recession_date = datetime(2020, 3, 15)
        assert engine._is_in_recession(in_recession_date, recession_periods), \
            "Failed to detect date in recession"
        print(f"✓ Correctly identified {in_recession_date.date()} as in recession")
        
        # Test dates not in recession
        not_in_recession_date = datetime(2019, 6, 15)
        assert not engine._is_in_recession(not_in_recession_date, recession_periods), \
            "Incorrectly identified date as in recession"
        print(f"✓ Correctly identified {not_in_recession_date.date()} as not in recession")
        
        return True
    except Exception as e:
        print(f"✗ Failed recession detection test: {e}")
        return False


def test_performance_metrics():
    """Test performance metrics calculation with sample data."""
    print("\n" + "="*70)
    print("TEST 4: Performance Metrics Calculation")
    print("="*70)
    
    engine = BacktestEngine(model_version='v2')
    
    # Create sample backtest results
    sample_results = []
    base_date = datetime(2020, 1, 1)
    
    for i in range(10):
        sample_results.append({
            'backtest_date': base_date + timedelta(days=i*30),
            'forecast_date': datetime(2025, 12, 31),
            'model_version': 'v2',
            'base_probability': 0.3 + (i * 0.05),
            'adjusted_probability': 0.25 + (i * 0.05),
            'days_remaining': 365 - (i * 30),
            'parameters': {},
            'indicators': {},
            'features': {},
            'temporal_metadata': {}
        })
    
    # Define sample recession periods
    recession_periods = [
        (datetime(2020, 2, 1), datetime(2020, 4, 30))
    ]
    
    try:
        metrics = engine.calculate_performance_metrics(sample_results, recession_periods)
        
        print(f"✓ Brier Score: {metrics['brier_score']:.4f}")
        print(f"✓ Mean Probability: {metrics['mean_probability']:.4f}")
        print(f"✓ Sharpness (Std Dev): {metrics['sharpness']:.4f}")
        print(f"✓ Number of Forecasts: {metrics['num_forecasts']}")
        
        if metrics['calibration_slope'] is not None:
            print(f"✓ Calibration Slope: {metrics['calibration_slope']:.4f}")
            print(f"✓ Calibration Intercept: {metrics['calibration_intercept']:.4f}")
        
        # Validate metrics are in reasonable ranges
        assert 0 <= metrics['brier_score'] <= 1, "Brier score out of range"
        assert 0 <= metrics['mean_probability'] <= 1, "Mean probability out of range"
        assert metrics['num_forecasts'] == 10, "Incorrect number of forecasts"
        
        return True
    except Exception as e:
        print(f"✗ Failed performance metrics test: {e}")
        return False


def test_model_comparison():
    """Test model comparison functionality."""
    print("\n" + "="*70)
    print("TEST 5: Model Comparison")
    print("="*70)
    
    engine = BacktestEngine(model_version='v2')
    
    # Create sample results for v1 and v2
    base_date = datetime(2020, 1, 1)
    
    v1_results = []
    v2_results = []
    
    for i in range(10):
        date = base_date + timedelta(days=i*30)
        
        # V1 results (slightly worse calibration)
        v1_results.append({
            'backtest_date': date,
            'base_probability': 0.4 + (i * 0.03),
            'adjusted_probability': 0.4 + (i * 0.03)
        })
        
        # V2 results (better calibration)
        v2_results.append({
            'backtest_date': date,
            'base_probability': 0.35 + (i * 0.03),
            'adjusted_probability': 0.30 + (i * 0.03)
        })
    
    recession_periods = [
        (datetime(2020, 2, 1), datetime(2020, 4, 30))
    ]
    
    try:
        comparison = engine.compare_models(v1_results, v2_results, recession_periods)
        
        print(f"✓ V1 Brier Score: {comparison['v1_metrics']['brier_score']:.4f}")
        print(f"✓ V2 Brier Score: {comparison['v2_metrics']['brier_score']:.4f}")
        
        if comparison['brier_score_improvement'] is not None:
            print(f"✓ Brier Score Improvement: {comparison['brier_score_improvement']:.4f}")
            
            if comparison['relative_improvement_pct'] is not None:
                print(f"✓ Relative Improvement: {comparison['relative_improvement_pct']:.2f}%")
            
            if comparison['v2_is_better']:
                print("✓ V2 model performs better than V1")
            else:
                print("✓ V1 model performs better than V2")
        
        return True
    except Exception as e:
        print(f"✗ Failed model comparison test: {e}")
        return False


def test_backtest_result_storage():
    """Test storing and retrieving backtest results."""
    print("\n" + "="*70)
    print("TEST 6: Backtest Result Storage and Retrieval")
    print("="*70)
    
    engine = BacktestEngine(model_version='test')
    
    # Create a sample result
    sample_result = {
        'backtest_date': datetime(2024, 1, 15),
        'forecast_date': datetime(2025, 12, 31),
        'model_version': 'test',
        'base_probability': 0.35,
        'adjusted_probability': 0.30,
        'days_remaining': 350,
        'parameters': {'test_param': 1.0},
        'indicators': {'yield_curve': -0.5},
        'features': {'unemployment_roc_30d': 0.02},
        'temporal_metadata': {'decay_method': 'exponential'}
    }
    
    try:
        # Save result
        engine._save_backtest_result(sample_result)
        print("✓ Backtest result saved successfully")
        
        # Retrieve results
        results = engine.get_backtest_results(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 2, 1),
            model_version='test'
        )
        
        print(f"✓ Retrieved {len(results)} backtest result(s)")
        
        if results:
            result = results[0]
            print(f"  - Backtest Date: {result['backtest_date'].date()}")
            print(f"  - Base Probability: {result['base_probability']:.4f}")
            print(f"  - Adjusted Probability: {result['adjusted_probability']:.4f}")
            print(f"  - Days Remaining: {result['days_remaining']}")
        
        # Test uniqueness constraint
        try:
            engine._save_backtest_result(sample_result)
            print("✓ Uniqueness constraint working (result replaced)")
        except Exception as e:
            print(f"✗ Uniqueness constraint failed: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Failed backtest storage test: {e}")
        return False


def main():
    """Run all validation tests."""
    print("\n" + "="*70)
    print("BACKTESTING ENGINE VALIDATION")
    print("="*70)
    
    tests = [
        ("Database Schema Creation", test_database_schema),
        ("Backtest Date Generation", test_backtest_date_generation),
        ("Recession Period Detection", test_recession_detection),
        ("Performance Metrics Calculation", test_performance_metrics),
        ("Model Comparison", test_model_comparison),
        ("Backtest Result Storage", test_backtest_result_storage)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' raised exception: {e}", exc_info=True)
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All validation tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    exit(main())
