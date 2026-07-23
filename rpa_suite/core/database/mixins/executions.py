# rpa_suite/core/database/mixins/executions.py
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from ..constants import DatabaseType
from ..exceptions import DatabaseError
from ..helpers import extract_row_id
from ..validation import validate_limit


class ExecutionsMixin:
    """Domain operations — use via the Database class."""

    def _on_interrupt_signal(self) -> None:
        """Flag the current execution as interrupted (thread-safe, no I/O in signal handler)."""
        if self._current_execution_id:
            self._interrupted_flag = True

    def _mark_execution_interrupted(self, execution_id: int) -> None:
        """Mark an execution as interrupted."""
        try:
            query = f"""
                UPDATE {self.executions_table}
                SET status = 'interrupted', finished_properly = 0
                WHERE id = ? AND status = 'running'
            """
            self._adapter.execute_query(query, (execution_id,))
            self._adapter.commit()
        except Exception:  # nosec B110
            pass

    def check_interrupted(self) -> bool:
        """
        Check whether an interruption was signaled and persist it in the database.

        Call this periodically in the main application loop to process
        interruptions signaled by the registered handlers.

        Returns:
        --------
        bool: True if an interruption was processed, False otherwise
        """
        if self._interrupted_flag and self._current_execution_id:
            try:
                self._mark_execution_interrupted(self._current_execution_id)
                return True
            except Exception:  # nosec B110
                pass
        return False

    def start_execution(
        self, automation_name: str, execution_id: str | None = None, metadata: dict[str, Any] | None = None
    ) -> int:
        """
        Start a new execution.

        Parameters:
        -----------
        automation_name: str
            Automation/bot name

        execution_id: Optional[str]
            Optional external execution identifier

        metadata: Optional[Dict[str, Any]]
            Additional metadata as JSON

        Returns:
        --------
        int: Created execution id

        """
        try:
            metadata_str = json.dumps(metadata) if metadata else None
            now = datetime.now()

            external_execution_id = execution_id
            if external_execution_id is None and self.auto_generate_execution_id:
                external_execution_id = str(uuid.uuid4())

            query = f"""
                INSERT INTO {self.executions_table}
                (execution_id, automation_name, status, started_at, metadata)
                VALUES (?, ?, 'running', ?, ?)
            """

            cursor = self._adapter.execute_query(
                query,
                (external_execution_id, automation_name, now, metadata_str),
            )

            exec_id = self._adapter.get_last_insert_id(cursor, self.executions_table)

            if external_execution_id is None:
                fallback_external_id = f"exec-{exec_id}"
                self._adapter.execute_query(
                    f"UPDATE {self.executions_table} SET execution_id = ? WHERE id = ?",
                    (fallback_external_id, exec_id),
                )

            self._adapter.commit()

            self._current_execution_id = exec_id  # type: ignore
            return exec_id

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to start execution: {str(e)}.") from e

    def finish_execution(self, execution_id: int, status: str = "completed", error_message: str | None = None) -> bool:
        """
        Finish an execution.

        Parameters:
        -----------
        execution_id: int
            Execution id

        status: str
            Final status: 'completed', 'failed', 'cancelled'
            Default: 'completed'

        error_message: Optional[str]
            Error message when applicable

        Returns:
        --------
        bool: True on success

        """
        try:
            if status not in ["completed", "failed", "cancelled"]:
                raise DatabaseError(f"Invalid status: {status}")

            exec_data = self.get_execution(execution_id)
            if not exec_data:
                raise DatabaseError(f"Execution {execution_id} not found")

            started_at = (
                datetime.fromisoformat(exec_data["started_at"])
                if isinstance(exec_data["started_at"], str)
                else exec_data["started_at"]
            )
            finished_at = datetime.now()
            execution_time = (finished_at - started_at).total_seconds()

            items_query = f"""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    SUM(CASE WHEN status = 'interrupted' THEN 1 ELSE 0 END) as interrupted
                FROM {self.items_table}
                WHERE execution_id = ?
            """
            items_cursor = self._adapter.execute_query(items_query, (execution_id,))
            items_result = items_cursor.fetchone()

            total_items = items_result[0] if items_result else 0
            successful_items = items_result[1] if items_result else 0
            failed_items = items_result[2] if items_result else 0
            interrupted_items = items_result[3] if items_result else 0

            query = f"""
                UPDATE {self.executions_table}
                SET status = ?,
                    finished_properly = 1,
                    finished_at = ?,
                    execution_time_seconds = ?,
                    total_items = ?,
                    successful_items = ?,
                    failed_items = ?,
                    interrupted_items = ?,
                    error_message = ?
                WHERE id = ?
            """

            self._adapter.execute_query(
                query,
                (
                    status,
                    finished_at,
                    execution_time,
                    total_items,
                    successful_items,
                    failed_items,
                    interrupted_items,
                    error_message,
                    execution_id,
                ),
            )

            self._adapter.commit()

            if self._current_execution_id == execution_id:
                self._current_execution_id = None

            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to finish execution: {str(e)}.") from e

    def get_execution(self, execution_id: int) -> dict[str, Any] | None:
        """
        Fetch an execution by id.

        Parameters:
        -----------
        execution_id: int
            Execution id

        Returns:
        --------
        Optional[Dict[str, Any]]: Execution data or None

        """
        try:
            query = f"SELECT * FROM {self.executions_table} WHERE id = ?"
            cursor = self._adapter.execute_query(query, (execution_id,))
            row = cursor.fetchone()

            if row:
                if self.db_type == DatabaseType.SQLITE:
                    return dict(row)
                else:
                    return dict(row) if hasattr(row, "keys") else row
            return None

        except Exception as e:
            raise DatabaseError(f"Failed to fetch execution: {str(e)}.") from e

    def get_executions(
        self, status: str | None = None, automation_name: str | None = None, limit: int | None = None
    ) -> list[dict[str, Any]]:
        """
        List executions with optional filters.

        Parameters:
        -----------
        status: Optional[str]
            Filter by status

        automation_name: Optional[str]
            Filter by automation name

        limit: Optional[int]
            Limit number of results

        Returns:
        --------
        List[Dict[str, Any]]: List of executions

        """
        try:
            query = f"SELECT * FROM {self.executions_table} WHERE 1=1"
            params = []

            if status:
                query += " AND status = ?"
                params.append(status)

            if automation_name:
                query += " AND automation_name = ?"
                params.append(automation_name)

            query += " ORDER BY started_at DESC"

            safe_limit = validate_limit(limit)
            if safe_limit is not None:
                query += f" LIMIT {safe_limit}"

            cursor = self._adapter.execute_query(query, tuple(params) if params else None)
            rows = cursor.fetchall()

            if self.db_type == DatabaseType.SQLITE:
                return [dict(row) for row in rows]
            else:
                return [dict(row) if hasattr(row, "keys") else row for row in rows]

        except Exception as e:
            raise DatabaseError(f"Failed to list executions: {str(e)}.") from e

    def detect_and_mark_interrupted_executions(
        self,
        execution_id: int | None = None,
        scope: str = "current",
    ) -> list[int]:
        """
        Detect and mark executions that were not finished properly.

        Parameters:
        -----------
        execution_id: Optional[int]
            Specific id. When provided, takes precedence over scope.
        scope: str
            'current' (default) scopes to the active execution;
            'all' marks every running execution (explicit opt-in).
        """
        try:
            self._ensure_open()
            target_id = execution_id or (self._current_execution_id if scope == "current" else None)
            if target_id is None and scope == "current":
                return []

            if target_id is not None:
                query = f"""
                    UPDATE {self.executions_table}
                    SET status = 'interrupted', finished_properly = 0
                    WHERE id = ? AND status = 'running' AND finished_properly = 0
                """
                self._adapter.execute_query(query, (target_id,))
                query_ids = f"""
                    SELECT id FROM {self.executions_table}
                    WHERE id = ? AND status = 'interrupted'
                """
                cursor = self._adapter.execute_query(query_ids, (target_id,))
            else:
                query = f"""
                    UPDATE {self.executions_table}
                    SET status = 'interrupted', finished_properly = 0
                    WHERE status = 'running' AND finished_properly = 0
                """
                self._adapter.execute_query(query)
                query_ids = f"""
                    SELECT id FROM {self.executions_table}
                    WHERE status = 'interrupted' AND finished_properly = 0
                """
                cursor = self._adapter.execute_query(query_ids)

            rows = cursor.fetchall()
            interrupted_ids = [extract_row_id(row) for row in rows]
            self._adapter.commit()
            return interrupted_ids

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to detect interruptions: {str(e)}.") from e
