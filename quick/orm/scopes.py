from typing import Optional, List, Dict, Any, Type
from quick.orm.models.base import Model


class Scope:
    def apply(self, query_builder):
        raise NotImplementedError


class SoftDeleteScope(Scope):
    def apply(self, query_builder):
        return query_builder.where("deleted_at IS NULL")


class PublishedScope(Scope):
    def apply(self, query_builder):
        return query_builder.where("published_at IS NOT NULL")


class ActiveScope(Scope):
    def apply(self, query_builder):
        return query_builder.where("active = $1", True)


class ScopeMixin:
    _global_scopes: List[Scope] = []
    
    @classmethod
    def add_global_scope(cls, scope: Scope) -> None:
        if not hasattr(cls, '_global_scopes'):
            cls._global_scopes = []
        cls._global_scopes.append(scope)
    
    @classmethod
    def remove_global_scope(cls, scope_class: Type[Scope]) -> None:
        if not hasattr(cls, '_global_scopes'):
            return
        cls._global_scopes = [s for s in cls._global_scopes if not isinstance(s, scope_class)]
    
    @classmethod
    def get_global_scopes(cls) -> List[Scope]:
        if not hasattr(cls, '_global_scopes'):
            return []
        return cls._global_scopes
    
    @classmethod
    def without_global_scopes(cls, query_builder):
        query_builder._skip_global_scopes = True
        return query_builder


def with_trashed():
    def decorator(query_builder):
        query_builder._with_trashed = True
        return query_builder
    return decorator


def only_trashed():
    def decorator(query_builder):
        query_builder._only_trashed = True
        return query_builder
    return decorator
