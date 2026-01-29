from typing import Dict, List, Any
from pathlib import Path


class CodeGenerator:
    COLUMN_TYPE_MAP = {
        "integer": "columns.Integer",
        "bigint": "columns.BigInt",
        "smallint": "columns.SmallInt",
        "float": "columns.Float",
        "decimal": "columns.Decimal",
        "string": "columns.String",
        "text": "columns.Text",
        "char": "columns.Char",
        "uuid": "columns.UUID",
        "boolean": "columns.Boolean",
        "datetime": "columns.DateTime",
        "date": "columns.Date",
        "time": "columns.Time",
        "json": "columns.JSON",
        "jsonb": "columns.JSONB",
        "binary": "columns.Binary",
        "array": "columns.Array",
    }
    
    VALIDATOR_TYPE_MAP = {
        "min_length": "validators.MinLength",
        "max_length": "validators.MaxLength",
        "regex": "validators.Regex",
        "email": "validators.Email",
        "url": "validators.URL",
        "phone_number": "validators.PhoneNumber",
        "range": "validators.Range",
        "positive": "validators.Positive",
        "negative": "validators.Negative",
        "non_negative": "validators.NonNegative",
        "non_positive": "validators.NonPositive",
    }
    
    RELATION_TYPE_MAP = {
        "belongs_to": "relations.BelongsTo",
        "has_one": "relations.HasOne",
        "has_many": "relations.HasMany",
        "many_to_many": "relations.ManyToMany",
    }
    
    def __init__(self, output_dir: str = "models"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_column(self, column: Dict[str, Any]) -> str:
        column_name = column["name"]
        column_type = column["type"]
        
        if column_type not in self.COLUMN_TYPE_MAP:
            raise ValueError(f"Unknown column type: {column_type}")
        
        column_class = self.COLUMN_TYPE_MAP[column_type]
        
        params = []
        
        if column.get("primary_key"):
            params.append("primary_key=True")
        
        if column.get("unique"):
            params.append("unique=True")
        
        if column.get("nullable") is not None:
            params.append(f"nullable={column['nullable']}")
        
        if column.get("default") is not None:
            default_value = column["default"]
            if isinstance(default_value, str):
                params.append(f'default="{default_value}"')
            else:
                params.append(f"default={default_value}")
        
        if column.get("auto_increment"):
            params.append("auto_increment=True")
        
        if column.get("auto_generate"):
            params.append("auto_generate=True")
        
        if column.get("auto_now"):
            params.append("auto_now=True")
        
        if column.get("auto_now_add"):
            params.append("auto_now_add=True")
        
        if column.get("max_length"):
            params.append(f"max_length={column['max_length']}")
        
        if column.get("precision"):
            params.append(f"precision={column['precision']}")
        
        if column.get("scale"):
            params.append(f"scale={column['scale']}")
        
        validators_list = []
        if column.get("validators"):
            for validator in column["validators"]:
                validator_type = validator["type"]
                if validator_type not in self.VALIDATOR_TYPE_MAP:
                    continue
                
                validator_class = self.VALIDATOR_TYPE_MAP[validator_type]
                
                if validator_type in ["email", "url", "phone_number", "positive", "negative", "non_negative", "non_positive"]:
                    validators_list.append(f"{validator_class}()")
                elif validator_type in ["min_length", "max_length"]:
                    validators_list.append(f"{validator_class}({validator['value']})")
                elif validator_type == "regex":
                    validators_list.append(f"{validator_class}(r'{validator['pattern']}')")
                elif validator_type == "range":
                    min_val = validator.get("min_value")
                    max_val = validator.get("max_value")
                    args = []
                    if min_val is not None:
                        args.append(f"min_value={min_val}")
                    if max_val is not None:
                        args.append(f"max_value={max_val}")
                    validators_list.append(f"{validator_class}({', '.join(args)})")
        
        if validators_list:
            params.append(f"validators=[{', '.join(validators_list)}]")
        
        params_str = ", ".join(params) if params else ""
        
        return f"    {column_name} = {column_class}({params_str})"
    
    def generate_relation(self, relation: Dict[str, Any]) -> str:
        relation_name = relation["name"]
        relation_type = relation["type"]
        
        if relation_type not in self.RELATION_TYPE_MAP:
            raise ValueError(f"Unknown relation type: {relation_type}")
        
        relation_class = self.RELATION_TYPE_MAP[relation_type]
        
        params = [f'"{relation["target"]}"']
        
        if relation.get("foreign_key"):
            params.append(f'foreign_key="{relation["foreign_key"]}"')
        
        if relation.get("local_key"):
            params.append(f'local_key="{relation["local_key"]}"')
        
        if relation.get("pivot_table"):
            params.append(f'pivot_table="{relation["pivot_table"]}"')
        
        params_str = ", ".join(params)
        
        return f"    {relation_name} = {relation_class}({params_str})"
    
    def generate_model(self, model: Dict[str, Any]) -> str:
        table_name = model["name"]
        model_name = model["model"]
        
        lines = []
        lines.append("from quick.orm import models, columns, validators, relations")
        lines.append("")
        lines.append("")
        lines.append(f'@models.table("{table_name}")')
        lines.append(f"class {model_name}(models.Model):")
        
        for column in model["columns"]:
            lines.append(self.generate_column(column))
        
        if model.get("relations"):
            lines.append("")
            for relation in model["relations"]:
                lines.append(self.generate_relation(relation))
        
        return "\n".join(lines) + "\n"
    
    def generate_file(self, model: Dict[str, Any]) -> Path:
        model_name = model["model"]
        filename = f"{model_name.lower()}.py"
        filepath = self.output_dir / filename
        
        code = self.generate_model(model)
        
        with open(filepath, "w") as f:
            f.write(code)
        
        return filepath
    
    def generate_all(self, models: List[Dict[str, Any]]) -> List[Path]:
        generated_files = []
        
        for model in models:
            filepath = self.generate_file(model)
            generated_files.append(filepath)
        
        init_file = self.output_dir / "__init__.py"
        with open(init_file, "w") as f:
            for model in models:
                model_name = model["model"]
                filename = model_name.lower()
                f.write(f"from .{filename} import {model_name}\n")
            
            f.write("\n__all__ = [")
            f.write(", ".join([f'"{model["model"]}"' for model in models]))
            f.write("]\n")
        
        generated_files.append(init_file)
        
        return generated_files
