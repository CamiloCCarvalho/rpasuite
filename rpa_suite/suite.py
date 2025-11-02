# rpa_suite/suite.py

# imports internal
import hashlib

# imports third-party
import subprocess
import sys
from importlib.metadata import version
from typing import TYPE_CHECKING, Optional

# imports external
from colorama import Fore

from .core.asyncrun import AsyncRunner
from .core.clock import Clock
from .core.database import Database
from .core.date import Date
from .core.dir import Directory
from .core.email import Email
from .core.file import File
from .core.log import Log
from .core.parallel import ParallelRunner
from .core.print import Print
from .core.regex import Regex
from .core.validate import Validate

if TYPE_CHECKING:
    from .core.artemis import Artemis
    from .core.browser import Browser
    from .core.iris import Iris


class SuiteError(Exception):
    """Custom exception for Suite errors."""

    def __init__(self, message):
        super().__init__(f"SuiteError: {message}")


# Windows bash colors
class Colors:  # pylint: disable=duplicate-code
    """
    This class provides color constants based on the colorama library,
    allowing for visual formatting of texts in the Windows terminal.

    Attributes:
        black (str): Black color
        blue (str): Blue color
        green (str): Green color
        cyan (str): Cyan color
        red (str): Red color
        magenta (str): Magenta color
        yellow (str): Yellow color
        white (str): White color
        default (str): Default color (white)
        call_fn (str): Light magenta color (used for function calls)
        retur_fn (str): Light yellow color (used for function returns)
    """

    black = f"{Fore.BLACK}"
    blue = f"{Fore.BLUE}"
    green = f"{Fore.GREEN}"
    cyan = f"{Fore.CYAN}"
    red = f"{Fore.RED}"
    magenta = f"{Fore.MAGENTA}"
    yellow = f"{Fore.YELLOW}"
    white = f"{Fore.WHITE}"
    default = f"{Fore.WHITE}"
    call_fn = f"{Fore.LIGHTMAGENTA_EX}"
    retur_fn = f"{Fore.LIGHTYELLOW_EX}"


