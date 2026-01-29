from typing import Any, Type, Optional, Callable
from quick.orm.models.base import Model


class Relation:
    def __init__(
        self,
        related_model: Type[Model] | str,
        foreign_key: str,
        local_key: str = "id",
        on_delete: str = "CASCADE",
        on_update: str = "CASCADE",
    ):
        self.related_model = related_model
        self.foreign_key = foreign_key
        self.local_key = local_key
        self.on_delete = on_delete
        self.on_update = on_update
        self._name: Optional[str] = None
        self._model_class: Optional[Type[Model]] = None
    
    def __set_name__(self, owner: Type[Model], name: str) -> None:
        self._name = name
        self._model_class = owner
    
    def __get__(self, instance: Any, owner: Type[Model]) -> Any:
        if instance is None:
            return self
        
        if not hasattr(instance, f"_{self._name}_loaded"):
            return None
        
        return getattr(instance, f"_{self._name}_loaded", None)
    
    def __set__(self, instance: Any, value: Any) -> None:
        setattr(instance, f"_{self._name}_loaded", value)
    
    def get_related_model(self) -> Type[Model]:
        if isinstance(self.related_model, str):
            from quick.orm.models.decorators import get_model_by_table_name
            model = get_model_by_table_name(self.related_model)
            if model is None:
                raise ValueError(f"Model with table name '{self.related_model}' not found")
            return model
        return self.related_model


class BelongsTo(Relation):
    def __init__(
        self,
        related_model: Type[Model] | str,
        foreign_key: str,
        owner_key: str = "id",
        on_delete: str = "CASCADE",
        on_update: str = "CASCADE",
    ):
        super().__init__(
            related_model=related_model,
            foreign_key=foreign_key,
            local_key=owner_key,
            on_delete=on_delete,
            on_update=on_update,
        )


class HasOne(Relation):
    def __init__(
        self,
        related_model: Type[Model] | str,
        foreign_key: str,
        local_key: str = "id",
        on_delete: str = "CASCADE",
        on_update: str = "CASCADE",
    ):
        super().__init__(
            related_model=related_model,
            foreign_key=foreign_key,
            local_key=local_key,
            on_delete=on_delete,
            on_update=on_update,
        )


class HasMany(Relation):
    def __init__(
        self,
        related_model: Type[Model] | str,
        foreign_key: str,
        local_key: str = "id",
        on_delete: str = "CASCADE",
        on_update: str = "CASCADE",
    ):
        super().__init__(
            related_model=related_model,
            foreign_key=foreign_key,
            local_key=local_key,
            on_delete=on_delete,
            on_update=on_update,
        )


class ManyToMany(Relation):
    def __init__(
        self,
        related_model: Type[Model] | str,
        pivot_table: str,
        foreign_pivot_key: str,
        related_pivot_key: str,
        local_key: str = "id",
        related_key: str = "id",
    ):
        super().__init__(
            related_model=related_model,
            foreign_key=foreign_pivot_key,
            local_key=local_key,
        )
        self.pivot_table = pivot_table
        self.foreign_pivot_key = foreign_pivot_key
        self.related_pivot_key = related_pivot_key
        self.related_key = related_key


from .polymorphic import MorphTo, MorphOne, MorphMany, HasManyThrough

__all__ = [
    "Relation", 
    "BelongsTo", 
    "HasOne", 
    "HasMany", 
    "ManyToMany",
    "MorphTo",
    "MorphOne",
    "MorphMany",
    "HasManyThrough",
]
