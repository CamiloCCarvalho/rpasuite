import os
from rpa_suite.log.loggin import logging_decorator

@logging_decorator
def count_files(
                dir_to_count: list[str], 
                type_extension: str = '*'
                ) -> dict:
    
    """
    Função responsavel por fazer a contagem de arquivos dentro de uma pasta, considera subpastas para fazer a contagem, busca por tipo de arquivo, sendo todos arquivos por default. \n
    
    Retorno sendo (dicionário):
        - 'success': bool \n
        - 'qt': int \n
    """
    
    # Variaveis locais
    counter_result: dict = {
        'success': bool,
        'qt': int
    }
    
    # Pré tratamento
    counter_result['qt'] = 0
    counter_result['success'] = False
    
    # Processo
    try:
        for dir in dir_to_count:
            for current_dir, sub_dir, files in os.walk(dir):
                for file in files:
                    if file.endswith(f'.{type_extension}'):
                        counter_result['qt'] += 1
        counter_result['success'] = True
    except Exception as e:
        counter_result['success'] = False
        print(f'Erro ao tentar fazer contagem de arquivos! Erro: {str(e)}')
        
    # Pós tratamento
    ...
    
    # Retorno
    return counter_result
