# rpa_suite/core/mail_validator.py

# imports third party
import email_validator

# imports internal
from rpa_suite.functions._printer import success_print


class ValidateError(Exception):
    """Custom exception for Validate errors."""

    def __init__(self, message):
        clean_message = message.replace("ValidateError:", "").strip()
        super().__init__(f"ValidateError: {clean_message}")


class Validate:
    """
    Class responsible for validating email addresses and searching for words within text.

    This class offers functionalities to:
        - Validate a list of emails, checking if each one complies with email formatting standards.
        - Search for specific words or patterns within a given text, providing information about their occurrences.
        - Return a dictionary with information about the validity of the emails, including lists of valid and invalid emails, as well as counts for each category.

    The class uses the email_validator library to perform rigorous validation of email addresses, ensuring that the provided data is correct and ready for use in applications that require email communication. Additionally, it provides methods for searching words in text, enhancing its utility for text processing.
    """

    def __init__(self) -> None:
        """
        Class responsible for validating email addresses and searching for words within text.

        This class offers functionalities to:
            - Validate a list of emails, checking if each one complies with email formatting standards.
            - Search for specific words or patterns within a given text, providing information about their occurrences.
            - Return a dictionary with information about the validity of the emails, including lists of valid and invalid emails, as well as counts for each category.

        The class uses the email_validator library to perform rigorous validation of email addresses, ensuring that the provided data is correct and ready for use in applications that require email communication. Additionally, it provides methods for searching words in text, enhancing its utility for text processing.
        """

    def emails(self, email_list: list[str], verbose: bool = False) -> dict:
        """
        Validates a list of emails using the email_validator library.

        Parameters:
        -----------
        email_list : list[str]
            A list of strings containing the emails to be validated.

        verbose : bool, optional
            If True, prints a success message after execution. Default: False.

        Returns:
        --------
        dict
            Dictionary with the following keys:
            - 'success' (bool): True if all emails are valid, False otherwise
            - 'valid_emails' (list): List of valid emails
            - 'invalid_emails' (list): List of invalid emails
            - 'qt_valids' (int): Number of valid emails
            - 'qt_invalids' (int): Number of invalid emails
            - 'map_validation' (list): Validation result for each email

        Example:
        --------
        >>> from rpa_suite.core.validate import Validate
        >>> v = Validate()
        >>> v.emails(['test@example.com', 'invalid-email'])
        {
            'success': False,
            'valid_emails': ['test@example.com'],
            'invalid_emails': ['invalid-email'],
            'qt_valids': 1,
            'qt_invalids': 1,
            'map_validation': [<ValidationResult object>, ...]
        }
        """

        # Local Variables
        result: dict = {
            "success": bool,
            "valid_emails": list,
            "invalid_emails": list,
            "qt_valids": int,
            "qt_invalids": int,
            "map_validation": list[dict],
        }

        # Preprocessing
        validated_emails: list = []
        invalid_emails: list = []
        map_validation: list[dict] = []

        # Process
        try:
            for email in email_list:
                try:
                    v = email_validator.validate_email(email)
                    validated_emails.append(email)
                    map_validation.append(v)

                except email_validator.EmailNotValidError:
                    invalid_emails.append(email)

            if verbose:
                success_print(f"Function: {self.emails.__name__} executed.")

        except Exception as e:
            raise ValidateError(f"Error when trying to validate email list: {str(e)}") from e

        # Postprocessing
        result = {
            "success": len(invalid_emails) == 0,
            "valid_emails": validated_emails,
            "invalid_emails": invalid_emails,
            "qt_valids": len(validated_emails),
            "qt_invalids": len(invalid_emails),
            "map_validation": map_validation,
        }

        return result

    def word(  # pylint: disable=too-many-positional-arguments
        self,
        origin_text: str,
        searched_word: str,
        case_sensitivy: bool = True,
        search_by: str = "string",
        verbose: bool = False,
    ) -> dict:
        """
        Searches for a string, substring, or word within a provided text.

        Parameters:
        -----------
        origin_text : str
            The text where the search should be performed.

        searched_word : str
            The word, substring, or pattern to search for.

        case_sensitivy : bool, optional
            If True, the search is case sensitive. Default: True.

        search_by : str, optional
            Search mode. Accepts:
            - 'string' - finds the requested substring (default)
            - 'word' - finds only the exact word
            - 'regex' - finds regex patterns [UNDER DEVELOPMENT]
            Default: "string".

        verbose : bool, optional
            If True, prints a message with the result. Default: False.

        Returns:
        --------
        dict
            Dictionary with the following keys:
            - 'is_found' (bool): True if the pattern was found at least once
            - 'number_occurrences' (int): Number of times the pattern was found
            - 'positions' (list): All positions where the pattern appeared (currently empty)

        Example:
        --------
        >>> from rpa_suite.core.validate import Validate
        >>> v = Validate()
        >>> v.word("Hello world, hello!", "hello", case_sensitivy=False, search_by="word")
        {'is_found': True, 'number_occurrences': 2, 'positions': []}
        """

        # Local Variables
        result: dict = {"is_found": False, "number_occurrences": 0, "positions": []}

        # Preprocessing
        result["is_found"] = False

        # Process
        try:
            if search_by == "word":
                origin_words = origin_text.split()
                try:
                    if case_sensitivy:
                        result["number_occurrences"] = origin_words.count(searched_word)
                        result["is_found"] = result["number_occurrences"] > 0
                    else:
                        words_lowercase = [word.lower() for word in origin_words]
                        searched_word_lower = searched_word.lower()
                        result["number_occurrences"] = words_lowercase.count(searched_word_lower)
                        result["is_found"] = result["number_occurrences"] > 0

                except Exception as e:
                    raise ValidateError(f"Unable to complete the search: {searched_word}. Error: {str(e)}") from e

            elif search_by == "string":
                try:
                    if case_sensitivy:
                        result["number_occurrences"] = origin_text.count(searched_word)
                        result["is_found"] = result["number_occurrences"] > 0
                    else:
                        origin_text_lower = origin_text.lower()
                        searched_word_lower = searched_word.lower()
                        result["number_occurrences"] = origin_text_lower.count(searched_word_lower)
                        result["is_found"] = result["number_occurrences"] > 0

                except Exception as e:
                    raise ValidateError(f"Unable to complete the search: {searched_word}. Error: {str(e)}") from e

        except Exception as e:
            raise ValidateError(f"Unable to search for: {searched_word}. Error: {str(e)}") from e

        # Postprocessing
        if result["is_found"]:
            if verbose:
                success_print(
                    f'Function: {self.word.__name__} found: {result["number_occurrences"]} occurrences for "{searched_word}".'
                )
        else:
            if verbose:
                success_print(
                    f'Function: {self.word.__name__} found no occurrences of "{searched_word}" during the search.'
                )

        return result
