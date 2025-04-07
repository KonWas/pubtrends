import time
from functools import lru_cache
from typing import Dict, Any, List, Tuple

# Simple in-memory cache for API results
pmid_cache: Dict[str, Dict[str, Any]] = {}
geo_cache: Dict[str, Dict[str, Any]] = {}

# Time-based expiration (24 hours)
CACHE_EXPIRY = 86400


def get_from_cache(cache_dict: Dict[str, Dict[str, Any]], key: str) -> Any:
    """Get an item from the cache if it exists and is not expired."""
    if key in cache_dict:
        timestamp, data = cache_dict[key]
        if time.time() - timestamp < CACHE_EXPIRY:
            return data
    return None


def add_to_cache(cache_dict: Dict[str, Dict[str, Any]], key: str, data: Any) -> None:
    """Add an item to the cache with the current timestamp."""
    cache_dict[key] = (time.time(), data)


# Decorator for caching functions with multiple arguments
def cached_result(max_size=128):
    def decorator(func):
        cache = {}

        def wrapper(*args, **kwargs):
            # Create a key from the function arguments
            key = str(args) + str(sorted(kwargs.items()))

            # Check if result is in cache and not expired
            cached = get_from_cache(cache, key)
            if cached is not None:
                return cached

            # Call the function and cache the result
            result = func(*args, **kwargs)
            add_to_cache(cache, key, result)

            # Limit cache size
            if len(cache) > max_size:
                oldest_key = min(cache.keys(), key=lambda k: cache[k][0])
                del cache[oldest_key]

            return result

        return wrapper

    return decorator