class Suite:
    """
    RPA Suite is a Python module that provides a set of tools for process automation.

    To use the module, import it as follows:
        >>> from rpa_suite import rpa

    Example of usage:
        >>> from rpa_suite import rpa
        >>> rpa.email.send_smtp(
        ...     email_user="your@email.com",
        ...     email_password="123",
        ...     email_to="destination@email.com",
        ...     subject_title="Test",
        ...     body_message="<p>Test message</p>"
        ... )
        >>> rpa.alert_print("Hello World")

    Available modules:
        ``clock``: Utilities for time and stopwatch manipulation
        ``date``: Functions for date manipulation
        ``email``: Functionalities for sending emails via SMTP
        ``directory``: Operations with directories
        ``file``: File manipulation
        ``log``: Logging system
        ``printer``: Functions for formatted output
        ``regex``: Operations with regular expressions
        ``validate``: Data validation functions
        ``ParallelRunner``: Object ParallelRunner functions to run in parallel
        ``AsyncRunner``: Object AsyncRunner functions to run asynchronously
        ``Browser``: Object Browser automation functions (requires Selenium and Webdriver_Manager)
        ``Iris``: Object Iris automation functions to convert documents with OCR + AI based on ``docling``
        ``Artemis``: Object Artemis automation functions for desktop automation similar to Botcity with ``pyautogui``
        ``database``: Database module for execution tracking and management with multi-database support
    """

    # VARIABLES INTERNAL
    try:
        # old: __version__ = pkg_resources.get_distribution("rpa_suite").version

        __version__ = version("package_name")

    except Exception:
        __version__ = "unknown"

    __id_hash__ = "rpa_suite"

    def __init__(self):
        # Initialize instance hash
        self.__id_hash__ = "rpa_suite"
        self.__id_hash__ = hashlib.sha256(self.__version__.encode()).hexdigest()

        # SUBMODULES - Object instances
        self.clock: type[Clock] = Clock()
        self.date: type[Date] = Date()
        self.email: type[Email] = Email()
        self.directory: type[Directory] = Directory()
        self.file: type[File] = File()
        self.log: type[Log] = Log()
        self.printer: type[Print] = Print()
        self.regex: type[Regex] = Regex()
        self.validate: type[Validate] = Validate()

        # Classes that are not instantiated
        self.parallel: type[ParallelRunner] = ParallelRunner
        self.asyn: type[AsyncRunner] = AsyncRunner

        # Conditional import for optional modules
        import importlib.util  # pylint: disable=import-outside-toplevel

        # Browser - conditional import
        if importlib.util.find_spec("selenium") and importlib.util.find_spec("webdriver_manager"):
            from .core.browser import Browser  # pylint: disable=import-outside-toplevel

            self.browser: type[Browser] = Browser
        else:
            self.browser: Optional[type["Browser"]] = None

        # Iris - conditional import
        if importlib.util.find_spec("docling"):
            from .core.iris import Iris  # pylint: disable=import-outside-toplevel

            self.iris: type[Iris] = Iris
        else:
            self.iris: Optional[type["Iris"]] = None

        # Artemis - conditional import
        if importlib.util.find_spec("pyautogui"):
            from .core.artemis import Artemis  # pylint: disable=import-outside-toplevel

            self.artemis: type[Artemis] = Artemis
        else:
            self.artemis: Optional[type["Artemis"]] = None

        # Database - Database class (not instance, following type[Object] pattern)
        # Check if any database library is available
        if (
            importlib.util.find_spec("sqlite3")
            or importlib.util.find_spec("psycopg2")
            or importlib.util.find_spec("pymysql")
        ):
            self.database: type[Database] = Database
        else:
            self.database: Optional[type[Database]] = None

    # pylint: disable=duplicate-code
    def success_print(self, string_text: str, color=Colors.green, ending="\n") -> None:
        """
        Print that indicates ``SUCCESS``. Customized with the color Green.

        Returns:
        --------
            None
        """

        print(f"{color}{string_text}{Colors.default}", end=ending)

    # pylint: disable=duplicate-code
    def alert_print(self, string_text: str, color=Colors.yellow, ending="\n") -> None:
        """
        Print that indicates ``ALERT``. Customized with the color Yellow.

        Returns:
        --------
            None
        """
        print(f"{color}{string_text}{Colors.default}", end=ending)

    # pylint: disable=duplicate-code
    def info_print(self, string_text: str, color=Colors.cyan, ending="\n") -> None:
        """
        Print that indicates ``INFORMATION``. Customized with the color Cyan.

        Returns:
        --------
            None
        """
        print(f"{color}{string_text}{Colors.default}", end=ending)

    # pylint: disable=duplicate-code
    def error_print(self, string_text: str, color=Colors.red, ending="\n") -> None:
        """
        Print that indicates ``ERROR``. Customized with the color Red.

        Returns:
        --------
            None
        """
        print(f"{color}{string_text}{Colors.default}", end=ending)

    # pylint: disable=duplicate-code
    def magenta_print(self, string_text: str, color=Colors.magenta, ending="\n") -> None:
        """
        Print customized with the color Magenta.

        Returns:
        --------
            None
        """
        print(f"{color}{string_text}{Colors.default}", end=ending)

    # pylint: disable=duplicate-code
    def blue_print(self, string_text: str, color=Colors.blue, ending="\n") -> None:
        """
        Print customized with the color Blue.

        Returns:
        --------
            None
        """
        print(f"{color}{string_text}{Colors.default}", end=ending)

    # pylint: disable=duplicate-code
    def print_call_fn(self, string_text: str, color=Colors.call_fn, ending="\n") -> None:
        """
        Print customized for function called (log).
        Color: Magenta Light

        Returns:
        --------
            None
        """
        print(f"{color}{string_text}{Colors.default}", end=ending)

    # pylint: disable=duplicate-code
    def print_retur_fn(self, string_text: str, color=Colors.retur_fn, ending="\n") -> None:
        """
        Print customized for function return (log).
        Color: Yellow Light

        Returns:
        --------
            None
        """
        print(f"{color}{string_text}{Colors.default}", end=ending)

    def __install_all_libs(self):  # pylint: disable=unused-private-member
        """
        Method responsible for installing all libraries for advanced use of RPA-Suite,
        including all features such as OCR and AI agent.
        """

        libs = [
            "colorama",
            "colorlog",
            "email_validator",
            "loguru",
            "pyautogui",
            "selenium",
            "typing",
            "webdriver_manager",
            "docling",
            "sqlite3",
        ]

        for lib in libs:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                self.success_print(f"Suite RPA: Library {lib} installed successfully!")

            except subprocess.CalledProcessError:
                self.error_print(f"Suite RPA: Error installing library {lib}")


rpa = Suite()
