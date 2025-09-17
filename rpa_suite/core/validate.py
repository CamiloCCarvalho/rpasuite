# rpa_suite/core/mail_validator.py

# imports third party
import email_validator

# imports internal
from rpa_suite.functions._printer import success_print

class ValidateError(Exception):
    """Custom exception for Validate errors."""
    def __init__(self, message):
        super().__init__(f'Validate Error: {message}')

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
        """Initialize the Validate class."""
        pass

    def emails(self, email_list: list[str], display_message: bool = False) -> dict:
        """
        Function responsible for rigorously validating a list of emails using the email_validator library.

        Parameters:
        ------------
        ``email_list: list`` a list of strings containing the emails to be validated

        Return:
        ------------
        >>> type: dict
        Returns a dictionary with the respective data:
            * 'success': bool - represents if the list is 100% valid
            * 'valid_emails': list - list of valid emails
            * 'invalid_emails': list - list of invalid emails
            * 'qt_valids': int - number of valid emails
            * 'qt_invalids': int - number of invalid emails
            * 'map_validation' - map of the validation of each email
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

            if display_message:
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

    def word(
        self,
        origin_text: str,
        searched_word: str,
        case_sensitivy: bool = True,
        search_by: str = "string",
        display_message: bool = False,
    ) -> dict:
        """
        Function responsible for searching for a string, substring or word within a provided text.

        Parameters:
        -----------
        ``origin_text: str`` 
            It is the text where the search should be made, in string format.

        ``search_by: str`` accepts the values:
            * 'string' - can find a requested writing excerpt. (default)
            * 'word' - finds only the word written out exclusively.
            * 'regex' - find regex patterns, [ UNDER DEVELOPMENT ...]

        Return:
        -----------
        >>> type:dict
        a dictionary with all information that may be necessary about the validation.
        Respectively being:
            * 'is_found': bool -  if the pattern was found in at least one case
            * 'number_occurrences': int - represents the number of times this pattern was found
            * 'positions': list[set(int, int), ...] - represents all positions where the pattern appeared in the original text

        About `Positions`:
        -----------
        >>> type: list[set(int, int), ...]
            * at `index = 0` we find the first occurrence of the text, and the occurrence is composed of a PAIR of numbers in a set, the other indexes represent other positions where occurrences were found if any.
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
                    return ValidateError(f"Unable to complete the search: {searched_word}. Error: {str(e)}")

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
                    return ValidateError(f"Unable to complete the search: {searched_word}. Error: {str(e)}")

        except Exception as e:
            raise ValidateError(f"Unable to search for: {searched_word}. Error: {str(e)}") from e

        # Postprocessing
        if result["is_found"]:
            if display_message:
                success_print(
                    f'Function: {self.word.__name__} found: {result["number_occurrences"]} occurrences for "{searched_word}".'
                )
        else:
            if display_message:
                success_print(
                    f'Function: {self.word.__name__} found no occurrences of "{searched_word}" during the search.'
                )

        return result
