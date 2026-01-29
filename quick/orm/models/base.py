from typing import Any, Type, get_type_hints
from quick.orm.columns.base import Column


class ModelMeta(type):
    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> Type["Model"]:
        cls = super().__new__(mcs, name, bases, namespace)
        
        if name == "Model":
            return cls
        
        columns: dict[str, Column] = dict()
        
        for base in reversed(bases):
            if hasattr(base, "__columns__"):
                columns.update(base.__columns__)
        
        for attr_name, attr_value in namespace.items():
            if isinstance(attr_value, Column):
                columns[attr_name] = attr_value
        
        cls.__columns__ = columns
        cls.__table_name__ = getattr(cls, "__table_name__", None) or mcs._get_table_name(name)
        
        return cls
    
    @staticmethod
    def _get_table_name(class_name: str) -> str:
        import re
        snake_case = re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower()
        if not snake_case.endswith("s"):
            snake_case += "s"
        return snake_case


class Model(metaclass=ModelMeta):
    __table_name__: str
    __columns__: dict[str, Column]
    
    def __init__(self, **kwargs: Any):
        for column_name, column in self.__columns__.items():
            value = kwargs.get(column_name)
            
            if value is None and column.metadata.default is not None:
                if callable(column.metadata.default):
                    value = column.metadata.default()
                else:
                    value = column.metadata.default
            
            setattr(self, column_name, value)
    
    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{name}={getattr(self, name, None)!r}"
            for name in self.__columns__.keys()
        )
        return f"{self.__class__.__name__}({attrs})"
    
    def to_dict(self) -> dict[str, Any]:
        return {
            name: getattr(self, name, None)
            for name in self.__columns__.keys()
        }
    
    @classmethod
    def get_primary_keys(cls) -> list[str]:
        return [
            name
            for name, column in cls.__columns__.items()
            if column.metadata.primary_key
        ]
    
    @classmethod
    def get_table_name(cls) -> str:
        return cls.__table_name__


__all__ = ["Model", "ModelMeta"]
