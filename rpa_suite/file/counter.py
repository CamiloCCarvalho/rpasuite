import os
from rpa_suite.log.printer import error_print, success_print

def count_files(
                dir_to_count: list[str], 
                type_extension: str = '*'
                ) -> dict:
    
    """
    Função responsavel por fazer a contagem de arquivos dentro de uma pasta, considera subpastas para fazer a contagem, busca por tipo de arquivo, sendo todos arquivos por default. \n
    
    Parametros:
    ----------
    ``dir_to_count: list`` - deve ser uma lista, aceita mais de um caminho para contar arquivos.
    ``type_extension: str`` - deve ser uma string com o formato/extensão do tipo de arquivo que deseja ser buscado para contagem, se vazio por default sera usado ``*`` que contará todos arquivos.

    
    Retorno:
    ----------
    >>> type:dict
        * 'success': bool - representa se ação foi realizada com sucesso
        * 'qt': int - numero que representa a quantidade de arquivos que foram contados
    """
    
    # Variáveis locais
    result: dict = {
        'success': bool,
        'qt': int
    }
    
    # Pré tratamento
    result['qt'] = 0
    result['success'] = False
    
    # Processo
    try:
        for dir in dir_to_count:
            for current_dir, sub_dir, files in os.walk(dir):
                for file in files:
                    if file.endswith(f'.{type_extension}'):
                        result['qt'] += 1
        result['success'] = True
        success_print(f'Função: {count_files.__name__} encontrou {result['qt']} arquivos.')
        
    except Exception as e:
        result['success'] = False
        error_print(f'Erro ao tentar fazer contagem de arquivos! Erro: {str(e)}')
        
    return result
