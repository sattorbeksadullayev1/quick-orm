from typing import Callable
from quick.orm.columns.base import Column


class String(Column):
    def __init__(
        self,
        max_length: int = 255,
        *,
        unique: bool = False,
        nullable: bool = False,
        default: str | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        super().__init__(
            python_type=str,
            sql_type=f"VARCHAR({max_length})",
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            max_length=max_length,
            validators=validators,
        )


class Text(Column):
    def __init__(
        self,
        *,
        unique: bool = False,
        nullable: bool = False,
        default: str | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        super().__init__(
            python_type=str,
            sql_type="TEXT",
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            validators=validators,
        )


class Char(Column):
    def __init__(
        self,
        length: int,
        *,
        unique: bool = False,
        nullable: bool = False,
        default: str | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        super().__init__(
            python_type=str,
            sql_type=f"CHAR({length})",
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            max_length=length,
            validators=validators,
        )


__all__ = ["String", "Text", "Char"]
