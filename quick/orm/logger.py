from typing import Optional, List
from pathlib import Path
from datetime import datetime


class QueryLogger:
    def __init__(self, log_file: Optional[str] = None, log_slow_queries: int = 1000):
        self.log_file = Path(log_file) if log_file else None
        self.log_slow_queries = log_slow_queries
        self.enabled = True
        self.queries: List[dict] = []
    
    def enable(self) -> None:
        self.enabled = True
    
    def disable(self) -> None:
        self.enabled = False
    
    def log_query(
        self, 
        query: str, 
        params: Optional[tuple] = None, 
        duration_ms: Optional[float] = None,
        error: Optional[str] = None
    ) -> None:
        if not self.enabled:
            return
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "params": params,
            "duration_ms": duration_ms,
            "error": error,
            "is_slow": duration_ms and duration_ms > self.log_slow_queries
        }
        
        self.queries.append(log_entry)
        
        if self.log_file:
            self._write_to_file(log_entry)
    
    def _write_to_file(self, entry: dict) -> None:
        if not self.log_file:
            return
        
        with open(self.log_file, "a") as f:
            timestamp = entry["timestamp"]
            query = entry["query"]
            params = entry.get("params", "")
            duration = entry.get("duration_ms", 0)
            error = entry.get("error", "")
            
            if error:
                f.write(f"[{timestamp}] ERROR: {error}\n")
            
            f.write(f"[{timestamp}] {query}\n")
            
            if params:
                f.write(f"  Params: {params}\n")
            
            if duration:
                f.write(f"  Duration: {duration:.2f}ms\n")
            
            if entry.get("is_slow"):
                f.write(f"  WARNING: Slow query detected!\n")
            
            f.write("\n")
    
    def get_queries(self, slow_only: bool = False) -> List[dict]:
        if slow_only:
            return [q for q in self.queries if q.get("is_slow")]
        return self.queries
    
    def clear(self) -> None:
        self.queries.clear()
    
    def get_stats(self) -> dict:
        if not self.queries:
            return {
                "total": 0,
                "slow": 0,
                "errors": 0,
                "avg_duration_ms": 0,
                "max_duration_ms": 0
            }
        
        durations = [q["duration_ms"] for q in self.queries if q["duration_ms"]]
        
        return {
            "total": len(self.queries),
            "slow": len([q for q in self.queries if q.get("is_slow")]),
            "errors": len([q for q in self.queries if q.get("error")]),
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0
        }
