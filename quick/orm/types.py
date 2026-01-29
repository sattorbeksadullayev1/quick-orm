from typing import TypeVar, Optional, List, Union
from datetime import datetime, date, time
from uuid import UUID, uuid4
from decimal import Decimal

T = TypeVar("T")

BigInt = int
SmallInt = int

__all__ = [
    "Optional",
    "List",
    "Union",
    "UUID",
    "uuid4",
    "datetime",
    "date",
    "time",
    "Decimal",
    "BigInt",
    "SmallInt",
]
