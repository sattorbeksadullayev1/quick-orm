from typing import Callable, Any
from quick.orm.models.base import Model


_table_registry: dict[str, type[Model]] = dict()


def table(
    name: str | None = None,
    *,
    schema: str | None = None,
    comment: str | None = None,
) -> Callable[[type[Model]], type[Model]]:
    def decorator(cls: type[Model]) -> type[Model]:
        table_name = name or cls.__name__
        
        cls.__table_name__ = table_name
        cls.__schema__ = schema
        cls.__comment__ = comment
        
        _table_registry[table_name] = cls
        
        return cls
    
    return decorator


def get_model_by_table_name(table_name: str) -> type[Model] | None:
    return _table_registry.get(table_name)


def get_all_models() -> list[type[Model]]:
    return list(_table_registry.values())


__all__ = ["table", "get_model_by_table_name", "get_all_models"]
