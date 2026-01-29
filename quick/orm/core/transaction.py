from typing import Any, Optional
import asyncpg
from contextlib import asynccontextmanager


class Transaction:
    def __init__(self, connection: asyncpg.Connection):
        self._connection = connection
        self._transaction: Optional[asyncpg.transaction.Transaction] = None
    
    async def __aenter__(self) -> "Transaction":
        self._transaction = self._connection.transaction()
        await self._transaction.start()
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._transaction is None:
            return
        
        if exc_type is not None:
            await self._transaction.rollback()
        else:
            await self._transaction.commit()
        
        self._transaction = None
    
    async def commit(self) -> None:
        if self._transaction is None:
            raise RuntimeError("Transaction not started")
        await self._transaction.commit()
    
    async def rollback(self) -> None:
        if self._transaction is None:
            raise RuntimeError("Transaction not started")
        await self._transaction.rollback()
    
    async def execute(self, query: str, *args: Any) -> str:
        return await self._connection.execute(query, *args)
    
    async def fetch(self, query: str, *args: Any) -> list[asyncpg.Record]:
        return await self._connection.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args: Any) -> Optional[asyncpg.Record]:
        return await self._connection.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args: Any, column: int = 0) -> Any:
        return await self._connection.fetchval(query, *args, column=column)


__all__ = ["Transaction"]
