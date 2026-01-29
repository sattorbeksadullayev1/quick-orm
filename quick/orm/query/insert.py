from typing import Any, TypeVar, Generic, Optional
from quick.orm.models.base import Model

T = TypeVar("T", bound=Model)


class InsertBuilder(Generic[T]):
    def __init__(self, model: type[T], database: Any):
        self._model = model
        self._database = database
        self._values: dict[str, Any] = dict()
        self._returning_fields: list[str] = []
    
    def values(self, **kwargs: Any) -> "InsertBuilder[T]":
        new_builder = self._clone()
        new_builder._values.update(kwargs)
        return new_builder
    
    def returning(self, *fields: str) -> "InsertBuilder[T]":
        new_builder = self._clone()
        if not fields:
            new_builder._returning_fields = ["*"]
        else:
            new_builder._returning_fields = list(fields)
        return new_builder
    
    def _clone(self) -> "InsertBuilder[T]":
        new_builder = InsertBuilder(self._model, self._database)
        new_builder._values = self._values.copy()
        new_builder._returning_fields = self._returning_fields.copy()
        return new_builder
    
    def _build_insert_query(self) -> tuple[str, list[Any]]:
        table_name = self._model.get_table_name()
        
        if not self._values:
            raise ValueError("No values provided for insert")
        
        columns = list(self._values.keys())
        placeholders = [f"${i+1}" for i in range(len(columns))]
        params = [self._values[col] for col in columns]
        
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        if self._returning_fields:
            query += f" RETURNING {', '.join(self._returning_fields)}"
        
        return query, params
    
    async def execute(self) -> Optional[T]:
        query, params = self._build_insert_query()
        
        if self._returning_fields:
            row = await self._database.fetchrow(query, *params)
            if row is None:
                return None
            return self._row_to_model(row)
        else:
            await self._database.execute(query, *params)
            return None
    
    def _row_to_model(self, row: Any) -> T:
        data = dict(row)
        return self._model(**data)


__all__ = ["InsertBuilder"]
