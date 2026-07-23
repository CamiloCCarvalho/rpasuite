# rpa_suite/core/database/mixins/reprocess.py
from __future__ import annotations

import json
from typing import Any

from ..constants import CONFIRMATION_CODES, TRANSIENT_ERROR_KEYWORDS, DatabaseType
from ..exceptions import DatabaseError
from ..helpers import extract_row_id, row_to_dict, rows_to_dicts
from ..item_dedup import (
    extract_item_unique_value,
    json_extract_sql,
    resolve_item_identifier_for_storage,
)
from ..validation import validate_days, validate_limit


class ReprocessMixin:
    """Domain operations — use via the Database class."""

    def is_reprocessable(
        self,
        item: dict[str, Any],
        allow_failed: bool = True,
        allow_interrupted: bool = True,
        allow_pending_queued: bool = True,
        transient_only_for_failed: bool = True,
    ) -> bool:
        """
        Decide whether an item is eligible for reprocessing.

        Regras:
        - Requires allow_reprocess = 1
        - Requires retry_count < max_retries when max_retries > 0
        - Interrupted items are reprocessable when enabled
        - Failed items are optionally reprocessable with transient-error filtering
        - Pending/queued/retrying items are reprocessable for resume in a new run
        """
        status = str(item.get("status", "")).lower()
        allow_reprocess = int(item.get("allow_reprocess", 1)) == 1
        retry_count = int(item.get("retry_count", 0) or 0)
        max_retries = int(item.get("max_retries", 0) or 0)
        error_message = str(item.get("error_message") or "").lower()

        if not allow_reprocess:
            return False

        # max_retries <= 0 significa "sem limite" para manter compatibilidade.
        if max_retries > 0 and retry_count >= max_retries:
            return False

        if status == "interrupted":
            return allow_interrupted

        if status == "failed":
            if not allow_failed:
                return False
            if not transient_only_for_failed:
                return True
            return any(keyword in error_message for keyword in TRANSIENT_ERROR_KEYWORDS)

        if status in ("pending", "queued", "retrying"):
            return allow_pending_queued

        return False

    def can_reprocess_execution(self, execution_id: int) -> bool:
        """
        Check whether an execution can be reprocessed.

        Parameters:
        -----------
        execution_id: int
            Execution id

        Returns:
        --------
        bool: True when reprocessing is allowed

        """
        try:
            exec_data = self.get_execution(execution_id)
            if not exec_data:
                return False

            return (
                exec_data.get("status") in ("interrupted", "failed")
                and exec_data.get("allow_reprocess", 1) == 1
                and self.allow_reprocess_executions
            )
        except Exception:
            return False

    def reprocess_interrupted_execution(
        self, execution_id: int, keep_items: bool = True, reset_items_status: bool = False
    ) -> int | None:
        """
        Create a new execution based on an interrupted/failed one.

        Parameters:
        -----------
        execution_id: int
            Execution id interrompida/falha

        keep_items: bool
            When True, copy items from the original execution
            Default: True

        reset_items_status: bool
            When True, reset copied item status to pending
            Default: False

        Returns:
        --------
        Optional[int]: New execution id or None when not allowed

        """
        try:
            if not self.can_reprocess_execution(execution_id):
                return None

            exec_data = self.get_execution(execution_id)
            if not exec_data:
                return None

            # Cria nova execução
            new_exec_id = self.start_execution(
                automation_name=exec_data["automation_name"],
                execution_id=None,  # Novo execution_id
                metadata=json.loads(exec_data["metadata"]) if exec_data.get("metadata") else None,
            )

            # Atualiza parent_execution_id e reprocess_count
            update_query = f"""
                UPDATE {self.executions_table}
                SET parent_execution_id = ?, reprocess_count = reprocess_count + 1
                WHERE id = ?
            """
            self._adapter.execute_query(update_query, (execution_id, new_exec_id))

            # Se manter itens, copia itens elegíveis para nova execução
            if keep_items:
                items = self.get_items(execution_id, status="all")
                for item in items:
                    should_copy = reset_items_status or self.is_reprocessable(
                        item, allow_failed=True, allow_interrupted=True, allow_pending_queued=True
                    )
                    if not should_copy:
                        continue

                    new_status = "pending"
                    item_id_query = f"""
                        INSERT INTO {self.items_table}
                        (execution_id, item_identifier, status, priority, queue_position,
                         processing_schema, item_data, allow_reprocess)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    self._adapter.execute_query(
                        item_id_query,
                        (
                            new_exec_id,
                            item.get("item_identifier"),
                            new_status,
                            item.get("priority", 0),
                            item.get("queue_position"),
                            item.get("processing_schema"),
                            item.get("item_data"),
                            item.get("allow_reprocess", 1),
                        ),
                    )

            self._adapter.commit()
            return new_exec_id

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to reprocess execution: {str(e)}.") from e

    def can_reprocess_item(self, item_id: int) -> bool:
        """
        Check whether an item can be reprocessed.

        Parameters:
        -----------
        item_id: int
            Item id

        Returns:
        --------
        bool: True when reprocessing is allowed

        """
        try:
            item_data = self.get_item(item_id)
            if not item_data:
                return False

            if not self.allow_reprocess_items:
                return False
            return self.is_reprocessable(item_data)
        except Exception:
            return False

    def reprocess_interrupted_item(self, item_id: int) -> bool:
        """
        Reprocess an eligible item (interrupted/failed/pending/queued).

        Parameters:
        -----------
        item_id: int
            Item id

        Returns:
        --------
        bool: True on success

        """
        try:
            if not self.can_reprocess_item(item_id):
                raise DatabaseError(f"Item {item_id} cannot be reprocessed")

            query = f"""
                UPDATE {self.items_table}
                SET status = 'pending',
                    started_at = NULL,
                    finished_at = NULL,
                    execution_time_seconds = NULL,
                    error_message = NULL,
                    last_checkpoint = NULL,
                    retry_count = retry_count + 1
                WHERE id = ?
            """

            self._adapter.execute_query(query, (item_id,))
            self._adapter.commit()
            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to reprocess item: {str(e)}.") from e

    def reprocess_items_from_execution(
        self,
        execution_id: int,
        statuses: list[str] | None = None,
        transient_only_for_failed: bool = True,
        limit: int | None = None,
    ) -> list[int]:
        """
        Batch reprocess eligible items from an execution.

        Parameters:
        -----------
        execution_id: int
            Execution id origem

        statuses: Optional[List[str]]
            Filter by desired statuses (e.g. ['failed', 'interrupted'])
            When None, use every status allowed by the reprocessing rules.

        transient_only_for_failed: bool
            When True, reprocess failed items only for transient errors.

        limit: Optional[int]
            Limit the number of reprocessed items.

        Returns:
        --------
        List[int]: Reprocessed item ids
        """
        try:
            if not self.allow_reprocess_items:
                return []

            items = self.get_items(execution_id, status="all")
            reprocessed_ids: list[int] = []
            allowed_statuses = {s.lower() for s in statuses} if statuses else None

            for item in items:
                status = str(item.get("status", "")).lower()
                if allowed_statuses is not None and status not in allowed_statuses:
                    continue

                if not self.is_reprocessable(
                    item,
                    allow_failed=True,
                    allow_interrupted=True,
                    allow_pending_queued=True,
                    transient_only_for_failed=transient_only_for_failed,
                ):
                    continue

                item_id = int(item["id"])
                self.reprocess_interrupted_item(item_id)
                reprocessed_ids.append(item_id)

                if limit and len(reprocessed_ids) >= limit:
                    break

            return reprocessed_ids

        except Exception as e:
            raise DatabaseError(f"Failed to batch reprocess items: {str(e)}.") from e
