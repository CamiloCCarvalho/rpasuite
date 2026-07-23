# rpa_suite/core/database/validation.py

import re

from .exceptions import DatabaseError


def validate_table_name(table_name: str) -> str:
    """Validate and sanitize table names to prevent SQL injection."""
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
        raise DatabaseError(
            f"Invalid table name: '{table_name}'. "
            "Only letters, numbers, and underscores are allowed. "
            "The name must start with a letter or underscore."
        )
    if len(table_name) > 64:
        raise DatabaseError(f"Table name too long: '{table_name}'. " "Maximum 64 characters allowed.")
    return table_name


def validate_limit(limit: int | None) -> int | None:
    """Validate the LIMIT parameter for safe SQL usage."""
    if limit is None:
        return None
    if not isinstance(limit, int) or limit < 0:
        raise DatabaseError(f"Invalid LIMIT: {limit!r}. Must be an integer >= 0.")
    return limit


def validate_days(days: int | None) -> int | None:
    """Validate the day-count parameter for time-based filters."""
    if days is None:
        return None
    if not isinstance(days, int) or days < 0:
        raise DatabaseError(f"Invalid older_than_days: {days!r}. Must be an integer >= 0.")
    return days


def validate_json_key(json_key: str) -> str:
    """Validate JSON object keys used in SQL JSON path expressions."""
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", json_key):
        raise DatabaseError(
            f"Invalid JSON key: '{json_key}'. "
            "Only letters, numbers, and underscores are allowed. "
            "The key must start with a letter or underscore."
        )
    if len(json_key) > 64:
        raise DatabaseError(f"JSON key too long: '{json_key}'. Maximum 64 characters allowed.")
    return json_key


def validate_unique_item_field(unique_item_field: str) -> str:
    """Validate the deduplication field configuration."""
    if unique_item_field == "item_identifier":
        return unique_item_field
    if unique_item_field.startswith("item_data."):
        json_key = unique_item_field.split(".", 1)[1]
        if not json_key:
            raise DatabaseError("Invalid unique_item_field. Use 'item_identifier' or 'item_data.<key>'.")
        validate_json_key(json_key)
        return unique_item_field
    raise DatabaseError(
        f"Invalid unique_item_field: '{unique_item_field}'. " "Use 'item_identifier' or 'item_data.<key>'."
    )
