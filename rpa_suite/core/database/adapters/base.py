# rpa_suite/core/database/adapters/base.py

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from typing import Any

from ..exceptions import DatabaseError


class DatabaseAdapter(ABC):
    """Abstract database adapter with locking and placeholder normalization."""

    param_style: str = "?"

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.connection: Any = None

    def _prepare_query(self, query: str) -> str:
        if self.param_style == "?":
            return query
        return query.replace("?", self.param_style)

    @abstractmethod
    def connect(self) -> Any:
        pass

    def execute_query(self, query: str, params: tuple | None = None) -> Any:
        with self._lock:
            return self._execute_query_impl(self._prepare_query(query), params)

    @abstractmethod
    def _execute_query_impl(self, query: str, params: tuple | None = None) -> Any:
        pass

    def execute_many(self, query: str, params_list: list[tuple]) -> None:
        with self._lock:
            self._execute_many_impl(self._prepare_query(query), params_list)

    @abstractmethod
    def _execute_many_impl(self, query: str, params_list: list[tuple]) -> None:
        pass

    def commit(self) -> None:
        with self._lock:
            self._commit_impl()

    @abstractmethod
    def _commit_impl(self) -> None:
        pass

    def rollback(self) -> None:
        with self._lock:
            self._rollback_impl()

    @abstractmethod
    def _rollback_impl(self) -> None:
        pass

    def close(self) -> None:
        with self._lock:
            self._close_impl()

    @abstractmethod
    def _close_impl(self) -> None:
        pass

    @abstractmethod
    def get_last_insert_id(self, cursor: Any, table_name: str) -> int:
        pass

    @abstractmethod
    def get_table_exists_query(self, table_name: str) -> str:
        pass

    @abstractmethod
    def escape_table_name(self, table_name: str) -> str:
        pass

    def rowcount(self, cursor: Any) -> int:
        return cursor.rowcount if hasattr(cursor, "rowcount") and cursor.rowcount is not None else 0
