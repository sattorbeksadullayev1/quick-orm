from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml


class ModelParser:
    def __init__(self, config_path: str = "quick.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        
    def load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        return self.config
    
    def get_models(self) -> List[Dict[str, Any]]:
        if not self.config:
            self.load_config()
        
        return self.config.get("models", {}).get("definitions", [])
    
    def get_model_directory(self) -> str:
        if not self.config:
            self.load_config()
        
        return self.config.get("models", {}).get("directory", "models")
    
    def validate_model(self, model: Dict[str, Any]) -> bool:
        required_fields = ["name", "model", "columns"]
        
        for field in required_fields:
            if field not in model:
                raise ValueError(f"Model missing required field: {field}")
        
        if not model["columns"]:
            raise ValueError(f"Model {model['name']} has no columns defined")
        
        for column in model["columns"]:
            if "name" not in column or "type" not in column:
                raise ValueError(f"Column in model {model['name']} missing name or type")
        
        return True
