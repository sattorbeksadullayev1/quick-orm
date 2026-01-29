from typing import Callable, Any
from uuid import UUID
from quick.orm.columns.base import Column


class UUIDColumn(Column):
    def __init__(
        self,
        *,
        primary_key: bool = False,
        auto_generate: bool = False,
        unique: bool = False,
        nullable: bool = False,
        default: UUID | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        sql_default = None
        if auto_generate:
            sql_default = "gen_random_uuid()"
        elif default is not None:
            sql_default = f"'{default}'"
        
        super().__init__(
            python_type=UUID,
            sql_type="UUID",
            primary_key=primary_key,
            unique=unique,
            nullable=nullable,
            default=sql_default,
            index=index,
            validators=validators,
        )


class Boolean(Column):
    def __init__(
        self,
        *,
        unique: bool = False,
        nullable: bool = False,
        default: bool | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        super().__init__(
            python_type=bool,
            sql_type="BOOLEAN",
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            validators=validators,
        )


class JSON(Column):
    def __init__(
        self,
        *,
        unique: bool = False,
        nullable: bool = False,
        default: dict | list | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        super().__init__(
            python_type=dict,
            sql_type="JSON",
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            validators=validators,
        )


class JSONB(Column):
    def __init__(
        self,
        *,
        unique: bool = False,
        nullable: bool = False,
        default: dict | list | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        super().__init__(
            python_type=dict,
            sql_type="JSONB",
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            validators=validators,
        )


class Binary(Column):
    def __init__(
        self,
        *,
        unique: bool = False,
        nullable: bool = False,
        default: bytes | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        super().__init__(
            python_type=bytes,
            sql_type="BYTEA",
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            validators=validators,
        )


class Array(Column):
    def __init__(
        self,
        item_type: str,
        *,
        unique: bool = False,
        nullable: bool = False,
        default: list | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        super().__init__(
            python_type=list,
            sql_type=f"{item_type}[]",
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            validators=validators,
        )


__all__ = ["UUIDColumn", "Boolean", "JSON", "JSONB", "Binary", "Array"]
