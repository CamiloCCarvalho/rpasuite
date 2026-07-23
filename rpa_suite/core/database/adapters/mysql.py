# rpa_suite/core/database/adapters/mysql.py

from __future__ import annotations

from typing import Any

from ..exceptions import DatabaseError
from ..validation import validate_table_name
from .base import DatabaseAdapter

try:
    import mysql.connector
    from mysql.connector import pooling

    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


class MySQLAdapter(DatabaseAdapter):
    """MySQL adapter."""

    param_style = "%s"

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        use_pool: bool = True,
        pool_size: int = 5,
    ):
        super().__init__()
        if not MYSQL_AVAILABLE:
            raise DatabaseError("MySQL is not available. Install: pip install mysql-connector-python")
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.use_pool = use_pool
        self.pool_size = pool_size
        self.pool = None

    def connect(self) -> Any:
        try:
            if self.use_pool and self.pool is None:
                self.pool = pooling.MySQLConnectionPool(
                    pool_name="rpa_pool",
                    pool_size=self.pool_size,
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                )
            if self.use_pool:
                self.connection = self.pool.get_connection()
            else:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                )
            return self.connection
        except Exception as e:
            raise DatabaseError(f"Failed to connect to MySQL: {str(e)}.") from e

    def _execute_query_impl(self, query: str, params: tuple | None = None) -> Any:
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except Exception as e:
            raise DatabaseError(f"Failed to execute MySQL query: {str(e)}.") from e

    def _execute_many_impl(self, query: str, params_list: list[tuple]) -> None:
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
        except Exception as e:
            raise DatabaseError(f"Failed to execute MySQL executemany: {str(e)}.") from e

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
        if self.use_pool and self.pool:
            self.pool = None

    def get_last_insert_id(self, cursor: Any, table_name: str) -> int:
        return cursor.lastrowid

    def get_table_exists_query(self, table_name: str) -> str:
        validated_name = validate_table_name(table_name)
        return f"""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_name = '{validated_name}'
        """

    def escape_table_name(self, table_name: str) -> str:
        return f"`{validate_table_name(table_name)}`"
