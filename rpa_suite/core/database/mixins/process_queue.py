# rpa_suite/core/database/mixins/process_queue.py

# imports standard
import traceback
from typing import Any, Callable, Dict, Optional


class ProcessQueueMixin:
    """
    High-level queue loop for Database — use via the Database class.

    Provides `process_queue(...)`, which repeatedly claims the next pending
    item, calls a user-supplied handler with it, and automatically marks the
    item as success/failed based on the handler outcome. Designed so RPA users
    do not have to hand-roll the claim/try/except/finish plumbing.
    """

    def process_queue(
        self,
        execution_id: int,
        handler: Callable[[Dict[str, Any]], Any],
        max_items: Optional[int] = None,
        stop_on_error: bool = False,
        include_interrupted: Optional[bool] = None,
        on_success: Optional[Callable[[Dict[str, Any], Any], None]] = None,
        on_error: Optional[Callable[[Dict[str, Any], BaseException], None]] = None,
    ) -> Dict[str, int]:
        """
        Process pending items from the queue by delegating each one to `handler`.

        Behavior:
            * Repeatedly calls `claim_next_item_from_queue(execution_id, ...)`.
            * When an item is claimed, `handler(item)` is invoked. Whatever the
              handler returns is treated as the item's `notes` (if not str, it is
              coerced with `str(...)`).
            * If the handler raises, the item is marked as `failed` with the
              exception message. If `stop_on_error` is True, the loop exits.
            * When there is no item to claim, the loop terminates gracefully.

        Parameters:
        ----------
        execution_id : int
            Execution id that will own the processed items.
        handler : Callable[[dict], Any]
            User function that receives the claimed item as a dict.
        max_items : int, optional
            Upper bound on items to process this call. `None` means no limit.
        stop_on_error : bool
            If True, stop processing on the first handler exception.
        include_interrupted : bool, optional
            Forwarded to `claim_next_item_from_queue`. `None` uses the
            Database default.
        on_success : Callable[[item, result], None], optional
            Called after `finish_item(status='success')`.
        on_error : Callable[[item, exception], None], optional
            Called after `finish_item(status='failed')`.

        Returns:
        ----------
        dict with keys:
            * 'processed' : total items handled (success + failed).
            * 'success'   : count of successful items.
            * 'failed'    : count of failed items.
        """
        stats = {"processed": 0, "success": 0, "failed": 0}

        while True:
            if max_items is not None and stats["processed"] >= max_items:
                break

            item = self.claim_next_item_from_queue(  # type: ignore[attr-defined]
                execution_id,
                include_interrupted=include_interrupted,
            )
            if item is None:
                break

            item_id = item.get("id")
            if item_id is None:
                stats["processed"] += 1
                stats["failed"] += 1
                continue

            try:
                result = handler(item)
            except BaseException as exc:  # noqa: BLE001 - reported to on_error
                error_message = str(exc) or exc.__class__.__name__
                notes = traceback.format_exc()
                try:
                    self.finish_item(  # type: ignore[attr-defined]
                        item_id,
                        status="failed",
                        error_message=error_message,
                        notes=notes,
                    )
                finally:
                    stats["processed"] += 1
                    stats["failed"] += 1
                if on_error is not None:
                    try:
                        on_error(item, exc)
                    except Exception:  # noqa: BLE001
                        pass
                if stop_on_error:
                    break
                continue

            notes = None if result is None else str(result)
            self.finish_item(  # type: ignore[attr-defined]
                item_id,
                status="success",
                notes=notes,
            )
            stats["processed"] += 1
            stats["success"] += 1
            if on_success is not None:
                try:
                    on_success(item, result)
                except Exception:  # noqa: BLE001
                    pass

        return stats
