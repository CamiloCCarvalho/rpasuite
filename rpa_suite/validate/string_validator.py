# /string_validator.py

from rpa_suite.log.printer import success_print, error_print

def search_str_in(
            origin_text: str,
            searched_word: str,
            case_sensitivy: bool = True,
            search_by: str = 'string',
            ) -> dict:
    
    """
    Function responsible for searching for a string, substring or word within a provided text. \n
    
    Parameters:
    -----------
    ``origin_text: str`` \n
        
        * It is the text where the search should be made, in string format. \n
        
    ``search_by: str`` accepts the values: \n
        
        * 'string' - can find a requested writing excerpt. (default) \n
        * 'word' - finds only the word written out exclusively. \n
        * 'regex' - find regex patterns, [ UNDER DEVELOPMENT ...] \n
    
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
        
    Description: pt-br
    ----------
    Função responsavel por fazer busca de uma string, sbustring ou palavra dentro de um texto fornecido. \n
    
    Parametros:
    -----------
    ``origin_text: str`` \n
        
        * É o texto onde deve ser feita a busca, no formato string. \n
        
    ``search_by: str`` aceita os valores: \n
        
        * 'string' - consegue encontrar um trecho de escrita solicitado. (default) \n
        * 'word' - encontra apenas a palavra escrita por extenso exclusivamente. \n
        * 'regex' - encontrar padrões de regex, [ EM DESENVOLVIMENTO ...] \n
    
    Retorno:
    -----------
    >>> type:dict
    um dicionário com todas informações que podem ser necessarias sobre a validação.
    Sendo respectivamente:
        * 'is_found': bool -  se o pattern foi encontrado em pelo menos um caso
        * 'number_occurrences': int - representa o número de vezes que esse pattern foi econtrado
        * 'positions': list[set(int, int), ...] - representa todas posições onde apareceu o pattern no texto original
        
    Sobre o `Positions`:
    -----------
    >>> type: list[set(int, int), ...]
        * no `index = 0` encontramos a primeira ocorrência do texto, e a ocorrência é composta por um PAR de números em um set, os demais indexes representam outras posições onde foram encontradas ocorrências caso hajam.
    """
    
    # Local Variables
    result: dict = {
        'is_found': bool,
        'number_occurrences': int,
        'positions': list[set]
    }
    
    # Preprocessing
    result['is_found'] = False
    result['number_occurrences'] = 0
    
    # Process
    try:
        if search_by == 'word':
            origin_words = origin_text.split()
            try:
                if case_sensitivy:
                    result['is_found'] = searched_word in origin_words
                else:
                    words_lowercase = [word.lower() for word in origin_words]
                    searched_word = searched_word.lower()
                    result['is_found'] = searched_word in words_lowercase
                    
            except Exception as e:
                return error_print(f'Unable to complete the search: {searched_word}. Error: {str(e)}')
                
        elif search_by == 'string':
            try:
                if case_sensitivy:
                    result['is_found'] = origin_text.__contains__(searched_word)
                else:
                    origin_text_lower: str = origin_text.lower()
                    searched_word_lower: str = searched_word.lower()
                    result['is_found'] = origin_text_lower.__contains__(searched_word_lower)
                    
            except Exception as e:
                return error_print(f'Unable to complete the search: {searched_word}. Error: {str(e)}')


    except Exception as e:
        return error_print(f'Unable to search for: {searched_word}. Error: {str(e)}')
    
    # Postprocessing
    if result['is_found']:
        success_print(f'Function: {search_str_in.__name__} found: {result["number_occurrences"]} occurrences for "{searched_word}".')
    else:
        success_print(f'Function: {search_str_in.__name__} found no occurrences of "{searched_word}" during the search.')
    
    return result
