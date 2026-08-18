# rpa_suite/core/database/dialect_sql.py

from __future__ import annotations

from .constants import DatabaseType


def paginate_clause(db_type: DatabaseType) -> str:
    """
    Return the pagination SQL suffix for the active backend.

    Placeholders use ``?`` and are normalized by the adapter.
    """
    if db_type == DatabaseType.SQLSERVER:
        return "OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
    return "LIMIT ? OFFSET ?"


def paginate_params(db_type: DatabaseType, page_size: int, offset: int) -> tuple[int, int]:
    """Return ``(limit, offset)`` params in the order expected by ``paginate_clause``."""
    if db_type == DatabaseType.SQLSERVER:
        return (offset, page_size)
    return (page_size, offset)


def select_top_prefix(db_type: DatabaseType, n: int = 1) -> str:
    """Return ``TOP (n)`` prefix for SQL Server or an empty string for other backends."""
    if db_type == DatabaseType.SQLSERVER:
        return f"TOP ({int(n)}) "
    return ""


def limit_suffix(db_type: DatabaseType, n: int | str) -> str:
    """
    Append-style limit for queries that already have ``ORDER BY``.

    SQL Server uses ``OFFSET/FETCH``; others use ``LIMIT``.
    """
    if db_type == DatabaseType.SQLSERVER:
        return f"OFFSET 0 ROWS FETCH NEXT {n} ROWS ONLY"
    return f"LIMIT {n}"


def limit_one_suffix(db_type: DatabaseType) -> str:
    """Return ``LIMIT 1`` for backends that do not use ``select_top_prefix``."""
    if db_type == DatabaseType.SQLSERVER:
        return ""
    return "LIMIT 1"


def drop_index_sql(db_type: DatabaseType, index_name: str, table_name: str) -> str:
    """Return a best-effort ``DROP INDEX`` statement for the backend."""
    if db_type == DatabaseType.SQLSERVER:
        return f"DROP INDEX IF EXISTS {index_name} ON {table_name}"
    return f"DROP INDEX IF EXISTS {index_name}"


def create_index_sql(
    db_type: DatabaseType,
    index_name: str,
    table_name: str,
    columns: str,
    *,
    unique: bool = False,
    where: str | None = None,
) -> str:
    """Return a ``CREATE INDEX`` statement appropriate for the backend."""
    unique_kw = "UNIQUE " if unique else ""
    where_clause = f" WHERE {where}" if where else ""
    if db_type == DatabaseType.SQLSERVER:
        return f"CREATE {unique_kw}INDEX {index_name} ON {table_name}({columns}){where_clause}"
    return f"CREATE {unique_kw}INDEX IF NOT EXISTS {index_name} " f"ON {table_name}({columns}){where_clause}"


def supports_returning(db_type: DatabaseType) -> bool:
    """Return True when ``UPDATE ... RETURNING`` can be used natively."""
    return db_type in (DatabaseType.SQLITE, DatabaseType.POSTGRESQL)


def uses_mysql_claim_path(db_type: DatabaseType) -> bool:
    """Return True when queue claim should use SELECT + conditional UPDATE."""
    return db_type == DatabaseType.MYSQL


def uses_sqlserver_output_claim(db_type: DatabaseType) -> bool:
    """Return True when queue claim should use ``UPDATE ... OUTPUT INSERTED.*``."""
    return db_type == DatabaseType.SQLSERVER
