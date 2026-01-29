from typing import Any


class Range:
    def __init__(self, min_value: float | None = None, max_value: float | None = None, message: str | None = None):
        self.min_value = min_value
        self.max_value = max_value
        
        if message is None:
            if min_value is not None and max_value is not None:
                self.message = f"Value must be between {min_value} and {max_value}"
            elif min_value is not None:
                self.message = f"Value must be at least {min_value}"
            elif max_value is not None:
                self.message = f"Value must be at most {max_value}"
            else:
                self.message = "Value out of range"
        else:
            self.message = message
    
    def __call__(self, value: float | int) -> None:
        if self.min_value is not None and value < self.min_value:
            raise ValueError(self.message)
        if self.max_value is not None and value > self.max_value:
            raise ValueError(self.message)


class Positive:
    def __init__(self, message: str | None = None):
        self.message = message or "Value must be positive"
    
    def __call__(self, value: float | int) -> None:
        if value <= 0:
            raise ValueError(self.message)


class Negative:
    def __init__(self, message: str | None = None):
        self.message = message or "Value must be negative"
    
    def __call__(self, value: float | int) -> None:
        if value >= 0:
            raise ValueError(self.message)


class NonNegative:
    def __init__(self, message: str | None = None):
        self.message = message or "Value must be non-negative"
    
    def __call__(self, value: float | int) -> None:
        if value < 0:
            raise ValueError(self.message)


class NonPositive:
    def __init__(self, message: str | None = None):
        self.message = message or "Value must be non-positive"
    
    def __call__(self, value: float | int) -> None:
        if value > 0:
            raise ValueError(self.message)


__all__ = ["Range", "Positive", "Negative", "NonNegative", "NonPositive"]
