# rpa_suite/core/database/adapters/sqlite.py

from __future__ import annotations

import sqlite3

from ..constants import DEFAULT_SQLITE_BUSY_TIMEOUT_MS
from ..exceptions import DatabaseError
from ..validation import validate_table_name
from .base import DatabaseAdapter


class SQLiteAdapter(DatabaseAdapter):
    """SQLite adapter with WAL, busy_timeout, and locking."""

    param_style = "?"

    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
            )
            self.connection.row_factory = sqlite3.Row
            self.connection.execute(f"PRAGMA busy_timeout = {DEFAULT_SQLITE_BUSY_TIMEOUT_MS}")
            self.connection.execute("PRAGMA journal_mode = WAL")
            return self.connection
        except Exception as e:
            raise DatabaseError(f"Failed to connect to SQLite: {str(e)}.") from e

    def _execute_query_impl(self, query: str, params: tuple | None = None) -> sqlite3.Cursor:
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except Exception as e:
            raise DatabaseError(f"Failed to execute SQLite query: {str(e)}.") from e

    def _execute_many_impl(self, query: str, params_list: list[tuple]) -> None:
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
        except Exception as e:
            raise DatabaseError(f"Failed to execute SQLite executemany: {str(e)}.") from e

    def _commit_impl(self) -> None:
        if self.connection:
            self.connection.commit()

    def _rollback_impl(self) -> None:
        if self.connection:
            self.connection.rollback()

    def _close_impl(self) -> None:
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_last_insert_id(self, cursor: sqlite3.Cursor, table_name: str) -> int:
        return cursor.lastrowid

    def get_table_exists_query(self, table_name: str) -> str:
        validated_name = validate_table_name(table_name)
        return f"SELECT name FROM sqlite_master WHERE type='table' AND name='{validated_name}'"

    def escape_table_name(self, table_name: str) -> str:
        return validate_table_name(table_name)
