# /screen_shot.py

import os, time
from datetime import datetime
from rpa_suite.log.printer import error_print, success_print
from .__create_ss_dir import __create_ss_dir




def screen_shot(path_dir:str = None, file_name: str = 'screenshot', save_with_date: bool = True, delay: int = 1, use_default_path_and_name: bool = True, name_ss_dir:str = None) -> str | None:

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
        
        try:
            import pyautogui
            import pyscreeze
            
        except ImportError:
            raise ImportError(" The ‘pyautogui’ e ‘Pillow’ libraries are necessary to use this module. Please install them with ‘pip install pyautogui pillow.")
        
        time.sleep(delay)

        if not use_default_path_and_name:
            result_tryed: dict = __create_ss_dir(path_dir, name_ss_dir)
            path_dir = result_tryed['path_created']
        else:
            if path_dir == None and name_ss_dir == None:
                result_tryed: dict = __create_ss_dir()
                path_dir = result_tryed['path_created']

        
        if save_with_date: # use date on file name
            image = pyautogui.screenshot()
            file_name = f'{file_name}_{datetime.today().strftime("%d_%m_%Y-%H_%M_%S")}.png'
            path_file_screenshoted = os.path.join(path_dir, file_name)
            
            success_print(path_file_screenshoted)
            
            image.save(path_file_screenshoted)
            return path_file_screenshoted
        
        else: # not use date on file name
            image = pyautogui.screenshot()
            file_name = f'{file_name}.png'
            path_file_screenshoted = os.path.join(path_dir, file_name)
            
            image.save(path_file_screenshoted)
            return path_file_screenshoted
    
    except Exception as e:

        error_print(f'Erro durante a função {screen_shot.__name__}! Error: {str(e)}')
        return None
