# rpa_suite/core/clock.py

# imports standard
import time
from datetime import datetime as dt
from typing import Any, Callable

# imports internal
from rpa_suite.functions._printer import success_print


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
        wait_for_exec: Waits for a specified time before executing a function
        exec_and_wait: Executes a function and then waits for a specified time

    The Clock class is part of RPA Suite and can be accessed through the rpa object:
        >>> from rpa_suite import rpa
        >>> rpa.clock.exec_at_hour("14:30", my_function)
    """

    def __init__(self) -> None:
        """Initialize the Clock class."""

    def exec_at_hour(
        self,
        hour_to_exec: str | None,
        fn_to_exec: Callable[..., Any],
        *args,
        **kwargs,
    ) -> dict[str, bool]:
        """
        Timed function that executes the function at the specified time. By default, it executes at runtime.
        Optionally you can choose the time for execution.

        Parameters:
        -----------
        hour_to_exec : str | None
            Time for function execution in format 'HH:MM'. If None, the function executes immediately.

        fn_to_exec : Callable
            Function to be called by the handler. If there are parameters in this function,
            they can be passed as next arguments in ``*args`` and ``**kwargs``.

        *args : Any
            Positional arguments to pass to the function.

        **kwargs : Any
            Keyword arguments to pass to the function.

        Returns:
        --------
        dict[str, bool]
            Dictionary with:
            - 'tried' (bool): Indicates if it tried to execute the function passed in the argument
            - 'success' (bool): Indicates if there was success in trying to execute the requested function

        Example:
        --------
        Execute the function ``sum`` that adds values a and b at 11:00:
        >>> result = exec_at_hour("11:00", sum, 10, 5)
        >>> # Will wait until 11:00 and then execute sum(10, 5) -> 15
        """

        # Local Variables
        result: dict = {"tried": bool, "successs": bool}
        run: bool
        now: dt
        hours: str
        minutes: str
        moment_now: str

        try:
            # Preprocessing
            run = True
            now = dt.now()
            hours = str(now.hour) if now.hour >= 10 else f"0{now.hour}"
            minutes = str(now.minute) if now.minute >= 10 else f"0{now.minute}"
            moment_now = f"{hours}:{minutes}"

            if hour_to_exec is None:

                # Process
                while run:
                    try:
                        fn_to_exec(*args, **kwargs)
                        run = False
                        result["tried"] = not run
                        result["success"] = True
                        success_print(f"{fn_to_exec.__name__}: Successfully executed!")
                        break

                    except Exception:
                        run = False
                        result["tried"] = not run
                        result["success"] = False
                        break
            else:
                # Executes the function call only at the time provided in the argument.
                while run:
                    if moment_now == hour_to_exec:
                        try:
                            fn_to_exec(*args, **kwargs)
                            run = False
                            result["tried"] = not run
                            result["success"] = True
                            success_print(f"{fn_to_exec.__name__}: Successfully executed!")
                            break

                        except Exception as e:
                            run = False
                            result["tried"] = not run
                            result["success"] = False
                            raise ClockError(
                                f"An error occurred that prevented the function from executing: {fn_to_exec.__name__} correctly. Error: {str(e)}"
                            ) from e
                    else:
                        time.sleep(30)
                        now = dt.now()
                        hours = str(now.hour) if now.hour >= 10 else f"0{now.hour}"
                        minutes = str(now.minute) if now.minute >= 10 else f"0{now.minute}"
                        moment_now = f"{hours}:{minutes}"

            return result

        except Exception as e:
            result["success"] = False
            raise ClockError(str(e)) from e

    def wait_for_exec(self, wait_time: int, fn_to_exec: Callable[..., Any], *args, **kwargs) -> dict[str, bool]:
        """
        Timer function that waits for a specified number of seconds before executing the function.

        Parameters:
        -----------
        wait_time : int
            Time in seconds to wait before executing the function.

        fn_to_exec : Callable
            Function to be called after the waiting time. If there are parameters in this function,
            they can be passed as next arguments in ``*args`` and ``**kwargs``.

        *args : Any
            Positional arguments to pass to the function.

        **kwargs : Any
            Keyword arguments to pass to the function.

        Returns:
        --------
        dict[str, bool]
            Dictionary with:
            - 'success' (bool): Indicates if the action was performed successfully

        Example:
        --------
        Wait 30 seconds before executing the sum function:
        >>> result = wait_for_exec(30, sum, 10, 5)
        >>> # Will wait 30 seconds and then execute sum(10, 5) -> 15
        """

        # Local Variables
        result: dict = {"success": bool}

        # Process
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
        Timer function that executes a function and then waits for a specified number of seconds.

        Parameters:
        -----------
        wait_time : int
            Time in seconds to wait after executing the requested function.

        fn_to_exec : Callable
            Function to be called before waiting. If there are parameters in this function,
            they can be passed as arguments in ``*args`` and ``**kwargs``.

        *args : Any
            Positional arguments to pass to the function.

        **kwargs : Any
            Keyword arguments to pass to the function.

        Returns:
        --------
        dict[str, bool]
            Dictionary with:
            - 'success' (bool): Indicates if the action was performed successfully

        Example:
        --------
        Execute the sum function and then wait 30 seconds:
        >>> result = exec_and_wait(30, sum, 10, 5)
        >>> # Will execute sum(10, 5) -> 15, then wait 30 seconds before continuing
        """

        # Local Variables
        result: dict = {"success": bool}

        # Process
        try:
            fn_to_exec(*args, **kwargs)
            time.sleep(wait_time)
            result["success"] = True
            success_print(f"Function: {self.wait_for_exec.__name__} executed the function: {fn_to_exec.__name__}.")

        except Exception as e:
            result["success"] = False
            raise ClockError(
                f"Error while trying to wait to execute the function: {fn_to_exec.__name__} \nMessage: {str(e)}"
            ) from e

        return result
