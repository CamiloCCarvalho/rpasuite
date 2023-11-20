from rpa_suite.log.loggin import logging_decorator

@logging_decorator
def search_in(
                origin_text: str,
                searched_word: str,
                case_sensitivy: bool = True,
                search_by: str = 'string',
                ) -> dict:
    
    """
    Função responsavel por fazer busca de uma string, sbustring ou palavra dentro de um texto fornecido. \n
    
    o parametro search_by aceita os valores: \n
        
        - 'string' -> consegue encontrar um trecho de escrita solicitado. (default) \n
        - 'word' -> encontra apenas a palavra escrita por extenso exclusivamente. \n
    
    Retorno é um dicionário da seguinte forma:
        - encontrou: bool 
        - numero de ocorrencias: int
        - posição inicial e final de cada ocorrencia: list[set(start; end), ...]
    """
    
    # Variaveis locais
    string_validator_result: dict = {
        'is_found': bool,
        'number_occurrences': int,
        'positions_in_text': list[set]
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
    
    """elif search_by == 'regex':
        # regex search
        pass
    else:
        print(f'por favor digite alguma forma de busca valida para a função, a função aceita: string, word e regex, como padrões de busca para fazer a pesquisa no texto original.')"""    
    
    # Pós tratamento
    ...
    
    # Retorno
    return string_validator_result

if __name__ == '__main__':
    print(search_in('Camilo Costa de Carvalho', 'costa', True, 'word'))
