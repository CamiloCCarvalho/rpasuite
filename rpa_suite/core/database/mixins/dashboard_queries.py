# rpa_suite/core/database/mixins/dashboard_queries.py

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from ..constants import DatabaseType, VALID_LOG_LEVELS


_ALLOWED_EXECUTION_SORT = {
    "id",
    "started_at",
    "finished_at",
    "status",
    "automation_name",
    "total_items",
    "successful_items",
    "failed_items",
    "execution_time_seconds",
}
_ALLOWED_ITEM_SORT = {
    "id",
    "execution_id",
    "status",
    "priority",
    "started_at",
    "finished_at",
    "created_at",
    "updated_at",
    "retry_count",
}
_ALLOWED_LOG_SORT = {"id", "execution_id", "log_level", "timestamp", "step_name"}
_ALLOWED_ORDER = {"asc", "desc"}
_LIKE_CHARS = ("\\", "%", "_")


class DashboardQueriesMixin:
    """
    Read-only, paginated + filterable queries built for the dashboard.

    All methods here are safe to call against large tables: they enforce a
    reasonable page-size cap and only bind user input as SQL parameters, never
    interpolating raw strings into the SQL text. Column names for sorting are
    validated against explicit allowlists.
    """

    _MAX_PAGE_SIZE = 500

    @staticmethod
    def _clamp_pagination(page: int, page_size: int, cap: int) -> Tuple[int, int, int]:
        """Normalize `page`/`page_size` to safe values and compute offset."""
        page = max(1, int(page or 1))
        page_size = max(1, min(int(page_size or 25), int(cap)))
        offset = (page - 1) * page_size
        return page, page_size, offset

    @staticmethod
    def _escape_like(value: str) -> str:
        """Escape LIKE wildcards so user input is treated literally."""
        for ch in _LIKE_CHARS:
            value = value.replace(ch, f"\\{ch}")
        return value

    def _rows_as_dicts(self, cursor) -> List[Dict[str, Any]]:
        cols = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall() or []
        return [dict(zip(cols, row)) for row in rows]

    # ---------------- Executions ---------------------------------------------

    def list_executions(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        status: Optional[str] = None,
        automation_name: Optional[str] = None,
        started_after: Optional[str] = None,
        started_before: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
        sort_by: str = "started_at",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """
        List executions with filters and pagination.

        Filters:
            * status: exact match against `status` column
            * automation_name: case-insensitive substring
            * started_after / started_before: ISO-ish date strings

        Returns dict `{items, page, page_size, total, pages}`.
        """
        self._ensure_open()  # type: ignore[attr-defined]

        sort_by = sort_by if sort_by in _ALLOWED_EXECUTION_SORT else "started_at"
        sort_order = sort_order if sort_order in _ALLOWED_ORDER else "desc"

        where: List[str] = []
        params: List[Any] = []
        if status:
            where.append("status = ?")
            params.append(status)
        if automation_name:
            where.append("LOWER(automation_name) LIKE ? ESCAPE '\\'")
            params.append(f"%{self._escape_like(automation_name.lower())}%")
        if started_after:
            where.append("started_at >= ?")
            params.append(started_after)
        if started_before:
            where.append("started_at <= ?")
            params.append(started_before)

        where_sql = f" WHERE {' AND '.join(where)}" if where else ""

        count_cursor = self._adapter.execute_query(  # type: ignore[attr-defined]
            f"SELECT COUNT(*) FROM {self.executions_table}{where_sql}",  # type: ignore[attr-defined]
            tuple(params),
        )
        total_row = count_cursor.fetchone()
        total = int(total_row[0]) if total_row else 0

        page, page_size, offset = self._clamp_pagination(page, page_size, self._MAX_PAGE_SIZE)

        list_sql = (
            f"SELECT id, execution_id, automation_name, status, finished_properly, "
            f"       started_at, finished_at, execution_time_seconds, total_items, "
            f"       successful_items, failed_items, interrupted_items, error_message "
            f"FROM {self.executions_table}"  # type: ignore[attr-defined]
            f"{where_sql} "
            f"ORDER BY {sort_by} {sort_order.upper()} "
            f"LIMIT ? OFFSET ?"
        )
        cursor = self._adapter.execute_query(  # type: ignore[attr-defined]
            list_sql,
            tuple(params) + (page_size, offset),
        )
        rows = self._rows_as_dicts(cursor)

        pages = (total + page_size - 1) // page_size if page_size else 1
        return {
            "items": rows,
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": max(1, pages),
        }

    # ---------------- Items --------------------------------------------------

    def list_items(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        execution_id: Optional[int] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
        sort_by: str = "id",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """
        List items with filters and pagination.

        Filters:
            * execution_id: exact match
            * status: exact match
            * search: case-insensitive substring on `item_identifier`

        Returns dict `{items, page, page_size, total, pages}`.
        """
        self._ensure_open()  # type: ignore[attr-defined]

        sort_by = sort_by if sort_by in _ALLOWED_ITEM_SORT else "id"
        sort_order = sort_order if sort_order in _ALLOWED_ORDER else "desc"

        where: List[str] = []
        params: List[Any] = []
        if execution_id is not None:
            where.append("execution_id = ?")
            params.append(int(execution_id))
        if status:
            where.append("status = ?")
            params.append(status)
        if search:
            where.append("LOWER(item_identifier) LIKE ? ESCAPE '\\'")
            params.append(f"%{self._escape_like(search.lower())}%")

        where_sql = f" WHERE {' AND '.join(where)}" if where else ""

        count_cursor = self._adapter.execute_query(  # type: ignore[attr-defined]
            f"SELECT COUNT(*) FROM {self.items_table}{where_sql}",  # type: ignore[attr-defined]
            tuple(params),
        )
        total_row = count_cursor.fetchone()
        total = int(total_row[0]) if total_row else 0

        page, page_size, offset = self._clamp_pagination(page, page_size, self._MAX_PAGE_SIZE)

        list_sql = (
            f"SELECT id, execution_id, item_identifier, status, priority, "
            f"       started_at, finished_at, execution_time_seconds, "
            f"       retry_count, max_retries, error_message, created_at, updated_at "
            f"FROM {self.items_table}"  # type: ignore[attr-defined]
            f"{where_sql} "
            f"ORDER BY {sort_by} {sort_order.upper()} "
            f"LIMIT ? OFFSET ?"
        )
        cursor = self._adapter.execute_query(  # type: ignore[attr-defined]
            list_sql,
            tuple(params) + (page_size, offset),
        )
        rows = self._rows_as_dicts(cursor)

        pages = (total + page_size - 1) // page_size if page_size else 1
        return {
            "items": rows,
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": max(1, pages),
        }

    # ---------------- Logs ---------------------------------------------------

    def list_logs(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        execution_id: Optional[int] = None,
        log_level: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "timestamp",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """
        List log entries with filters and pagination.

        Filters:
            * execution_id: exact match
            * log_level: exact match (must be a known level)
            * search: case-insensitive substring on `message`

        Returns dict `{items, page, page_size, total, pages}`.
        """
        self._ensure_open()  # type: ignore[attr-defined]

        sort_by = sort_by if sort_by in _ALLOWED_LOG_SORT else "timestamp"
        sort_order = sort_order if sort_order in _ALLOWED_ORDER else "desc"

        where: List[str] = []
        params: List[Any] = []
        if execution_id is not None:
            where.append("execution_id = ?")
            params.append(int(execution_id))
        if log_level and log_level in VALID_LOG_LEVELS:
            where.append("log_level = ?")
            params.append(log_level)
        if search:
            where.append("LOWER(message) LIKE ? ESCAPE '\\'")
            params.append(f"%{self._escape_like(search.lower())}%")

        where_sql = f" WHERE {' AND '.join(where)}" if where else ""

        count_cursor = self._adapter.execute_query(  # type: ignore[attr-defined]
            f"SELECT COUNT(*) FROM {self.logs_table}{where_sql}",  # type: ignore[attr-defined]
            tuple(params),
        )
        total_row = count_cursor.fetchone()
        total = int(total_row[0]) if total_row else 0

        page, page_size, offset = self._clamp_pagination(page, page_size, self._MAX_PAGE_SIZE)

        list_sql = (
            f"SELECT id, execution_id, log_level, step_name, message, timestamp "
            f"FROM {self.logs_table}"  # type: ignore[attr-defined]
            f"{where_sql} "
            f"ORDER BY {sort_by} {sort_order.upper()} "
            f"LIMIT ? OFFSET ?"
        )
        cursor = self._adapter.execute_query(  # type: ignore[attr-defined]
            list_sql,
            tuple(params) + (page_size, offset),
        )
        rows = self._rows_as_dicts(cursor)

        pages = (total + page_size - 1) // page_size if page_size else 1
        return {
            "items": rows,
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": max(1, pages),
        }

    # ---------------- Aggregations for charts --------------------------------

    def _date_expr(self, column: str) -> str:
        """Return a SQL expression that truncates `column` to a date string."""
        if self.db_type == DatabaseType.SQLITE:  # type: ignore[attr-defined]
            return f"substr({column}, 1, 10)"
        if self.db_type == DatabaseType.POSTGRESQL:  # type: ignore[attr-defined]
            return f"to_char({column}::date, 'YYYY-MM-DD')"
        if self.db_type == DatabaseType.MYSQL:  # type: ignore[attr-defined]
            return f"DATE_FORMAT({column}, '%Y-%m-%d')"
        return f"substr({column}, 1, 10)"

    def executions_over_time(self, days: int = 14) -> List[Dict[str, Any]]:
        """
        Aggregate executions per day for the last `days` days.

        Returns list of `{date, total, completed, failed, interrupted}`.
        """
        self._ensure_open()  # type: ignore[attr-defined]
        days = max(1, min(int(days), 365))
        date_expr = self._date_expr("started_at")

        if self.db_type == DatabaseType.SQLITE:  # type: ignore[attr-defined]
            date_filter = "started_at >= datetime('now', '-' || ? || ' days')"
            params: Tuple[Any, ...] = (days,)
        elif self.db_type == DatabaseType.POSTGRESQL:  # type: ignore[attr-defined]
            date_filter = f"started_at >= NOW() - INTERVAL '{days} days'"
            params = ()
        else:
            date_filter = f"started_at >= DATE_SUB(NOW(), INTERVAL {days} DAY)"
            params = ()

        sql = (
            f"SELECT {date_expr} AS date, "
            f"       COUNT(*) AS total, "
            f"       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed, "
            f"       SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed, "
            f"       SUM(CASE WHEN status = 'interrupted' THEN 1 ELSE 0 END) AS interrupted "
            f"FROM {self.executions_table} "  # type: ignore[attr-defined]
            f"WHERE {date_filter} "
            f"GROUP BY date ORDER BY date ASC"
        )
        cursor = self._adapter.execute_query(sql, params)  # type: ignore[attr-defined]
        return [
            {
                "date": row[0],
                "total": int(row[1] or 0),
                "completed": int(row[2] or 0),
                "failed": int(row[3] or 0),
                "interrupted": int(row[4] or 0),
            }
            for row in (cursor.fetchall() or [])
        ]

    def item_status_distribution(self, execution_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Count items per status. When `execution_id` is set, scoped to it.

        Returns list of `{status, count}`.
        """
        self._ensure_open()  # type: ignore[attr-defined]
        where = ""
        params: Tuple[Any, ...] = ()
        if execution_id is not None:
            where = " WHERE execution_id = ?"
            params = (int(execution_id),)
        sql = (
            f"SELECT status, COUNT(*) AS c "
            f"FROM {self.items_table}"  # type: ignore[attr-defined]
            f"{where} GROUP BY status ORDER BY c DESC"
        )
        cursor = self._adapter.execute_query(sql, params)  # type: ignore[attr-defined]
        return [
            {"status": row[0], "count": int(row[1] or 0)}
            for row in (cursor.fetchall() or [])
        ]

    def log_level_distribution(self, execution_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Count log entries per level. When `execution_id` is set, scoped to it.

        Returns list of `{log_level, count}`.
        """
        self._ensure_open()  # type: ignore[attr-defined]
        where = ""
        params: Tuple[Any, ...] = ()
        if execution_id is not None:
            where = " WHERE execution_id = ?"
            params = (int(execution_id),)
        sql = (
            f"SELECT log_level, COUNT(*) AS c "
            f"FROM {self.logs_table}"  # type: ignore[attr-defined]
            f"{where} GROUP BY log_level ORDER BY c DESC"
        )
        cursor = self._adapter.execute_query(sql, params)  # type: ignore[attr-defined]
        return [
            {"log_level": row[0], "count": int(row[1] or 0)}
            for row in (cursor.fetchall() or [])
        ]

    def top_automations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Return the automations with the most executions.

        Returns list of `{automation_name, executions, failed, completed}`.
        """
        self._ensure_open()  # type: ignore[attr-defined]
        limit = max(1, min(int(limit), 50))
        sql = (
            f"SELECT automation_name, "
            f"       COUNT(*) AS executions, "
            f"       SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed, "
            f"       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed "
            f"FROM {self.executions_table} "  # type: ignore[attr-defined]
            f"GROUP BY automation_name ORDER BY executions DESC LIMIT ?"
        )
        cursor = self._adapter.execute_query(sql, (limit,))  # type: ignore[attr-defined]
        return [
            {
                "automation_name": row[0],
                "executions": int(row[1] or 0),
                "failed": int(row[2] or 0),
                "completed": int(row[3] or 0),
            }
            for row in (cursor.fetchall() or [])
        ]

    def dashboard_summary(self) -> Dict[str, Any]:
        """
        High-level aggregated summary used by the overview page.

        Combines `get_storage_stats` with per-status counts and running totals.
        """
        self._ensure_open()  # type: ignore[attr-defined]

        storage = self.get_storage_stats()  # type: ignore[attr-defined]

        exec_cursor = self._adapter.execute_query(  # type: ignore[attr-defined]
            f"SELECT status, COUNT(*) FROM {self.executions_table} GROUP BY status"  # type: ignore[attr-defined]
        )
        exec_by_status = {row[0]: int(row[1] or 0) for row in (exec_cursor.fetchall() or [])}

        item_status = self.item_status_distribution()
        log_levels = self.log_level_distribution()

        return {
            "storage": storage,
            "executions_by_status": exec_by_status,
            "items_by_status": item_status,
            "logs_by_level": log_levels,
        }
