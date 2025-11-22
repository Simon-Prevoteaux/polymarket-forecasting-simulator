"""
Real API tests for data fetching utilities.

These tests use the actual FRED API with the API key from .env file.
They verify that the data fetcher works correctly with real API calls.
"""

import pytest
import os
from datetime import datetime
from dotenv import load_dotenv

from lib.data_fetcher import (
    fetch_fred_data,
    get_cached_data,
    clear_cache,
    DataFetchError
)

# Load environment variables
load_dotenv()


@pytest.fixture(autouse=True)
def cleanup_cache():
    """Clean up cache before and after each test."""
    clear_cache()
    yield
    clear_cache()


@pytest.fixture
def api_key():
    """Get API key from environment."""
    key = os.environ.get('FRED_API_KEY')
    if not key:
        pytest.skip("FRED_API_KEY not set in environment")
    return key


class TestRealFredAPI:
    """Test with real FRED API calls."""
    
    def test_fetch_unemployment_rate(self, api_key):
        """Test fetching real unemployment rate data."""
        data = fetch_fred_data(
            'UNRATE',
            start_date='2024-01-01',
            end_date='2024-12-31',
            api_key=api_key
        )
        
        # Verify response structure
        assert 'observations' in data
        assert isinstance(data['observations'], list)
        assert len(data['observations']) > 0
        
        # Verify observation structure
        obs = data['observations'][0]
        assert 'date' in obs
        assert 'value' in obs
        
        print(f"\n✓ Fetched {len(data['observations'])} unemployment rate observations")
        print(f"  Latest: {data['observations'][-1]['date']} = {data['observations'][-1]['value']}%")
    
    def test_fetch_gdp_data(self, api_key):
        """Test fetching real GDP data."""
        data = fetch_fred_data(
            'GDP',
            start_date='2023-01-01',
            api_key=api_key
        )
        
        assert 'observations' in data
        assert len(data['observations']) > 0
        
        # GDP is quarterly data
        obs = data['observations'][-1]
        print(f"\n✓ Fetched GDP data")
        print(f"  Latest: {obs['date']} = ${obs['value']} billion")
    
    def test_fetch_yield_curve(self, api_key):
        """Test fetching real yield curve data (10Y-2Y spread)."""
        data = fetch_fred_data(
            'T10Y2Y',
            start_date='2024-01-01',
            api_key=api_key
        )
        
        assert 'observations' in data
        assert len(data['observations']) > 0
        
        obs = data['observations'][-1]
        print(f"\n✓ Fetched yield curve data")
        print(f"  Latest: {obs['date']} = {obs['value']}%")
    
    def test_caching_with_real_api(self, api_key):
        """Test that caching works with real API calls."""
        import time
        
        # First call - should hit API
        start = time.time()
        data1 = fetch_fred_data('UNRATE', start_date='2024-01-01', api_key=api_key)
        time1 = time.time() - start
        
        # Second call - should use cache
        start = time.time()
        data2 = fetch_fred_data('UNRATE', start_date='2024-01-01', api_key=api_key)
        time2 = time.time() - start
        
        # Verify data is identical
        assert data1 == data2
        
        # Cached call should be significantly faster
        assert time2 < time1 * 0.5  # At least 50% faster
        
        print(f"\n✓ Caching works correctly")
        print(f"  First call (API): {time1:.3f}s")
        print(f"  Second call (cache): {time2:.3f}s")
        print(f"  Speedup: {time1/time2:.1f}x")
    
    def test_invalid_series_id(self, api_key):
        """Test that invalid series ID raises appropriate error."""
        with pytest.raises(DataFetchError) as exc_info:
            fetch_fred_data('INVALID_SERIES_12345', api_key=api_key)
        
        error_msg = str(exc_info.value)
        assert '400' in error_msg or 'Bad Request' in error_msg
        print(f"\n✓ Invalid series ID correctly raises error")
    
    def test_multiple_series_independent_caching(self, api_key):
        """Test that multiple series are cached independently."""
        # Fetch three different series
        unrate = fetch_fred_data('UNRATE', start_date='2024-01-01', api_key=api_key)
        gdp = fetch_fred_data('GDP', start_date='2023-01-01', api_key=api_key)
        yield_curve = fetch_fred_data('T10Y2Y', start_date='2024-01-01', api_key=api_key)
        
        # Verify all are different
        assert unrate != gdp
        assert unrate != yield_curve
        assert gdp != yield_curve
        
        # Verify all are cached
        cached_unrate = get_cached_data('fred_UNRATE_2024-01-01_None')
        cached_gdp = get_cached_data('fred_GDP_2023-01-01_None')
        cached_yield = get_cached_data('fred_T10Y2Y_2024-01-01_None')
        
        assert cached_unrate is not None
        assert cached_gdp is not None
        assert cached_yield is not None
        
        print(f"\n✓ Multiple series cached independently")
        print(f"  UNRATE: {len(unrate['observations'])} observations")
        print(f"  GDP: {len(gdp['observations'])} observations")
        print(f"  T10Y2Y: {len(yield_curve['observations'])} observations")
    
    def test_date_range_filtering(self, api_key):
        """Test that date range parameters work correctly."""
        # Fetch with specific date range
        data = fetch_fred_data(
            'UNRATE',
            start_date='2024-01-01',
            end_date='2024-03-31',
            api_key=api_key
        )
        
        assert 'observations' in data
        observations = data['observations']
        
        # Verify all dates are within range
        for obs in observations:
            date = datetime.strptime(obs['date'], '%Y-%m-%d')
            assert date >= datetime(2024, 1, 1)
            assert date <= datetime(2024, 3, 31)
        
        print(f"\n✓ Date range filtering works")
        print(f"  Requested: 2024-01-01 to 2024-03-31")
        print(f"  Received: {observations[0]['date']} to {observations[-1]['date']}")
    
    def test_api_key_from_env(self):
        """Test that API key is automatically loaded from .env file."""
        # Don't pass api_key parameter - should use environment variable
        data = fetch_fred_data('UNRATE', start_date='2024-01-01')
        
        assert 'observations' in data
        assert len(data['observations']) > 0
        
        print(f"\n✓ API key loaded from .env file automatically")


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '-s'])
