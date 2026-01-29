from typing import Optional, Dict, Any
from datetime import datetime


class SoftDeleteMixin:
    deleted_at: Optional[datetime] = None
    
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
    
    async def soft_delete(self, database) -> None:
        from quick.orm.models.base import Model
        if not isinstance(self, Model):
            raise TypeError("SoftDeleteMixin can only be used with Model classes")
        
        table_name = self.get_table_name()
        primary_keys = self.get_primary_keys()
        
        set_clause = "deleted_at = NOW()"
        where_parts = []
        params = []
        param_count = 1
        
        for key in primary_keys:
            value = getattr(self, key, None)
            where_parts.append(f"{key} = ${param_count}")
            params.append(value)
            param_count += 1
        
        where_clause = " AND ".join(where_parts)
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause} RETURNING *"
        
        result = await database.fetchrow(query, *params)
        
        if result:
            self.deleted_at = result["deleted_at"]
    
    async def restore(self, database) -> None:
        from quick.orm.models.base import Model
        if not isinstance(self, Model):
            raise TypeError("SoftDeleteMixin can only be used with Model classes")
        
        table_name = self.get_table_name()
        primary_keys = self.get_primary_keys()
        
        set_clause = "deleted_at = NULL"
        where_parts = []
        params = []
        param_count = 1
        
        for key in primary_keys:
            value = getattr(self, key, None)
            where_parts.append(f"{key} = ${param_count}")
            params.append(value)
            param_count += 1
        
        where_clause = " AND ".join(where_parts)
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause} RETURNING *"
        
        result = await database.fetchrow(query, *params)
        
        if result:
            self.deleted_at = None
    
    async def force_delete(self, database) -> None:
        from quick.orm.models.base import Model
        if not isinstance(self, Model):
            raise TypeError("SoftDeleteMixin can only be used with Model classes")
        
        table_name = self.get_table_name()
        primary_keys = self.get_primary_keys()
        
        where_parts = []
        params = []
        param_count = 1
        
        for key in primary_keys:
            value = getattr(self, key, None)
            where_parts.append(f"{key} = ${param_count}")
            params.append(value)
            param_count += 1
        
        where_clause = " AND ".join(where_parts)
        query = f"DELETE FROM {table_name} WHERE {where_clause}"
        
        await database.execute(query, *params)


__all__ = ["SoftDeleteMixin"]
