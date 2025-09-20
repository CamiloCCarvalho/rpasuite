# rpa_suite/core/asyncrun.py

# imports standard
from typing import Any, Callable, Dict, Optional, TypeVar, Generic
import asyncio
import time
import traceback
from functools import wraps


T = TypeVar("T")

class AsyncRunnerError(Exception):
    """Custom exception for AsyncRunner errors."""
    def __init__(self, message):
        super().__init__(f'AsyncRunnerError: {message}')

class AsyncRunner(Generic[T]):
    """
    Class to execute asynchronous functions while maintaining the main application flow.

    Allows executing asynchronous functions and retrieving their results later.
    Optimized for I/O bound operations (network, files, etc).
    """

    def __init__(self) -> None:
        """Start AsyncRunner."""
        self._task = None
        self._start_time = None
        self._result = {}

    @staticmethod
    def _to_async(func: Callable) -> Callable:
        """
        Converts a synchronous function into an asynchronous one if necessary.

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

    async def _execute_function(self, function, args, kwargs) -> None:
        """
        Executes the function and manages results/errors.

        Args:
            function: The function to be executed.
            args: Positional arguments for the function.
            kwargs: Keyword arguments for the function.
        """
        try:
            async_func = self._to_async(function)
            result = await async_func(*args, **kwargs)

            self._result = {"status": "success", "result": result, "success": True}

        except Exception as e:
            self._result = {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "success": False,
            }

    def run(self, function: Callable[..., T], *args, **kwargs) -> "AsyncRunner[T]":
        """
        Starts the execution of the function asynchronously.

        Args:
            function: The function to be executed.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            self: Returns the instance itself.
        """
        try:
            self._result.clear()
            self._start_time = time.time()

            # Creates and schedules the asynchronous task
            loop = asyncio.get_event_loop()
            self._task = loop.create_task(self._execute_function(function, args, kwargs))

            return self
        except Exception as e:
            raise AsyncRunnerError(f"Erro ao iniciar a execução da função: {str(e)}.") from e

    def is_running(self) -> bool:
        """
        Checks if the task is still running.

        Returns:
            True if the task is running, False otherwise.
        """
        return self._task is not None and not self._task.done()

    async def get_result(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Retrieves the result of the asynchronous execution.

        Args:
            timeout: Maximum time (in seconds) to wait.

        Returns:
            A dictionary with the result or error information.
        """
        if self._task is None:
            return {
                "success": False,
                "error": "No task has been started",
                "execution_time": 0,
            }

        try:
            await asyncio.wait_for(self._task, timeout=timeout)

        except asyncio.TimeoutError:
            self._task.cancel()
            return {
                "success": False,
                "error": f"Operation canceled due to timeout after {time.time() - self._start_time:.2f} seconds",
                "execution_time": time.time() - self._start_time,
            }

        result = dict(self._result)
        result["execution_time"] = time.time() - self._start_time
        return result

    def cancel(self) -> None:
        """
        Cancels the running task.
        """
        if self.is_running():
            self._task.cancel()
