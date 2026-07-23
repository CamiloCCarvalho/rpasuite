# rpa_suite/core/database/schema_migrations.py

from __future__ import annotations

from .constants import DatabaseType
from .exceptions import DatabaseError


def _sqlite_columns(adapter, table_name: str) -> set[str]:
    cursor = adapter.execute_query(f"PRAGMA table_info({table_name})")
    return {str(row[1]) for row in cursor.fetchall()}


def _postgresql_has_column(adapter, table_name: str, column_name: str) -> bool:
    cursor = adapter.execute_query(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = ?
          AND column_name = ?
        LIMIT 1
        """,
        (table_name, column_name),
    )
    return cursor.fetchone() is not None


def _mysql_has_column(adapter, table_name: str, column_name: str) -> bool:
    cursor = adapter.execute_query(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = ?
          AND column_name = ?
        LIMIT 1
        """,
        (table_name, column_name),
    )
    return cursor.fetchone() is not None


def _has_column(db_type: DatabaseType, adapter, table_name: str, column_name: str) -> bool:
    if db_type == DatabaseType.SQLITE:
        return column_name in _sqlite_columns(adapter, table_name)
    if db_type == DatabaseType.POSTGRESQL:
        return _postgresql_has_column(adapter, table_name, column_name)
    if db_type == DatabaseType.MYSQL:
        return _mysql_has_column(adapter, table_name, column_name)
    return False


def ensure_items_updated_at_column(
    db_type: DatabaseType,
    adapter,
    items_table: str,
) -> bool:
    """
    Add ``updated_at`` to the items table when missing (legacy databases).

    Returns True when a migration was applied.
    """
    if _has_column(db_type, adapter, items_table, "updated_at"):
        return False

    try:
        if db_type == DatabaseType.SQLITE:
            adapter.execute_query(
                f"""
                ALTER TABLE {items_table}
                ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                """
            )
        elif db_type == DatabaseType.POSTGRESQL:
            adapter.execute_query(
                f"""
                ALTER TABLE {items_table}
                ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                """
            )
        elif db_type == DatabaseType.MYSQL:
            adapter.execute_query(
                f"""
                ALTER TABLE {items_table}
                ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                """
            )
        else:
            raise DatabaseError(f"Unsupported database type for migration: {db_type}")

        adapter.execute_query(
            f"""
            UPDATE {items_table}
            SET updated_at = COALESCE(finished_at, started_at, created_at)
            WHERE updated_at IS NULL
            """
        )

        index_name = f"idx_{items_table}_updated_at"
        adapter.execute_query(
            f"CREATE INDEX IF NOT EXISTS {index_name} ON {items_table}(updated_at)"
        )
        adapter.commit()
        return True
    except Exception as e:
        adapter.rollback()
        raise DatabaseError(f"Failed to migrate items.updated_at column: {str(e)}.") from e


def run_schema_migrations(
    db_type: DatabaseType,
    adapter,
    items_table: str,
) -> list[str]:
    """Apply idempotent schema migrations. Returns applied migration names."""
    applied: list[str] = []
    if ensure_items_updated_at_column(db_type, adapter, items_table):
        applied.append("items.updated_at")
    return applied
