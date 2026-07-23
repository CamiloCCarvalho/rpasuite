# rpa_suite/core/database/mixins/items.py
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from ..constants import ITEM_STATUS_FILTER_GROUPS, DatabaseType
from ..exceptions import DatabaseError
from ..helpers import (
    build_item_status_filter,
    extract_row_id,
    resolve_execution_id,
    row_to_dict,
    rows_to_dicts,
)
from ..item_dedup import (
    extract_item_unique_value,
    json_extract_comparable_sql,
    resolve_item_identifier_for_storage,
)


class ItemsMixin:
    """Domain operations — use via the Database class."""

    def _resolve_item_unique_value(
        self,
        item_identifier: str | None,
        item_data: dict[str, Any] | None,
    ) -> str | None:
        if not self.prevent_duplicate_items:
            return None
        return extract_item_unique_value(
            self.unique_item_field,
            item_identifier,
            item_data,
        )

    def _find_existing_item_by_unique_value(
        self,
        unique_value: str,
    ) -> dict[str, Any] | None:
        if self.unique_item_field == "item_identifier":
            query = f"SELECT * FROM {self.items_table} WHERE item_identifier = ? LIMIT 1"
            cursor = self._adapter.execute_query(query, (unique_value,))
        else:
            json_key = self.unique_item_field.split(".", 1)[1]
            expr = json_extract_comparable_sql(self.db_type.name, "item_data", json_key)
            query = f"SELECT * FROM {self.items_table} WHERE {expr} = ? LIMIT 1"
            cursor = self._adapter.execute_query(query, (unique_value,))

        row = cursor.fetchone()
        if not row:
            return None
        return row_to_dict(row, self.db_type)

    def get_item_by_unique_key(
        self,
        unique_value: str,
    ) -> dict[str, Any] | None:
        """
        Find an existing item by the configured global unique key.

        Uses ``unique_item_field`` from the Database constructor.
        """
        self._ensure_open()
        return self._find_existing_item_by_unique_value(str(unique_value).strip())

    def _handle_duplicate_item(
        self,
        unique_value: str,
        existing: dict[str, Any],
    ) -> int:
        if self.duplicate_item_behavior == "error":
            raise DatabaseError(
                f"Duplicate item detected for '{unique_value}'. "
                f"Record id={existing.get('id')} already exists "
                f"in execution {existing.get('execution_id')}."
            )
        return int(existing["id"])

    def add_item(
        self,
        execution_id: int | None = None,
        item_identifier: str | None = None,
        item_data: dict[str, Any] | None = None,
        processing_schema: dict[str, Any] | None = None,
        priority: int = 0,
        max_retries: int = 0,
    ) -> int:
        """
        Add an item to the processing queue.

        Parameters:
        -----------
        execution_id: Optional[int]
            Execution id. When omitted, uses the active execution from start_execution().

        item_identifier: Optional[str]
            Unique item identifier

        item_data: Optional[Dict[str, Any]]
            Item payload as JSON

        processing_schema: Optional[Dict[str, Any]]
            Processing schema/instructions as JSON

        priority: int
            Item priority (higher = more important)
            Default: 0

        max_retries: int
            Maximum number of reprocessing attempts.
            0 = unlimited
            Default: 0

        Returns:
        --------
        int: Created item id
        """
        try:
            self._ensure_open()
            resolved_execution_id = resolve_execution_id(
                execution_id,
                self._current_execution_id,
                operation="add item",
            )

            item_identifier = resolve_item_identifier_for_storage(
                self.unique_item_field,
                item_identifier,
                item_data,
            )

            unique_value = self._resolve_item_unique_value(item_identifier, item_data)
            if unique_value is not None:
                existing = self._find_existing_item_by_unique_value(unique_value)
                if existing:
                    return self._handle_duplicate_item(unique_value, existing)

            # Calcula próxima posição na fila
            queue_query = f"""
                SELECT COALESCE(MAX(queue_position), 0) + 1 as next_pos
                FROM {self.items_table}
                WHERE execution_id = ?
            """
            queue_cursor = self._adapter.execute_query(queue_query, (resolved_execution_id,))
            queue_result = queue_cursor.fetchone()
            queue_position = queue_result[0] if queue_result else 1

            item_data_str = json.dumps(item_data) if item_data else None
            schema_str = json.dumps(processing_schema) if processing_schema else None

            query = f"""
                INSERT INTO {self.items_table}
                (execution_id, item_identifier, status, priority, queue_position, 
                 processing_schema, item_data, max_retries)
                VALUES (?, ?, 'pending', ?, ?, ?, ?, ?)
            """

            cursor = self._adapter.execute_query(
                query,
                (
                    resolved_execution_id,
                    item_identifier,
                    priority,
                    queue_position,
                    schema_str,
                    item_data_str,
                    max_retries,
                ),
            )

            item_id = self._adapter.get_last_insert_id(cursor, self.items_table)

            # Atualiza contador total de itens na execução
            update_query = f"""
                UPDATE {self.executions_table}
                SET total_items = total_items + 1
                WHERE id = ?
            """
            self._adapter.execute_query(update_query, (resolved_execution_id,))

            self._adapter.commit()
            return item_id

        except DatabaseError:
            raise
        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to add item: {str(e)}.") from e

    def add_items(
        self,
        items: list[dict[str, Any]],
        execution_id: int | None = None,
        default_priority: int = 0,
        default_max_retries: int = 0,
    ) -> list[int]:
        """
        Add multiple items to the processing queue in batch (more efficient).

        Parameters:
        -----------
        execution_id: Optional[int]
            Execution id. When omitted, uses the active execution from start_execution().

        items: List[Dict[str, Any]]
            List of item dicts. Each dict may contain:
            - item_identifier (Optional[str]): Unique item identifier
            - item_data (Optional[Dict[str, Any]]): Item payload as JSON
            - processing_schema (Optional[Dict[str, Any]]): Schema/instruções de processamento
            - priority (Optional[int]): Item priority (uses default_priority when omitted)
            - max_retries (Optional[int]): Max retries (uses default_max_retries when omitted)

        default_priority: int
            Default priority for items without an explicit priority
            Default: 0

        default_max_retries: int
            Default max retries for items without an explicit value
            0 = unlimited
            Default: 0

        Returns:
        --------
        List[int]: List of created item ids in the same order as the input

        Example:
        --------
        >>> items = [
        ...     {
        ...         "item_identifier": "001",
        ...         "item_data": {"name": "Item 1"},
        ...         "priority": 1
        ...     },
        ...     {
        ...         "item_identifier": "002",
        ...         "item_data": {"name": "Item 2"}
        ...     }
        ... ]
        >>> item_ids = register.add_items(execution_id=exec_id, items=items)

        """
        try:
            self._ensure_open()
            if not items or len(items) == 0:
                return []

            resolved_execution_id = resolve_execution_id(
                execution_id,
                self._current_execution_id,
                operation="add items",
            )

            if self.prevent_duplicate_items:
                item_ids: list[int] = []
                for item in items:
                    item_ids.append(
                        self.add_item(
                            execution_id=resolved_execution_id,
                            item_identifier=item.get("item_identifier"),
                            item_data=item.get("item_data"),
                            processing_schema=item.get("processing_schema"),
                            priority=item.get("priority", default_priority),
                            max_retries=item.get("max_retries", default_max_retries),
                        )
                    )
                return item_ids

            # Calcula posição inicial na fila
            queue_query = f"""
                SELECT COALESCE(MAX(queue_position), 0) as max_pos
                FROM {self.items_table}
                WHERE execution_id = ?
            """
            queue_cursor = self._adapter.execute_query(queue_query, (resolved_execution_id,))
            queue_result = queue_cursor.fetchone()
            start_position = (queue_result[0] if queue_result else 0) + 1

            # Prepara dados para batch insert
            params_list = []
            for idx, item in enumerate(items):
                item_identifier = item.get("item_identifier")
                item_data = item.get("item_data")
                processing_schema = item.get("processing_schema")
                priority = item.get("priority", default_priority)
                max_retries = item.get("max_retries", default_max_retries)
                queue_position = start_position + idx

                item_data_str = json.dumps(item_data) if item_data else None
                schema_str = json.dumps(processing_schema) if processing_schema else None

                params_list.append(
                    (
                        resolved_execution_id,
                        item_identifier,
                        priority,
                        queue_position,
                        schema_str,
                        item_data_str,
                        max_retries,
                    )
                )

            # Insere todos os itens em batch
            query = f"""
                INSERT INTO {self.items_table}
                (execution_id, item_identifier, status, priority, queue_position, 
                 processing_schema, item_data, max_retries)
                VALUES (?, ?, 'pending', ?, ?, ?, ?, ?)
            """

            self._adapter.execute_many(query, params_list)

            # Busca os IDs dos itens recém-inseridos usando queue_position
            # Busca todos os itens inseridos nesta execução com queue_position >= start_position
            id_query = f"""
                SELECT id FROM {self.items_table}
                WHERE execution_id = ? AND queue_position >= ?
                ORDER BY queue_position ASC
                LIMIT ?
            """
            id_cursor = self._adapter.execute_query(id_query, (resolved_execution_id, start_position, len(items)))
            id_results = id_cursor.fetchall()

            # Extrai IDs dos resultados
            if self.db_type == DatabaseType.SQLITE:
                item_ids = [row["id"] for row in id_results]
            else:
                item_ids = [(row[0] if isinstance(row, tuple) else row["id"]) for row in id_results]

            # Atualiza contador total de itens na execução (uma única vez)
            update_query = f"""
                UPDATE {self.executions_table}
                SET total_items = total_items + ?
                WHERE id = ?
            """
            self._adapter.execute_query(update_query, (len(items), resolved_execution_id))

            self._adapter.commit()
            return item_ids

        except DatabaseError:
            raise
        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to add items in batch: {str(e)}.") from e

    def get_next_item_from_queue(
        self, execution_id: int, include_interrupted: bool | None = None
    ) -> dict[str, Any] | None:
        """
        Return the next queue item ordered by priority and queue_position.

        Parameters:
        -----------
        execution_id: int
            Execution id

        include_interrupted: Optional[bool]
            When None, uses the class setting (allow_reprocess_items)
            When True, include interrupted items
            When False, exclude interrupted items

        Returns:
        --------
        Optional[Dict[str, Any]]: Next item or None

        """
        try:
            if include_interrupted is None:
                include_interrupted = self.allow_reprocess_items

            status_filter = "('pending', 'queued')"
            if include_interrupted:
                status_filter = "('pending', 'queued', 'interrupted')"

            query = f"""
                SELECT * FROM {self.items_table}
                WHERE execution_id = ? AND status IN {status_filter}
                ORDER BY priority DESC, queue_position ASC
                LIMIT 1
            """

            cursor = self._adapter.execute_query(query, (execution_id,))
            row = cursor.fetchone()

            if row:
                if self.db_type == DatabaseType.SQLITE:
                    return dict(row)
                else:
                    return dict(row) if hasattr(row, "keys") else row
            return None

        except Exception as e:
            raise DatabaseError(f"Failed to fetch next queue item: {str(e)}.") from e

    def start_processing_item(self, item_id: int) -> bool:
        """
        Mark an item as processing and set started_at.

        Parameters:
        -----------
        item_id: int
            Item id

        Returns:
        --------
        bool: True on success

        """
        try:
            query = f"""
                UPDATE {self.items_table}
                SET status = 'processing', started_at = ?
                WHERE id = ? AND status IN ('pending', 'queued', 'interrupted')
            """

            cursor = self._adapter.execute_query(query, (datetime.now(), item_id))
            updated = self._adapter.rowcount(cursor) > 0
            self._adapter.commit()
            return updated

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to start item processing: {str(e)}.") from e

    def claim_next_item_from_queue(
        self,
        execution_id: int,
        include_interrupted: bool | None = None,
    ) -> dict[str, Any] | None:
        """
        Atomically claim the next queue item (SELECT + UPDATE in one transaction).

        Prefer this over get_next_item_from_queue() + start_processing_item().
        """
        self._ensure_open()
        if include_interrupted is None:
            include_interrupted = self.allow_reprocess_items

        status_filter = "('pending', 'queued', 'interrupted')" if include_interrupted else "('pending', 'queued')"

        try:
            update_query = f"""
                UPDATE {self.items_table}
                SET status = 'processing', started_at = ?
                WHERE id = (
                    SELECT id FROM {self.items_table}
                    WHERE execution_id = ? AND status IN {status_filter}
                    ORDER BY priority DESC, queue_position ASC
                    LIMIT 1
                ) AND status IN {status_filter}
                RETURNING *
            """
            with self._adapter._lock:
                cursor = self._adapter._execute_query_impl(
                    self._adapter._prepare_query(update_query),
                    (datetime.now(), execution_id),
                )
                row = cursor.fetchone()
                if not row:
                    self._adapter._rollback_impl()
                    return None
                self._adapter._commit_impl()
                return row_to_dict(row, self.db_type)

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to claim next queue item: {str(e)}.") from e

    def update_checkpoint(self, item_id: int, checkpoint: str) -> bool:
        """
        Update the item last_checkpoint.

        Parameters:
        -----------
        item_id: int
            Item id

        checkpoint: str
            Current checkpoint description

        Returns:
        --------
        bool: True on success

        """
        try:
            query = f"""
                UPDATE {self.items_table}
                SET last_checkpoint = ?
                WHERE id = ?
            """

            self._adapter.execute_query(query, (checkpoint, item_id))
            self._adapter.commit()
            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to update checkpoint: {str(e)}.") from e

    def finish_item(
        self, item_id: int, status: str = "success", error_message: str | None = None, notes: str | None = None
    ) -> bool:
        """
        Finish processing an item.

        Parameters:
        -----------
        item_id: int
            Item id

        status: str
            Status final: 'success', 'failed', 'skipped'
            Default: 'success'

        error_message: Optional[str]
            Error message when applicable

        notes: Optional[str]
            Additional notes

        Returns:
        --------
        bool: True on success

        """
        try:
            if status not in ["success", "failed", "skipped"]:
                raise DatabaseError(f"Invalid status: {status}")

            # Busca dados do item
            item_data = self.get_item(item_id)
            if not item_data:
                raise DatabaseError(f"Item {item_id} not found")

            started_at = None
            if item_data.get("started_at"):
                started_at = (
                    datetime.fromisoformat(item_data["started_at"])
                    if isinstance(item_data["started_at"], str)
                    else item_data["started_at"]
                )

            finished_at = datetime.now()
            execution_time = None
            if started_at:
                execution_time = (finished_at - started_at).total_seconds()

            query = f"""
                UPDATE {self.items_table}
                SET status = ?,
                    finished_at = ?,
                    execution_time_seconds = ?,
                    error_message = ?,
                    notes = ?
                WHERE id = ?
            """

            self._adapter.execute_query(query, (status, finished_at, execution_time, error_message, notes, item_id))

            # Atualiza contadores na execução
            count_query = f"""
                UPDATE {self.executions_table}
                SET successful_items = (
                    SELECT COUNT(*) FROM {self.items_table}
                    WHERE execution_id = {self.items_table}.execution_id AND status = 'success'
                ),
                failed_items = (
                    SELECT COUNT(*) FROM {self.items_table}
                    WHERE execution_id = {self.items_table}.execution_id AND status = 'failed'
                )
                WHERE id = (SELECT execution_id FROM {self.items_table} WHERE id = ?)
            """
            self._adapter.execute_query(count_query, (item_id,))

            self._adapter.commit()
            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to finish item: {str(e)}.") from e

    def get_item(self, item_id: int) -> dict[str, Any] | None:
        """
        Fetch an item by id.

        Parameters:
        -----------
        item_id: int
            Item id

        Returns:
        --------
        Optional[Dict[str, Any]]: Item data or None

        """
        try:
            query = f"SELECT * FROM {self.items_table} WHERE id = ?"
            cursor = self._adapter.execute_query(query, (item_id,))
            row = cursor.fetchone()

            if row:
                if self.db_type == DatabaseType.SQLITE:
                    return dict(row)
                else:
                    return dict(row) if hasattr(row, "keys") else row
            return None

        except Exception as e:
            raise DatabaseError(f"Failed to fetch item: {str(e)}.") from e

    def get_items(
        self,
        execution_id: int | None = None,
        status: str | None = None,
        scope: str = "current",
    ) -> list[dict[str, Any]]:
        """
        List items with flexible execution and status filters.

        Parameters:
        -----------
        execution_id: Optional[int]
            Execution id. When provided, takes precedence over ``scope``.

        status: Optional[str]
            Status filter. Default: ``pending`` (queued/pending items).

            Groups:
            - ``pending``: pending + queued
            - ``executed``: success + failed + skipped
            - ``interrupted``: interrupted
            - ``backlog``: unfinished work (pending, queued, interrupted, retrying, failed, processing)
            - ``reprocessavel``: alias of ``backlog``
            - ``all``: every status

            Also accepts exact database statuses (e.g. ``failed``, ``processing``).

        scope: str
            ``current`` (default): scope to the active execution (``start_execution``).
            ``all``: search across **all executions** in the persistent database.

            Values such as ``backlog`` or ``pending`` belong to the
            ``status`` parameter, not ``scope``.

        Returns:
        --------
        List[Dict[str, Any]]: List of items ordered by queue position

        """
        try:
            self._ensure_open()

            normalized_scope = scope.lower().strip()
            if normalized_scope not in ("current", "all"):
                if normalized_scope in ITEM_STATUS_FILTER_GROUPS:
                    raise DatabaseError(
                        f"'{scope}' is a status filter, not a scope. "
                        f"Use get_items(scope='all', status='{scope}') to search "
                        "across all executions, or get_items(status='{}') "
                        "for the current execution only.".format(scope)
                    )
                raise DatabaseError("Invalid scope. Use 'current' (default) or 'all'.")
            scope = normalized_scope

            where_parts: list[str] = []
            params: list[Any] = []

            if execution_id is not None:
                where_parts.append("execution_id = ?")
                params.append(execution_id)
            elif scope == "all":
                pass
            else:
                where_parts.append("execution_id = ?")
                params.append(
                    resolve_execution_id(
                        execution_id,
                        self._current_execution_id,
                        operation="list items",
                    )
                )

            status_clause, status_params = build_item_status_filter(status)
            where_sql = " AND ".join(where_parts) if where_parts else "1=1"
            query = f"SELECT * FROM {self.items_table} WHERE {where_sql}{status_clause}"
            params.extend(status_params)

            if scope == "all" and execution_id is None:
                query += " ORDER BY execution_id ASC, queue_position ASC, created_at ASC"
            else:
                query += " ORDER BY queue_position ASC"

            cursor = self._adapter.execute_query(query, tuple(params))
            rows = cursor.fetchall()
            return rows_to_dicts(rows, self.db_type)

        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to list items: {str(e)}.") from e

    def detect_and_mark_interrupted_items(
        self,
        execution_id: int | None = None,
        scope: str = "current",
    ) -> list[int]:
        """
        Detect and mark items that were not finished properly.

        Parameters:
        -----------
        execution_id: Optional[int]
            Execution id. Se informado, tem prioridade sobre scope.
        scope: str
            'current' (default) scopes to the active execution;
            'all' marks every processing item (explicit opt-in).
        """
        try:
            self._ensure_open()
            target_id = execution_id or (self._current_execution_id if scope == "current" else None)
            if target_id is None and scope == "current":
                return []

            if target_id is not None:
                query = f"""
                    UPDATE {self.items_table}
                    SET status = 'interrupted'
                    WHERE execution_id = ? AND status = 'processing'
                """
                self._adapter.execute_query(query, (target_id,))
                query_ids = f"""
                    SELECT id FROM {self.items_table}
                    WHERE execution_id = ? AND status = 'interrupted'
                """
                cursor = self._adapter.execute_query(query_ids, (target_id,))
            else:
                query = f"""
                    UPDATE {self.items_table}
                    SET status = 'interrupted'
                    WHERE status = 'processing'
                """
                self._adapter.execute_query(query)
                query_ids = f"SELECT id FROM {self.items_table} WHERE status = 'interrupted'"
                cursor = self._adapter.execute_query(query_ids)

            rows = cursor.fetchall()
            interrupted_ids = [extract_row_id(row) for row in rows]
            self._adapter.commit()
            return interrupted_ids

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to detect interrupted items: {str(e)}.") from e
