from typing import Any, TypeVar, Generic
from quick.orm.models.base import Model

T = TypeVar("T", bound=Model)


class DeleteBuilder(Generic[T]):
    def __init__(self, model: type[T], database: Any):
        self._model = model
        self._database = database
        self._where_clauses: list[str] = []
        self._where_params: list[Any] = []
        self._returning_fields: list[str] = []
    
    def where(self, condition: str, *params: Any) -> "DeleteBuilder[T]":
        new_builder = self._clone()
        new_builder._where_clauses.append(condition)
        new_builder._where_params.extend(params)
        return new_builder
    
    def returning(self, *fields: str) -> "DeleteBuilder[T]":
        new_builder = self._clone()
        if not fields:
            new_builder._returning_fields = ["*"]
        else:
            new_builder._returning_fields = list(fields)
        return new_builder
    
    def _clone(self) -> "DeleteBuilder[T]":
        new_builder = DeleteBuilder(self._model, self._database)
        new_builder._where_clauses = self._where_clauses.copy()
        new_builder._where_params = self._where_params.copy()
        new_builder._returning_fields = self._returning_fields.copy()
        return new_builder
    
    def _build_delete_query(self) -> tuple[str, list[Any]]:
        table_name = self._model.get_table_name()
        
        query = f"DELETE FROM {table_name}"
        params = list(self._where_params)
        
        if self._where_clauses:
            where_str = " AND ".join(self._where_clauses)
            query += f" WHERE {where_str}"
        
        if self._returning_fields:
            query += f" RETURNING {', '.join(self._returning_fields)}"
        
        return query, params
    
    async def execute(self) -> int:
        query, params = self._build_delete_query()
        
        if self._returning_fields:
            rows = await self._database.fetch(query, *params)
            return len(rows)
        else:
            result = await self._database.execute(query, *params)
            return int(result.split()[-1]) if result else 0


__all__ = ["DeleteBuilder"]
