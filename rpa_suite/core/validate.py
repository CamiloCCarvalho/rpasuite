# rpa_suite/core/mail_validator.py

# imports standard
import re

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
        ----------
        email_list : list
            A list of strings containing the emails to be validated.
        verbose : bool, optional
            If True, prints a success message after execution. Default is False.

        Returns:
        ----------
        dict
            Returns a dictionary with the following data:
                * 'success': bool - True if all emails are valid, False otherwise
                * 'valid_emails': list - list of valid emails
                * 'invalid_emails': list - list of invalid emails
                * 'qt_valids': int - number of valid emails
                * 'qt_invalids': int - number of invalid emails
                * 'map_validation': list - validation result for each email

        Example:
        ----------
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
            "success": False,
            "valid_emails": [],
            "invalid_emails": [],
            "qt_valids": 0,
            "qt_invalids": 0,
            "map_validation": [],
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
        ----------
        origin_text : str
            The text where the search should be performed.
        searched_word : str
            The word, substring, or pattern to search for.
        case_sensitivy : bool, optional
            If True, the search is case sensitive. Default is True.
        search_by : str, optional
            Accepts the values:
                * 'string' - finds the requested substring (default)
                * 'word' - finds only the exact word
                * 'regex' - finds regex patterns [UNDER DEVELOPMENT...]
        verbose : bool, optional
            If True, prints a message with the result. Default is False.

        Returns:
        ----------
        dict
            Returns a dictionary with the following information:
                * 'is_found': bool - True if the pattern was found at least once
                * 'number_occurrences': int - number of times the pattern was found
                * 'positions': list[tuple[int, int]] - `(start, end)` character
                  offsets in the original text for each occurrence

        Example:
        ----------
        >>> from rpa_suite.core.validate import Validate
        >>> v = Validate()
        >>> v.word("Hello world, hello!", "hello", case_sensitivy=False, search_by="word")
        {'is_found': True, 'number_occurrences': 2, 'positions': [(0, 5), (13, 18)]}

        """

        result: dict = {"is_found": False, "number_occurrences": 0, "positions": []}

        try:
            flags = 0 if case_sensitivy else re.IGNORECASE

            if search_by == "word":
                pattern = re.compile(rf"\b{re.escape(searched_word)}\b", flags)
            elif search_by == "string":
                pattern = re.compile(re.escape(searched_word), flags)
            elif search_by == "regex":
                pattern = re.compile(searched_word, flags)
            else:
                raise ValidateError(f"Invalid search_by value: {search_by!r}. Use 'string', 'word' or 'regex'.")

            matches = list(pattern.finditer(origin_text))
            result["positions"] = [(m.start(), m.end()) for m in matches]
            result["number_occurrences"] = len(matches)
            result["is_found"] = result["number_occurrences"] > 0

        except ValidateError:
            raise
        except re.error as e:
            raise ValidateError(f"Invalid regex for: {searched_word!r}. Error: {str(e)}") from e
        except Exception as e:
            raise ValidateError(f"Unable to search for: {searched_word}. Error: {str(e)}") from e

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

    @staticmethod
    def _only_digits(value: str) -> str:
        return re.sub(r"\D", "", value or "")

    def cpf(self, value: str) -> bool:
        """
        Validate a Brazilian CPF (Cadastro de Pessoas Físicas).

        Accepts formatted (`123.456.789-09`) or unformatted (`12345678909`)
        inputs. Rejects sequences with all equal digits (e.g. `11111111111`).

        Returns:
            True if the CPF is structurally and check-digit valid, False otherwise.
        """
        digits = self._only_digits(value)
        if len(digits) != 11 or digits == digits[0] * 11:
            return False

        def _dv(nums: list[int], weights: range) -> int:
            total = sum(n * w for n, w in zip(nums, weights))
            rest = total % 11
            return 0 if rest < 2 else 11 - rest

        nums = [int(d) for d in digits]
        dv1 = _dv(nums[:9], range(10, 1, -1))
        dv2 = _dv(nums[:9] + [dv1], range(11, 1, -1))
        return nums[9] == dv1 and nums[10] == dv2

    def cnpj(self, value: str) -> bool:
        """
        Validate a Brazilian CNPJ (Cadastro Nacional da Pessoa Jurídica).

        Accepts formatted (`12.345.678/0001-95`) or unformatted (`12345678000195`)
        inputs. Rejects sequences with all equal digits.
        """
        digits = self._only_digits(value)
        if len(digits) != 14 or digits == digits[0] * 14:
            return False

        weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        weights2 = [6] + weights1

        def _dv(nums: list[int], weights: list[int]) -> int:
            total = sum(n * w for n, w in zip(nums, weights))
            rest = total % 11
            return 0 if rest < 2 else 11 - rest

        nums = [int(d) for d in digits]
        dv1 = _dv(nums[:12], weights1)
        dv2 = _dv(nums[:12] + [dv1], weights2)
        return nums[12] == dv1 and nums[13] == dv2

    def cep(self, value: str) -> bool:
        """
        Validate a Brazilian CEP (Código de Endereçamento Postal).

        Accepts formatted (`12345-678`) or unformatted (`12345678`) inputs.
        Only the structure (8 digits) is validated; existence in Correios' base
        is not checked.
        """
        digits = self._only_digits(value)
        return len(digits) == 8

    def phone_br(self, value: str) -> bool:
        """
        Validate a Brazilian phone number.

        Accepted formats (with or without country code `+55`):
            * 10 digits: landline `AA XXXX-XXXX`
            * 11 digits: mobile `AA 9XXXX-XXXX` (the ninth digit must be 9)

        Area codes (`AA`) are constrained to the 11-99 range used by ANATEL.
        """
        digits = self._only_digits(value)
        if digits.startswith("55") and len(digits) in (12, 13):
            digits = digits[2:]
        if len(digits) not in (10, 11):
            return False
        area_code = int(digits[:2])
        if not 11 <= area_code <= 99:
            return False
        if len(digits) == 11 and digits[2] != "9":
            return False
        return True
