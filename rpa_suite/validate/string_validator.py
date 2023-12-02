from rpa_suite.log.printer import success_print, error_print

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
        * 'number_occurrences': int - representa o número de vezes que esse pattern foi econtrado
        * 'positions': list[set(int, int), ...] - representa todas posições onde apareceu o pattern no texto original
        
    Sobre o `Positions`:
    -----------
    >>> type: list[set(int, int), ...]
        * no `index = 0` encontramos a primeira ocorrência do texto, e a ocorrência é composta por um PAR de números em um set, os demais indexes representam outras posições onde foram encontradas ocorrências caso hajam. 
    
    """
    
    # Variaveis locais
    result: dict = {
        'is_found': bool,
        'number_occurrences': int,
        'positions': list[set]
    }
    
    # Pré tratamento
    result['is_found'] = False
    result['number_occurrences'] = 0
    
    # Processo
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
                return error_print(f'Não foi possivel concluir a busca de: {searched_word}. Erro: {str(e)}')
                
        elif search_by == 'string':
            try:
                if case_sensitivy:
                    result['is_found'] = origin_text.__contains__(searched_word)
                else:
                    origin_text_lower: str = origin_text.lower()
                    searched_word_lower: str = searched_word.lower()
                    result['is_found'] = origin_text_lower.__contains__(searched_word_lower)
            except Exception as e:
                return error_print(f'Não foi possivel concluir a busca de: {searched_word}. Erro: {str(e)}')
            
        elif search_by == 'regex':
            pass
            """try:
                if case_sensitivy:
                    print(f'metodo para buscar com sensitivy...')
                else:
                    print(f'metodo para buscar sem sensitive...')
            except Exception as e:
                return print(f'Não foi possivel concluir a busca de: {searched_word}. Erro: {str(e)}')"""
            
    except Exception as e:
        return error_print(f'Não foi possivel realizar a busca por: {searched_word}. Erro: {str(e)}')
    
    # Pós tratamento
    if result['is_found']:
        success_print(f'Função: {search_in.__name__} encontrou: {result["number_occurrences"]} ocorrências para "{searched_word}".')
    else:
        success_print(f'Função: {search_in.__name__} não encontrou ocorrências de "{searched_word}" durante a busca.')
    
    return result
