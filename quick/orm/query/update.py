from typing import Any, TypeVar, Generic
from quick.orm.models.base import Model

T = TypeVar("T", bound=Model)


class UpdateBuilder(Generic[T]):
    def __init__(self, model: type[T], database: Any):
        self._model = model
        self._database = database
        self._values: dict[str, Any] = dict()
        self._where_clauses: list[str] = []
        self._where_params: list[Any] = []
        self._returning_fields: list[str] = []
    
    def set(self, **kwargs: Any) -> "UpdateBuilder[T]":
        new_builder = self._clone()
        new_builder._values.update(kwargs)
        return new_builder
    
    def where(self, condition: str, *params: Any) -> "UpdateBuilder[T]":
        new_builder = self._clone()
        new_builder._where_clauses.append(condition)
        new_builder._where_params.extend(params)
        return new_builder
    
    def returning(self, *fields: str) -> "UpdateBuilder[T]":
        new_builder = self._clone()
        if not fields:
            new_builder._returning_fields = ["*"]
        else:
            new_builder._returning_fields = list(fields)
        return new_builder
    
    def _clone(self) -> "UpdateBuilder[T]":
        new_builder = UpdateBuilder(self._model, self._database)
        new_builder._values = self._values.copy()
        new_builder._where_clauses = self._where_clauses.copy()
        new_builder._where_params = self._where_params.copy()
        new_builder._returning_fields = self._returning_fields.copy()
        return new_builder
    
    def _build_update_query(self) -> tuple[str, list[Any]]:
        table_name = self._model.get_table_name()
        
        if not self._values:
            raise ValueError("No values provided for update")
        
        set_clauses = []
        params = []
        param_index = 1
        
        for column, value in self._values.items():
            set_clauses.append(f"{column} = ${param_index}")
            params.append(value)
            param_index += 1
        
        query = f"UPDATE {table_name} SET {', '.join(set_clauses)}"
        
        if self._where_clauses:
            where_clauses_with_params = []
            for clause in self._where_clauses:
                adjusted_clause = clause
                for old_param in range(len(self._where_params)):
                    old_placeholder = f"${old_param + 1}"
                    new_placeholder = f"${param_index}"
                    if old_placeholder in adjusted_clause:
                        adjusted_clause = adjusted_clause.replace(old_placeholder, new_placeholder, 1)
                        param_index += 1
                where_clauses_with_params.append(adjusted_clause)
            
            query += f" WHERE {' AND '.join(where_clauses_with_params)}"
            params.extend(self._where_params)
        
        if self._returning_fields:
            query += f" RETURNING {', '.join(self._returning_fields)}"
        
        return query, params
    
    async def execute(self) -> int:
        query, params = self._build_update_query()
        
        if self._returning_fields:
            rows = await self._database.fetch(query, *params)
            return len(rows)
        else:
            result = await self._database.execute(query, *params)
            return int(result.split()[-1]) if result else 0


__all__ = ["UpdateBuilder"]
