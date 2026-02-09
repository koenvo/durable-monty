"""Function registry for external functions."""

from typing import Callable, Any

FUNCTION_REGISTRY: dict[str, Callable] = {}


def register_function(name: str):
    """Decorator to register a function for use in workflows."""
    def decorator(func: Callable) -> Callable:
        FUNCTION_REGISTRY[name] = func
        return func
    return decorator


def get_function(name: str) -> Callable:
    """Get a registered function by name."""
    if name not in FUNCTION_REGISTRY:
        raise KeyError(f"Function '{name}' not found in registry")
    return FUNCTION_REGISTRY[name]


def execute_function(name: str, args: list, kwargs: dict | None = None) -> Any:
    """Execute a registered function with given arguments."""
    func = get_function(name)
    return func(*args, **(kwargs or {}))
