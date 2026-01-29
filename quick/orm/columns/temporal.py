from typing import Callable, Any
from datetime import datetime, date, time
from quick.orm.columns.base import Column


class DateTime(Column):
    def __init__(
        self,
        *,
        auto_now: bool = False,
        auto_now_add: bool = False,
        unique: bool = False,
        nullable: bool = False,
        default: datetime | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add
        
        sql_default = None
        if auto_now_add or auto_now:
            sql_default = "CURRENT_TIMESTAMP"
        elif default is not None:
            sql_default = default
        
        super().__init__(
            python_type=datetime,
            sql_type="TIMESTAMP",
            unique=unique,
            nullable=nullable,
            default=sql_default,
            index=index,
            validators=validators,
        )


class Date(Column):
    def __init__(
        self,
        *,
        unique: bool = False,
        nullable: bool = False,
        default: date | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        super().__init__(
            python_type=date,
            sql_type="DATE",
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            validators=validators,
        )


class Time(Column):
    def __init__(
        self,
        *,
        unique: bool = False,
        nullable: bool = False,
        default: time | None = None,
        index: bool = False,
        validators: list[Callable] | None = None,
    ):
        super().__init__(
            python_type=time,
            sql_type="TIME",
            unique=unique,
            nullable=nullable,
            default=default,
            index=index,
            validators=validators,
        )


__all__ = ["DateTime", "Date", "Time"]
