# rpa_suite/core/database/mixins/retention.py

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional, Tuple

from ..constants import DatabaseType, VALID_LOG_LEVELS
from ..exceptions import DatabaseError
from ..retention import RetentionPolicy


class RetentionMixin:
    """Automatic retention and storage statistics — use via the Database class."""

    retention_policy: RetentionPolicy

    def finish_execution(
        self,
        execution_id: int,
        status: str = "completed",
        error_message: Optional[str] = None,
    ) -> bool:
        """Finish an execution and optionally run automatic retention."""
        result = super().finish_execution(execution_id, status, error_message)  # type: ignore[misc]
        self._run_auto_retention_on_finish()
        return result

    def _run_auto_retention_on_finish(self) -> None:
        policy = getattr(self, "retention_policy", None)
        if not policy or not policy.enabled or not policy.auto_on_finish_execution:
            return
        try:
            self.apply_retention_policy(dry_run=False)
        except Exception:
            pass

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Return row counts and approximate storage usage.

        Returns:
        --------
        dict: ``executions``, ``items``, ``logs`` row counts and optional ``database`` size.
        """
        self._ensure_open()
        try:
            stats: Dict[str, Any] = {}
            for table_key, table_name in (
                ("executions", self.executions_table),
                ("items", self.items_table),
                ("logs", self.logs_table),
            ):
                cursor = self._adapter.execute_query(
                    f"SELECT COUNT(*) FROM {table_name}"
                )
                row = cursor.fetchone()
                stats[table_key] = {"rows": int(row[0]) if row else 0}

            if self.db_type == DatabaseType.SQLITE:
                db_path = getattr(self._adapter, "db_path", None)
                if db_path and os.path.isfile(db_path):
                    approx_mb = round(os.path.getsize(db_path) / (1024 * 1024), 3)
                    stats["database"] = {"path": db_path, "approx_mb": approx_mb}

            return stats
        except Exception as e:
            raise DatabaseError(f"Failed to fetch storage stats: {str(e)}.") from e

    def apply_retention_policy(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Apply configured retention rules (TTL + row caps).

        Parameters:
        -----------
        dry_run: bool
            When True, only counts rows that would be deleted.

        Returns:
        --------
        dict: Summary with ``dry_run``, ``would_delete`` or ``deleted``, ``duration_ms``.
        """
        self._ensure_open()
        policy = getattr(self, "retention_policy", None)
        if not policy or not policy.enabled:
            raise DatabaseError(
                "Retention policy is disabled. "
                "Pass retention_policy={'enabled': True, ...} to Database()."
            )

        started = time.perf_counter()
        summary_key = "would_delete" if dry_run else "deleted"
        summary: Dict[str, int] = {"logs": 0, "items": 0, "executions": 0}

        try:
            summary["logs"] = self._apply_logs_retention(policy, dry_run=dry_run)
            summary["items"] = self._apply_items_retention(policy, dry_run=dry_run)
            summary["executions"] = self._apply_executions_retention(policy, dry_run=dry_run)

            if not dry_run:
                self._adapter.commit()
                if self.db_type == DatabaseType.SQLITE:
                    self._maybe_vacuum_sqlite(summary)

            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            return {
                "dry_run": dry_run,
                summary_key: summary,
                "duration_ms": duration_ms,
            }
        except DatabaseError:
            if not dry_run:
                self._adapter.rollback()
            raise
        except Exception as e:
            if not dry_run:
                self._adapter.rollback()
            raise DatabaseError(f"Failed to apply retention policy: {str(e)}.") from e

    def _maybe_vacuum_sqlite(self, summary: Dict[str, int]) -> None:
        deleted_total = summary["logs"] + summary["items"] + summary["executions"]
        if deleted_total >= 10_000:
            try:
                self._adapter.execute_query("VACUUM")
            except Exception:
                pass

    def _running_execution_filter(self, alias: str = "") -> str:
        prefix = f"{alias}." if alias else ""
        return (
            f"{prefix}execution_id NOT IN "
            f"(SELECT id FROM {self.executions_table} WHERE status = 'running')"
        )

    def _older_than_clause(self, column: str, days: int) -> Tuple[str, Tuple[Any, ...]]:
        if self.db_type == DatabaseType.SQLITE:
            return f"{column} < datetime('now', '-' || ? || ' days')", (days,)
        if self.db_type == DatabaseType.POSTGRESQL:
            return f"{column} < NOW() - INTERVAL '{days} days'", ()
        if self.db_type == DatabaseType.MYSQL:
            return f"{column} < DATE_SUB(NOW(), INTERVAL {days} DAY)", ()
        return f"{column} < datetime('now', '-' || ? || ' days')", (days,)

    def _fetch_scalar(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> int:
        cursor = self._adapter.execute_query(query, params)
        row = cursor.fetchone()
        return int(row[0]) if row and row[0] is not None else 0

    def _delete_in_batches(
        self,
        *,
        select_ids_query: str,
        select_params: Tuple[Any, ...],
        table_name: str,
        batch_size: int,
        dry_run: bool,
    ) -> int:
        if dry_run:
            base_query = select_ids_query.split("ORDER BY", 1)[0]
            count_query = base_query.replace("SELECT id", "SELECT COUNT(*)", 1)
            return self._fetch_scalar(count_query, select_params)

        total_deleted = 0
        while True:
            id_query = f"{select_ids_query} LIMIT ?"
            id_params: Tuple[Any, ...] = (*select_params, batch_size)
            cursor = self._adapter.execute_query(id_query, id_params)
            ids = [row[0] for row in cursor.fetchall()]
            if not ids:
                break

            placeholders = ", ".join("?" for _ in ids)
            delete_query = f"DELETE FROM {table_name} WHERE id IN ({placeholders})"
            delete_cursor = self._adapter.execute_query(delete_query, tuple(ids))
            total_deleted += self._adapter.rowcount(delete_cursor)
            self._adapter.commit()

        return total_deleted

    def _apply_logs_retention(self, policy: RetentionPolicy, *, dry_run: bool) -> int:
        cfg = policy.logs
        deleted = 0

        extended_levels = set(cfg.max_age_days_by_level.keys())
        default_levels = [level for level in VALID_LOG_LEVELS if level not in extended_levels]

        if default_levels:
            deleted += self._purge_logs_by_age(
                log_levels=default_levels,
                days=cfg.max_age_days,
                protect_running=cfg.protect_running_executions,
                batch_size=cfg.batch_size,
                dry_run=dry_run,
            )

        for level, days in cfg.max_age_days_by_level.items():
            deleted += self._purge_logs_by_age(
                log_levels=[level],
                days=days,
                protect_running=cfg.protect_running_executions,
                batch_size=cfg.batch_size,
                dry_run=dry_run,
            )

        if cfg.max_rows > 0:
            deleted += self._purge_logs_over_row_cap(
                max_rows=cfg.max_rows,
                protect_running=cfg.protect_running_executions,
                batch_size=cfg.batch_size,
                dry_run=dry_run,
            )

        return deleted

    def _purge_logs_by_age(
        self,
        *,
        log_levels: list[str],
        days: int,
        protect_running: bool,
        batch_size: int,
        dry_run: bool,
    ) -> int:
        age_clause, age_params = self._older_than_clause("timestamp", days)
        level_placeholders = ", ".join("?" for _ in log_levels)
        where_parts = [
            f"log_level IN ({level_placeholders})",
            age_clause,
        ]
        params: list[Any] = [*log_levels, *age_params]
        if protect_running:
            where_parts.append(self._running_execution_filter())
        where_sql = " AND ".join(where_parts)

        select_ids = f"""
            SELECT id FROM {self.logs_table}
            WHERE {where_sql}
            ORDER BY timestamp ASC
        """
        return self._delete_in_batches(
            select_ids_query=select_ids,
            select_params=tuple(params),
            table_name=self.logs_table,
            batch_size=batch_size,
            dry_run=dry_run,
        )

    def _purge_logs_over_row_cap(
        self,
        *,
        max_rows: int,
        protect_running: bool,
        batch_size: int,
        dry_run: bool,
    ) -> int:
        total_rows = self._fetch_scalar(f"SELECT COUNT(*) FROM {self.logs_table}")
        overflow = total_rows - max_rows
        if overflow <= 0:
            return 0

        where_parts = ["1=1"]
        if protect_running:
            where_parts.append(self._running_execution_filter())
        where_sql = " AND ".join(where_parts)

        select_ids = f"""
            SELECT id FROM {self.logs_table}
            WHERE {where_sql}
            ORDER BY timestamp ASC
        """
        if dry_run:
            count_query = f"""
                SELECT COUNT(*) FROM (
                    {select_ids}
                    LIMIT ?
                )
            """
            return self._fetch_scalar(count_query, (overflow,))

        deleted = 0
        remaining = overflow
        while remaining > 0:
            batch = min(batch_size, remaining)
            id_query = f"{select_ids} LIMIT ?"
            cursor = self._adapter.execute_query(id_query, (batch,))
            ids = [row[0] for row in cursor.fetchall()]
            if not ids:
                break
            placeholders = ", ".join("?" for _ in ids)
            delete_cursor = self._adapter.execute_query(
                f"DELETE FROM {self.logs_table} WHERE id IN ({placeholders})",
                tuple(ids),
            )
            batch_deleted = self._adapter.rowcount(delete_cursor)
            deleted += batch_deleted
            remaining -= batch_deleted
            self._adapter.commit()
            if batch_deleted == 0:
                break
        return deleted

    def _apply_items_retention(self, policy: RetentionPolicy, *, dry_run: bool) -> int:
        cfg = policy.items
        deleted = 0

        for status, days in cfg.max_age_days_by_status.items():
            if status in cfg.protect_statuses:
                continue
            deleted += self._purge_items_by_status_age(
                status=status,
                days=days,
                batch_size=cfg.batch_size,
                dry_run=dry_run,
            )

        for status, max_rows in cfg.max_rows_by_status.items():
            if status in cfg.protect_statuses:
                continue
            deleted += self._purge_items_over_status_cap(
                status=status,
                max_rows=max_rows,
                batch_size=cfg.batch_size,
                dry_run=dry_run,
            )

        return deleted

    def _purge_items_by_status_age(
        self,
        *,
        status: str,
        days: int,
        batch_size: int,
        dry_run: bool,
    ) -> int:
        age_clause, age_params = self._older_than_clause(
            "COALESCE(updated_at, finished_at, created_at)",
            days,
        )
        where_sql = f"status = ? AND {age_clause}"
        params: Tuple[Any, ...] = (status, *age_params)
        select_ids = f"""
            SELECT id FROM {self.items_table}
            WHERE {where_sql}
            ORDER BY COALESCE(updated_at, finished_at, created_at) ASC
        """
        return self._delete_in_batches(
            select_ids_query=select_ids,
            select_params=params,
            table_name=self.items_table,
            batch_size=batch_size,
            dry_run=dry_run,
        )

    def _purge_items_over_status_cap(
        self,
        *,
        status: str,
        max_rows: int,
        batch_size: int,
        dry_run: bool,
    ) -> int:
        total_rows = self._fetch_scalar(
            f"SELECT COUNT(*) FROM {self.items_table} WHERE status = ?",
            (status,),
        )
        overflow = total_rows - max_rows
        if overflow <= 0:
            return 0

        select_ids = f"""
            SELECT id FROM {self.items_table}
            WHERE status = ?
            ORDER BY COALESCE(updated_at, finished_at, created_at) ASC
        """
        if dry_run:
            count_query = f"""
                SELECT COUNT(*) FROM (
                    {select_ids}
                    LIMIT ?
                )
            """
            return self._fetch_scalar(count_query, (status, overflow))

        deleted = 0
        remaining = overflow
        while remaining > 0:
            batch = min(batch_size, remaining)
            cursor = self._adapter.execute_query(f"{select_ids} LIMIT ?", (status, batch))
            ids = [row[0] for row in cursor.fetchall()]
            if not ids:
                break
            placeholders = ", ".join("?" for _ in ids)
            delete_cursor = self._adapter.execute_query(
                f"DELETE FROM {self.items_table} WHERE id IN ({placeholders})",
                tuple(ids),
            )
            batch_deleted = self._adapter.rowcount(delete_cursor)
            deleted += batch_deleted
            remaining -= batch_deleted
            self._adapter.commit()
            if batch_deleted == 0:
                break
        return deleted

    def _apply_executions_retention(self, policy: RetentionPolicy, *, dry_run: bool) -> int:
        cfg = policy.executions
        deleted = 0

        for status, days in cfg.max_age_days_by_status.items():
            if status in cfg.protect_statuses:
                continue
            deleted += self._purge_executions_by_status_age(
                status=status,
                days=days,
                batch_size=cfg.batch_size,
                dry_run=dry_run,
            )

        return deleted

    def _purge_executions_by_status_age(
        self,
        *,
        status: str,
        days: int,
        batch_size: int,
        dry_run: bool,
    ) -> int:
        age_clause, age_params = self._older_than_clause(
            "COALESCE(finished_at, started_at)",
            days,
        )
        where_sql = f"status = ? AND {age_clause}"
        params: Tuple[Any, ...] = (status, *age_params)
        select_ids = f"""
            SELECT id FROM {self.executions_table}
            WHERE {where_sql}
            ORDER BY COALESCE(finished_at, started_at) ASC
        """
        return self._delete_in_batches(
            select_ids_query=select_ids,
            select_params=params,
            table_name=self.executions_table,
            batch_size=batch_size,
            dry_run=dry_run,
        )
