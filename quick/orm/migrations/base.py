from typing import Optional
from datetime import datetime


class Migration:
    name: str = ""
    
    async def up(self, database: any) -> None:
        raise NotImplementedError("up() method must be implemented")
    
    async def down(self, database: any) -> None:
        raise NotImplementedError("down() method must be implemented")


class MigrationRecord:
    def __init__(self, name: str, batch: int, executed_at: datetime):
        self.name = name
        self.batch = batch
        self.executed_at = executed_at


__all__ = ["Migration", "MigrationRecord"]
