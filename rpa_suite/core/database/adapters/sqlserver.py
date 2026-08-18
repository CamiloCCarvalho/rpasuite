# rpa_suite/core/database/adapters/sqlserver.py

from __future__ import annotations

from typing import Any, List, Optional, Tuple

from ..exceptions import DatabaseError
from ..validation import validate_table_name
from .base import DatabaseAdapter

try:
    import pyodbc

    SQLSERVER_AVAILABLE = True
except ImportError:
    SQLSERVER_AVAILABLE = False


class _DictCursor:
    """Wrap a pyodbc cursor so fetch methods return column-name dict rows."""

    def __init__(self, cursor: Any) -> None:
        self._cursor = cursor
        self.description = cursor.description
        self.rowcount = cursor.rowcount if cursor.rowcount is not None else 0
        self._columns = [column[0] for column in (cursor.description or [])]

    def fetchone(self) -> Optional[dict[str, Any]]:
        row = self._cursor.fetchone()
        if row is None:
            return None
        return dict(zip(self._columns, row))

    def fetchall(self) -> list[dict[str, Any]]:
        return [dict(zip(self._columns, row)) for row in self._cursor.fetchall()]


class SQLServerAdapter(DatabaseAdapter):
    """Microsoft SQL Server adapter via pyodbc."""

    param_style = "?"

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        driver: str = "ODBC Driver 17 for SQL Server",
        trust_server_certificate: bool = True,
        encrypt: bool = True,
    ) -> None:
        super().__init__()
        if not SQLSERVER_AVAILABLE:
            raise DatabaseError("SQL Server is not available. Install: pip install rpa-suite[sqlserver]")
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.driver = driver
        self.trust_server_certificate = trust_server_certificate
        self.encrypt = encrypt

    def _connection_string(self) -> str:
        trust = "yes" if self.trust_server_certificate else "no"
        encrypt = "yes" if self.encrypt else "no"
        return (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.host},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.user};"
            f"PWD={self.password};"
            f"TrustServerCertificate={trust};"
            f"Encrypt={encrypt};"
        )

    def connect(self) -> Any:
        try:
            self.connection = pyodbc.connect(self._connection_string(), autocommit=False)
            return self.connection
        except Exception as e:
            raise DatabaseError(f"Failed to connect to SQL Server: {str(e)}.") from e

    def _execute_query_impl(self, query: str, params: Optional[Tuple] = None) -> _DictCursor:
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return _DictCursor(cursor)
        except Exception as e:
            raise DatabaseError(f"Failed to execute SQL Server query: {str(e)}.") from e

    def _execute_many_impl(self, query: str, params_list: List[Tuple]) -> None:
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
        except Exception as e:
            raise DatabaseError(f"Failed to execute SQL Server executemany: {str(e)}.") from e

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

    def get_last_insert_id(self, cursor: Any, table_name: str) -> int:
        validated_name = validate_table_name(table_name)
        try:
            id_cursor = self._execute_query_impl("SELECT CAST(SCOPE_IDENTITY() AS INT) AS id")
            row = id_cursor.fetchone()
            if row and row.get("id") is not None:
                return int(row["id"])
        except Exception:
            pass
        try:
            id_cursor = self._execute_query_impl(f"SELECT IDENT_CURRENT('{validated_name}')")
            row = id_cursor.fetchone()
            if row:
                value = next(iter(row.values()))
                if value is not None:
                    return int(value)
        except Exception:
            pass
        return 0

    def get_table_exists_query(self, table_name: str) -> str:
        validated_name = validate_table_name(table_name)
        return f"""
            SELECT COUNT(*)
            FROM sys.tables
            WHERE name = '{validated_name}'
        """

    def escape_table_name(self, table_name: str) -> str:
        return f"[{validate_table_name(table_name)}]"
