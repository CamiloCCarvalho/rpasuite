# rpa_suite/core/database/mixins/logs.py
from __future__ import annotations

import inspect
import os
from datetime import datetime
from typing import Any

from ..constants import (
    CONFIRMATION_CODES,
    LOG_LEVEL_CRITICAL,
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_INFO,
    LOG_LEVEL_SUCCESS,
    LOG_LEVEL_WARNING,
    TRANSIENT_ERROR_KEYWORDS,
    DatabaseType,
)
from ..exceptions import DatabaseError
from ..helpers import extract_row_id, row_to_dict, rows_to_dicts
from ..item_dedup import (
    extract_item_unique_value,
    json_extract_sql,
    resolve_item_identifier_for_storage,
)
from ..validation import validate_days, validate_limit


class LogsMixin:
    """Domain operations — use via the Database class."""

    def add_log(
        self,
        message: str,
        execution_id: int | None = None,
        log_level: str = LOG_LEVEL_INFO,
        step_name: str | None = None,
    ) -> int:
        """
        Add a log entry to an execution.

        Parameters:
        -----------
        message: str
            Log message (may be long text)

        execution_id: Optional[int]
            Execution id. When omitted, uses the active execution from start_execution().

        log_level: str
            Log level (use the class LOG_LEVEL_* constants).
            Default: LOG_LEVEL_INFO

        step_name: Optional[str]
            Step name (e.g. "Step 1", "Phase 2", "Validation")

        Returns:
        --------
        int: Created log id

        """
        try:
            if log_level not in self.VALID_LOG_LEVELS:
                raise DatabaseError(f"Invalid log level: {log_level}")

            resolved_execution_id = execution_id or self._current_execution_id
            if not resolved_execution_id:
                raise DatabaseError(
                    "execution_id was not provided and no active execution was found. "
                    "Call start_execution() before adding logs or pass execution_id."
                )

            now = datetime.now()

            query = f"""
                INSERT INTO {self.logs_table}
                (execution_id, log_level, step_name, message, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """

            cursor = self._adapter.execute_query(query, (resolved_execution_id, log_level, step_name, message, now))

            log_id = self._adapter.get_last_insert_id(cursor, self.logs_table)
            self._adapter.commit()

            # Se log_instance foi fornecido, dispara também no objeto Log
            if self.log_instance is not None:
                try:
                    # Formata mensagem incluindo step_name se fornecido
                    formatted_message = message
                    if step_name:
                        formatted_message = f"[{step_name}] {message}"

                    # Captura o frame do arquivo que chamou add_log() (não do database.py)
                    caller_frame = None
                    current_file = os.path.normpath(__file__)

                    # Percorre a pilha de chamadas para encontrar o primeiro frame que não é do database.py
                    # Começa do frame atual (add_log) e vai para trás
                    frame = inspect.currentframe()
                    # Pula o frame atual (add_log) e vai para quem chamou
                    while frame:
                        frame = frame.f_back
                        if frame:
                            frame_file = os.path.normpath(frame.f_code.co_filename)
                            # Se encontrou um frame que não é do database.py, usa ele
                            if frame_file != current_file:
                                caller_frame = frame
                                break

                    # Se encontrou o caller, extrai filename e lineno
                    if caller_frame:
                        full_path_filename = caller_frame.f_code.co_filename
                        full_path_filename = os.path.normpath(full_path_filename)
                        parent_folder = os.path.basename(os.path.dirname(full_path_filename))
                        file_name = os.path.basename(full_path_filename)
                        display_filename = f"{parent_folder}/{file_name}"
                        caller_lineno = caller_frame.f_lineno

                        # Mapeia níveis do Database para níveis do Log
                        log_level_mapping = {
                            self.LOG_LEVEL_DEBUG: "DEBUG",
                            self.LOG_LEVEL_INFO: "INFO",
                            self.LOG_LEVEL_WARNING: "WARNING",
                            self.LOG_LEVEL_ERROR: "ERROR",
                            self.LOG_LEVEL_CRITICAL: "CRITICAL",
                            self.LOG_LEVEL_SUCCESS: "INFO",  # success usa INFO no Log
                        }

                        # Usa _log_with_context para passar o contexto correto
                        log_level = log_level_mapping.get(log_level, "INFO")
                        self.log_instance.log_with_context(
                            level=log_level, msg=formatted_message, filename=display_filename, lineno=caller_lineno
                        )
                    else:
                        # Fallback: se não encontrou o caller, usa os métodos normais
                        log_level_mapping = {
                            self.LOG_LEVEL_DEBUG: self.log_instance.log_debug,  # type: ignore
                            self.LOG_LEVEL_INFO: self.log_instance.log_info,  # type: ignore
                            self.LOG_LEVEL_WARNING: self.log_instance.log_warning,  # type: ignore
                            self.LOG_LEVEL_ERROR: self.log_instance.log_error,  # type: ignore
                            self.LOG_LEVEL_CRITICAL: self.log_instance.log_critical,  # type: ignore
                            self.LOG_LEVEL_SUCCESS: self.log_instance.log_info,  # type: ignore # success usa info no Log
                        }

                        # Chama o método correspondente do Log
                        log_method = log_level_mapping.get(log_level, self.log_instance.log_info)
                        log_method(formatted_message)  # type: ignore

                except Exception as log_error:
                    # Não falha se o log externo falhar, apenas registra silenciosamente
                    # Isso evita que problemas no Log externo quebrem o fluxo principal
                    pass

            return log_id

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to add log: {str(e)}.") from e

    def add_log_debug(self, message: str, execution_id: int | None = None, step_name: str | None = None) -> int:
        """Add a log entry with DEBUG level."""
        return self.add_log(
            message=message, execution_id=execution_id, log_level=self.LOG_LEVEL_DEBUG, step_name=step_name
        )

    def add_log_info(self, message: str, execution_id: int | None = None, step_name: str | None = None) -> int:
        """Add a log entry with INFO level."""
        return self.add_log(
            message=message, execution_id=execution_id, log_level=self.LOG_LEVEL_INFO, step_name=step_name
        )

    def add_log_warn(self, message: str, execution_id: int | None = None, step_name: str | None = None) -> int:
        """Add a log entry with WARNING level."""
        return self.add_log(
            message=message, execution_id=execution_id, log_level=self.LOG_LEVEL_WARNING, step_name=step_name
        )

    def add_log_warning(self, message: str, execution_id: int | None = None, step_name: str | None = None) -> int:
        """Alias for add_log_warn at WARNING level."""
        return self.add_log_warn(message=message, execution_id=execution_id, step_name=step_name)

    def add_log_error(self, message: str, execution_id: int | None = None, step_name: str | None = None) -> int:
        """Add a log entry with ERROR level."""
        return self.add_log(
            message=message, execution_id=execution_id, log_level=self.LOG_LEVEL_ERROR, step_name=step_name
        )

    def add_log_critical(self, message: str, execution_id: int | None = None, step_name: str | None = None) -> int:
        """Add a log entry with CRITICAL level."""
        return self.add_log(
            message=message, execution_id=execution_id, log_level=self.LOG_LEVEL_CRITICAL, step_name=step_name
        )

    def add_log_success(self, message: str, execution_id: int | None = None, step_name: str | None = None) -> int:
        """Add a log entry with SUCCESS level."""
        return self.add_log(
            message=message, execution_id=execution_id, log_level=self.LOG_LEVEL_SUCCESS, step_name=step_name
        )

    def get_logs(
        self,
        execution_id: int | None = None,
        log_level: str | None = None,
        step_name: str | None = None,
        limit: int | None = None,
        order_desc: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Fetch logs for an execution.

        Parameters:
        -----------
        execution_id: Optional[int]
            Execution id. When omitted, uses the active execution from start_execution().

        log_level: Optional[str]
            Filter by log level

        step_name: Optional[str]
            Filter by step name

        limit: Optional[int]
            Limit number of results

        order_desc: bool
            Se True, ordena por timestamp DESC (mais recentes primeiro)
            Se False, ordena por timestamp ASC (mais antigos primeiro)
            Default: True

        Returns:
        --------
        List[Dict[str, Any]]: List of logs

        """
        try:
            resolved_execution_id = execution_id or self._current_execution_id
            if not resolved_execution_id:
                raise DatabaseError(
                    "execution_id was not provided and no active execution was found. "
                    "Call start_execution() before fetching logs or pass execution_id."
                )

            query = f"SELECT * FROM {self.logs_table} WHERE execution_id = ?"
            params = [resolved_execution_id]

            if log_level:
                query += " AND log_level = ?"
                params.append(log_level)  # type: ignore

            if step_name:
                query += " AND step_name = ?"
                params.append(step_name)  # type: ignore

            query += f" ORDER BY timestamp {'DESC' if order_desc else 'ASC'}"

            safe_limit = validate_limit(limit)
            if safe_limit is not None:
                if self.db_type == DatabaseType.SQLSERVER:
                    query = query.replace("SELECT ", f"SELECT TOP ({safe_limit}) ", 1)
                else:
                    query += f" LIMIT {safe_limit}"

            cursor = self._adapter.execute_query(query, tuple(params))
            rows = cursor.fetchall()

            if self.db_type == DatabaseType.SQLITE:
                return [dict(row) for row in rows]
            else:
                return [dict(row) if hasattr(row, "keys") else row for row in rows]

        except Exception as e:
            raise DatabaseError(f"Failed to fetch logs: {str(e)}.") from e

    def clear_logs(
        self,
        execution_id: int | None = None,
        log_level: str | None = None,
        older_than_days: int | None = None,
        confirm: bool = False,
    ) -> int:
        """
        Delete logs.

        Parameters:
        -----------
        execution_id: Optional[int]
            Execution id. When None, delete across all executions.

        log_level: Optional[str]
            Filter by log level

        older_than_days: Optional[int]
            Delete only logs older than X days

        confirm: bool
            Deve ser True para executar (proteção contra limpeza acidental)

        Returns:
        --------
        int: Number of deleted logs

        """
        if not confirm:
            raise DatabaseError("This operation permanently deletes logs. " "Pass confirm=True to proceed.")

        try:
            query = f"DELETE FROM {self.logs_table} WHERE 1=1"
            params = []
            resolved_execution_id = execution_id or self._current_execution_id

            if resolved_execution_id:
                query += " AND execution_id = ?"
                params.append(resolved_execution_id)

            if log_level:
                query += " AND log_level = ?"
                params.append(log_level)  # type: ignore

            if older_than_days:
                safe_days = validate_days(older_than_days)
                if self.db_type == DatabaseType.SQLITE:
                    query += " AND timestamp < datetime('now', '-' || ? || ' days')"
                    params.append(safe_days)
                elif self.db_type == DatabaseType.POSTGRESQL:
                    query += f" AND timestamp < NOW() - INTERVAL '{safe_days} days'"
                elif self.db_type == DatabaseType.MYSQL:
                    query += f" AND timestamp < DATE_SUB(NOW(), INTERVAL {safe_days} DAY)"
                elif self.db_type == DatabaseType.SQLSERVER:
                    query += " AND timestamp < DATEADD(day, -?, GETDATE())"
                    params.append(safe_days)

            cursor = self._adapter.execute_query(query, tuple(params) if params else None)

            count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            self._adapter.commit()
            return count

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to clear logs: {str(e)}.") from e
