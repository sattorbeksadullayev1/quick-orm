from typing import Optional, Any


class QuickORMError(Exception):
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConnectionError(QuickORMError):
    pass


class QueryError(QuickORMError):
    def __init__(self, message: str, query: Optional[str] = None, params: Optional[tuple] = None):
        super().__init__(message, {"query": query, "params": params})
        self.query = query
        self.params = params


class ValidationError(QuickORMError):
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        super().__init__(message, {"field": field, "value": value})
        self.field = field
        self.value = value


class ModelNotFoundError(QuickORMError):
    def __init__(self, model: str, conditions: Optional[dict] = None):
        message = f"Model {model} not found"
        if conditions:
            message += f" with conditions: {conditions}"
        super().__init__(message, {"model": model, "conditions": conditions})
        self.model = model
        self.conditions = conditions


class RelationError(QuickORMError):
    pass


class MigrationError(QuickORMError):
    pass


class ConfigurationError(QuickORMError):
    pass


class TransactionError(QuickORMError):
    pass


class SchemaError(QuickORMError):
    pass


class DuplicateEntryError(QuickORMError):
    def __init__(self, message: str, key: Optional[str] = None):
        super().__init__(message, {"key": key})
        self.key = key
