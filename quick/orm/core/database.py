from typing import Any, Optional, Type, TypeVar, AsyncIterator
import asyncpg
from quick.orm.core.config import DatabaseConfig
from quick.orm.core.connection import ConnectionPool
from quick.orm.core.transaction import Transaction
from quick.orm.models.base import Model
from quick.orm.query.builder import QueryBuilder
from quick.orm.query.insert import InsertBuilder
from quick.orm.query.update import UpdateBuilder
from quick.orm.query.delete import DeleteBuilder
from quick.orm.query.bulk import BulkInsertBuilder, BulkUpdateBuilder, BulkDeleteBuilder
from quick.orm.schema.inspector import SchemaInspector

T = TypeVar("T", bound=Model)


class Quick:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "",
        user: str = "",
        password: str = "",
        min_pool_size: int = 10,
        max_pool_size: int = 20,
        **kwargs: Any,
    ):
        self.config = DatabaseConfig(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            min_pool_size=min_pool_size,
            max_pool_size=max_pool_size,
            **kwargs,
        )
        self._pool = ConnectionPool(self.config)
    
    @classmethod
    def from_url(cls, url: str) -> "Quick":
        config = DatabaseConfig.from_url(url)
        return cls(
            host=config.host,
            port=config.port,
            database=config.database,
            user=config.user,
            password=config.password,
            min_pool_size=config.min_pool_size,
            max_pool_size=config.max_pool_size,
        )
    
    async def connect(self) -> None:
        await self._pool.connect()
    
    async def disconnect(self) -> None:
        await self._pool.disconnect()
    
    async def __aenter__(self) -> "Quick":
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.disconnect()
    
    async def execute(self, query: str, *args: Any) -> str:
        return await self._pool.execute(query, *args)
    
    async def fetch(self, query: str, *args: Any) -> list[asyncpg.Record]:
        return await self._pool.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args: Any) -> Optional[asyncpg.Record]:
        return await self._pool.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args: Any, column: int = 0) -> Any:
        return await self._pool.fetchval(query, *args, column=column)
    
    async def transaction(self) -> Transaction:
        connection = await self._pool.acquire().__aenter__()
        return Transaction(connection)
    
    def select(self, model: Type[T]) -> QueryBuilder[T]:
        return QueryBuilder(model, self)
    
    def insert(self, model: Type[T]) -> InsertBuilder[T]:
        return InsertBuilder(model, self)
    
    def update(self, model: Type[T]) -> UpdateBuilder[T]:
        return UpdateBuilder(model, self)
    
    def delete(self, model: Type[T]) -> DeleteBuilder[T]:
        return DeleteBuilder(model, self)
    
    def bulk_insert(self, model: Type[T]) -> BulkInsertBuilder[T]:
        return BulkInsertBuilder(model, self)
    
    def bulk_update(self, model: Type[T]) -> BulkUpdateBuilder[T]:
        return BulkUpdateBuilder(model, self)
    
    def bulk_delete(self, model: Type[T]) -> BulkDeleteBuilder[T]:
        return BulkDeleteBuilder(model, self)
    
    @property
    def schema(self) -> SchemaInspector:
        return SchemaInspector(self)
    
    @property
    def is_connected(self) -> bool:
        return self._pool.is_connected


__all__ = ["Quick"]
