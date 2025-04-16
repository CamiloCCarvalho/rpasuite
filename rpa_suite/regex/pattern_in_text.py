# /pattern_in_text.py

import re
from rpa_suite.log.printer import error_print, success_print


def check_pattern_in_text(origin_text: str,
                        pattern_to_search: str, 
                        case_sensitive: bool = True,
                        display_message: bool = False) -> bool:

    """
    Function responsible for searching in a string ``origin_text`` a pattern ``pattern_to_search`` and returning True if the pattern is found, otherwise False. ``case_sensitive`` used for exact cases or cases with diferencce upper and lower cases

    Return:
    ----------
    A boolean indicating whether the pattern was found in the text.

    Description: pt-br
    ----------
    Função responsável por buscar em um texto de leitura humana uma string ``origin_text`` por um padrão ``pattern_to_search`` e retornar True se o padrão for encontrado, caso contrário, False. ``case_sensitive`` usado para casos exatos ou casos com diferença entre caixa alta e baixa nos caracteres.

    Retorno:
    ----------
    Um booleano indicando se o padrão foi encontrado no texto.
    """

    try:

        if case_sensitive:
            
            # Check if the pattern is found in the text
            if re.search(pattern_to_search, origin_text):
                if display_message: success_print(f'Pattern found successfully!')
                return True
            
            else:
                if display_message: success_print(f'Pattern not found.')
                return False
        else:
            
            # normalize text to search without case sensitive
            origin_text = origin_text.lower()
            pattern_to_search = pattern_to_search.lower()
            
            # Check if the pattern is found in the text
            if re.search(pattern_to_search, origin_text):
                if display_message: success_print(f'Pattern found successfully!')
                return True
            
            else:
                if display_message: success_print(f'Pattern not found.')
                return False
            
    except Exception as e:
        
        error_print(f"Error when trying to check pattern in text. Error: {str(e)}")
        return False
