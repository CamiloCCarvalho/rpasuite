# rpa_suite/core/database/retention.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .constants import (
    LOG_LEVEL_CRITICAL,
    LOG_LEVEL_ERROR,
    VALID_LOG_LEVELS,
)
from .exceptions import DatabaseError

DEFAULT_LOG_PROTECT_LEVELS = (LOG_LEVEL_ERROR, LOG_LEVEL_CRITICAL)
DEFAULT_ITEM_PROTECT_STATUSES = (
    "pending",
    "queued",
    "processing",
    "interrupted",
    "retrying",
)
DEFAULT_EXECUTION_PROTECT_STATUSES = ("running", "interrupted")
DEFAULT_RETENTION_BATCH_SIZE = 5000


@dataclass
class LogsRetentionConfig:
    """Retention rules for the logs table."""

    max_age_days: int = 30
    max_age_days_by_level: dict[str, int] = field(
        default_factory=lambda: {LOG_LEVEL_ERROR: 90, LOG_LEVEL_CRITICAL: 180}
    )
    max_rows: int = 1_000_000
    protect_running_executions: bool = True
    batch_size: int = DEFAULT_RETENTION_BATCH_SIZE


@dataclass
class ItemsRetentionConfig:
    """Retention rules for the items table."""

    max_age_days_by_status: dict[str, int] = field(
        default_factory=lambda: {
            "success": 60,
            "failed": 120,
            "skipped": 60,
        }
    )
    max_rows_by_status: dict[str, int] = field(
        default_factory=lambda: {"success": 500_000}
    )
    protect_statuses: tuple[str, ...] = DEFAULT_ITEM_PROTECT_STATUSES
    batch_size: int = DEFAULT_RETENTION_BATCH_SIZE


@dataclass
class ExecutionsRetentionConfig:
    """Retention rules for the executions table."""

    max_age_days_by_status: dict[str, int] = field(
        default_factory=lambda: {
            "completed": 90,
            "failed": 120,
            "cancelled": 90,
        }
    )
    protect_statuses: tuple[str, ...] = DEFAULT_EXECUTION_PROTECT_STATUSES
    cascade_delete_children: bool = True
    batch_size: int = DEFAULT_RETENTION_BATCH_SIZE


@dataclass
class RetentionPolicy:
    """Automatic retention configuration for Database tables."""

    enabled: bool = False
    auto_on_init: bool = False
    auto_on_finish_execution: bool = False
    logs: LogsRetentionConfig = field(default_factory=LogsRetentionConfig)
    items: ItemsRetentionConfig = field(default_factory=ItemsRetentionConfig)
    executions: ExecutionsRetentionConfig = field(default_factory=ExecutionsRetentionConfig)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> RetentionPolicy:
        """Build a policy from a plain dict (Database constructor helper)."""
        if not data:
            return cls()

        policy = cls(
            enabled=bool(data.get("enabled", False)),
            auto_on_init=bool(data.get("auto_on_init", False)),
            auto_on_finish_execution=bool(data.get("auto_on_finish_execution", False)),
        )

        logs_data = data.get("logs") or {}
        policy.logs = LogsRetentionConfig(
            max_age_days=_validate_positive_int(logs_data.get("max_age_days", 30), "logs.max_age_days"),
            max_age_days_by_level=_normalize_level_days(
                logs_data.get("max_age_days_by_level"),
                default=policy.logs.max_age_days_by_level,
            ),
            max_rows=_validate_positive_int(logs_data.get("max_rows", 1_000_000), "logs.max_rows"),
            protect_running_executions=bool(
                logs_data.get("protect_running_executions", True)
            ),
            batch_size=_validate_positive_int(
                logs_data.get("batch_size", DEFAULT_RETENTION_BATCH_SIZE),
                "logs.batch_size",
            ),
        )

        items_data = data.get("items") or {}
        policy.items = ItemsRetentionConfig(
            max_age_days_by_status=_normalize_status_days(
                items_data.get("max_age_days_by_status"),
                default=policy.items.max_age_days_by_status,
            ),
            max_rows_by_status=_normalize_status_rows(
                items_data.get("max_rows_by_status"),
                default=policy.items.max_rows_by_status,
            ),
            protect_statuses=_normalize_status_tuple(
                items_data.get("protect_statuses"),
                default=DEFAULT_ITEM_PROTECT_STATUSES,
            ),
            batch_size=_validate_positive_int(
                items_data.get("batch_size", DEFAULT_RETENTION_BATCH_SIZE),
                "items.batch_size",
            ),
        )

        executions_data = data.get("executions") or {}
        policy.executions = ExecutionsRetentionConfig(
            max_age_days_by_status=_normalize_status_days(
                executions_data.get("max_age_days_by_status"),
                default=policy.executions.max_age_days_by_status,
            ),
            protect_statuses=_normalize_status_tuple(
                executions_data.get("protect_statuses"),
                default=DEFAULT_EXECUTION_PROTECT_STATUSES,
            ),
            cascade_delete_children=bool(
                executions_data.get("cascade_delete_children", True)
            ),
            batch_size=_validate_positive_int(
                executions_data.get("batch_size", DEFAULT_RETENTION_BATCH_SIZE),
                "executions.batch_size",
            ),
        )
        return policy


def _validate_positive_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise DatabaseError(f"Invalid retention policy: {field_name} must be a positive integer.")
    return value


def _normalize_level_days(
    raw: Any,
    *,
    default: dict[str, int],
) -> dict[str, int]:
    if raw is None:
        return dict(default)
    if not isinstance(raw, dict):
        raise DatabaseError("Invalid retention policy: logs.max_age_days_by_level must be a dict.")
    normalized: dict[str, int] = {}
    for level, days in raw.items():
        level_key = str(level).lower().strip()
        if level_key not in VALID_LOG_LEVELS:
            raise DatabaseError(f"Invalid retention policy: unknown log level '{level}'.")
        normalized[level_key] = _validate_positive_int(days, f"logs.max_age_days_by_level[{level_key}]")
    return normalized


def _normalize_status_days(
    raw: Any,
    *,
    default: dict[str, int],
) -> dict[str, int]:
    if raw is None:
        return dict(default)
    if not isinstance(raw, dict):
        raise DatabaseError("Invalid retention policy: status day map must be a dict.")
    normalized: dict[str, int] = {}
    for status, days in raw.items():
        status_key = str(status).lower().strip()
        normalized[status_key] = _validate_positive_int(
            days,
            f"retention max_age_days_by_status[{status_key}]",
        )
    return normalized


def _normalize_status_rows(
    raw: Any,
    *,
    default: dict[str, int],
) -> dict[str, int]:
    if raw is None:
        return dict(default)
    if not isinstance(raw, dict):
        raise DatabaseError("Invalid retention policy: max_rows_by_status must be a dict.")
    normalized: dict[str, int] = {}
    for status, max_rows in raw.items():
        status_key = str(status).lower().strip()
        normalized[status_key] = _validate_positive_int(
            max_rows,
            f"retention max_rows_by_status[{status_key}]",
        )
    return normalized


def _normalize_status_tuple(raw: Any, *, default: tuple[str, ...]) -> tuple[str, ...]:
    if raw is None:
        return default
    if not isinstance(raw, (list, tuple)):
        raise DatabaseError("Invalid retention policy: protect_statuses must be a list or tuple.")
    return tuple(str(status).lower().strip() for status in raw if str(status).strip())
