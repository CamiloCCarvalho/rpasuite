# rpa_suite/core/clock.py

# imports standard
import re
import time
from datetime import datetime as dt
from typing import Any, Callable

# imports internal
from rpa_suite.functions._printer import success_print

_HHMM_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


class ClockError(Exception):
    """Custom exception for Clock errors."""

    def __init__(self, message):
        clean_message = message.replace("ClockError:", "").strip()
        super().__init__(f"ClockError: {clean_message}")


class Clock:
    """
    Class that provides utilities for time manipulation and stopwatch.

    This class offers functionalities for:
        - Timed function execution
        - Execution time control
        - Task scheduling

    Methods:
        exec_at_hour: Executes a function at a specific time
        wait_for_exec: Waits N seconds, then executes a function
        exec_and_wait: Executes a function, then waits N seconds

    The Clock class is part of RPA Suite and can be accessed through the rpa object:
        >>> from rpa_suite import rpa
        >>> rpa.clock.exec_at_hour("14:30", my_function)
    """

    def __init__(self) -> None:
        """
        Initialize the Clock utility.
        """

    def exec_at_hour(
        self,
        hour_to_exec: str | None,
        fn_to_exec: Callable[..., Any],
        *args,
        **kwargs,
    ) -> dict[str, bool]:
        """
        Timed function, executes the function at the specified time.

        Parameters:
        ----------
            hour_to_exec (str | None): Time in `HH:MM` (24h) format. If None, runs immediately.
            fn_to_exec (Callable): Function to be executed.

        Returns:
        ----------
            dict with keys:
                * 'tried': bool - whether an execution attempt was made.
                * 'success': bool - whether the execution succeeded.

        Raises:
        ----------
            ClockError: If `hour_to_exec` is not a valid `HH:MM` string or if the
            target function raises an exception at the scheduled time.

        Example:
        ---------
        >>> exec_at_hour("11:00", sum, 10, 5)
        """

        result: dict = {"tried": False, "success": False}

        if hour_to_exec is not None:
            if not isinstance(hour_to_exec, str) or not _HHMM_PATTERN.match(hour_to_exec):
                raise ClockError(f"Invalid hour_to_exec format: {hour_to_exec!r}. Expected 'HH:MM' in 24h.")

        try:
            if hour_to_exec is None:
                try:
                    fn_to_exec(*args, **kwargs)
                    result["tried"] = True
                    result["success"] = True
                    success_print(f"{fn_to_exec.__name__}: Successfully executed!")
                except Exception:
                    result["tried"] = True
                    result["success"] = False
                return result

            run = True
            while run:
                now = dt.now()
                moment_now = f"{now.hour:02d}:{now.minute:02d}"
                if moment_now == hour_to_exec:
                    try:
                        fn_to_exec(*args, **kwargs)
                        result["tried"] = True
                        result["success"] = True
                        success_print(f"{fn_to_exec.__name__}: Successfully executed!")
                        run = False
                    except Exception as e:
                        result["tried"] = True
                        result["success"] = False
                        raise ClockError(
                            f"An error occurred that prevented the function from executing: "
                            f"{fn_to_exec.__name__} correctly. Error: {str(e)}"
                        ) from e
                else:
                    time.sleep(30)

            return result

        except ClockError:
            raise
        except Exception as e:
            result["success"] = False
            raise ClockError(str(e)) from e

    def wait_for_exec(self, wait_time: int, fn_to_exec: Callable[..., Any], *args, **kwargs) -> dict[str, bool]:
        """
        Timer function: wait `wait_time` seconds, then execute the function.

        Parameters:
        ----------
            wait_time (int): Seconds to wait before executing the function.
            fn_to_exec (Callable): Function to execute after waiting.

        Returns:
        ----------
            dict with 'success' (bool).

        Example:
        ----------
        >>> wait_for_exec(30, sum, 10, 5)
        """

        result: dict = {"success": False}

        try:
            time.sleep(wait_time)
            fn_to_exec(*args, **kwargs)
            result["success"] = True
            success_print(f"Function: {self.wait_for_exec.__name__} executed the function: {fn_to_exec.__name__}.")

        except Exception as e:
            result["success"] = False
            raise ClockError(
                f"Error while trying to wait to execute the function: {fn_to_exec.__name__} \nMessage: {str(e)}"
            ) from e

        return result

    def exec_and_wait(self, wait_time: int, fn_to_exec: Callable[..., Any], *args, **kwargs) -> dict[str, bool]:
        """
        Timer function: execute the function, then wait `wait_time` seconds.

        Parameters:
        ----------
            wait_time (int): Seconds to wait after executing the function.
            fn_to_exec (Callable): Function to execute before waiting.

        Returns:
        ----------
            dict with 'success' (bool).

        Example:
        ----------
        >>> exec_and_wait(30, sum, 10, 5)
        """

        result: dict = {"success": False}

        try:
            fn_to_exec(*args, **kwargs)
            time.sleep(wait_time)
            result["success"] = True
            success_print(f"Function: {self.exec_and_wait.__name__} executed the function: {fn_to_exec.__name__}.")

        except Exception as e:
            result["success"] = False
            raise ClockError(
                f"Error while trying to execute the function: {fn_to_exec.__name__} \nMessage: {str(e)}"
            ) from e

        return result
