# rpa_suite/core/asyncrun.py

# imports standard
import asyncio
import threading
import time
import traceback
from concurrent.futures import Future
from concurrent.futures import TimeoutError as FuturesTimeoutError
from functools import wraps
from typing import Any, Callable, Dict, Generic, Optional, TypeVar

T = TypeVar("T")


class AsyncRunnerError(Exception):
    """Custom exception for AsyncRunner errors."""

    def __init__(self, message):
        clean_message = message.replace("AsyncRunnerError:", "").strip()
        super().__init__(f"AsyncRunnerError: {clean_message}")


class AsyncRunner(Generic[T]):
    """
    Class to execute asynchronous functions while maintaining the main application flow.

    Runs a dedicated background thread with a persistent event loop, so synchronous
    scripts can schedule coroutines (or regular functions) and retrieve their result
    later without needing to manage `asyncio.run` themselves.

    Optimized for I/O bound operations (network, files, etc).

    Example:
    ----------
    >>> import asyncio
    >>> async def slow(x):
    ...     await asyncio.sleep(0.1)
    ...     return x * 2
    >>> runner = AsyncRunner()
    >>> runner.run(slow, 5)
    >>> result = runner.get_result(timeout=2)
    >>> result["result"]
    10
    """

    def __init__(self) -> None:
        """
        Initialize the runner and start a background thread with a persistent event loop.
        """
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._loop_ready = threading.Event()
        self._future: Optional[Future] = None
        self._start_time: Optional[float] = None
        self._result: Dict[str, Any] = {}
        self._shutdown = False
        self._start_loop_thread()

    def _start_loop_thread(self) -> None:
        """Create the background thread that owns the event loop."""

        def _thread_target() -> None:
            loop = asyncio.new_event_loop()
            self._loop = loop
            asyncio.set_event_loop(loop)
            self._loop_ready.set()
            try:
                loop.run_forever()
            finally:
                try:
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()
                    if pending:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                finally:
                    loop.close()

        self._thread = threading.Thread(
            target=_thread_target,
            name="AsyncRunnerLoop",
            daemon=True,
        )
        self._thread.start()
        self._loop_ready.wait()

    @staticmethod
    def _to_async(func: Callable) -> Callable:
        """
        Convert a synchronous function into an asynchronous one if necessary.

        Args:
            func: The function to be converted.

        Returns:
            A callable that is asynchronous.
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return await asyncio.to_thread(func, *args, **kwargs)

        return wrapper

    async def _execute_function(self, function, args, kwargs) -> Dict[str, Any]:
        """
        Execute the function and return a result dict.

        Args:
            function: The function to be executed.
            args: Positional arguments for the function.
            kwargs: Keyword arguments for the function.

        Returns:
            Result dictionary with success/error information.
        """
        try:
            async_func = self._to_async(function)
            result = await async_func(*args, **kwargs)
            return {"status": "success", "result": result, "success": True}
        except asyncio.CancelledError:
            return {
                "status": "cancelled",
                "error": "Task was cancelled",
                "success": False,
            }
        except Exception as e:  # noqa: BLE001 - propagate as structured result
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "success": False,
            }

    def run(self, function: Callable[..., T], *args, **kwargs) -> "AsyncRunner[T]":
        """
        Schedule the given function to run on the background event loop.

        Args:
            function: The function (sync or async) to execute.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            self: The runner instance (for chaining).
        """
        if self._shutdown or self._loop is None or not self._loop.is_running():
            raise AsyncRunnerError("AsyncRunner has been shut down or the event loop is not running.")
        try:
            self._result = {}
            self._start_time = time.time()
            coro = self._execute_function(function, args, kwargs)
            self._future = asyncio.run_coroutine_threadsafe(coro, self._loop)
            return self
        except Exception as e:  # noqa: BLE001
            raise AsyncRunnerError(f"Error starting async execution: {str(e)}.") from e

    def is_running(self) -> bool:
        """
        Check whether the scheduled task is still running.

        Returns:
            True if the task is running, False otherwise.
        """
        if self._future is None:
            return False
        return not self._future.done()

    def get_result(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Retrieve the result of the asynchronous execution (synchronous wait).

        Args:
            timeout: Maximum time (in seconds) to wait. `None` waits indefinitely.

        Returns:
            Dictionary with the result or error information plus `execution_time`.
        """
        if self._future is None:
            return {
                "success": False,
                "error": "No task has been started",
                "execution_time": 0,
            }

        try:
            result = self._future.result(timeout=timeout)
        except FuturesTimeoutError:
            self._future.cancel()
            elapsed = time.time() - (self._start_time or time.time())
            return {
                "success": False,
                "error": f"Operation canceled due to timeout after {elapsed:.2f} seconds",
                "execution_time": elapsed,
            }
        except Exception as e:  # noqa: BLE001
            elapsed = time.time() - (self._start_time or time.time())
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "execution_time": elapsed,
            }

        elapsed = time.time() - (self._start_time or time.time())
        payload = dict(result)
        payload["execution_time"] = elapsed
        self._result = payload
        return payload

    def cancel(self) -> None:
        """
        Cancel the running task, if any.
        """
        if self._future is not None and not self._future.done():
            self._future.cancel()

    def shutdown(self, wait: bool = True) -> None:
        """
        Stop the background event loop and thread.

        Args:
            wait: If True, blocks until the thread has fully stopped.
        """
        if self._shutdown:
            return
        self._shutdown = True
        loop = self._loop
        if loop is not None and loop.is_running():
            loop.call_soon_threadsafe(loop.stop)
        if wait and self._thread is not None:
            self._thread.join(timeout=5)

    def __del__(self):
        try:
            self.shutdown(wait=False)
        except Exception:
            pass
