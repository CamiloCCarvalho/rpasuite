# /screen_shot.py

import os, time
from datetime import datetime
from rpa_suite.log.printer import error_print


try:
    import pyautogui
    import pyscreeze
    
except ImportError:
    raise ImportError(" The ‘pyautogui’, ‘Pillow’, and ‘PyScreeze’ libraries are necessary to use this module. Please install them with ‘pip install pyautogui pillow pyscreeze’.")


def screen_shot(file_path: str, file_name: str = 'screenshot', save_with_date: bool = True, delay: int = 1) -> str | None:

    """
    Function responsible for create a dir for screenshot, and file screenshot and save this in dir to create, if dir exists save it on original dir. By default uses date on file name. \n

    Parameters:
    ----------
    ``file_path: str`` - should be a string, not have a default path.
    ``file_name: str`` - should be a string, by default name is `screenshot`.
    ``save_with_date: bool`` - should be a boolean, by default `True` save namefile with date `foo_dd_mm_yyyy-hh_mm_ss.png`.
    ``delay: int`` - should be a int, by default 1 (represents seconds).

    Return:
    ----------
    >>> type:str
        * 'screenshot_path': str - represents the absulute path created for this file

    Description: pt-br
    ----------
    Função responsável por criar um diretório para captura de tela, e arquivo de captura de tela e salvar isso no diretório a ser criado, se o diretório existir, salve-o no diretório original. Por padrão, usa a data no nome do arquivo.

    Parâmetros:
    ----------
    ``file_path: str`` - deve ser uma string, não tem um caminho padrão.
    ``file_name: str`` - deve ser uma string, por padrão o nome é `screenshot`.
    ``save_with_date: bool`` - deve ser um booleano, por padrão `True` salva o nome do arquivo com a data `foo_dd_mm_yyyy-hh_mm_ss.png`.
    ``delay: int`` - deve ser um int, por padrão 1 representado em segundo(s).
    
    Retorno:
    ----------
    >>> tipo: str
        * 'screenshot_path': str - representa o caminho absoluto do arquivo criado
    """

    # proccess
    try:
        
        time.sleep(delay)
        if not os.path.exists(file_path):

            # if dir not exists create it
            try:
                os.makedirs(file_path)

            except OSError as e:
                error_print(f"Falha ao criar o diretório em: '{file_path}'! Error: {str(e)}")

        
        if save_with_date: # use date on file name
            image = pyautogui.screenshot()
            path_file_screenshoted =  fr'{file_path}/{file_name}_{datetime.today().strftime("%d_%m_%Y-%H_%M_%S")}.png'

            image.save(path_file_screenshoted)
            return os.path.abspath(path_file_screenshoted)
        
        else: # not use date on file name
            image = pyautogui.screenshot()
            path_file_screenshoted =  fr'{file_path}/{file_name}.png'

            image.save(path_file_screenshoted)
            return os.path.abspath(path_file_screenshoted)
    
    except Exception as e:

        error_print(f'Erro durante a função {screen_shot.__name__}! Error: {str(e)}')
        return None
