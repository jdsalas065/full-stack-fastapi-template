"""
Utility functions and helpers.

Common helper functions used across the application.
Organize into submodules as the project grows.
"""

import re
from datetime import datetime, timezone
from typing import Any


def get_current_utc_time() -> datetime:
    """
    Get current UTC time.

    Returns:
        Current datetime in UTC timezone
    """
    return datetime.now(timezone.utc)


def snake_to_camel(snake_str: str) -> str:
    """
    Convert snake_case to camelCase.

    Args:
        snake_str: String in snake_case format

    Returns:
        String in camelCase format

    Example:
        >>> snake_to_camel("hello_world")
        'helloWorld'
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def camel_to_snake(camel_str: str) -> str:
    """
    Convert camelCase to snake_case.

    Args:
        camel_str: String in camelCase format

    Returns:
        String in snake_case format

    Example:
        >>> camel_to_snake("helloWorld")
        'hello_world'
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()


def remove_none_values(data: dict[str, Any]) -> dict[str, Any]:
    """
    Remove None values from a dictionary.

    Args:
        data: Dictionary with potential None values

    Returns:
        Dictionary with None values removed

    Example:
        >>> remove_none_values({"a": 1, "b": None, "c": 3})
        {'a': 1, 'c': 3}
    """
    return {k: v for k, v in data.items() if v is not None}
