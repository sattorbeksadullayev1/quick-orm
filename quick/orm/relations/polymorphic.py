from typing import Optional, Type, Any
from .base import Relation
from quick.orm.models.base import Model


class MorphTo:
    def __init__(
        self,
        morph_type_column: str = "morphable_type",
        morph_id_column: str = "morphable_id",
    ):
        self.morph_type_column = morph_type_column
        self.morph_id_column = morph_id_column
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


class MorphOne(Relation):
    def __init__(
        self,
        related_model: Type[Model] | str,
        morph_name: str,
        morph_type_column: Optional[str] = None,
        morph_id_column: Optional[str] = None,
    ):
        self.related_model = related_model
        self.morph_name = morph_name
        self.morph_type_column = morph_type_column or f"{morph_name}_type"
        self.morph_id_column = morph_id_column or f"{morph_name}_id"
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


class MorphMany(Relation):
    def __init__(
        self,
        related_model: Type[Model] | str,
        morph_name: str,
        morph_type_column: Optional[str] = None,
        morph_id_column: Optional[str] = None,
    ):
        self.related_model = related_model
        self.morph_name = morph_name
        self.morph_type_column = morph_type_column or f"{morph_name}_type"
        self.morph_id_column = morph_id_column or f"{morph_name}_id"
        self._name: Optional[str] = None
        self._model_class: Optional[Type[Model]] = None
    
    def __set_name__(self, owner: Type[Model], name: str) -> None:
        self._name = name
        self._model_class = owner
    
    def __get__(self, instance: Any, owner: Type[Model]) -> Any:
        if instance is None:
            return self
        
        if not hasattr(instance, f"_{self._name}_loaded"):
            return []
        
        return getattr(instance, f"_{self._name}_loaded", [])
    
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


class HasManyThrough(Relation):
    def __init__(
        self,
        related_model: Type[Model] | str,
        through_model: Type[Model] | str,
        first_key: str,
        second_key: str,
        local_key: str = "id",
        second_local_key: str = "id",
    ):
        self.related_model = related_model
        self.through_model = through_model
        self.first_key = first_key
        self.second_key = second_key
        self.local_key = local_key
        self.second_local_key = second_local_key
        self._name: Optional[str] = None
        self._model_class: Optional[Type[Model]] = None
    
    def __set_name__(self, owner: Type[Model], name: str) -> None:
        self._name = name
        self._model_class = owner
    
    def __get__(self, instance: Any, owner: Type[Model]) -> Any:
        if instance is None:
            return self
        
        if not hasattr(instance, f"_{self._name}_loaded"):
            return []
        
        return getattr(instance, f"_{self._name}_loaded", [])
    
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
    
    def get_through_model(self) -> Type[Model]:
        if isinstance(self.through_model, str):
            from quick.orm.models.decorators import get_model_by_table_name
            model = get_model_by_table_name(self.through_model)
            if model is None:
                raise ValueError(f"Model with table name '{self.through_model}' not found")
            return model
        return self.through_model
