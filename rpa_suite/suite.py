# rpa_suite/suite.py

# imports internal
import hashlib

# imports third-party
import importlib.util
import subprocess
import sys
from importlib.metadata import version
from typing import TYPE_CHECKING, Optional

# imports external
from colorama import Fore  # noqa: F401 — mantido para compatibilidade histórica

from .core.asyncrun import AsyncRunner
from .core.clock import Clock
from .core.database import Database
from .core.date import Date
from .core.dir import Directory
from .core.email import Email
from .core.file import File
from .core.log import Log
from .core.notify import Notifier
from .core.parallel import ParallelRunner
from .core.print import Print
from .core.regex import Regex
from .core.retry import RetryError, retry
from .core.validate import Validate
from .utils.system import Utils

if TYPE_CHECKING:
    from .core.artemis import Artemis
    from .core.browser import Browser
    from .core.iris import Iris


class SuiteError(Exception):
    """Custom exception for Suite errors."""

    def __init__(self, message):
        super().__init__(f"SuiteError: {message}")


# Windows bash colors — reexport de Print para compatibilidade
Colors = Print.colors  # type: ignore[attr-defined]


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
        ``AsyncRunner``: Object AsyncRunner functions to run in Assyncronous
        ``Browser``: Object Browser automation functions (neeeds Selenium and Webdriver_Manager)
        ``Iris``: Object Iris automation functions to convert documents with OCR + IA based on ``docling``
        ``Artemis``: Object Artemis automation functions to desktopbot similar Botcity with ``pyautogui``
        ``database``: Class Database for RPA execution tracking (SQLite/PostgreSQL/MySQL).
            Use ``from rpa_suite.core import Database, DatabaseType`` for the enum.
        ``utils``: Utility class for system configuration

    """

    # VARIABLES INTERNAL
    try:
        # old: __version__ = pkg_resources.get_distribution("rpa_suite").version

        __version__ = version("rpa_suite")

    except Exception:
        __version__ = "unknown"

    __id_hash__ = "rpa_suite"

    def __init__(self):
        # Inicializa o hash da instância
        self.__id_hash__ = "rpa_suite"
        self.__id_hash__ = hashlib.sha256(self.__version__.encode()).hexdigest()

        # SUBMODULES - Instâncias de objetos
        self.clock: Clock = Clock()
        self.date: Date = Date()
        self.email: Email = Email()
        self.directory: Directory = Directory()
        self.file: File = File()
        self.log: Log = Log()
        self.printer: Print = Print()
        self.regex: Regex = Regex()
        self.validate: Validate = Validate()
        self.notifier: Notifier = Notifier()
        self.utils: Utils = Utils()

        # Classes que não são instanciadas
        self.parallel: type[ParallelRunner] = ParallelRunner
        self.asyn: type[AsyncRunner] = AsyncRunner
        self.database: type[Database] = Database

        # Retry decorator (exposed as a callable on the suite)
        self.retry = retry
        self.RetryError = RetryError

        # Dashboard helpers (Flask is an optional dep; import lazily)
        if importlib.util.find_spec("flask"):
            from .core.dashboard import create_app, run_dashboard  # pylint: disable=import-outside-toplevel

            self.dashboard_create_app = create_app
            self.dashboard_run = run_dashboard
        else:
            self.dashboard_create_app = None
            self.dashboard_run = None

        # Browser - importação condicional
        if importlib.util.find_spec("selenium") and importlib.util.find_spec("webdriver_manager"):
            from .core.browser import Browser  # pylint: disable=import-outside-toplevel

            self.browser: type[Browser] = Browser
        else:
            self.browser: Optional[type["Browser"]] = None

        # Iris - importação condicional
        if importlib.util.find_spec("docling"):
            from .core.iris import Iris  # pylint: disable=import-outside-toplevel

            self.iris: type[Iris] = Iris
        else:
            self.iris: Optional[type["Iris"]] = None

        # Artemis - importação condicional
        if importlib.util.find_spec("pyautogui"):
            from .core.artemis import Artemis  # pylint: disable=import-outside-toplevel

            self.artemis: type[Artemis] = Artemis
        else:
            self.artemis: Optional[type["Artemis"]] = None

    def success_print(self, string_text: str, color=Colors.green, ending="\n") -> None:
        """Print a SUCCESS message (delegates to ``printer``)."""
        self.printer.success_print(string_text, color=color, ending=ending)

    def alert_print(self, string_text: str, color=Colors.yellow, ending="\n") -> None:
        """Print an ALERT message (delegates to ``printer``)."""
        self.printer.alert_print(string_text, color=color, ending=ending)

    def info_print(self, string_text: str, color=Colors.cyan, ending="\n") -> None:
        """Print an INFO message (delegates to ``printer``)."""
        self.printer.info_print(string_text, color=color, ending=ending)

    def error_print(self, string_text: str, color=Colors.red, ending="\n") -> None:
        """Print an ERROR message (delegates to ``printer``)."""
        self.printer.error_print(string_text, color=color, ending=ending)

    def magenta_print(self, string_text: str, color=Colors.magenta, ending="\n") -> None:
        """Print a custom Magenta message (delegates to ``printer``)."""
        self.printer.magenta_print(string_text, color=color, ending=ending)

    def blue_print(self, string_text: str, color=Colors.blue, ending="\n") -> None:
        """Print a custom Blue message (delegates to ``printer``)."""
        self.printer.blue_print(string_text, color=color, ending=ending)

    def print_call_fn(self, string_text: str, color=Colors.call_fn, ending="\n") -> None:
        """Print a function-call log message (delegates to ``printer``)."""
        self.printer.print_call_fn(string_text, color=color, ending=ending)

    def print_retur_fn(self, string_text: str, color=Colors.retur_fn, ending="\n") -> None:
        """Print a function-return log message (delegates to ``printer``)."""
        self.printer.print_retur_fn(string_text, color=color, ending=ending)

    def __install_all_libs(self):  # pylint: disable=unused-private-member
        """
        Install all libraries required for advanced RPA-Suite usage,
        including OCR and AI agent features.
        """

        libs = [
            "setuptools",
            "wheel",
            "pyperclip",
            "pywin32",
            "colorama",
            "colorlog",
            "email_validator",
            "loguru",
            "openpyxl",
            "pandas",
            "pyautogui",
            "selenium",
            "typing",
            "webdriver_manager",
            "docling",
        ]

        for lib in libs:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                self.success_print(f"Suite RPA: Library {lib} installed successfully!")

            except subprocess.CalledProcessError:
                self.error_print(f"Suite RPA: Error installing library {lib}")


rpa = Suite()
