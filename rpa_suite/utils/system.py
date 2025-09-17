# rpa_suite/utils/system.py

# imports third-party
import sys
import os
import ctypes

# imports internal
from rpa_suite.functions._printer import error_print, success_print

class UtilsError(Exception):
    """Custom exception for Utils errors."""
    def __init__(self, message):
        super().__init__(f'UtilsError: {message}')

class Utils:
    """
    Utility class for system configuration and directory management.

    Provides methods for manipulating import paths and system configurations.
    """

    def __init__(self):
        """
        Initializes the Utils class.

        Does not require specific initialization parameters.
        """
        try:
            pass
        except Exception as e:
            UtilsError(f"Error during Utils class initialization: {str(e)}.")

    def set_importable_dir(self, display_message: bool = False) -> None:
        """
        Configures the current directory as importable by adding it to the system path.

        Adds the parent directory of the current module to sys.path, allowing
        dynamic imports of local modules.

        Parameters:
        ----------
        display_message : bool, optional
            If True, displays a success message after setting the directory.
            Default is False.

        Returns:
        --------
        None

        Exceptions:
        -----------
        Captures and logs any errors during the configuration process.
        """

        try:
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            if display_message:
                success_print("Directory successfully configured for import!")

        except Exception as e:
            UtilsError(f"Error configuring importable directory: {str(e)}.")


class KeepSessionActive:
    """
    Advanced context manager to prevent screen lock on Windows.

    Uses Windows API calls to keep the system active during
    critical task execution, preventing suspension or screen lock.

    Class Attributes:
    ----------------
    ES_CONTINUOUS : int
        Flag to maintain the current system execution state.
    ES_SYSTEM_REQUIRED : int
        Flag to prevent system suspension.
    ES_DISPLAY_REQUIRED : int
        Flag to keep the display active.

    Usage Example:
    -------------
    with KeepSessionActive():
        # Code that requires the system to remain active
        perform_long_task()
    """

    def __init__(self) -> None:
        """
        Initializes system execution state settings.

        Configures Windows-specific constants for power control
        and operating system state management.
        """
        try:
            self.ES_CONTINUOUS = 0x80000000
            self.ES_SYSTEM_REQUIRED = 0x00000001
            self.ES_DISPLAY_REQUIRED = 0x00000002
        except Exception as e:
            UtilsError(f"Error initializing KeepSessionActive: {str(e)}.")

    def __enter__(self) -> None:
        """
        Configures execution state to prevent screen lock.

        Uses Windows API call to keep system and display active
        during code block execution.

        Returns:
        --------
        KeepSessionActive
            The context manager instance itself.

        Exceptions:
        -----------
        Captures and logs any errors during state configuration.
        """
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(
                self.ES_CONTINUOUS | self.ES_SYSTEM_REQUIRED | self.ES_DISPLAY_REQUIRED
            )
            return self
        except Exception as e:
            UtilsError(f"Error configuring execution state: {str(e)}.")

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Restores default system power settings.

        Method called automatically when exiting the context block,
        reverting execution state settings to default.

        Parameters:
        ----------
        exc_type : type, optional
            Type of exception that may have occurred.
        exc_val : Exception, optional
            Value of exception that may have occurred.
        exc_tb : traceback, optional
            Traceback of exception that may have occurred.

        Exceptions:
        -----------
        Captures and logs any errors during state restoration.
        """
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(self.ES_CONTINUOUS)
        except Exception as e:
            UtilsError(f"Error restoring execution state: {str(e)}.")


class Tools(Utils):
    """
    Utility class for system configuration and directory management.

    Provides methods for manipulating import paths and system configurations.
    """

    keep_session_active: KeepSessionActive = KeepSessionActive
