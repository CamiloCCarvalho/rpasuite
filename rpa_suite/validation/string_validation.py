
def buscar_por(
                origin_text: str,
                searched_word: str,
                case_sensitivy: bool = True,
                search_by: str = 'string',
                ) -> None:
    
    """
    Function responsability, etc \n
    
    Return is ...
    """
    
    # Variaveis locais
    contains_in_text = False
    
        
    # Pré tratamento
    if search_by == 'word':
        origin_words = origin_text.split()
        if case_sensitivy:
            contains_in_text = searched_word in origin_words

        else:
            words_lowercase = [word.lower() for word in origin_words]
            searched_word = searched_word.lower()
            contains_in_text = searched_word in words_lowercase
    elif search_by == 'string':
        if case_sensitivy:
            contains_in_text = origin_text.__contains__(searched_word)
        else:
            origin_text_lower: str = origin_text.lower()
            searched_word_lower: str = searched_word.lower()
            contains_in_text = origin_text_lower.__contains__(searched_word_lower)
    
    elif search_by == 'regex':
        # regex search
        pass
    else:
        print(f'por favor digite alguma forma de busca valida para a função, a função aceita: string, word e regex, como padrões de busca para fazer a pesquisa no texto original.')    
    
    # Pós tratamento
    
    # Retorno
    return contains_in_text

if __name__ == '__main__':
    print(buscar_por('Camilo Costa de Carvalho', 'costa', True, 'word'))