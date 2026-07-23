# rpa_suite/core/retry.py

# imports standard
import functools
import random
import time
from typing import Any, Callable, Iterable, Optional, Tuple, Type


class RetryError(Exception):
    """Custom exception raised when all retry attempts fail."""

    def __init__(self, message: str, last_exception: Optional[BaseException] = None) -> None:
        clean_message = message.replace("RetryError:", "").strip()
        super().__init__(f"RetryError: {clean_message}")
        self.last_exception = last_exception


def _normalize_exceptions(
    exceptions: Optional[Iterable[Type[BaseException]] | Type[BaseException]],
) -> Tuple[Type[BaseException], ...]:
    if exceptions is None:
        return (Exception,)
    if isinstance(exceptions, type) and issubclass(exceptions, BaseException):
        return (exceptions,)
    normalized: list[Type[BaseException]] = []
    for exc in exceptions:
        if not (isinstance(exc, type) and issubclass(exc, BaseException)):
            raise TypeError(f"Invalid exception type in `exceptions`: {exc!r}")
        normalized.append(exc)
    if not normalized:
        return (Exception,)
    return tuple(normalized)


def retry(
    attempts: int = 3,
    delay: float = 0.5,
    backoff: float = 2.0,
    exceptions: Optional[Iterable[Type[BaseException]] | Type[BaseException]] = None,
    max_delay: Optional[float] = None,
    jitter: float = 0.0,
    on_retry: Optional[Callable[[int, BaseException, float], None]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Retry a function on failure with exponential backoff.

    Parameters:
        attempts: Total number of tries (>= 1). The function is called at most
            this many times.
        delay: Base delay in seconds before the first retry.
        backoff: Multiplier applied to `delay` between attempts (>= 1).
        exceptions: Exception class or iterable of classes that should trigger a
            retry. Defaults to `(Exception,)`.
        max_delay: Optional cap on the delay between attempts.
        jitter: Random jitter (in seconds, absolute) added to each sleep to
            avoid thundering-herd effects. `0` disables jitter.
        on_retry: Optional callback `fn(attempt_index, exception, sleep_seconds)`
            invoked before each sleep.

    Returns:
        A decorator that wraps a callable with retry semantics. When all
        attempts are exhausted, `RetryError` is raised with the last exception
        chained as `__cause__`.

    Example:
        >>> @retry(attempts=4, delay=0.1, backoff=2.0, exceptions=IOError)
        ... def read_from_flaky_source():
        ...     ...
    """
    if attempts < 1:
        raise ValueError("`attempts` must be >= 1")
    if delay < 0 or backoff < 0 or (max_delay is not None and max_delay < 0) or jitter < 0:
        raise ValueError("`delay`, `backoff`, `max_delay` and `jitter` must be non-negative")

    retriable = _normalize_exceptions(exceptions)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exc: Optional[BaseException] = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retriable as exc:
                    last_exc = exc
                    if attempt == attempts:
                        break
                    sleep_for = current_delay
                    if jitter > 0:
                        sleep_for += random.uniform(0, jitter)
                    if max_delay is not None:
                        sleep_for = min(sleep_for, max_delay)
                    if on_retry is not None:
                        try:
                            on_retry(attempt, exc, sleep_for)
                        except Exception:  # noqa: BLE001 - callbacks must not break retry
                            pass
                    if sleep_for > 0:
                        time.sleep(sleep_for)
                    current_delay *= backoff
            raise RetryError(
                f"Function {func.__name__!r} failed after {attempts} attempts.",
                last_exception=last_exc,
            ) from last_exc

        return wrapper

    return decorator
