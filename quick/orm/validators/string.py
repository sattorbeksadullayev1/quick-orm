from typing import Any, Protocol


class Validator(Protocol):
    def __call__(self, value: Any) -> None:
        ...


class MinLength:
    def __init__(self, min_length: int, message: str | None = None):
        self.min_length = min_length
        self.message = message or f"Value must be at least {min_length} characters long"
    
    def __call__(self, value: str) -> None:
        if len(value) < self.min_length:
            raise ValueError(self.message)


class MaxLength:
    def __init__(self, max_length: int, message: str | None = None):
        self.max_length = max_length
        self.message = message or f"Value must be at most {max_length} characters long"
    
    def __call__(self, value: str) -> None:
        if len(value) > self.max_length:
            raise ValueError(self.message)


class Regex:
    def __init__(self, pattern: str, message: str | None = None):
        import re
        self.pattern = re.compile(pattern)
        self.message = message or f"Value does not match pattern: {pattern}"
    
    def __call__(self, value: str) -> None:
        if not self.pattern.match(value):
            raise ValueError(self.message)


class Email:
    def __init__(self, message: str | None = None):
        import re
        self.pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        self.message = message or "Invalid email address"
    
    def __call__(self, value: str) -> None:
        if not self.pattern.match(value):
            raise ValueError(self.message)


class URL:
    def __init__(self, message: str | None = None):
        import re
        self.pattern = re.compile(
            r"^https?://"
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
            r"localhost|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        self.message = message or "Invalid URL"
    
    def __call__(self, value: str) -> None:
        if not self.pattern.match(value):
            raise ValueError(self.message)


class PhoneNumber:
    def __init__(self, message: str | None = None):
        import re
        self.pattern = re.compile(r"^\+?1?\d{9,15}$")
        self.message = message or "Invalid phone number"
    
    def __call__(self, value: str) -> None:
        if not self.pattern.match(value):
            raise ValueError(self.message)


__all__ = ["Validator", "MinLength", "MaxLength", "Regex", "Email", "URL", "PhoneNumber"]
