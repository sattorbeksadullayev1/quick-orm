from typing import Any, Callable
from quick.orm.columns.base import Column


class Integer(Column):
    def __init__(
        self,
        *,
        primary_key: bool = False,
        auto_increment: bool = False,
        unique: bool = False,
        nullable: bool = False,
        default: int | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        sql_type = "SERIAL" if auto_increment else "INTEGER"
        super().__init__(
            python_type=int,
            sql_type=sql_type,
            primary_key=primary_key,
            auto_increment=auto_increment,
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            validators=validators,
        )


class BigInt(Column):
    def __init__(
        self,
        *,
        primary_key: bool = False,
        auto_increment: bool = False,
        unique: bool = False,
        nullable: bool = False,
        default: int | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        sql_type = "BIGSERIAL" if auto_increment else "BIGINT"
        super().__init__(
            python_type=int,
            sql_type=sql_type,
            primary_key=primary_key,
            auto_increment=auto_increment,
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            validators=validators,
        )


class SmallInt(Column):
    def __init__(
        self,
        *,
        primary_key: bool = False,
        auto_increment: bool = False,
        unique: bool = False,
        nullable: bool = False,
        default: int | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        sql_type = "SMALLSERIAL" if auto_increment else "SMALLINT"
        super().__init__(
            python_type=int,
            sql_type=sql_type,
            primary_key=primary_key,
            auto_increment=auto_increment,
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            validators=validators,
        )


class Float(Column):
    def __init__(
        self,
        *,
        unique: bool = False,
        nullable: bool = False,
        default: float | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        super().__init__(
            python_type=float,
            sql_type="DOUBLE PRECISION",
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            validators=validators,
        )


class Decimal(Column):
    def __init__(
        self,
        precision: int = 10,
        scale: int = 2,
        *,
        unique: bool = False,
        nullable: bool = False,
        default: Any = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        from decimal import Decimal as DecimalType
        
        super().__init__(
            python_type=DecimalType,
            sql_type=f"NUMERIC({precision}, {scale})",
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            validators=validators,
        )


__all__ = ["Integer", "BigInt", "SmallInt", "Float", "Decimal"]
