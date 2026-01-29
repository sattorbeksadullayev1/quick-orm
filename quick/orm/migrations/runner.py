from typing import Optional, Any
from datetime import datetime
from pathlib import Path
import importlib.util


class MigrationRunner:
    def __init__(self, database: Any, migrations_path: str = "migrations"):
        self._database = database
        self._migrations_path = Path(migrations_path)
        self._table_name = "migrations"
    
    async def setup(self) -> None:
        query = f"""
            CREATE TABLE IF NOT EXISTS {self._table_name} (
                id SERIAL PRIMARY KEY,
                migration VARCHAR(255) NOT NULL,
                batch INTEGER NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        await self._database.execute(query)
    
    async def run(self) -> list[str]:
        await self.setup()
        
        pending = await self._get_pending_migrations()
        
        if not pending:
            return []
        
        batch = await self._get_next_batch()
        executed = []
        
        for migration_file in pending:
            migration = await self._load_migration(migration_file)
            
            await migration.up(self._database)
            await self._record_migration(migration_file.stem, batch)
            executed.append(migration_file.stem)
        
        return executed
    
    async def rollback(self, steps: int = 1) -> list[str]:
        await self.setup()
        
        batch = await self._get_last_batch()
        
        if batch is None:
            return []
        
        migrations_to_rollback = await self._get_migrations_by_batch(batch)
        rolled_back = []
        
        for migration_name in reversed(migrations_to_rollback):
            migration_file = self._migrations_path / f"{migration_name}.py"
            migration = await self._load_migration(migration_file)
            
            await migration.down(self._database)
            await self._remove_migration(migration_name)
            rolled_back.append(migration_name)
        
        return rolled_back
    
    async def reset(self) -> list[str]:
        await self.setup()
        
        all_migrations = await self._get_executed_migrations()
        rolled_back = []
        
        for migration_name in reversed(all_migrations):
            migration_file = self._migrations_path / f"{migration_name}.py"
            migration = await self._load_migration(migration_file)
            
            await migration.down(self._database)
            await self._remove_migration(migration_name)
            rolled_back.append(migration_name)
        
        return rolled_back
    
    async def status(self) -> list[dict[str, Any]]:
        await self.setup()
        
        executed = await self._get_executed_migrations()
        all_migration_files = list(self._migrations_path.glob("*.py"))
        
        status_list = []
        for migration_file in sorted(all_migration_files):
            if migration_file.stem.startswith("__"):
                continue
            
            status_list.append({
                "name": migration_file.stem,
                "executed": migration_file.stem in executed,
            })
        
        return status_list
    
    async def _get_pending_migrations(self) -> list[Path]:
        executed = await self._get_executed_migrations()
        all_migration_files = list(self._migrations_path.glob("*.py"))
        
        pending = []
        for migration_file in sorted(all_migration_files):
            if migration_file.stem.startswith("__"):
                continue
            if migration_file.stem not in executed:
                pending.append(migration_file)
        
        return pending
    
    async def _get_executed_migrations(self) -> list[str]:
        query = f"SELECT migration FROM {self._table_name} ORDER BY id"
        rows = await self._database.fetch(query)
        return [row["migration"] for row in rows]
    
    async def _get_migrations_by_batch(self, batch: int) -> list[str]:
        query = f"SELECT migration FROM {self._table_name} WHERE batch = $1 ORDER BY id"
        rows = await self._database.fetch(query, batch)
        return [row["migration"] for row in rows]
    
    async def _get_next_batch(self) -> int:
        query = f"SELECT MAX(batch) as max_batch FROM {self._table_name}"
        result = await self._database.fetchval(query)
        return (result or 0) + 1
    
    async def _get_last_batch(self) -> Optional[int]:
        query = f"SELECT MAX(batch) as max_batch FROM {self._table_name}"
        return await self._database.fetchval(query)
    
    async def _record_migration(self, name: str, batch: int) -> None:
        query = f"INSERT INTO {self._table_name} (migration, batch) VALUES ($1, $2)"
        await self._database.execute(query, name, batch)
    
    async def _remove_migration(self, name: str) -> None:
        query = f"DELETE FROM {self._table_name} WHERE migration = $1"
        await self._database.execute(query, name)
    
    async def _load_migration(self, migration_file: Path) -> Any:
        spec = importlib.util.spec_from_file_location(migration_file.stem, migration_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and hasattr(attr, "up") and hasattr(attr, "down"):
                if attr_name != "Migration":
                    return attr()
        
        raise ValueError(f"No migration class found in {migration_file}")


__all__ = ["MigrationRunner"]
