from typing import Optional, Callable, Any
from functools import wraps
import time


class QueryProfiler:
    def __init__(self):
        self.enabled = False
        self._profiles = []
    
    def enable(self) -> None:
        self.enabled = True
    
    def disable(self) -> None:
        self.enabled = False
    
    def profile(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not self.enabled:
                return await func(*args, **kwargs)
            
            start_time = time.perf_counter()
            result = None
            error = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = e
                raise
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                
                self._profiles.append({
                    "function": func.__name__,
                    "duration_ms": duration_ms,
                    "error": str(error) if error else None,
                    "args": args,
                    "kwargs": kwargs
                })
        
        return wrapper
    
    def get_profiles(self) -> list:
        return self._profiles
    
    def clear(self) -> None:
        self._profiles.clear()
    
    def get_stats(self) -> dict:
        if not self._profiles:
            return {
                "total_calls": 0,
                "total_time_ms": 0,
                "avg_time_ms": 0,
                "max_time_ms": 0,
                "min_time_ms": 0,
                "errors": 0
            }
        
        durations = [p["duration_ms"] for p in self._profiles]
        
        return {
            "total_calls": len(self._profiles),
            "total_time_ms": sum(durations),
            "avg_time_ms": sum(durations) / len(durations),
            "max_time_ms": max(durations),
            "min_time_ms": min(durations),
            "errors": len([p for p in self._profiles if p["error"]])
        }


profiler = QueryProfiler()

__all__ = ["QueryProfiler", "profiler"]
