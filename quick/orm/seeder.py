from typing import List, Dict, Any
from pathlib import Path
import json


class Seeder:
    def __init__(self, database):
        self.database = database
    
    async def seed(self, model_class, data: List[Dict[str, Any]]) -> List[Any]:
        from quick.orm.query.bulk import BulkInsertBuilder
        
        builder = BulkInsertBuilder(model_class, self.database)
        builder = builder.values(*data)
        return await builder.returning().execute()
    
    async def seed_from_json(self, model_class, json_file: str) -> List[Any]:
        file_path = Path(json_file)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Seed file not found: {json_file}")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return await self.seed(model_class, data)
    
    async def truncate(self, model_class) -> None:
        table_name = model_class.get_table_name()
        query = f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"
        await self.database.execute(query)


class Factory:
    def __init__(self, model_class):
        self.model_class = model_class
        self._definition = {}
        self._sequence = 0
    
    def define(self, **fields) -> 'Factory':
        self._definition = fields
        return self
    
    def create(self, count: int = 1, **overrides) -> List[Dict[str, Any]]:
        results = []
        
        for i in range(count):
            self._sequence += 1
            data = {}
            
            for key, value in self._definition.items():
                if callable(value):
                    data[key] = value(self._sequence, i)
                else:
                    data[key] = value
            
            data.update(overrides)
            results.append(data)
        
        return results if count > 1 else results[0]
    
    async def seed(self, database, count: int = 1, **overrides) -> List[Any]:
        data = self.create(count, **overrides)
        
        if not isinstance(data, list):
            data = [data]
        
        seeder = Seeder(database)
        return await seeder.seed(self.model_class, data)


__all__ = ["Seeder", "Factory"]
