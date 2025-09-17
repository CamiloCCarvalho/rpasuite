# rpa_suite/core/parallel.py

# imports standard
from multiprocessing import Process, Manager
from typing import Any, Callable, Dict, Optional, TypeVar, Generic
import time
import traceback

from rpa_suite.functions._printer import error_print, alert_print, success_print

# Define a generic type for the function return
T = TypeVar("T")

class ParallelRunnerError(Exception):
    """Custom exception for ParallelRunner errors."""
    def __init__(self, message):
        clean_message = message.replace("ParallelRunner Error:", "").strip()
        super().__init__(f'ParallelRunner Error: {clean_message}')

class ParallelRunner(Generic[T]):
    """
    Class to execute functions in parallel while maintaining the main application flow.

    Allows starting a function in a separate process and retrieving its result later.
    """

    display_message = None

    def __init__(self, display_message: bool = False) -> None:
        """
        Initializes the ParallelRunner.

        Args:
            display_message (bool): If True, displays debug messages during execution.
        """
        try:
            self._manager = Manager()
            self._result_dict = self._manager.dict()
            self._process = None
            self._start_time = None
            self.display_message = display_message
            
            if self.display_message:
                success_print("ParallelRunner initialized successfully")
                
        except Exception as e:
            raise ParallelRunnerError(f"Error initializing ParallelRunner: {str(e)}") from e

    @staticmethod
    def _execute_function(function, args, kwargs, result_dict):
        """
        Static method that executes the target function and stores the result.
        This function needs to be defined at the module level to be "picklable".
        """
        try:
            # Execute the user function with the provided arguments
            result = function(*args, **kwargs)

            # Store the result in the shared dictionary
            result_dict["status"] = "success"
            result_dict["result"] = result

        except Exception as e:
            # In case of error, store information about the error
            result_dict["status"] = "error"
            result_dict["error"] = str(e)
            result_dict["traceback"] = traceback.format_exc()

            # For debug
            error_print(f"[Child Process] Error occurred: {str(e)}")

    @staticmethod
    def _execute_function_w_disp_msg(function, args, kwargs, result_dict):
        """
        Static method that executes the target function and stores the result.
        This function needs to be defined at the module level to be "picklable".
        """
        try:
            # Execute the user function with the provided arguments
            result = function(*args, **kwargs)

            # Store the result in the shared dictionary
            result_dict["status"] = "success"
            result_dict["result"] = result

            # For debug
            success_print(f"[Child Process] Result calculated: {result}")
            success_print(f"[Child Process] Result dictionary: {dict(result_dict)}")

        except Exception as e:
            # In case of error, store information about the error
            result_dict["status"] = "error"
            result_dict["error"] = str(e)
            result_dict["traceback"] = traceback.format_exc()

            # For debug
            error_print(f"[Child Process] Error occurred: {str(e)}")

    def run(self, function: Callable[..., T], *args, **kwargs) -> "ParallelRunner[T]":
        """
        Starts the execution of the function in a parallel process.

        Args:
            function: Function to be executed in parallel
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            self: Returns the instance itself to allow chained calls
        """
        try:
            # Clear previous result, if any
            if self._result_dict:
                self._result_dict.clear()

            # Configure initial values in the shared dictionary
            self._result_dict["status"] = "running"

            # Start the process with the static helper function
            if self.display_message:
                self._process = Process(
                    target=ParallelRunner._execute_function_w_disp_msg,
                    args=(function, args, kwargs, self._result_dict),
                )
            else:
                self._process = Process(
                    target=ParallelRunner._execute_function,
                    args=(function, args, kwargs, self._result_dict),
                )

            self._process.daemon = True  # Child process terminates when main terminates
            self._process.start()
            self._start_time = time.time()

            if self.display_message:
                success_print(f"Parallel process started successfully")

            return self
            
        except Exception as e:
            raise ParallelRunnerError(f"Error starting parallel process: {str(e)}") from e

    def is_running(self) -> bool:
        """
        Checks if the process is still running.

        Returns:
            bool: True if the process is still running, False otherwise
        """
        try:
            if self._process is None:
                return False
            return self._process.is_alive()
        except Exception as e:
            if self.display_message:
                error_print(f"Error checking process status: {str(e)}")
            return False

    def get_result(self, timeout: Optional[float] = 60, terminate_on_timeout: bool = True) -> Dict[str, Any]:
        """
        Retrieves the result of the parallel execution.

        Args:
            timeout: Maximum time (in seconds) to wait for the process to finish.
            None means wait indefinitely.
            terminate_on_timeout: If True, terminates the process if the timeout is reached.

        Returns:
            Dict containing:
            - success: bool indicating if the operation was successful.
            - result: result of the function (if successful).
            - error: error message (if any).
            - traceback: full stack trace (if an error occurred).
            - execution_time: execution time in seconds.
            - terminated: True if the process was terminated due to timeout.
        """
        try:
            if self._process is None:
                return {
                    "success": False,
                    "error": "No process was started",
                    "execution_time": 0,
                    "terminated": False,
                }

            # Wait for the process to finish with timeout
            self._process.join(timeout=timeout)
            execution_time = time.time() - self._start_time

            # Prepare the response dictionary
            result = {"execution_time": execution_time, "terminated": False}

            # Debug - show the shared dictionary
            if self.display_message:
                success_print(f"[Main Process] Shared dictionary: {dict(self._result_dict)}")

            # Check if the process finished or reached timeout
            if self._process.is_alive():
                if terminate_on_timeout:
                    try:
                        self._process.terminate()
                        self._process.join(timeout=1)  # Small timeout to ensure process terminates
                        result["terminated"] = True
                        result["success"] = False
                        result["error"] = f"Operation cancelled due to timeout after {execution_time:.2f} seconds"
                        
                        if self.display_message:
                            alert_print(f"Process terminated due to timeout")
                            
                    except Exception as e:
                        result["success"] = False
                        result["error"] = f"Error terminating process: {str(e)}"
                        if self.display_message:
                            error_print(f"Error terminating process: {str(e)}")
                else:
                    result["success"] = False
                    result["error"] = f"Operation still running after {execution_time:.2f} seconds"
            else:
                # Process finished normally - check the status
                try:
                    status = self._result_dict.get("status", "unknown")

                    if status == "success":
                        result["success"] = True
                        # Ensure the result is being copied correctly
                        if "result" in self._result_dict:
                            result["result"] = self._result_dict["result"]
                            if self.display_message:
                                success_print("Result retrieved successfully")
                        else:
                            result["success"] = False
                            result["error"] = "Result not found in shared dictionary"
                            if self.display_message:
                                error_print("Result not found in shared dictionary")
                    else:
                        result["success"] = False
                        result["error"] = self._result_dict.get("error", "Unknown error")
                        if "traceback" in self._result_dict:
                            result["traceback"] = self._result_dict["traceback"]
                        if self.display_message:
                            error_print(f"Process failed with error: {result['error']}")
                            
                except Exception as e:
                    result["success"] = False
                    result["error"] = f"Error retrieving result from shared dictionary: {str(e)}"
                    if self.display_message:
                        error_print(f"Error retrieving result: {str(e)}")

            # Finalize the Manager if the process finished and we're no longer waiting for result
            if not self._process.is_alive() and (result.get("success", False) or result.get("terminated", False)):
                self._cleanup()

            return result
            
        except Exception as e:
            error_message = f"Error getting result from parallel process: {str(e)}"
            if self.display_message:
                error_print(error_message)
            return {
                "success": False,
                "error": error_message,
                "execution_time": 0,
                "terminated": False,
            }

    def terminate(self) -> None:
        """
        Terminates the running process.
        """
        try:
            if self._process and self._process.is_alive():
                self._process.terminate()
                self._process.join(timeout=1)
                self._cleanup()
                
                if self.display_message:
                    success_print("Process terminated successfully")
                    
        except Exception as e:
            if self.display_message:
                error_print(f"Error terminating process: {str(e)}")

    def _cleanup(self) -> None:
        """
        Cleans up resources used by the process.
        """
        try:
            if hasattr(self, "_manager") and self._manager is not None:
                try:
                    self._manager.shutdown()
                except Exception as e:
                    if self.display_message:
                        error_print(f"Error shutting down manager: {str(e)}")
                self._manager = None
            self._process = None
            
            if self.display_message:
                success_print("Resources cleaned up successfully")
                
        except Exception as e:
            if self.display_message:
                error_print(f"Error during cleanup: {str(e)}")

    def __del__(self):
        """
        Destructor of the class, ensures resources are released.
        """
        try:
            self.terminate()
        except Exception:
            # Silently handle any errors during destruction
            pass
