# rpa_suite/core/database/helpers.py

from typing import Any

from .constants import DatabaseType


def row_to_dict(row: Any, db_type: DatabaseType) -> dict[str, Any]:
    """Convert a cursor row to a dict regardless of database backend."""
    if row is None:
        return {}
    if db_type == DatabaseType.SQLITE:
        return dict(row)
    if hasattr(row, "keys"):
        return dict(row)
    if isinstance(row, tuple):
        return {index: value for index, value in enumerate(row)}
    return dict(row)


def rows_to_dicts(rows: list[Any], db_type: DatabaseType) -> list[dict[str, Any]]:
    """Convert multiple cursor rows to dicts."""
    return [row_to_dict(row, db_type) for row in rows]


def resolve_execution_id(
    execution_id: int | None,
    current_execution_id: int | None,
    *,
    operation: str = "perform this operation",
) -> int:
    """Resolve an explicit execution_id or fall back to the active execution."""
    from .exceptions import DatabaseError

    resolved = execution_id if execution_id is not None else current_execution_id
    if not resolved:
        raise DatabaseError(
            "execution_id was not provided and no active execution was found. "
            f"Call start_execution() before {operation} or pass execution_id."
        )
    return int(resolved)


def extract_row_id(row: Any) -> int:
    """Extract the integer id from a single-column query result."""
    if isinstance(row, tuple):
        return int(row[0])
    if isinstance(row, dict):
        return int(row["id"])
    return int(row[0])


def build_item_status_filter(
    status: str | None,
    default_status: str | None = None,
) -> tuple[str, list[Any]]:
    """
    Build SQL clause and parameters for get_items status filtering.

    Groups:
    - pending/pendente: pending, queued
    - executed/executado: success, failed, skipped
    - interrupted/interrompido: interrupted
    - backlog/reprocessavel: unfinished work (excludes success/skipped)
    - all/todos: no status filter
    - any other value: exact status match
    """
    from .constants import DEFAULT_GET_ITEMS_STATUS, ITEM_STATUS_FILTER_GROUPS

    resolved = status if status is not None else (default_status or DEFAULT_GET_ITEMS_STATUS)
    normalized = resolved.lower().strip()

    if normalized in ITEM_STATUS_FILTER_GROUPS:
        group = ITEM_STATUS_FILTER_GROUPS[normalized]
        if group is None:
            return "", []
        placeholders = ", ".join("?" for _ in group)
        return f" AND status IN ({placeholders})", list(group)

    return " AND status = ?", [resolved]
