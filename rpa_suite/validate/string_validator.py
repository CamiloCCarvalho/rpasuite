
def search_in(
            origin_text: str,
            searched_word: str,
            case_sensitivy: bool = True,
            search_by: str = 'string',
            ) -> dict:
    
    """
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
        * 'number_occurrences': int - representa o numero de vezes que esse pattern foi econtrado
        * 'positions': list[set(int, int), ...] - representa todas posições onde apareceu o pattern no texto original
        
    Sobre o `Position`:
    -----------
    >>> type: list[set(int, int), ...]
        * no ``index = 0`` encontramos a primeira ocorrencia do texto, e a ocorrencia é composta por um PAR de numeros em um set, os demais indexes representam outras posições onde foram encontradas ocorrencias caso hajam. 
    
    """
    
    # Variaveis locais
    string_validator_result: dict = {
        'is_found': bool,
        'number_occurrences': int,
        'positions': list[set]
    }
    
    # Pré tratamento
    string_validator_result['is_found'] = False
    string_validator_result['number_occurrences'] = 0
    
    # Processo
    if search_by == 'word':
        origin_words = origin_text.split()
        if case_sensitivy:
            string_validator_result['is_found'] = searched_word in origin_words

        else:
            words_lowercase = [word.lower() for word in origin_words]
            searched_word = searched_word.lower()
            string_validator_result['is_found'] = searched_word in words_lowercase
            
    elif search_by == 'string':
        if case_sensitivy:
            string_validator_result['is_found'] = origin_text.__contains__(searched_word)
        else:
            origin_text_lower: str = origin_text.lower()
            searched_word_lower: str = searched_word.lower()
            string_validator_result['is_found'] = origin_text_lower.__contains__(searched_word_lower)
    
    """
    elif search_by == 'regex':
        # regex search
        pass
    else:
        print(f'por favor digite alguma forma de busca valida para a função, a função aceita: string, word e regex, como padrões de busca para fazer a pesquisa no texto original.')
    """    
    
    # Pós tratamento
    ...
    
    return string_validator_result
