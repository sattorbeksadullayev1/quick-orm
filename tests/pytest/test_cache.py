import pytest
from quick.orm.cache import QueryCache, CacheManager


def test_cache_set_and_get():
    cache = QueryCache(ttl=300)
    
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


def test_cache_expiration():
    cache = QueryCache(ttl=0)
    
    cache.set("key1", "value1")
    
    import time
    time.sleep(0.1)
    
    assert cache.get("key1") is None


def test_cache_max_size():
    cache = QueryCache(max_size=2)
    
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    
    assert len(cache._cache) <= 2


def test_cache_disable():
    cache = QueryCache()
    
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"
    
    cache.disable()
    assert cache.get("key1") is None
    
    cache.set("key2", "value2")
    assert cache.get("key2") is None


def test_cache_clear():
    cache = QueryCache()
    
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    cache.clear()
    
    assert cache.get("key1") is None
    assert cache.get("key2") is None


def test_generate_key():
    key1 = QueryCache.generate_key("SELECT * FROM users", (1, 2))
    key2 = QueryCache.generate_key("SELECT * FROM users", (1, 2))
    key3 = QueryCache.generate_key("SELECT * FROM users", (2, 3))
    
    assert key1 == key2
    assert key1 != key3


def test_cache_manager_singleton():
    manager1 = CacheManager()
    manager2 = CacheManager()
    
    assert manager1 is manager2


def test_cache_manager_get_cache():
    manager = CacheManager()
    
    cache1 = manager.get_cache("test")
    cache2 = manager.get_cache("test")
    
    assert cache1 is cache2


def test_cache_manager_clear_all():
    manager = CacheManager()
    
    cache1 = manager.get_cache("cache1")
    cache2 = manager.get_cache("cache2")
    
    cache1.set("key1", "value1")
    cache2.set("key2", "value2")
    
    manager.clear_all()
    
    assert cache1.get("key1") is None
    assert cache2.get("key2") is None
