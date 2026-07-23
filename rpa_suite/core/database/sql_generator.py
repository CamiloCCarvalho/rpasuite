# rpa_suite/core/database/sql_generator.py

from typing import List

from .constants import (
    LOG_LEVEL_INFO,
    VALID_LOG_LEVELS_SQL,
    DatabaseType,
)


class SQLGenerator:
    """Generate SQL compatible with different database backends."""

    def __init__(
        self,
        db_type: DatabaseType,
        executions_table: str,
        items_table: str,
        logs_table: str,
    ):
        self.db_type = db_type
        self.executions_table = executions_table
        self.items_table = items_table
        self.logs_table = logs_table

    def _get_pk_type(self) -> str:
        if self.db_type == DatabaseType.SQLITE:
            return "INTEGER PRIMARY KEY AUTOINCREMENT"
        if self.db_type == DatabaseType.POSTGRESQL:
            return "SERIAL PRIMARY KEY"
        if self.db_type == DatabaseType.MYSQL:
            return "INT AUTO_INCREMENT PRIMARY KEY"
        return "INTEGER PRIMARY KEY AUTOINCREMENT"

    def _get_text_type(self) -> str:
        if self.db_type in (DatabaseType.POSTGRESQL, DatabaseType.MYSQL):
            return "VARCHAR(255)"
        return "TEXT"

    def _get_long_text_type(self) -> str:
        return "TEXT"

    def _get_boolean_type(self) -> str:
        if self.db_type == DatabaseType.SQLITE:
            return "INTEGER"
        return "BOOLEAN"

    def _get_datetime_type(self) -> str:
        if self.db_type == DatabaseType.POSTGRESQL:
            return "TIMESTAMP"
        return "DATETIME"

    def _get_real_type(self) -> str:
        if self.db_type == DatabaseType.POSTGRESQL:
            return "DOUBLE PRECISION"
        if self.db_type == DatabaseType.MYSQL:
            return "DOUBLE"
        return "REAL"

    def create_executions_table(self) -> str:
        pk_type = self._get_pk_type()
        text_type = self._get_text_type()
        long_text_type = self._get_long_text_type()
        bool_type = self._get_boolean_type()
        datetime_type = self._get_datetime_type()
        real_type = self._get_real_type()
        bool_default_false = "DEFAULT 0" if self.db_type == DatabaseType.SQLITE else "DEFAULT FALSE"
        default_timestamp = "DEFAULT CURRENT_TIMESTAMP"

        sql = f"""
            CREATE TABLE IF NOT EXISTS {self.executions_table} (
                id {pk_type},
                execution_id {text_type} UNIQUE,
                automation_name {text_type} NOT NULL,
                status {text_type} NOT NULL DEFAULT 'running',
                finished_properly {bool_type} {bool_default_false},
                allow_reprocess {bool_type} DEFAULT 1,
                reprocess_count INTEGER DEFAULT 0,
                parent_execution_id INTEGER,
                started_at {datetime_type} NOT NULL {default_timestamp},
                finished_at {datetime_type},
                execution_time_seconds {real_type},
                total_items INTEGER DEFAULT 0,
                successful_items INTEGER DEFAULT 0,
                failed_items INTEGER DEFAULT 0,
                interrupted_items INTEGER DEFAULT 0,
                error_message {long_text_type},
                metadata {long_text_type},
                created_at {datetime_type} NOT NULL {default_timestamp},
                FOREIGN KEY (parent_execution_id) REFERENCES {self.executions_table}(id) ON DELETE SET NULL,
                CHECK (status IN ('running', 'completed', 'failed', 'cancelled', 'interrupted'))
            )
        """
        if self.db_type == DatabaseType.MYSQL:
            sql += " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        return sql

    def create_items_table(self) -> str:
        pk_type = self._get_pk_type()
        text_type = self._get_text_type()
        long_text_type = self._get_long_text_type()
        bool_type = self._get_boolean_type()
        datetime_type = self._get_datetime_type()
        real_type = self._get_real_type()
        default_timestamp = "DEFAULT CURRENT_TIMESTAMP"

        sql = f"""
            CREATE TABLE IF NOT EXISTS {self.items_table} (
                id {pk_type},
                execution_id INTEGER NOT NULL,
                item_identifier {text_type},
                status {text_type} NOT NULL DEFAULT 'pending',
                priority INTEGER DEFAULT 0,
                queue_position INTEGER,
                processing_schema {long_text_type},
                item_data {long_text_type},
                last_checkpoint {text_type},
                started_at {datetime_type},
                finished_at {datetime_type},
                execution_time_seconds {real_type},
                error_message {long_text_type},
                notes {long_text_type},
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 0,
                allow_reprocess {bool_type} DEFAULT 1,
                created_at {datetime_type} NOT NULL {default_timestamp},
                FOREIGN KEY (execution_id) REFERENCES {self.executions_table}(id) ON DELETE CASCADE,
                CHECK (status IN ('pending', 'queued', 'processing', 'success', 'failed', 'skipped', 'interrupted', 'retrying'))
            )
        """
        if self.db_type == DatabaseType.MYSQL:
            sql += " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        return sql

    def create_logs_table(self) -> str:
        pk_type = self._get_pk_type()
        text_type = self._get_text_type()
        long_text_type = self._get_long_text_type()
        datetime_type = self._get_datetime_type()
        default_timestamp = "DEFAULT CURRENT_TIMESTAMP"

        sql = f"""
            CREATE TABLE IF NOT EXISTS {self.logs_table} (
                id {pk_type},
                execution_id INTEGER NOT NULL,
                log_level {text_type} DEFAULT '{LOG_LEVEL_INFO}',
                step_name {text_type},
                message {long_text_type} NOT NULL,
                timestamp {datetime_type} NOT NULL {default_timestamp},
                created_at {datetime_type} NOT NULL {default_timestamp},
                FOREIGN KEY (execution_id) REFERENCES {self.executions_table}(id) ON DELETE CASCADE,
                CHECK (log_level IN ('{VALID_LOG_LEVELS_SQL}'))
            )
        """
        if self.db_type == DatabaseType.MYSQL:
            sql += " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        return sql

    def create_indexes(self) -> List[str]:
        return [
            f"CREATE INDEX IF NOT EXISTS idx_{self.executions_table}_execution_id ON {self.executions_table}(execution_id)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.executions_table}_status ON {self.executions_table}(status)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.executions_table}_finished_properly ON {self.executions_table}(finished_properly)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.executions_table}_started_at ON {self.executions_table}(started_at)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.items_table}_execution_id ON {self.items_table}(execution_id)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.items_table}_status ON {self.items_table}(status)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.items_table}_queue ON {self.items_table}(execution_id, queue_position, status)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.items_table}_priority ON {self.items_table}(priority DESC, status)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.logs_table}_execution_id ON {self.logs_table}(execution_id)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.logs_table}_timestamp ON {self.logs_table}(timestamp)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.logs_table}_log_level ON {self.logs_table}(log_level)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.logs_table}_execution_timestamp ON {self.logs_table}(execution_id, timestamp)",
        ]
