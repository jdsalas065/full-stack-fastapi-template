"""
Application constants and enumerations.

This module contains all constants used throughout the application.
Organize by domain as the project grows.
"""

from enum import Enum


class Environment(str, Enum):
    """Application environment types."""

    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class Tags(str, Enum):
    """OpenAPI tags for grouping endpoints."""

    UTILS = "utils"
    DOCUMENT = "document"
    FILES = "files"
    # Add more tags as you add features:
    # USERS = "users"
    # ITEMS = "items"
    # AUTH = "auth"
