# rpa_suite/core/database/signals.py

from __future__ import annotations

import atexit
import signal
import weakref
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import Database


_handlers_installed = False
_registered: weakref.WeakSet[Database] = weakref.WeakSet()


def register_database(db: Database) -> None:
    """Register a Database instance for interruption detection (singleton handlers)."""
    _registered.add(db)
    _ensure_handlers()


def unregister_database(db: Database) -> None:
    _registered.discard(db)


def _ensure_handlers() -> None:
    global _handlers_installed
    if _handlers_installed:
        return
    atexit.register(_handle_exit)
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)
    _handlers_installed = True


def _handle_exit() -> None:
    for db in list(_registered):
        db._on_interrupt_signal()


def _handle_signal(signum, frame) -> None:
    _handle_exit()
