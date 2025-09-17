# rpa_suite/core/regex.py

# imports standard
import re

# imports internal
from rpa_suite.functions._printer import success_print

class RegexError(Exception):
    """Custom exception for Regex errors."""
    def __init__(self, message):
        super().__init__(f'Regex Error: {message}')

class Regex:
    """
    Class that provides utilities for working with regular expressions.

    This class offers functionalities for:
        - Searching for patterns in text
        - Validating strings against specific patterns

    The Regex class is part of the RPA Suite and can be used to enhance text processing capabilities.
    """

    def __init__(self) -> None:
        """Initialize the Regex class."""
        pass

    def check_pattern_in_text(
        self,
        origin_text: str,
        pattern_to_search: str,
        case_sensitive: bool = True,
        display_message: bool = False,
    ) -> bool:
        """
        Function responsible for searching for a pattern in a text string and returning True if the pattern is found, otherwise False.

        Parameters:
        -----------
        ``origin_text: str``
            The text where the search should be performed.

        ``pattern_to_search: str``
            The regex pattern to search for in the text.

        ``case_sensitive: bool``
            Whether the search should be case sensitive. Default is True.

        ``display_message: bool``
            Whether to display success/failure messages. Default is False.

        Return:
        ----------
        A boolean indicating whether the pattern was found in the text.
        """

        try:

            if case_sensitive:

                # Check if the pattern is found in the text
                if re.search(pattern_to_search, origin_text):
                    if display_message:
                        success_print(f"Pattern found successfully!")
                    return True

                else:
                    if display_message:
                        success_print(f"Pattern not found.")
                    return False
            else:

                # normalize text to search without case sensitive
                origin_text = origin_text.lower()
                pattern_to_search = pattern_to_search.lower()

                # Check if the pattern is found in the text
                if re.search(pattern_to_search, origin_text):
                    if display_message:
                        success_print(f"Pattern found successfully!")
                    return True

                else:
                    if display_message:
                        success_print(f"Pattern not found.")
                    return False

        except Exception as e:
            RegexError(
                f"Error in function: {self.check_pattern_in_text.__name__} when trying to check pattern in text. Error: {str(e)}"
            ) from e
