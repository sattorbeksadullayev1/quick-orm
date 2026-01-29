from typing import Any, Optional
import asyncpg


class SchemaInspector:
    def __init__(self, database: Any):
        self._database = database
    
    async def get_tables(self) -> list[str]:
        query = """
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """
        rows = await self._database.fetch(query)
        return [row["tablename"] for row in rows]
    
    async def get_columns(self, table_name: str) -> list[dict[str, Any]]:
        query = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public' 
            AND table_name = $1
            ORDER BY ordinal_position
        """
        rows = await self._database.fetch(query, table_name)
        
        columns = []
        for row in rows:
            columns.append({
                "name": row["column_name"],
                "type": row["data_type"],
                "nullable": row["is_nullable"] == "YES",
                "default": row["column_default"],
                "max_length": row["character_maximum_length"],
            })
        
        return columns
    
    async def get_indexes(self, table_name: str) -> list[dict[str, Any]]:
        query = """
            SELECT
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND tablename = $1
        """
        rows = await self._database.fetch(query, table_name)
        
        indexes = []
        for row in rows:
            indexes.append({
                "name": row["indexname"],
                "definition": row["indexdef"],
            })
        
        return indexes
    
    async def get_foreign_keys(self, table_name: str) -> list[dict[str, Any]]:
        query = """
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = $1
        """
        rows = await self._database.fetch(query, table_name)
        
        foreign_keys = []
        for row in rows:
            foreign_keys.append({
                "constraint_name": row["constraint_name"],
                "column": row["column_name"],
                "foreign_table": row["foreign_table_name"],
                "foreign_column": row["foreign_column_name"],
            })
        
        return foreign_keys
    
    async def table_exists(self, table_name: str) -> bool:
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name = $1
            )
        """
        return await self._database.fetchval(query, table_name)
    
    async def get_primary_keys(self, table_name: str) -> list[str]:
        query = """
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_name = $1
            AND tc.table_schema = 'public'
        """
        rows = await self._database.fetch(query, table_name)
        return [row["column_name"] for row in rows]


__all__ = ["SchemaInspector"]
