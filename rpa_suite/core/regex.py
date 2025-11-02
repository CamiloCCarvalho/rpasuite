# rpa_suite/core/regex.py

# imports standard
import re

# imports internal
from rpa_suite.functions._printer import success_print


class RegexError(Exception):
    """Custom exception for Regex errors."""

    def __init__(self, message):
        clean_message = message.replace("RegexError:", "").strip()
        super().__init__(f"RegexError: {clean_message}")


class Regex:
    """
    Class that provides utilities for working with regular expressions.

    This class offers functionalities for:
        - Searching for patterns in text
        - Validating strings against specific patterns

    The Regex class is part of the RPA Suite and can be used to enhance text processing capabilities.
    """

    def __init__(self) -> None:
        """
        Class that provides utilities for working with regular expressions.

        This class offers functionalities for:
            - Searching for patterns in text
            - Validating strings against specific patterns

        The Regex class is part of the RPA Suite and can be used to enhance text processing capabilities.
        """

    def check_pattern_in_text(
        self,
        origin_text: str,
        pattern_to_search: str,
        case_sensitive: bool = True,
        verbose: bool = False,
    ) -> bool:
        """
        Checks if a regex pattern exists within a given text string and returns True if found, otherwise False.

        Parameters:
        -----------
        origin_text : str
            The text where the search will be performed.

        pattern_to_search : str
            The regex pattern to search for in the text.

        case_sensitive : bool, optional
            If True, the search is case sensitive. Default: True.

        verbose : bool, optional
            If True, prints a message indicating if the pattern was found. Default: False.

        Returns:
        --------
        bool
            True if the pattern is found in the text, False otherwise.

        Example:
        --------
        >>> from rpa_suite.core.regex import Regex
        >>> r = Regex()
        >>> r.check_pattern_in_text("Hello World", "World")
        True
        >>> r.check_pattern_in_text("Hello World", "world", case_sensitive=True)
        False
        >>> r.check_pattern_in_text("Hello World", "world", case_sensitive=False)
        True
        """
        try:
            if case_sensitive:
                if re.search(pattern_to_search, origin_text):
                    if verbose:
                        success_print("Pattern found successfully!")
                    return True
                if verbose:
                    success_print("Pattern not found.")
                return False
            # Busca sem diferenciar maiúsculas/minúsculas
            if re.search(pattern_to_search, origin_text, re.IGNORECASE):
                if verbose:
                    success_print("Pattern found successfully!")
                return True
            if verbose:
                success_print("Pattern not found.")
            return False

        except Exception as e:
            raise RegexError(
                f"Error in function: {self.check_pattern_in_text.__name__} when trying to check pattern in text. Error: {str(e)}"
            ) from e
