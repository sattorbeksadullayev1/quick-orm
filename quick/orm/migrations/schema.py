from typing import Any


class SchemaBuilder:
    def __init__(self, database: Any):
        self._database = database
        self._statements: list[str] = []
    
    async def create_table(self, table_name: str, callback: Any) -> None:
        from quick.orm.migrations.blueprint import Blueprint
        
        blueprint = Blueprint(table_name)
        callback(blueprint)
        
        columns_sql = []
        for column in blueprint._columns:
            columns_sql.append(column.to_sql())
        
        query = f"CREATE TABLE {table_name} ({', '.join(columns_sql)})"
        await self._database.execute(query)
    
    async def drop_table(self, table_name: str) -> None:
        query = f"DROP TABLE IF EXISTS {table_name}"
        await self._database.execute(query)
    
    async def drop_table_if_exists(self, table_name: str) -> None:
        await self.drop_table(table_name)
    
    async def rename_table(self, old_name: str, new_name: str) -> None:
        query = f"ALTER TABLE {old_name} RENAME TO {new_name}"
        await self._database.execute(query)
    
    async def has_table(self, table_name: str) -> bool:
        return await self._database.schema.table_exists(table_name)
    
    async def has_column(self, table_name: str, column_name: str) -> bool:
        columns = await self._database.schema.get_columns(table_name)
        return any(col["name"] == column_name for col in columns)
    
    async def add_column(self, table_name: str, column_name: str, column_type: str) -> None:
        query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        await self._database.execute(query)
    
    async def drop_column(self, table_name: str, column_name: str) -> None:
        query = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
        await self._database.execute(query)
    
    async def rename_column(self, table_name: str, old_name: str, new_name: str) -> None:
        query = f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name}"
        await self._database.execute(query)


__all__ = ["SchemaBuilder"]
