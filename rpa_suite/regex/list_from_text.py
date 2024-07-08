# /list_from_text.py

import re
from typing import Any
from rpa_suite.log.printer import error_print, success_print

def create_list_using_regex(origin_text: str, division_pattern: str) -> list[str] | Any:

    """
    Function responsible for searching in a string ``origin_text`` a pattern ``division_pattern`` and dividing the original text into substrings generating a list of strings, also does the cleaning and treatment to keep the list with the original strings, but divided

    Return:
    ----------
    A list of strings divided by the pattern used in the argument passed as a parameter.

    Description: pt-br
    ----------
    Função responsável por buscar em  um texto de leitura humana uma string ``origin_text`` por um padrão ``division_pattern`` e dividir o texto original em substrings gerando uma lista de strings, também faz a limpeza e tratamento para manter a lista com as strings originais, porem dividas

    Retorno:
    ----------
    Uma lista de strings dividas pelo padrão utilizada no argumento passado como parametro.
    """

    try:
        # creates a delimiter and uses it to split the string based on the pattern
        text_with_delim = re.sub(division_pattern, r'\1<DELIMITADOR>', origin_text)
        messages = text_with_delim.split('<DELIMITADOR>')

        # Remove the last string if it is empty or has excess spaces
        if messages[-1] == '':
            messages = messages[:-1]

        # Returns only messages with content.
        messages = [msg for msg in messages if msg.strip()]
        
        # Removes the delimiter \n both left and right from each element of the list
        messages_striped = [msg.strip() for i, msg in enumerate(messages)]
        messages_lstriped = [msg.lstrip() for msg in messages_striped]

        # Removes the delimiter that has been placed between punctuation within the same pattern.
        messages_final = [msg.replace('\n', ' ') for msg in messages_lstriped]
        success_print(f'List generated successfully!')
        return messages_final

    except Exception as e:
        error_print(f"Error when trying to create list using pattern-match (regex). Error: {str(e)}")
