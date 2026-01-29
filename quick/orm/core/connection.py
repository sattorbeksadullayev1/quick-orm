from typing import Any, Optional
import asyncpg
import asyncio
from quick.orm.core.config import DatabaseConfig


class ConnectionPool:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._pool: Optional[asyncpg.Pool] = None
        self.max_retries = 3
        self.retry_delay = 1.0
    
    async def connect(self) -> None:
        if self._pool is not None:
            return
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                self._pool = await asyncpg.create_pool(
                    host=self.config.host,
                    port=self.config.port,
                    database=self.config.database,
                    user=self.config.user,
                    password=self.config.password,
                    min_size=self.config.min_pool_size,
                    max_size=self.config.max_pool_size,
                    command_timeout=self.config.command_timeout,
                )
                return
            except (asyncpg.PostgresError, OSError, ConnectionRefusedError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                continue
        
        raise ConnectionError(f"Failed to connect after {self.max_retries} attempts: {last_error}")
    
    async def disconnect(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
    
    async def execute(self, query: str, *args: Any) -> str:
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized. Call connect() first.")
        
        return await self._execute_with_retry(lambda: self._pool.execute(query, *args))
    
    async def fetch(self, query: str, *args: Any) -> list[asyncpg.Record]:
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized. Call connect() first.")
        
        return await self._execute_with_retry(lambda: self._pool.fetch(query, *args))
    
    async def fetchrow(self, query: str, *args: Any) -> Optional[asyncpg.Record]:
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized. Call connect() first.")
        
        return await self._execute_with_retry(lambda: self._pool.fetchrow(query, *args))
    
    async def fetchval(self, query: str, *args: Any, column: int = 0) -> Any:
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized. Call connect() first.")
        
        return await self._execute_with_retry(lambda: self._pool.fetchval(query, *args, column=column))
    
    async def _execute_with_retry(self, operation):
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return await operation()
            except (asyncpg.PostgresError, asyncpg.InterfaceError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                continue
        
        raise last_error
    
    def acquire(self) -> asyncpg.pool.PoolAcquireContext:
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized. Call connect() first.")
        
        return self._pool.acquire()
    
    @property
    def is_connected(self) -> bool:
        return self._pool is not None


__all__ = ["ConnectionPool"]
