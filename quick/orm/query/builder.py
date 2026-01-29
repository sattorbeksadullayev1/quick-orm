from typing import Any, TypeVar, Generic, Optional, AsyncIterator
from quick.orm.models.base import Model
from quick.orm.relations.base import Relation

T = TypeVar("T", bound=Model)


class QueryBuilder(Generic[T]):
    def __init__(self, model: type[T], database: Any):
        self._model = model
        self._database = database
        self._select_fields: list[str] = []
        self._where_clauses: list[str] = []
        self._where_params: list[Any] = []
        self._order_by: list[str] = []
        self._limit_value: Optional[int] = None
        self._offset_value: Optional[int] = None
        self._with_relations: list[str] = []
        self._group_by: list[str] = []
        self._having_clauses: list[str] = []
        self._having_params: list[Any] = []
        self._joins: list[tuple[str, str, str]] = []
    
    def select(self, *fields: str) -> "QueryBuilder[T]":
        new_builder = self._clone()
        new_builder._select_fields = list(fields)
        return new_builder
    
    def where(self, condition: str, *params: Any) -> "QueryBuilder[T]":
        new_builder = self._clone()
        new_builder._where_clauses.append(condition)
        new_builder._where_params.extend(params)
        return new_builder
    
    def order_by(self, *fields: str) -> "QueryBuilder[T]":
        new_builder = self._clone()
        new_builder._order_by = list(fields)
        return new_builder
    
    def limit(self, value: int) -> "QueryBuilder[T]":
        new_builder = self._clone()
        new_builder._limit_value = value
        return new_builder
    
    def offset(self, value: int) -> "QueryBuilder[T]":
        new_builder = self._clone()
        new_builder._offset_value = value
        return new_builder
    
    def with_relations(self, *relations: str) -> "QueryBuilder[T]":
        new_builder = self._clone()
        new_builder._with_relations.extend(relations)
        return new_builder
    
    def group_by(self, *fields: str) -> "QueryBuilder[T]":
        new_builder = self._clone()
        new_builder._group_by = list(fields)
        return new_builder
    
    def having(self, condition: str, *params: Any) -> "QueryBuilder[T]":
        new_builder = self._clone()
        new_builder._having_clauses.append(condition)
        new_builder._having_params.extend(params)
        return new_builder
    
    def join(self, table: str, condition: str, join_type: str = "INNER") -> "QueryBuilder[T]":
        new_builder = self._clone()
        new_builder._joins.append((join_type, table, condition))
        return new_builder
    
    def left_join(self, table: str, condition: str) -> "QueryBuilder[T]":
        return self.join(table, condition, "LEFT")
    
    def right_join(self, table: str, condition: str) -> "QueryBuilder[T]":
        return self.join(table, condition, "RIGHT")
    
    def _clone(self) -> "QueryBuilder[T]":
        new_builder = QueryBuilder(self._model, self._database)
        new_builder._select_fields = self._select_fields.copy()
        new_builder._where_clauses = self._where_clauses.copy()
        new_builder._where_params = self._where_params.copy()
        new_builder._order_by = self._order_by.copy()
        new_builder._limit_value = self._limit_value
        new_builder._offset_value = self._offset_value
        new_builder._with_relations = self._with_relations.copy()
        new_builder._group_by = self._group_by.copy()
        new_builder._having_clauses = self._having_clauses.copy()
        new_builder._having_params = self._having_params.copy()
        new_builder._joins = self._joins.copy()
        return new_builder
    
    def _build_select_query(self) -> tuple[str, list[Any]]:
        table_name = self._model.get_table_name()
        
        if self._select_fields:
            fields = ", ".join(self._select_fields)
        else:
            fields = "*"
        
        query = f"SELECT {fields} FROM {table_name}"
        params = []
        
        if self._joins:
            for join_type, join_table, join_condition in self._joins:
                query += f" {join_type} JOIN {join_table} ON {join_condition}"
        
        if self._where_clauses:
            where_str = " AND ".join(self._where_clauses)
            query += f" WHERE {where_str}"
            params.extend(self._where_params)
        
        if self._group_by:
            group_str = ", ".join(self._group_by)
            query += f" GROUP BY {group_str}"
        
        if self._having_clauses:
            having_str = " AND ".join(self._having_clauses)
            query += f" HAVING {having_str}"
            params.extend(self._having_params)
        
        if self._order_by:
            order_str = ", ".join(self._order_by)
            query += f" ORDER BY {order_str}"
        
        if self._limit_value is not None:
            query += f" LIMIT {self._limit_value}"
        
        if self._offset_value is not None:
            query += f" OFFSET {self._offset_value}"
        
        return query, params
    
    async def get(self) -> list[T]:
        query, params = self._build_select_query()
        rows = await self._database.fetch(query, *params)
        
        models = [self._row_to_model(row) for row in rows]
        
        if self._with_relations:
            await self._load_relations(models)
        
        return models
    
    async def first(self) -> Optional[T]:
        query, params = self._build_select_query()
        query += " LIMIT 1"
        
        row = await self._database.fetchrow(query, *params)
        
        if row is None:
            return None
        
        model = self._row_to_model(row)
        
        if self._with_relations:
            await self._load_relations([model])
        
        return model
    
    async def count(self) -> int:
        table_name = self._model.get_table_name()
        query = f"SELECT COUNT(*) FROM {table_name}"
        params = []
        
        if self._where_clauses:
            where_str = " AND ".join(self._where_clauses)
            query += f" WHERE {where_str}"
            params.extend(self._where_params)
        
        result = await self._database.fetchval(query, *params)
        return result or 0
    
    async def sum(self, field: str) -> float:
        table_name = self._model.get_table_name()
        query = f"SELECT SUM({field}) FROM {table_name}"
        params = []
        
        if self._where_clauses:
            where_str = " AND ".join(self._where_clauses)
            query += f" WHERE {where_str}"
            params.extend(self._where_params)
        
        result = await self._database.fetchval(query, *params)
        return float(result) if result is not None else 0.0
    
    async def avg(self, field: str) -> float:
        table_name = self._model.get_table_name()
        query = f"SELECT AVG({field}) FROM {table_name}"
        params = []
        
        if self._where_clauses:
            where_str = " AND ".join(self._where_clauses)
            query += f" WHERE {where_str}"
            params.extend(self._where_params)
        
        result = await self._database.fetchval(query, *params)
        return float(result) if result is not None else 0.0
    
    async def min(self, field: str) -> Any:
        table_name = self._model.get_table_name()
        query = f"SELECT MIN({field}) FROM {table_name}"
        params = []
        
        if self._where_clauses:
            where_str = " AND ".join(self._where_clauses)
            query += f" WHERE {where_str}"
            params.extend(self._where_params)
        
        return await self._database.fetchval(query, *params)
    
    async def max(self, field: str) -> Any:
        table_name = self._model.get_table_name()
        query = f"SELECT MAX({field}) FROM {table_name}"
        params = []
        
        if self._where_clauses:
            where_str = " AND ".join(self._where_clauses)
            query += f" WHERE {where_str}"
            params.extend(self._where_params)
        
        return await self._database.fetchval(query, *params)
    
    def _row_to_model(self, row: Any) -> T:
        data = dict(row)
        return self._model(**data)
    
    async def _load_relations(self, models: list[T]) -> None:
        if not models:
            return
        
        for relation_name in self._with_relations:
            relation_attr = getattr(self._model, relation_name, None)
            
            if not isinstance(relation_attr, Relation):
                continue
            
            from quick.orm.relations.base import BelongsTo, HasOne, HasMany
            
            if isinstance(relation_attr, BelongsTo):
                await self._load_belongs_to(models, relation_name, relation_attr)
            elif isinstance(relation_attr, HasOne):
                await self._load_has_one(models, relation_name, relation_attr)
            elif isinstance(relation_attr, HasMany):
                await self._load_has_many(models, relation_name, relation_attr)
    
    async def _load_belongs_to(self, models: list[T], relation_name: str, relation: Relation) -> None:
        related_model = relation.get_related_model()
        foreign_keys = [getattr(model, relation.foreign_key, None) for model in models]
        foreign_keys = [fk for fk in foreign_keys if fk is not None]
        
        if not foreign_keys:
            return
        
        placeholders = ", ".join(f"${i+1}" for i in range(len(foreign_keys)))
        query = f"SELECT * FROM {related_model.get_table_name()} WHERE {relation.local_key} IN ({placeholders})"
        
        rows = await self._database.fetch(query, *foreign_keys)
        related_dict = {getattr(self._row_to_related_model(row, related_model), relation.local_key): self._row_to_related_model(row, related_model) for row in rows}
        
        for model in models:
            fk_value = getattr(model, relation.foreign_key, None)
            if fk_value in related_dict:
                setattr(model, relation_name, related_dict[fk_value])
    
    async def _load_has_one(self, models: list[T], relation_name: str, relation: Relation) -> None:
        related_model = relation.get_related_model()
        local_keys = [getattr(model, relation.local_key, None) for model in models]
        local_keys = [lk for lk in local_keys if lk is not None]
        
        if not local_keys:
            return
        
        placeholders = ", ".join(f"${i+1}" for i in range(len(local_keys)))
        query = f"SELECT * FROM {related_model.get_table_name()} WHERE {relation.foreign_key} IN ({placeholders})"
        
        rows = await self._database.fetch(query, *local_keys)
        related_dict = {getattr(self._row_to_related_model(row, related_model), relation.foreign_key): self._row_to_related_model(row, related_model) for row in rows}
        
        for model in models:
            lk_value = getattr(model, relation.local_key, None)
            if lk_value in related_dict:
                setattr(model, relation_name, related_dict[lk_value])
    
    async def _load_has_many(self, models: list[T], relation_name: str, relation: Relation) -> None:
        related_model = relation.get_related_model()
        local_keys = [getattr(model, relation.local_key, None) for model in models]
        local_keys = [lk for lk in local_keys if lk is not None]
        
        if not local_keys:
            return
        
        placeholders = ", ".join(f"${i+1}" for i in range(len(local_keys)))
        query = f"SELECT * FROM {related_model.get_table_name()} WHERE {relation.foreign_key} IN ({placeholders})"
        
        rows = await self._database.fetch(query, *local_keys)
        
        related_dict: dict[Any, list[Any]] = {lk: [] for lk in local_keys}
        for row in rows:
            related_instance = self._row_to_related_model(row, related_model)
            fk_value = getattr(related_instance, relation.foreign_key, None)
            if fk_value in related_dict:
                related_dict[fk_value].append(related_instance)
        
        for model in models:
            lk_value = getattr(model, relation.local_key, None)
            if lk_value in related_dict:
                setattr(model, relation_name, related_dict[lk_value])
    
    def _row_to_related_model(self, row: Any, model_class: type[Model]) -> Model:
        data = dict(row)
        return model_class(**data)
    
    async def stream(self) -> AsyncIterator[T]:
        query, params = self._build_select_query()
        
        async with self._database._pool.acquire() as connection:
            async with connection.transaction():
                cursor = await connection.cursor(query, *params)
                async for row in cursor:
                    yield self._row_to_model(row)
    
    async def paginate(self, page: int, per_page: int = 15) -> dict[str, Any]:
        offset = (page - 1) * per_page
        
        total = await self.count()
        items = await self.limit(per_page).offset(offset).get()
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }


__all__ = ["QueryBuilder"]
