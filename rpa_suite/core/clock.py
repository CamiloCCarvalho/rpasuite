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

    The Clock class is part of RPA Suite and can be accessed through the rpa object:
        >>> from rpa_suite import rpa
        >>> rpa.clock.exec_at_hour("14:30", my_function)

    """

    def __init__(self) -> None:
        """
        Class that provides utilities for time manipulation and stopwatch.

        This class offers functionalities for:
            - Timed function execution
            - Execution time control
            - Task scheduling

        Methods:
            exec_at_hour: Executes a function at a specific time

        The Clock class is part of RPA Suite and can be accessed through the rpa object:
            >>> from rpa_suite import rpa
            >>> rpa.clock.exec_at_hour("14:30", my_function)

        """

    def exec_at_hour(
        self,
        hour_to_exec: str | None,
        fn_to_exec: Callable[..., Any],
        *args,
        **kwargs,
    ) -> dict[str, bool]:
        """
        Timed function, executes the function at the specified time, by ``default`` it executes at runtime, optionally you can choose the time for execution.

        Parameters:
        ----------
            `hour_to_exec: 'xx:xx'` - time for function execution, if not passed the value will be by ``default`` at runtime at the time of this function call by the main code.

            ``fn_to_exec: function`` - (function) to be called by the handler, if there are parameters in this function they can be passed as next arguments in ``*args`` and ``**kwargs``

        Return:
        ----------
        >>> type:dict
            * 'tried': bool - represents if it tried to execute the function passed in the argument
            * 'success': bool - represents if there was success in trying to execute the requested function

        Example:
        ---------
        Let's execute the function ``sum`` responsible for adding the values of a and b and return x``sum(a, b) -> x`` and we want the code to wait for the specific time to be executed at ``11:00``
        >>> exec_at_hour("11:00", sum, 10, 5) -> 15 \n
            * NOTE:  `exec_at_hour` receives as first parameter the function that should be executed, then it can receive the arguments of the function, and explicitly we can define the time for execution.

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
        Timer function, wait for a value in ``seconds`` to execute the function of the argument.

        Parameters:
        ----------
            `wait_time: int` - (seconds) represents the time that should wait before executing the function passed as an argument.

            ``fn_to_exec: function`` - (function) to be called after the waiting time, if there are parameters in this function they can be passed as next arguments of this function in ``*args`` and ``**kwargs``

        Return:
        ----------
        >>> type:dict
            * 'success': bool - represents if the action was performed successfully

        Example:
        ---------
        We have a sum function in the following format ``sum(a, b) -> return x``, where ``x`` is the result of the sum. We want to wait `30 seconds` to execute this function, so:
        >>> wait_for_exec(30, sum, 10, 5) -> 15 \n
            * NOTE:  `wait_for_exec` receives as first argument the time to wait (sec), then the function `sum` and finally the arguments that the function will use.


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
        Timer function, executes a function and waits for the time in ``seconds``

        Parameters:
        ----------
            `wait_time: int` - (seconds) represents the time that should wait after executing the requested function

            ``fn_to_exec: function`` - (function) to be called before the time to wait, if there are parameters in this function they can be passed as an argument after the function, being: ``*args`` and ``**kwargs``

        Return:
        ----------
        >>> type:dict
            * 'success': bool - represents if the action was performed successfully

        Example:
        ---------
        We have a sum function in the following format ``sum(a, b) -> return x``, where ``x`` is the result of the sum. We want to execute the sum and then wait `30 seconds` to continue the main code:
        >>> wait_for_exec(30, sum, 10, 5) -> 15 \n
            * NOTE:  `wait_for_exec` receives as first argument the time to wait (sec), then the function `sum` and finally the arguments that the function will use.


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
