import pytest
from quick.orm.generator import ModelParser, CodeGenerator
from pathlib import Path
import tempfile
import yaml


def test_model_parser_load_config():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config = {
            "database": {"host": "localhost"},
            "models": {
                "directory": "models",
                "definitions": [
                    {
                        "name": "users",
                        "model": "User",
                        "columns": [
                            {"name": "id", "type": "integer", "primary_key": True}
                        ]
                    }
                ]
            }
        }
        yaml.dump(config, f)
        config_path = f.name
    
    try:
        parser = ModelParser(config_path)
        loaded = parser.load_config()
        
        assert "database" in loaded
        assert "models" in loaded
    finally:
        Path(config_path).unlink()


def test_model_parser_get_models():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config = {
            "models": {
                "definitions": [
                    {"name": "users", "model": "User", "columns": [{"name": "id", "type": "integer"}]},
                    {"name": "posts", "model": "Post", "columns": [{"name": "id", "type": "integer"}]}
                ]
            }
        }
        yaml.dump(config, f)
        config_path = f.name
    
    try:
        parser = ModelParser(config_path)
        models = parser.get_models()
        
        assert len(models) == 2
        assert models[0]["name"] == "users"
        assert models[1]["name"] == "posts"
    finally:
        Path(config_path).unlink()


def test_model_parser_validate_model():
    parser = ModelParser()
    
    valid_model = {
        "name": "users",
        "model": "User",
        "columns": [
            {"name": "id", "type": "integer"}
        ]
    }
    
    assert parser.validate_model(valid_model) is True


def test_model_parser_validate_model_missing_field():
    parser = ModelParser()
    
    invalid_model = {
        "name": "users",
        "columns": []
    }
    
    with pytest.raises(ValueError):
        parser.validate_model(invalid_model)


def test_code_generator_generate_column():
    generator = CodeGenerator()
    
    column = {
        "name": "id",
        "type": "integer",
        "primary_key": True,
        "auto_increment": True
    }
    
    code = generator.generate_column(column)
    
    assert "id = columns.Integer" in code
    assert "primary_key=True" in code
    assert "auto_increment=True" in code


def test_code_generator_generate_column_with_validators():
    generator = CodeGenerator()
    
    column = {
        "name": "email",
        "type": "string",
        "max_length": 100,
        "validators": [
            {"type": "email"}
        ]
    }
    
    code = generator.generate_column(column)
    
    assert "email = columns.String" in code
    assert "max_length=100" in code
    assert "validators.Email()" in code


def test_code_generator_generate_relation():
    generator = CodeGenerator()
    
    relation = {
        "name": "posts",
        "type": "has_many",
        "target": "posts",
        "foreign_key": "user_id"
    }
    
    code = generator.generate_relation(relation)
    
    assert "posts = relations.HasMany" in code
    assert 'foreign_key="user_id"' in code


def test_code_generator_generate_model():
    generator = CodeGenerator()
    
    model = {
        "name": "users",
        "model": "User",
        "columns": [
            {"name": "id", "type": "integer", "primary_key": True},
            {"name": "username", "type": "string", "max_length": 50}
        ],
        "relations": []
    }
    
    code = generator.generate_model(model)
    
    assert "@models.table(\"users\")" in code
    assert "class User(models.Model):" in code
    assert "id = columns.Integer" in code
    assert "username = columns.String" in code
