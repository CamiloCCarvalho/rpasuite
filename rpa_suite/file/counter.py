import os
from rpa_suite.log.printer import error_print, success_print

def count_files(
                dir_to_count: list[str], 
                type_extension: str = '*'
                ) -> dict:
    
    """
    Function responsible for counting files within a folder, considers subfolders to do the count, searches by file type, being all files by default. \n
    
    Parameters:
    ----------
    ``dir_to_count: list`` - should be a list, accepts more than one path to count files.
    ``type_extension: str`` - should be a string with the format/extension of the type of file you want to be searched for counting, if empty by default will be used ``*`` which will count all files.

    
    Return:
    ----------
    >>> type:dict
        * 'success': bool - represents if the action was performed successfully
        * 'qt': int - number that represents the quantity of files that were counted
        
    Description: pt-br
    ----------
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
    
    # Local Variables
    result: dict = {
        'success': bool,
        'qt': int
    }
    
    # Preprocessing
    result['qt'] = 0
    result['success'] = False
    
    # Process
    try:
        for dir in dir_to_count:
            for current_dir, sub_dir, files in os.walk(dir):
                for file in files:
                    if file.endswith(f'.{type_extension}'):
                        result['qt'] += 1
        result['success'] = True
        success_print(f'Function: {count_files.__name__} counted {result['qt']} files.')
        
    except Exception as e:
        result['success'] = False
        error_print(f'Error when trying to count files! Error: {str(e)}')
        
    return result
