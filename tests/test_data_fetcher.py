"""
Unit tests for data fetching utilities.

Tests cache functionality, error handling, and FRED API integration with mocked responses.
"""

import pytest
import json
import time
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from pathlib import Path

from lib.data_fetcher import (
    fetch_fred_data,
    cache_data,
    get_cached_data,
    clear_cache,
    DataFetchError,
    RateLimitError,
    CACHE_DIR
)


@pytest.fixture(autouse=True)
def cleanup_cache():
    """Clean up cache before and after each test."""
    clear_cache()
    yield
    clear_cache()


class TestCacheFunctionality:
    """Test cache storage and retrieval with expiration."""
    
    def test_cache_and_retrieve_data(self):
        """Test basic cache storage and retrieval."""
        test_data = {'value': 42, 'name': 'test'}
        cache_data('test_key', test_data, ttl=3600)
        
        retrieved = get_cached_data('test_key')
        assert retrieved == test_data
    
    def test_cache_expiration(self):
        """Test that cached data expires after TTL."""
        test_data = {'value': 42}
        # Cache with 1 second TTL
        cache_data('test_key', test_data, ttl=1)
        
        # Should be available immediately
        assert get_cached_data('test_key') == test_data
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be None after expiration
        assert get_cached_data('test_key') is None
    
    def test_cache_miss(self):
        """Test that non-existent cache returns None."""
        assert get_cached_data('nonexistent_key') is None
    
    def test_cache_overwrites_existing(self):
        """Test that caching with same key overwrites previous data."""
        cache_data('test_key', {'value': 1}, ttl=3600)
        cache_data('test_key', {'value': 2}, ttl=3600)
        
        retrieved = get_cached_data('test_key')
        assert retrieved == {'value': 2}
    
    def test_clear_specific_cache(self):
        """Test clearing a specific cache entry."""
        cache_data('key1', {'value': 1}, ttl=3600)
        cache_data('key2', {'value': 2}, ttl=3600)
        
        clear_cache('key1')
        
        assert get_cached_data('key1') is None
        assert get_cached_data('key2') == {'value': 2}
    
    def test_clear_all_cache(self):
        """Test clearing all cache entries."""
        cache_data('key1', {'value': 1}, ttl=3600)
        cache_data('key2', {'value': 2}, ttl=3600)
        
        clear_cache()
        
        assert get_cached_data('key1') is None
        assert get_cached_data('key2') is None


class TestFredAPIErrorHandling:
    """Test error handling for network failures and API errors."""
    
    @patch('lib.data_fetcher.requests.get')
    def test_network_connection_error(self, mock_get):
        """Test handling of network connection errors with retries."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
        
        with pytest.raises(DataFetchError) as exc_info:
            fetch_fred_data('UNRATE', api_key='test_key')
        
        assert "Network connection error" in str(exc_info.value)
        assert mock_get.call_count == 3  # Should retry 3 times
    
    @patch('lib.data_fetcher.requests.get')
    def test_timeout_error(self, mock_get):
        """Test handling of timeout errors with retries."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")
        
        with pytest.raises(DataFetchError) as exc_info:
            fetch_fred_data('UNRATE', api_key='test_key')
        
        assert "Timeout" in str(exc_info.value)
        assert mock_get.call_count == 3  # Should retry 3 times
    
    @patch('lib.data_fetcher.requests.get')
    def test_rate_limit_error(self, mock_get):
        """Test handling of API rate limit (429 status)."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        with pytest.raises(RateLimitError) as exc_info:
            fetch_fred_data('UNRATE', api_key='test_key')
        
        assert "rate limit exceeded" in str(exc_info.value).lower()
    
    @patch('lib.data_fetcher.requests.get')
    def test_api_error_response(self, mock_get):
        """Test handling of API error responses (non-200 status)."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error_message': 'Invalid series ID'}
        mock_get.return_value = mock_response
        
        with pytest.raises(DataFetchError) as exc_info:
            fetch_fred_data('INVALID', api_key='test_key')
        
        assert "400" in str(exc_info.value)
    
    def test_missing_api_key(self):
        """Test that missing API key raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                fetch_fred_data('UNRATE')
            
            assert "API key is required" in str(exc_info.value)
    
    @patch('lib.data_fetcher.requests.get')
    def test_retry_with_exponential_backoff(self, mock_get):
        """Test that retries use exponential backoff."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
        
        start_time = time.time()
        with pytest.raises(DataFetchError):
            fetch_fred_data('UNRATE', api_key='test_key')
        elapsed = time.time() - start_time
        
        # Should have delays: 1s, 2s = 3s total minimum
        assert elapsed >= 3.0


class TestFredAPISuccess:
    """Test successful FRED API calls with mocked responses."""
    
    @patch('lib.data_fetcher.requests.get')
    def test_successful_fetch(self, mock_get):
        """Test successful data fetch from FRED API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'observations': [
                {'date': '2024-01-01', 'value': '3.7'},
                {'date': '2024-02-01', 'value': '3.8'}
            ]
        }
        mock_get.return_value = mock_response
        
        result = fetch_fred_data('UNRATE', api_key='test_key')
        
        assert 'observations' in result
        assert len(result['observations']) == 2
        assert result['observations'][0]['value'] == '3.7'
    
    @patch('lib.data_fetcher.requests.get')
    def test_fetch_with_date_range(self, mock_get):
        """Test fetch with start and end dates."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'observations': []}
        mock_get.return_value = mock_response
        
        fetch_fred_data(
            'UNRATE',
            start_date='2024-01-01',
            end_date='2024-12-31',
            api_key='test_key'
        )
        
        # Verify the API was called with correct parameters
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert params['observation_start'] == '2024-01-01'
        assert params['observation_end'] == '2024-12-31'
    
    @patch('lib.data_fetcher.requests.get')
    def test_caching_reduces_api_calls(self, mock_get):
        """Test that caching reduces API calls."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'observations': [{'value': '3.7'}]}
        mock_get.return_value = mock_response
        
        # First call should hit API
        result1 = fetch_fred_data('UNRATE', api_key='test_key')
        assert mock_get.call_count == 1
        
        # Second call should use cache
        result2 = fetch_fred_data('UNRATE', api_key='test_key')
        assert mock_get.call_count == 1  # No additional API call
        
        # Results should be identical
        assert result1 == result2
    
    @patch('lib.data_fetcher.requests.get')
    def test_api_key_from_environment(self, mock_get):
        """Test that API key can be read from environment variable."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'observations': []}
        mock_get.return_value = mock_response
        
        with patch.dict('os.environ', {'FRED_API_KEY': 'env_test_key'}):
            fetch_fred_data('UNRATE')
        
        # Verify API key from environment was used
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert params['api_key'] == 'env_test_key'
    
    @patch('lib.data_fetcher.requests.get')
    def test_retry_succeeds_after_failure(self, mock_get):
        """Test that retry logic succeeds after initial failures."""
        import requests
        
        # First two calls fail, third succeeds
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'observations': [{'value': '3.7'}]}
        
        mock_get.side_effect = [
            requests.exceptions.ConnectionError("Network error"),
            requests.exceptions.ConnectionError("Network error"),
            mock_response
        ]
        
        result = fetch_fred_data('UNRATE', api_key='test_key')
        
        assert 'observations' in result
        assert mock_get.call_count == 3
