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
        ----------
        origin_text : str
            The text where the search will be performed.
        pattern_to_search : str
            The regex pattern to search for in the text.
        case_sensitive : bool, optional
            If True, the search is case sensitive. Default is True.
        verbose : bool, optional
            If True, prints a message indicating if the pattern was found. Default is False.

        Returns:
        ----------
        bool
            True if the pattern is found in the text, False otherwise.

        Example:
        ----------
        >>> from rpa_suite.core.regex import Regex
        >>> r = Regex()
        >>> r.check_pattern_in_text("Hello World", "World")
        True
        >>> r.check_pattern_in_text("Hello World", "world", case_sensitive=True)
        False
        >>> r.check_pattern_in_text("Hello World", "world", case_sensitive=False)
        True

        Descrição: pt-br
        ----------
        Verifica se um padrão regex existe dentro de uma string de texto e retorna True se encontrado, caso contrário False.

        Parâmetros:
        ----------
        origin_text : str
            O texto onde a busca será realizada.
        pattern_to_search : str
            O padrão regex a ser buscado no texto.
        case_sensitive : bool, opcional
            Se True, a busca diferencia maiúsculas de minúsculas. Padrão é True.
        verbose : bool, opcional
            Se True, imprime uma mensagem indicando se o padrão foi encontrado. Padrão é False.

        Retorno:
        ----------
        bool
            True se o padrão for encontrado no texto, False caso contrário.

        Exemplo:
        ----------
        >>> from rpa_suite.core.regex import Regex
        >>> r = Regex()
        >>> r.check_pattern_in_text("Olá Mundo", "Mundo")
        True
        >>> r.check_pattern_in_text("Olá Mundo", "mundo", case_sensitive=True)
        False
        >>> r.check_pattern_in_text("Olá Mundo", "mundo", case_sensitive=False)
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
