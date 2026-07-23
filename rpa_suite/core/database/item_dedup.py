# rpa_suite/core/database/item_dedup.py

from __future__ import annotations

from typing import Any

from .validation import validate_json_key


def extract_item_unique_value(
    unique_item_field: str,
    item_identifier: str | None,
    item_data: dict[str, Any] | None,
) -> str | None:
    """
    Extract the value used for global item deduplication.

    ``unique_item_field``:
    - ``item_identifier``: uses the item_identifier column
    - ``item_data.<key>``: uses a key from the item_data JSON (e.g. item_data.order_id)
    """
    if unique_item_field == "item_identifier":
        if item_identifier is None or str(item_identifier).strip() == "":
            return None
        return str(item_identifier).strip()

    if unique_item_field.startswith("item_data."):
        key = unique_item_field.split(".", 1)[1]
        if not item_data or key not in item_data:
            return None
        value = item_data[key]
        if value is None or str(value).strip() == "":
            return None
        return str(value).strip()

    raise ValueError(
        f"Invalid unique_item_field: '{unique_item_field}'. " "Use 'item_identifier' or 'item_data.<key>'."
    )


def resolve_item_identifier_for_storage(
    unique_item_field: str,
    item_identifier: str | None,
    item_data: dict[str, Any] | None,
) -> str | None:
    """Ensure item_identifier is populated when dedup uses an item_data field."""
    if item_identifier is not None and str(item_identifier).strip() != "":
        return str(item_identifier).strip()
    return extract_item_unique_value(unique_item_field, item_identifier, item_data)


def json_extract_sql(db_type_name: str, column: str, json_key: str) -> str:
    """Return the SQL expression to extract a JSON key for the given database."""
    safe_key = validate_json_key(json_key)
    if db_type_name == "SQLITE":
        return f"json_extract({column}, '$.{safe_key}')"
    if db_type_name == "POSTGRESQL":
        return f"{column}::jsonb ->> '{safe_key}'"
    if db_type_name == "MYSQL":
        return f"JSON_UNQUOTE(JSON_EXTRACT({column}, '$.{safe_key}'))"
    return f"json_extract({column}, '$.{safe_key}')"


def json_extract_comparable_sql(db_type_name: str, column: str, json_key: str) -> str:
    """
    SQL expression to compare a JSON value against a normalized Python string.

    Required because SQLite json_extract returns REAL/INTEGER and text comparison
    fails (e.g. 150.0 vs '150.0').
    """
    expr = json_extract_sql(db_type_name, column, json_key)
    if db_type_name == "SQLITE":
        return f"CAST({expr} AS TEXT)"
    return expr
