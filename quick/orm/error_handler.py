from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
import traceback
from .exceptions import QuickORMError, QueryError, ValidationError, ModelNotFoundError


console = Console()


class ErrorHandler:
    @staticmethod
    def format_error(error: Exception, show_traceback: bool = False) -> None:
        if isinstance(error, QueryError):
            ErrorHandler._format_query_error(error, show_traceback)
        elif isinstance(error, ValidationError):
            ErrorHandler._format_validation_error(error, show_traceback)
        elif isinstance(error, ModelNotFoundError):
            ErrorHandler._format_not_found_error(error, show_traceback)
        elif isinstance(error, QuickORMError):
            ErrorHandler._format_orm_error(error, show_traceback)
        else:
            ErrorHandler._format_generic_error(error, show_traceback)
    
    @staticmethod
    def _format_query_error(error: QueryError, show_traceback: bool) -> None:
        content = Text()
        content.append(f"❌ Query Error: {error.message}\n\n", style="bold red")
        
        if error.query:
            content.append("Query:\n", style="bold yellow")
            console.print(content)
            console.print(Syntax(error.query, "sql", theme="monokai", line_numbers=False))
        
        if error.params:
            console.print(Text(f"\nParameters: {error.params}", style="cyan"))
        
        if show_traceback:
            console.print("\n" + "".join(traceback.format_tb(error.__traceback__)), style="dim")
    
    @staticmethod
    def _format_validation_error(error: ValidationError, show_traceback: bool) -> None:
        content = Text()
        content.append(f"❌ Validation Error: {error.message}\n\n", style="bold red")
        
        if error.field:
            content.append(f"Field: {error.field}\n", style="yellow")
        
        if error.value is not None:
            content.append(f"Value: {error.value}\n", style="cyan")
        
        console.print(Panel(content, border_style="red", title="Validation Error"))
        
        if show_traceback:
            console.print("\n" + "".join(traceback.format_tb(error.__traceback__)), style="dim")
    
    @staticmethod
    def _format_not_found_error(error: ModelNotFoundError, show_traceback: bool) -> None:
        content = Text()
        content.append(f"❌ {error.message}\n\n", style="bold red")
        
        if error.conditions:
            content.append(f"Conditions: {error.conditions}\n", style="yellow")
        
        console.print(Panel(content, border_style="red", title="Not Found"))
        
        if show_traceback:
            console.print("\n" + "".join(traceback.format_tb(error.__traceback__)), style="dim")
    
    @staticmethod
    def _format_orm_error(error: QuickORMError, show_traceback: bool) -> None:
        content = Text()
        content.append(f"❌ {error.__class__.__name__}: {error.message}\n\n", style="bold red")
        
        if error.details:
            content.append(f"Details: {error.details}\n", style="yellow")
        
        console.print(Panel(content, border_style="red"))
        
        if show_traceback:
            console.print("\n" + "".join(traceback.format_tb(error.__traceback__)), style="dim")
    
    @staticmethod
    def _format_generic_error(error: Exception, show_traceback: bool) -> None:
        content = Text()
        content.append(f"❌ {error.__class__.__name__}: {str(error)}\n", style="bold red")
        
        console.print(Panel(content, border_style="red", title="Error"))
        
        if show_traceback:
            console.print("\n" + "".join(traceback.format_tb(error.__traceback__)), style="dim")


__all__ = ["ErrorHandler", "console"]
