# rpa_suite/core/database/constants.py

from enum import Enum


class DatabaseType(Enum):
    """Supported database backends."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLSERVER = "sqlserver"


CONFIRMATION_CODES = {
    "DELETE_SUCCESS": "DELETE_SUCCESS",
    "DELETE_FAILED": "DELETE_FAILED",
    "DELETE_SUCCESS_EXECUTIONS": "DELETE_SUCCESS_EXECUTIONS",
    "DELETE_FAILED_EXECUTIONS": "DELETE_FAILED_EXECUTIONS",
    "CLEAR_TABLE": "CLEAR_TABLE",
    "CLEAR_DATABASE": "CLEAR_DATABASE",
}

DEFAULT_DB_NAME = "athena_executions.db"
DEFAULT_EXECUTIONS_TABLE = "athena_executions"
DEFAULT_ITEMS_TABLE = "athena_items"
DEFAULT_LOGS_TABLE = "athena_logs"

LOG_LEVEL_DEBUG = "debug"
LOG_LEVEL_INFO = "info"
LOG_LEVEL_WARNING = "warning"
LOG_LEVEL_ERROR = "error"
LOG_LEVEL_CRITICAL = "critical"
LOG_LEVEL_SUCCESS = "success"
VALID_LOG_LEVELS = (
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_CRITICAL,
    LOG_LEVEL_SUCCESS,
)
VALID_LOG_LEVELS_SQL = "', '".join(VALID_LOG_LEVELS)

TRANSIENT_ERROR_KEYWORDS = (
    "timeout",
    "timed out",
    "temporar",
    "temporarily",
    "connection reset",
    "connection aborted",
    "connection refused",
    "network",
    "rate limit",
    "too many requests",
    "429",
    "500",
    "502",
    "503",
    "504",
    "lock",
    "deadlock",
)

DEFAULT_SQLITE_BUSY_TIMEOUT_MS = 30_000

# Filtros agrupados para get_items()
# Written statuses: pending → processing → success|failed|skipped|interrupted.
# queued/retrying appear only as read aliases for legacy rows.
ITEM_STATUS_FILTER_PENDING = "pending"
ITEM_STATUS_FILTER_EXECUTED = "executed"
ITEM_STATUS_FILTER_ALL = "all"
DEFAULT_GET_ITEMS_STATUS = ITEM_STATUS_FILTER_PENDING

ITEM_STATUS_FILTER_GROUPS: dict[str, tuple[str, ...] | None] = {
    "pending": ("pending", "queued"),
    "pendente": ("pending", "queued"),
    "executed": ("success", "failed", "skipped"),
    "executado": ("success", "failed", "skipped"),
    "interrupted": ("interrupted",),
    "interrompido": ("interrupted",),
    # Trabalho pendente: tudo que ainda não terminou com sucesso/skip
    "backlog": ("pending", "queued", "interrupted", "retrying", "failed", "processing"),
    "reprocessavel": ("pending", "queued", "interrupted", "retrying", "failed", "processing"),
    "all": None,
    "todos": None,
}
