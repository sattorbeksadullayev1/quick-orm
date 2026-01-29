from typing import Any, Callable
from dataclasses import dataclass, field


@dataclass
class ColumnMetadata:
    python_type: type
    sql_type: str
    primary_key: bool = False
    auto_increment: bool = False
    unique: bool = False
    nullable: bool = False
    default: Any = None
    index: bool = False
    max_length: int | None = None
    validators: list[Callable] = field(default_factory=list)
    
    def to_sql(self) -> str:
        parts = [self.sql_type]
        
        if self.primary_key:
            parts.append("PRIMARY KEY")
        
        if self.unique and not self.primary_key:
            parts.append("UNIQUE")
        
        if not self.nullable and not self.primary_key:
            parts.append("NOT NULL")
        
        if self.default is not None:
            if isinstance(self.default, str):
                parts.append(f"DEFAULT '{self.default}'")
            elif isinstance(self.default, bool):
                parts.append(f"DEFAULT {str(self.default).upper()}")
            else:
                parts.append(f"DEFAULT {self.default}")
        
        return " ".join(parts)


class Column:
    def __init__(
        self,
        python_type: type,
        sql_type: str,
        *,
        primary_key: bool = False,
        auto_increment: bool = False,
        unique: bool = False,
        nullable: bool = False,
        default: Any = None,
        index: bool = False,
        max_length: int | None = None,
        validators: list[Callable] | None = None,
    ):
        self.metadata = ColumnMetadata(
            python_type=python_type,
            sql_type=sql_type,
            primary_key=primary_key,
            auto_increment=auto_increment,
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            max_length=max_length,
            validators=validators or [],
        )
        self._name: str | None = None
        self._model_class: type | None = None
    
    def __set_name__(self, owner: type, name: str) -> None:
        self._name = name
        self._model_class = owner
    
    def __get__(self, instance: Any, owner: type) -> Any:
        if instance is None:
            return self
        return instance.__dict__.get(self._name)
    
    def __set__(self, instance: Any, value: Any) -> None:
        self.validate(value)
        instance.__dict__[self._name] = value
    
    def validate(self, value: Any) -> None:
        if value is None and not self.metadata.nullable:
            raise ValueError(f"{self._name} cannot be None")
        
        if value is not None:
            for validator in self.metadata.validators:
                validator(value)
    
    @property
    def name(self) -> str:
        if self._name is None:
            raise RuntimeError("Column name not set")
        return self._name
    
    @property
    def sql_definition(self) -> str:
        return self.metadata.to_sql()


__all__ = ["Column", "ColumnMetadata"]
