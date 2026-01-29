from typing import Any, Optional, Dict, Tuple
from datetime import datetime, timedelta
from hashlib import sha256
import json


class QueryCache:
    def __init__(self, ttl: int = 300, max_size: int = 1000):
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._ttl = ttl
        self._max_size = max_size
        self._enabled = True
    
    def enable(self) -> None:
        self._enabled = True
    
    def disable(self) -> None:
        self._enabled = False
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def get(self, key: str) -> Optional[Any]:
        if not self._enabled:
            return None
        
        if key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        
        if datetime.now() - timestamp > timedelta(seconds=self._ttl):
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        if not self._enabled:
            return
        
        if len(self._cache) >= self._max_size:
            self._evict_oldest()
        
        self._cache[key] = (value, datetime.now())
    
    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        self._cache.clear()
    
    def _evict_oldest(self) -> None:
        if not self._cache:
            return
        
        oldest_key = min(self._cache.items(), key=lambda x: x[1][1])[0]
        del self._cache[oldest_key]
    
    @staticmethod
    def generate_key(query: str, params: Optional[tuple] = None) -> str:
        cache_data = {"query": query, "params": params}
        cache_string = json.dumps(cache_data, sort_keys=True)
        return sha256(cache_string.encode()).hexdigest()


class CacheManager:
    _instance: Optional['CacheManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._caches: Dict[str, QueryCache] = {}
        return cls._instance
    
    def get_cache(self, name: str = "default") -> QueryCache:
        if name not in self._caches:
            self._caches[name] = QueryCache()
        return self._caches[name]
    
    def clear_all(self) -> None:
        for cache in self._caches.values():
            cache.clear()
    
    def disable_all(self) -> None:
        for cache in self._caches.values():
            cache.disable()
    
    def enable_all(self) -> None:
        for cache in self._caches.values():
            cache.enable()
