from typing import Any, TypeVar, Generic, Type
from quick.orm.models.base import Model

T = TypeVar("T", bound=Model)


class BulkInsertBuilder(Generic[T]):
    def __init__(self, model: type[T], database: Any):
        self._model = model
        self._database = database
        self._values_list: list[dict[str, Any]] = []
        self._returning_fields: list[str] = []
    
    def values(self, *records: dict[str, Any]) -> "BulkInsertBuilder[T]":
        new_builder = self._clone()
        new_builder._values_list.extend(records)
        return new_builder
    
    def returning(self, *fields: str) -> "BulkInsertBuilder[T]":
        new_builder = self._clone()
        if not fields:
            new_builder._returning_fields = ["*"]
        else:
            new_builder._returning_fields = list(fields)
        return new_builder
    
    def _clone(self) -> "BulkInsertBuilder[T]":
        new_builder = BulkInsertBuilder(self._model, self._database)
        new_builder._values_list = self._values_list.copy()
        new_builder._returning_fields = self._returning_fields.copy()
        return new_builder
    
    def _build_bulk_insert_query(self) -> tuple[str, list[Any]]:
        table_name = self._model.get_table_name()
        
        if not self._values_list:
            raise ValueError("No values provided for bulk insert")
        
        columns = list(self._values_list[0].keys())
        
        value_groups = []
        params = []
        param_index = 1
        
        for record in self._values_list:
            placeholders = []
            for col in columns:
                placeholders.append(f"${param_index}")
                params.append(record.get(col))
                param_index += 1
            value_groups.append(f"({', '.join(placeholders)})")
        
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES {', '.join(value_groups)}"
        
        if self._returning_fields:
            query += f" RETURNING {', '.join(self._returning_fields)}"
        
        return query, params
    
    async def execute(self) -> list[T]:
        query, params = self._build_bulk_insert_query()
        
        if self._returning_fields:
            rows = await self._database.fetch(query, *params)
            return [self._row_to_model(row) for row in rows]
        else:
            await self._database.execute(query, *params)
            return []
    
    def _row_to_model(self, row: Any) -> T:
        data = dict(row)
        return self._model(**data)


class BulkUpdateBuilder(Generic[T]):
    def __init__(self, model: type[T], database: Any):
        self._model = model
        self._database = database
        self._updates: list[tuple[dict[str, Any], str, list[Any]]] = []
    
    def add_update(self, values: dict[str, Any], condition: str, *params: Any) -> "BulkUpdateBuilder[T]":
        new_builder = self._clone()
        new_builder._updates.append((values, condition, list(params)))
        return new_builder
    
    def _clone(self) -> "BulkUpdateBuilder[T]":
        new_builder = BulkUpdateBuilder(self._model, self._database)
        new_builder._updates = self._updates.copy()
        return new_builder
    
    async def execute(self) -> int:
        table_name = self._model.get_table_name()
        total_updated = 0
        
        for values, condition, params in self._updates:
            set_clauses = []
            update_params = []
            param_index = 1
            
            for column, value in values.items():
                set_clauses.append(f"{column} = ${param_index}")
                update_params.append(value)
                param_index += 1
            
            adjusted_condition = condition
            for i in range(len(params)):
                old_placeholder = f"${i + 1}"
                new_placeholder = f"${param_index}"
                if old_placeholder in adjusted_condition:
                    adjusted_condition = adjusted_condition.replace(old_placeholder, new_placeholder, 1)
                    param_index += 1
            
            query = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {adjusted_condition}"
            update_params.extend(params)
            
            result = await self._database.execute(query, *update_params)
            if result:
                total_updated += int(result.split()[-1])
        
        return total_updated


class BulkDeleteBuilder(Generic[T]):
    def __init__(self, model: type[T], database: Any):
        self._model = model
        self._database = database
        self._conditions: list[tuple[str, list[Any]]] = []
    
    def add_condition(self, condition: str, *params: Any) -> "BulkDeleteBuilder[T]":
        new_builder = self._clone()
        new_builder._conditions.append((condition, list(params)))
        return new_builder
    
    def _clone(self) -> "BulkDeleteBuilder[T]":
        new_builder = BulkDeleteBuilder(self._model, self._database)
        new_builder._conditions = self._conditions.copy()
        return new_builder
    
    async def execute(self) -> int:
        table_name = self._model.get_table_name()
        total_deleted = 0
        
        for condition, params in self._conditions:
            query = f"DELETE FROM {table_name} WHERE {condition}"
            result = await self._database.execute(query, *params)
            if result:
                total_deleted += int(result.split()[-1])
        
        return total_deleted


__all__ = ["BulkInsertBuilder", "BulkUpdateBuilder", "BulkDeleteBuilder"]
