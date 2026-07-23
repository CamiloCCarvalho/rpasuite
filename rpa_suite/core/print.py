# rpa_suite/core/print.py

# imports internal
from rpa_suite.functions._printer import (
    Colors,
)
from rpa_suite.functions._printer import alert_print as _alert_print
from rpa_suite.functions._printer import blue_print as _blue_print
from rpa_suite.functions._printer import error_print as _error_print
from rpa_suite.functions._printer import info_print as _info_print
from rpa_suite.functions._printer import magenta_print as _magenta_print
from rpa_suite.functions._printer import print_call_fn as _print_call_fn
from rpa_suite.functions._printer import print_retur_fn as _print_retur_fn
from rpa_suite.functions._printer import success_print as _success_print


class PrintError(Exception):
    """Custom exception for Print errors."""

    def __init__(self, message):
        super().__init__(f"PrintError: {message}")


class Print:
    """
    Thin OO wrapper over `rpa_suite.functions._printer`.

    Both surfaces share a single implementation to keep colors/formatting
    consistent across the library. `_printer` is the source of truth; this
    class simply exposes the same behavior as instance methods so the
    `rpa.print_*` calls stay ergonomic.

    Example:
    ----------
        >>> from rpa_suite import rpa
        >>> rpa.alert_print('Hello World')
    """

    colors: Colors = Colors

    def __init__(self) -> None:
        """Instantiate the printer facade. No state is kept."""

    def success_print(self, string_text: str, color=Colors.green, ending: str = "\n") -> None:
        """Print in green (success)."""
        _success_print(string_text, color=color, ending=ending)

    def alert_print(self, string_text: str, color=Colors.yellow, ending: str = "\n") -> None:
        """Print in yellow (alert)."""
        _alert_print(string_text, color=color, ending=ending)

    def info_print(self, string_text: str, color=Colors.cyan, ending: str = "\n") -> None:
        """Print in cyan (informational)."""
        _info_print(string_text, color=color, ending=ending)

    def error_print(self, string_text: str, color=Colors.red, ending: str = "\n") -> None:
        """Print in red (error)."""
        _error_print(string_text, color=color, ending=ending)

    def magenta_print(self, string_text: str, color=Colors.magenta, ending: str = "\n") -> None:
        """Print in magenta."""
        _magenta_print(string_text, color=color, ending=ending)

    def blue_print(self, string_text: str, color=Colors.blue, ending: str = "\n") -> None:
        """Print in blue."""
        _blue_print(string_text, color=color, ending=ending)

    def print_call_fn(self, string_text: str, color=Colors.call_fn, ending: str = "\n") -> None:
        """Print in light magenta (used for logging function calls)."""
        _print_call_fn(string_text, color=color, ending=ending)

    def print_retur_fn(self, string_text: str, color=Colors.retur_fn, ending: str = "\n") -> None:
        """Print in light yellow (used for logging function returns)."""
        _print_retur_fn(string_text, color=color, ending=ending)
