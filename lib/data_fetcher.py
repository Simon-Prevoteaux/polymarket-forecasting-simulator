"""
Data fetching utilities for retrieving external data with caching support.

This module provides functions for fetching data from external sources like FRED API,
with built-in caching to reduce API calls and improve performance.
"""

import os
import json
import time
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)


# Cache directory
CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Default cache TTL (time to live) in seconds
DEFAULT_CACHE_TTL = 3600  # 1 hour


class DataFetchError(Exception):
    """Exception raised when data fetching fails."""
    pass


class RateLimitError(Exception):
    """Exception raised when API rate limit is exceeded."""
    pass


def fetch_fred_data(
    series_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch economic data from FRED (Federal Reserve Economic Data) API.
    
    Args:
        series_id: FRED series identifier (e.g., 'UNRATE' for unemployment rate)
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        api_key: FRED API key (optional, will use FRED_API_KEY env var if not provided)
    
    Returns:
        Dictionary containing the fetched data with 'observations' key
    
    Raises:
        DataFetchError: If the API request fails
        RateLimitError: If the API rate limit is exceeded
        ValueError: If API key is not provided
    """
    # Get API key from parameter or environment variable
    if api_key is None:
        api_key = os.environ.get('FRED_API_KEY')
    
    if not api_key:
        raise ValueError(
            "FRED API key is required. Set FRED_API_KEY environment variable "
            "or pass api_key parameter."
        )
    
    # Build API URL
    base_url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        'series_id': series_id,
        'api_key': api_key,
        'file_type': 'json'
    }
    
    if start_date:
        params['observation_start'] = start_date
    if end_date:
        params['observation_end'] = end_date
    
    # Try to fetch from cache first
    cache_key = f"fred_{series_id}_{start_date}_{end_date}"
    cached_data = get_cached_data(cache_key)
    if cached_data is not None:
        logger.info(f"Using cached data for FRED series {series_id}")
        return cached_data
    
    logger.info(f"Fetching data from FRED API for series {series_id}")
    
    # Make API request with retry logic
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.get(base_url, params=params, timeout=30)
            
            # Check for rate limiting
            if response.status_code == 429:
                logger.error(f"FRED API rate limit exceeded for series {series_id}")
                raise RateLimitError(
                    f"FRED API rate limit exceeded for series {series_id}. "
                    "Please wait before making more requests."
                )
            
            # Check for other errors
            if response.status_code != 200:
                error_msg = f"FRED API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error_message' in error_data:
                        error_msg += f": {error_data['error_message']}"
                except:
                    pass
                logger.error(error_msg)
                raise DataFetchError(error_msg)
            
            # Parse response
            data = response.json()
            logger.info(f"Successfully fetched data for FRED series {series_id}")
            
            # Cache the successful response
            cache_data(cache_key, data, ttl=DEFAULT_CACHE_TTL)
            
            return data
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1} for series {series_id}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            logger.error(f"Timeout fetching data for series {series_id} after {max_retries} attempts")
            raise DataFetchError(
                f"Timeout fetching data for series {series_id} after {max_retries} attempts"
            )
        
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error on attempt {attempt + 1} for series {series_id}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            logger.error(f"Network connection error for series {series_id} after {max_retries} attempts")
            raise DataFetchError(
                f"Network connection error fetching data for series {series_id} "
                f"after {max_retries} attempts"
            )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception for series {series_id}: {str(e)}")
            raise DataFetchError(f"Error fetching data for series {series_id}: {str(e)}")


def cache_data(key: str, data: Any, ttl: int = DEFAULT_CACHE_TTL) -> None:
    """
    Cache data locally with expiration time.
    
    Args:
        key: Unique cache key identifier
        data: Data to cache (must be JSON serializable)
        ttl: Time to live in seconds (default: 1 hour)
    """
    cache_file = CACHE_DIR / f"{key}.json"
    
    cache_entry = {
        'data': data,
        'cached_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(seconds=ttl)).isoformat()
    }
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache_entry, f)
        logger.debug(f"Cached data for key {key}")
    except Exception as e:
        # Log error but don't fail - caching is optional
        logger.warning(f"Failed to cache data for key {key}: {str(e)}")


def get_cached_data(key: str) -> Optional[Any]:
    """
    Retrieve cached data if it exists and hasn't expired.
    
    Args:
        key: Unique cache key identifier
    
    Returns:
        Cached data if valid, None if cache miss or expired
    """
    cache_file = CACHE_DIR / f"{key}.json"
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r') as f:
            cache_entry = json.load(f)
        
        # Check if cache has expired
        expires_at = datetime.fromisoformat(cache_entry['expires_at'])
        if datetime.now() > expires_at:
            # Cache expired, remove file
            logger.debug(f"Cache expired for key {key}")
            cache_file.unlink()
            return None
        
        logger.debug(f"Cache hit for key {key}")
        return cache_entry['data']
    
    except Exception as e:
        # If there's any error reading cache, treat as cache miss
        logger.warning(f"Failed to read cache for key {key}: {str(e)}")
        return None


def clear_cache(key: Optional[str] = None) -> None:
    """
    Clear cached data.
    
    Args:
        key: Specific cache key to clear. If None, clears all cache.
    """
    if key:
        cache_file = CACHE_DIR / f"{key}.json"
        if cache_file.exists():
            cache_file.unlink()
    else:
        # Clear all cache files
        for cache_file in CACHE_DIR.glob("*.json"):
            cache_file.unlink()
