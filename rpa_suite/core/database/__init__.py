# rpa_suite/core/database/__init__.py

"""
Database subpackage — RPA execution tracking with multi-database support.

Recommended import (backward compatible):
    >>> from rpa_suite.core import Database, DatabaseType
    >>> from rpa_suite import rpa
    >>> db = rpa.database(...)
"""

from .constants import (
    CONFIRMATION_CODES,
    DEFAULT_DB_NAME,
    DEFAULT_EXECUTIONS_TABLE,
    DEFAULT_ITEMS_TABLE,
    DEFAULT_LOGS_TABLE,
    LOG_LEVEL_CRITICAL,
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_INFO,
    LOG_LEVEL_SUCCESS,
    LOG_LEVEL_WARNING,
    TRANSIENT_ERROR_KEYWORDS,
    VALID_LOG_LEVELS,
    DatabaseType,
)
from .core import Database
from .exceptions import DatabaseError

__all__ = [
    "Database",
    "DatabaseType",
    "DatabaseError",
    "CONFIRMATION_CODES",
    "DEFAULT_DB_NAME",
    "DEFAULT_EXECUTIONS_TABLE",
    "DEFAULT_ITEMS_TABLE",
    "DEFAULT_LOGS_TABLE",
    "LOG_LEVEL_DEBUG",
    "LOG_LEVEL_INFO",
    "LOG_LEVEL_WARNING",
    "LOG_LEVEL_ERROR",
    "LOG_LEVEL_CRITICAL",
    "LOG_LEVEL_SUCCESS",
    "VALID_LOG_LEVELS",
    "TRANSIENT_ERROR_KEYWORDS",
]
