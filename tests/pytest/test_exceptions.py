import pytest
from quick.orm.exceptions import (
    QuickORMError,
    ConnectionError,
    QueryError,
    ValidationError,
    ModelNotFoundError,
    RelationError,
    MigrationError
)


def test_quick_orm_error():
    error = QuickORMError("Test error", {"detail": "test"})
    
    assert error.message == "Test error"
    assert error.details == {"detail": "test"}
    assert str(error) == "Test error"


def test_connection_error():
    error = ConnectionError("Connection failed")
    
    assert isinstance(error, QuickORMError)
    assert error.message == "Connection failed"


def test_query_error():
    error = QueryError("Query failed", query="SELECT * FROM users", params=(1, 2))
    
    assert isinstance(error, QuickORMError)
    assert error.message == "Query failed"
    assert error.query == "SELECT * FROM users"
    assert error.params == (1, 2)


def test_validation_error():
    error = ValidationError("Invalid field", field="email", value="invalid")
    
    assert isinstance(error, QuickORMError)
    assert error.message == "Invalid field"
    assert error.field == "email"
    assert error.value == "invalid"


def test_model_not_found_error():
    error = ModelNotFoundError("User", conditions={"id": 1})
    
    assert isinstance(error, QuickORMError)
    assert "User" in error.message
    assert error.model == "User"
    assert error.conditions == {"id": 1}


def test_relation_error():
    error = RelationError("Relation not found")
    
    assert isinstance(error, QuickORMError)
    assert error.message == "Relation not found"


def test_migration_error():
    error = MigrationError("Migration failed")
    
    assert isinstance(error, QuickORMError)
    assert error.message == "Migration failed"
