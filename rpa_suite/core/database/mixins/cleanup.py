# rpa_suite/core/database/mixins/cleanup.py
from __future__ import annotations

from ..constants import CONFIRMATION_CODES, TRANSIENT_ERROR_KEYWORDS, DatabaseType
from ..exceptions import DatabaseError
from ..helpers import extract_row_id, row_to_dict, rows_to_dicts
from ..item_dedup import (
    extract_item_unique_value,
    json_extract_sql,
    resolve_item_identifier_for_storage,
)
from ..validation import validate_days, validate_limit


class CleanupMixin:
    """Domain operations — use via the Database class."""

    def _execute_delete(self, query: str, params: tuple | None = None) -> int:
        """Execute a parameterized DELETE and return the row count."""
        self._ensure_open()
        try:
            cursor = self._adapter.execute_query(query, params)
            count = self._adapter.rowcount(cursor)
            self._adapter.commit()
            return count
        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to execute cleanup: {str(e)}.") from e

    def clear_pending_items(self, execution_id: int | None = None) -> int:
        """
        Delete items with status pending or queued.

        Parameters:
        -----------
        execution_id: Optional[int]
            Execution id. When omitted, uses the active execution from start_execution().
            When no active execution exists, deletes across all executions.

        Returns:
        --------
        int: Number of deleted items

        """
        try:
            if execution_id:
                query = f"""
                    DELETE FROM {self.items_table}
                    WHERE execution_id = ? AND status IN ('pending', 'queued')
                """
                return self._execute_delete(query, (execution_id,))
            query = f"""
                DELETE FROM {self.items_table}
                WHERE status IN ('pending', 'queued')
            """
            return self._execute_delete(query)

        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to clear pending items: {str(e)}.") from e

    def clear_interrupted_items(self, execution_id: int | None = None, allow_reprocess_check: bool = True) -> int:
        """
        Delete items with status interrupted.

        Parameters:
        -----------
        execution_id: Optional[int]
            Execution id. When None, delete across all executions.

        allow_reprocess_check: bool
            When True, delete only items that cannot be reprocessed

        Returns:
        --------
        int: Number of deleted items

        """
        try:
            if allow_reprocess_check:
                filter_clause = " AND allow_reprocess = 0"
            else:
                filter_clause = ""

            if execution_id:
                query = f"""
                    DELETE FROM {self.items_table}
                    WHERE execution_id = ? AND status = 'interrupted'{filter_clause}
                """
                cursor = self._adapter.execute_query(query, (execution_id,))
            else:
                query = f"""
                    DELETE FROM {self.items_table}
                    WHERE status = 'interrupted'{filter_clause}
                """
                cursor = self._adapter.execute_query(query)

            count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            self._adapter.commit()
            return count

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to clear interrupted items: {str(e)}.") from e

    def clear_interrupted_executions(self, allow_reprocess_check: bool = True) -> int:
        """
        Delete executions with status interrupted.

        Parameters:
        -----------
        allow_reprocess_check: bool
            When True, delete only executions that cannot be reprocessed

        Returns:
        --------
        int: Número de execuções removidas

        """
        try:
            if allow_reprocess_check:
                filter_clause = " AND allow_reprocess = 0"
            else:
                filter_clause = ""

            query = f"""
                DELETE FROM {self.executions_table}
                WHERE status = 'interrupted'{filter_clause}
            """
            cursor = self._adapter.execute_query(query)

            count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            self._adapter.commit()
            return count

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to clear interrupted executions: {str(e)}.") from e

    def clear_successful_items(
        self, execution_id: int | None = None, confirm: bool = False, confirmation_code: str | None = None
    ) -> int:
        """
        Delete items with status success.

        DANGER: permanently deletes successful data!
        Requer confirmação dupla para segurança.

        Parameters:
        -----------
        execution_id: Optional[int]
            Execution id. When None, delete across all executions.

        confirm: bool
            Deve ser True

        confirmation_code: Optional[str]
            Deve ser "DELETE_SUCCESS" para executar

        Returns:
        --------
        int: Number of deleted items

        Raises:
        ------
        DatabaseError: Se confirmação não fornecida corretamente

        """
        if not confirm:
            raise DatabaseError("This operation permanently deletes data. " "Pass confirm=True to proceed.")

        if confirmation_code != CONFIRMATION_CODES["DELETE_SUCCESS"]:
            raise DatabaseError(
                f"Invalid confirmation. " f"Pass confirmation_code='{CONFIRMATION_CODES['DELETE_SUCCESS']}'"
            )

        try:
            if execution_id:
                query = f"""
                    DELETE FROM {self.items_table}
                    WHERE execution_id = ? AND status = 'success'
                """
                cursor = self._adapter.execute_query(query, (execution_id,))
            else:
                query = f"""
                    DELETE FROM {self.items_table}
                    WHERE status = 'success'
                """
                cursor = self._adapter.execute_query(query)

            count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            self._adapter.commit()
            return count

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to clear successful items: {str(e)}.") from e

    def clear_failed_items(
        self, execution_id: int | None = None, confirm: bool = False, confirmation_code: str | None = None
    ) -> int:
        """
        Delete items with status failed.

        DANGER: permanently deletes failed data!
        Requer confirmação dupla para segurança.

        Parameters:
        -----------
        execution_id: Optional[int]
            Execution id. When None, delete across all executions.

        confirm: bool
            Deve ser True

        confirmation_code: Optional[str]
            Deve ser "DELETE_FAILED" para executar

        Returns:
        --------
        int: Number of deleted items

        """
        if not confirm:
            raise DatabaseError("This operation permanently deletes data. " "Pass confirm=True to proceed.")

        if confirmation_code != CONFIRMATION_CODES["DELETE_FAILED"]:
            raise DatabaseError(
                f"Invalid confirmation. " f"Pass confirmation_code='{CONFIRMATION_CODES['DELETE_FAILED']}'"
            )

        try:
            if execution_id:
                query = f"""
                    DELETE FROM {self.items_table}
                    WHERE execution_id = ? AND status = 'failed'
                """
                cursor = self._adapter.execute_query(query, (execution_id,))
            else:
                query = f"""
                    DELETE FROM {self.items_table}
                    WHERE status = 'failed'
                """
                cursor = self._adapter.execute_query(query)

            count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            self._adapter.commit()
            return count

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to clear failed items: {str(e)}.") from e

    def clear_successful_executions(self, confirm: bool = False, confirmation_code: str | None = None) -> int:
        """
        Delete completed executions.

        DANGER: permanently deletes successful executions!

        Parameters:
        -----------
        confirm: bool
            Deve ser True

        confirmation_code: Optional[str]
            Deve ser "DELETE_SUCCESS_EXECUTIONS" para executar

        Returns:
        --------
        int: Número de execuções removidas

        """
        if not confirm:
            raise DatabaseError("This operation permanently deletes data. " "Pass confirm=True to proceed.")

        if confirmation_code != CONFIRMATION_CODES["DELETE_SUCCESS_EXECUTIONS"]:
            raise DatabaseError(
                f"Invalid confirmation. " f"Pass confirmation_code='{CONFIRMATION_CODES['DELETE_SUCCESS_EXECUTIONS']}'"
            )

        try:
            query = f"""
                DELETE FROM {self.executions_table}
                WHERE status = 'completed'
            """
            cursor = self._adapter.execute_query(query)

            count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            self._adapter.commit()
            return count

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to clear successful executions: {str(e)}.") from e

    def clear_failed_executions(self, confirm: bool = False, confirmation_code: str | None = None) -> int:
        """
        Delete failed executions.

        DANGER: permanently deletes failed executions!

        Parameters:
        -----------
        confirm: bool
            Deve ser True

        confirmation_code: Optional[str]
            Deve ser "DELETE_FAILED_EXECUTIONS" para executar

        Returns:
        --------
        int: Número de execuções removidas

        """
        if not confirm:
            raise DatabaseError("This operation permanently deletes data. " "Pass confirm=True to proceed.")

        if confirmation_code != CONFIRMATION_CODES["DELETE_FAILED_EXECUTIONS"]:
            raise DatabaseError(
                f"Invalid confirmation. " f"Pass confirmation_code='{CONFIRMATION_CODES['DELETE_FAILED_EXECUTIONS']}'"
            )

        try:
            query = f"""
                DELETE FROM {self.executions_table}
                WHERE status = 'failed'
            """
            cursor = self._adapter.execute_query(query)

            count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            self._adapter.commit()
            return count

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to clear failed executions: {str(e)}.") from e

    def clear_executions_table(self, confirm: bool = False) -> bool:
        """
        Delete the entire executions table.

        DANGER: permanently deletes all executions!

        Parameters:
        -----------
        confirm: bool
            Deve ser True para executar

        Returns:
        --------
        bool: True se executado com sucesso

        """
        if not confirm:
            raise DatabaseError("Esta operação remove TODOS os dados permanentemente! " "Pass confirm=True to proceed.")

        try:
            query = f"DELETE FROM {self.executions_table}"
            self._adapter.execute_query(query)
            self._adapter.commit()
            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to clear executions table: {str(e)}.") from e

    def clear_items_table(self, confirm: bool = False) -> bool:
        """
        Delete the entire items table.

        DANGER: permanently deletes all items!

        Parameters:
        -----------
        confirm: bool
            Deve ser True para executar

        Returns:
        --------
        bool: True se executado com sucesso

        """
        if not confirm:
            raise DatabaseError("Esta operação remove TODOS os dados permanentemente! " "Pass confirm=True to proceed.")

        try:
            query = f"DELETE FROM {self.items_table}"
            self._adapter.execute_query(query)
            self._adapter.commit()
            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to clear items table: {str(e)}.") from e

    def clear_logs_table(self, confirm: bool = False) -> bool:
        """
        Delete the entire logs table.

        DANGER: permanently deletes all logs!

        Parameters:
        -----------
        confirm: bool
            Deve ser True para executar

        Returns:
        --------
        bool: True se executado com sucesso

        """
        if not confirm:
            raise DatabaseError("Esta operação remove TODOS os dados permanentemente! " "Pass confirm=True to proceed.")

        try:
            query = f"DELETE FROM {self.logs_table}"
            self._adapter.execute_query(query)
            self._adapter.commit()
            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to clear logs table: {str(e)}.") from e

    def clear_database(self, confirm: bool = False) -> bool:
        """
        Clear the entire database (all tables).

        DANGER: permanently deletes all data!

        Parameters:
        -----------
        confirm: bool
            Deve ser True para executar

        Returns:
        --------
        bool: True se executado com sucesso

        """
        if not confirm:
            raise DatabaseError("Esta operação remove TODOS os dados permanentemente! " "Pass confirm=True to proceed.")

        try:
            self.clear_items_table(confirm=True)
            self.clear_logs_table(confirm=True)  # Limpa logs antes de execuções
            self.clear_executions_table(confirm=True)
            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Failed to clear database: {str(e)}.") from e
