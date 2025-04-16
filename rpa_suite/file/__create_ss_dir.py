# /_create_ss_dir.py

import os
from typing import Union
from rpa_suite.log.printer import error_print, alert_print, success_print


def __create_ss_dir(path_to_create: str = 'default', name_ss_dir: str='screenshots') -> dict[str, Union[bool, str, None]]:

    """
    Function responsible for creating a ScreenShots directory to work with your screenshot files. \n

    Parameters:
    ----------
    ``path_to_create: str`` - should be a string with the full path pointing to the folder where the screenshots folder should be created, if it is empty the ``default`` value will be used which will create a folder in the current directory where the file containing this function was called.

    ``name_ss_dir: str`` - should be a string representing the name of the logger directory to be created. If it is empty, the ``temp`` value will be used as the default directory name.

    Return:
    ----------
    >>> type:dict
        * 'success': bool - represents case the action was performed successfully
        * 'path_created': str - path of the directory that was created on the process
        
    Description: pt-br
    ----------
    Função responsavel por criar diretório de screenshots para trabalhar com seus arquivos de sreenshot. \n

    Parametros:
    ----------
    ``path_to_create: str`` - deve ser uma string com o path completo apontando para a pasta onde deve ser criada a pasta temporaria, se estiver vazio sera usado valor ``default`` que criará pasta no diretório atual onde o arquivo contendo esta função foi chamada.

    ``name_ss_dir: str`` - deve ser uma string representando o nome do diretório de screenshots a ser criado. Se estiver vazio, o valor ``screenshots`` será usado como o nome padrão do diretório.

    Retorno:
    ----------
    >>> type:dict
        * 'success': bool - representa se ação foi realizada com sucesso
        * 'path_created': str - path do diretório que foi criado no processo
    """
    
    # Local Variables
    result: dict = {
        'success': bool,
        'path_created': str,
    }
    
    try:
        # by 'default', defines path to local script execution path
        if path_to_create == 'default':
            path_to_create: str = os.getcwd()

        # Build path to new dir
        full_path: str = os.path.join(path_to_create, name_ss_dir)

        # Create dir in this block
        try:

            # Successefully created
            os.makedirs(full_path, exist_ok=False)

            result['success'] = True
            result['path_created'] = fr'{full_path}'

            success_print(f"Diretório:'{full_path}' foi criado com sucesso.")

        except FileExistsError:
            result['success'] = False
            result['path_created'] = full_path
            # alert_print(f"Diretório:'{full_path}' já existe.")

        except PermissionError:
            result['success'] = False
            result['path_created'] = None
            alert_print(f"Permissão negada: não é possível criar o diretório '{full_path}'.")

    except Exception as e:
        result['success'] = False
        result['path_created'] = None
        error_print(f'Error capturing current path to create screenshots directory! Error: {str(e)}')
        
    finally:
        return result
