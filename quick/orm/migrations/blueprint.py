from typing import Any, Callable, Optional


class ColumnDefinition:
    def __init__(self, name: str, column_type: str):
        self.name = name
        self.type = column_type
        self.nullable = False
        self.default: Optional[Any] = None
        self.unique = False
        self.primary = False
        self.auto_increment = False
    
    def to_sql(self) -> str:
        parts = [f"{self.name} {self.type}"]
        
        if self.primary:
            parts.append("PRIMARY KEY")
        
        if self.auto_increment:
            if "SERIAL" not in self.type.upper():
                parts.append("GENERATED ALWAYS AS IDENTITY")
        
        if self.unique and not self.primary:
            parts.append("UNIQUE")
        
        if not self.nullable and not self.primary:
            parts.append("NOT NULL")
        
        if self.default is not None:
            if isinstance(self.default, str):
                parts.append(f"DEFAULT '{self.default}'")
            elif isinstance(self.default, bool):
                parts.append(f"DEFAULT {str(self.default).upper()}")
            else:
                parts.append(f"DEFAULT {self.default}")
        
        return " ".join(parts)


class Blueprint:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self._columns: list[ColumnDefinition] = []
    
    def id(self, name: str = "id") -> ColumnDefinition:
        col = ColumnDefinition(name, "SERIAL")
        col.primary = True
        self._columns.append(col)
        return col
    
    def big_id(self, name: str = "id") -> ColumnDefinition:
        col = ColumnDefinition(name, "BIGSERIAL")
        col.primary = True
        self._columns.append(col)
        return col
    
    def integer(self, name: str) -> ColumnDefinition:
        col = ColumnDefinition(name, "INTEGER")
        self._columns.append(col)
        return col
    
    def big_integer(self, name: str) -> ColumnDefinition:
        col = ColumnDefinition(name, "BIGINT")
        self._columns.append(col)
        return col
    
    def small_integer(self, name: str) -> ColumnDefinition:
        col = ColumnDefinition(name, "SMALLINT")
        self._columns.append(col)
        return col
    
    def string(self, name: str, length: int = 255) -> ColumnDefinition:
        col = ColumnDefinition(name, f"VARCHAR({length})")
        self._columns.append(col)
        return col
    
    def text(self, name: str) -> ColumnDefinition:
        col = ColumnDefinition(name, "TEXT")
        self._columns.append(col)
        return col
    
    def boolean(self, name: str) -> ColumnDefinition:
        col = ColumnDefinition(name, "BOOLEAN")
        self._columns.append(col)
        return col
    
    def decimal(self, name: str, precision: int = 10, scale: int = 2) -> ColumnDefinition:
        col = ColumnDefinition(name, f"NUMERIC({precision}, {scale})")
        self._columns.append(col)
        return col
    
    def float(self, name: str) -> ColumnDefinition:
        col = ColumnDefinition(name, "DOUBLE PRECISION")
        self._columns.append(col)
        return col
    
    def date(self, name: str) -> ColumnDefinition:
        col = ColumnDefinition(name, "DATE")
        self._columns.append(col)
        return col
    
    def time(self, name: str) -> ColumnDefinition:
        col = ColumnDefinition(name, "TIME")
        self._columns.append(col)
        return col
    
    def timestamp(self, name: str) -> ColumnDefinition:
        col = ColumnDefinition(name, "TIMESTAMP")
        self._columns.append(col)
        return col
    
    def uuid(self, name: str) -> ColumnDefinition:
        col = ColumnDefinition(name, "UUID")
        self._columns.append(col)
        return col
    
    def json(self, name: str) -> ColumnDefinition:
        col = ColumnDefinition(name, "JSON")
        self._columns.append(col)
        return col
    
    def jsonb(self, name: str) -> ColumnDefinition:
        col = ColumnDefinition(name, "JSONB")
        self._columns.append(col)
        return col
    
    def timestamps(self) -> None:
        created = ColumnDefinition("created_at", "TIMESTAMP")
        created.default = "CURRENT_TIMESTAMP"
        created.nullable = False
        self._columns.append(created)
        
        updated = ColumnDefinition("updated_at", "TIMESTAMP")
        updated.default = "CURRENT_TIMESTAMP"
        updated.nullable = False
        self._columns.append(updated)
    
    def foreign(self, column: str) -> "ForeignKeyDefinition":
        return ForeignKeyDefinition(self, column)


class ForeignKeyDefinition:
    def __init__(self, blueprint: Blueprint, column: str):
        self.blueprint = blueprint
        self.column = column
        self.referenced_table: Optional[str] = None
        self.referenced_column: str = "id"
        self.on_delete: str = "CASCADE"
        self.on_update: str = "CASCADE"
    
    def references(self, column: str) -> "ForeignKeyDefinition":
        self.referenced_column = column
        return self
    
    def on(self, table: str) -> "ForeignKeyDefinition":
        self.referenced_table = table
        return self
    
    def on_delete_cascade(self) -> "ForeignKeyDefinition":
        self.on_delete = "CASCADE"
        return self
    
    def on_delete_set_null(self) -> "ForeignKeyDefinition":
        self.on_delete = "SET NULL"
        return self
    
    def on_update_cascade(self) -> "ForeignKeyDefinition":
        self.on_update = "CASCADE"
        return self


__all__ = ["Blueprint", "ColumnDefinition", "ForeignKeyDefinition"]
