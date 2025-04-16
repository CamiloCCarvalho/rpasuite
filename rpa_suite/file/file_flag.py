# /file_flag.py

import os, time
from rpa_suite import suite as rpa


def file_flag_create(display_message: bool = True, path_to_create: str = None, name_file: str = 'running.flag') -> None:
    """
    Function responsible for create a file flag on root directory by default. Path, name file and display message was optional. \n

    Parameters:
    ----------
    ``display_message: bool`` - should be boolean, True prints message on console.
    ``path_to_create: str`` - should be a string, by default use root dir with "os.getcwd()".
    ``name_file: str`` - should be a string, by default "running.flag".

    Return:
    ----------
    >>> type:bool
        * 'bool' - represents the result of performance this action

    Description: pt-br
    ----------
    Função responsável por criar um arquivo de flag na raiz do projeto por padrão. O diretório, o nome do arquivo e a possibilidade de imprimir no console a mensagem de sucesso, são opcionais.

    Parâmetros:
    ----------
    ``display_message: bool`` - deve ser booleano, True para o caso de imprimir no console a mensagem de resultado.
    ``path_to_create: str`` - deve ser string, por padrão usa como raiz do projeto o comando "os.getcwd()".
    ``name_file: str`` - deve ser string, por padrão "running.flag".
    
    Retorno:
    ----------
    >>> tipo: bool
        * 'bool' - representa o resultado performado da ação
    """
    
    try:
        if path_to_create == None:
            path_origin: str = os.getcwd()
            full_path_with_name = fr'{path_origin}/{name_file}'
        else:
            full_path_with_name = fr'{path_to_create}/{name_file}'
            
        with open(full_path_with_name, 'w', encoding='utf-8') as file:
            file.write('[T-BOT Crédit Simulation] running in realtime, waiting finish to new execution')
            
        if display_message: rpa.success_print("Flag file created.")
        return True
    
    except Exception as e:
        rpa.error_print(f'Erro na função file_scheduling_create: {str(e)}')
        return False


def file_flag_delete(display_message: bool = True, path_to_delete: str = None, name_file: str = 'running.flag') -> None:
    """
    Function responsible for delete a file flag on root directory by default. Path, name file and display message was optional. \n

    Parameters:
    ----------
    ``display_message: bool`` - should be boolean, True prints message on console.
    ``path_to_delete: str`` - should be a string, by default use root dir with "os.getcwd()".
    ``name_file: str`` - should be a string, by default "running.flag".

    Return:
    ----------
    >>> type:bool
        * 'bool' - represents the result of performance this action

    Description: pt-br
    ----------
    Função responsável por deletar um arquivo de flag na raiz do projeto por padrão. O diretório, o nome do arquivo e a possibilidade de imprimir no console a mensagem de sucesso, são opcionais.

    Parâmetros:
    ----------
    ``display_message: bool`` - deve ser booleano, True para o caso de imprimir no console a mensagem de resultado.
    ``path_to_delete: str`` - deve ser string, por padrão usa como raiz do projeto o comando "os.getcwd()".
    ``name_file: str`` - deve ser string, por padrão "running.flag".
    
    Retorno:
    ----------
    >>> tipo: bool
        * 'bool' - representa o resultado performado da ação
    """
    
    try:

        if path_to_delete == None:
            path_origin: str = os.getcwd()
            full_path_with_name = fr'{path_origin}/{name_file}'
        else:
            full_path_with_name = fr'{path_to_delete}/{name_file}'
            
        if os.path.exists(full_path_with_name):
            os.remove(full_path_with_name)
            if display_message: print("Flag file deleted.")
        else:
            rpa.alert_print("Flag file not found.")

    except Exception as e:
        rpa.error_print(f'Erro na função file_scheduling_delete: {str(e)}')
        time.sleep(1)
