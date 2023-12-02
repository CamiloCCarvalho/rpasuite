import re
from typing import Any

def create_list_using_regex(origin_text: str, division_pattern: str) -> list[str] | Any:
    """
    Função responsável por buscar em uma string ``origin_text`` um padrão ``division_pattern`` e dividir o texto original em substrings gerando uma lista de strings, também faz a limpeza e tratamento para manter a lista com as strings originais, porem dividas
    
    Retorno:
    ----------
    Uma lista de strings dividas pelo padrão utilizada no argumento passado como parametro.
    """
    try:
        # cria um delimitador e usa ele para dividir a string baseado no pattern
        text_with_delim = re.sub(division_pattern, r'\1<DELIMITADOR>', origin_text)
        messages = text_with_delim.split('<DELIMITADOR>')

        # Remover ultima string caso esteja vazia ou excesso de espaços
        if messages[-1] == '':
            messages = messages[:-1]

        # Retorna apenas mensagens com conteudo
        messages = [msg for msg in messages if msg.strip()]
        
        # Retira o delimitador \n tanto left como right de cada elemento da lista
        messages_striped = [msg.strip() for i, msg in enumerate(messages)]
        messages_lstriped = [msg.lstrip() for msg in messages_striped]
        
        # Retira o delimitador que tenha sido colocado entre pontuações dentro de um mesmo pattern
        messages_final = [msg.replace('\n', ' ') for msg in messages_lstriped]
        return messages_final
            
    except Exception as e:
        return print(f"Erro ao tentar criar lista usando pattern-match (regex). Erro: {str(e)}")
