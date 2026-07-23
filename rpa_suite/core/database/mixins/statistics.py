# rpa_suite/core/database/mixins/statistics.py
from __future__ import annotations

from typing import Any

from ..constants import DatabaseType
from ..exceptions import DatabaseError


class StatisticsMixin:
    """Domain operations — use via the Database class."""

    def get_statistics(self, execution_id: int | None = None) -> dict[str, Any]:
        """
        Return execution/item statistics.

        Parameters:
        -----------
        execution_id: Optional[int]
            Execution id. When None, return global statistics

        Returns:
        --------
        Dict[str, Any]: Statistics

        """
        try:
            if execution_id:
                exec_data = self.get_execution(execution_id)
                if not exec_data:
                    return {}

                items = self.get_items(execution_id, status="all")

                return {
                    "execution": exec_data,
                    "total_items": len(items),
                    "items_by_status": {
                        status: len([i for i in items if i.get("status") == status])
                        for status in ["pending", "queued", "processing", "success", "failed", "interrupted"]
                    },
                }
            else:
                exec_query = f"""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                        SUM(CASE WHEN status = 'interrupted' THEN 1 ELSE 0 END) as interrupted
                    FROM {self.executions_table}
                """
                exec_cursor = self._adapter.execute_query(exec_query)
                exec_stats = exec_cursor.fetchone()

                items_query = f"""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                        SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                    FROM {self.items_table}
                """
                items_cursor = self._adapter.execute_query(items_query)
                items_stats = items_cursor.fetchone()

                if self.db_type == DatabaseType.SQLITE:
                    return {"executions": dict(exec_stats), "items": dict(items_stats)}
                else:
                    exec_dict = (
                        dict(exec_stats) if hasattr(exec_stats, "keys") else {i: v for i, v in enumerate(exec_stats)}
                    )
                    items_dict = (
                        dict(items_stats) if hasattr(items_stats, "keys") else {i: v for i, v in enumerate(items_stats)}
                    )
                    return {"executions": exec_dict, "items": items_dict}

        except Exception as e:
            raise DatabaseError(f"Failed to fetch statistics: {str(e)}.") from e
