# rpa_suite/core/file.py

# imports standard
import os, time
from datetime import datetime
from typing import Dict, List, Union

# imports third party
from colorama import Fore

# imports internal
from rpa_suite.functions._printer import error_print, success_print, alert_print
from rpa_suite.functions.__create_ss_dir import __create_ss_dir as create_ss_dir


class File:
    """
    Class that provides utilities for file management, including creation, deletion, and manipulation of files.

    This class offers functionalities for:
        - Creating and deleting flag files
        - Counting files in a directory
        - Capturing screenshots and managing their paths

    Methods:
        screen_shot: Creates a screenshot and saves it in a specified directory
        count_files: Counts the number of files in a specified directory
        flag_create: Creates a flag file
        flag_delete: Deletes a flag file

    The File class is part of the RPA Suite and can be accessed through the rpa object:
        >>> from rpa_suite import rpa
        >>> rpa.file.screen_shot('example')

    Parameters:
        file_name (str): The name of the screenshot file
        path_dir (str): The path of the directory where the screenshot should be saved
        save_with_date (bool): Indicates if the file name should include the date
        delay (int): The wait time before capturing the screen

    pt-br
    ----------
    Classe que fornece utilitários para gerenciamento de arquivos, incluindo criação, exclusão e manipulação de arquivos.

    Esta classe oferece funcionalidades para:
        - Criar e excluir arquivos de flag
        - Contar arquivos em um diretório
        - Capturar screenshots e gerenciar seus caminhos

    Métodos:
        screen_shot: Cria uma captura de tela e a salva em um diretório especificado
        count_files: Conta o número de arquivos em um diretório especificado
        flag_create: Cria um arquivo de flag
        flag_delete: Exclui um arquivo de flag

    A classe File é parte do RPA Suite e pode ser acessada através do objeto rpa:
        >>> from rpa_suite import rpa
        >>> rpa.file.screen_shot('exemplo')

    Parâmetros:
        file_name (str): O nome do arquivo de captura de tela
        path_dir (str): O caminho do diretório onde a captura de tela deve ser salva
        save_with_date (bool): Indica se o nome do arquivo deve incluir a data
        delay (int): O tempo de espera antes de capturar a tela
    """

    def __init__(self):
        self.__create_ss_dir = create_ss_dir

    def screen_shot(
        self,
        file_name: str = "screenshot",
        path_dir: str = None,
        save_with_date: bool = True,
        delay: int = 1,
        use_default_path_and_name: bool = True,
        name_ss_dir: str | None = None,
        display_message: bool = False,
    ) -> str | None:
        """
        Function responsible for create a dir for screenshot, and file screenshot and save this in dir to create, if dir exists save it on original dir. By default uses date on file name. \n

        Parameters:
        ----------
        ``file_name: str`` - should be a string, by default name is `screenshot`.
        ``path_dir: str`` - should be a string, not have a default path.
        ``save_with_date: bool`` - should be a boolean, by default `True` save namefile with date `foo_dd_mm_yyyy-hh_mm_ss.png`.
        ``delay: int`` - should be a int, by default 1 (represents seconds).
        ``use_default_path_and_name: bool`` - should be a boolean, by default `True`
        ``name_ss_dir: str`` - should be a string, by default type `None`
        ``display_message`` - should be a boolean, by default `False`

        Return:
        ----------
        >>> type:str
            * 'screenshot_path': str - represents the absulute path created for this file

        Description: pt-br
        ----------
        Função responsável por criar um diretório para captura de tela, e arquivo de captura de tela e salvar isso no diretório a ser criado, se o diretório existir, salve-o no diretório original. Por padrão, usa a data no nome do arquivo.

        Parâmetros:
        ----------
        ``file_name: str`` - deve ser uma string, por padrão o nome é `screenshot`.
        ``file_path: str`` - deve ser uma string, não tem um caminho padrão.
        ``save_with_date: bool`` - deve ser um booleano, por padrão `True` salva o nome do arquivo com a data `foo_dd_mm_yyyy-hh_mm_ss.png`.
        ``delay: int`` - deve ser um int, por padrão 1 representado em segundo(s).
        ``use_default_path_and_name: bool`` - deve ser um booleano, por padrão `True`
        ``name_ss_dir: str`` - deve ser uma string, por padrão do tipo `None`
        ``display_message`` - deve ser um booleano, por padrão `False`

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
                raise ImportError(
                    f"\nThe 'pyautogui' e 'Pillow' libraries are necessary to use this module. {Fore.YELLOW}Please install them with: 'pip install pyautogui pillow'{Fore.WHITE}"
                )

            time.sleep(delay)

            if not use_default_path_and_name:
                result_tryed: dict = self.__create_ss_dir(path_dir, name_ss_dir)
                path_dir = result_tryed["path_created"]
            else:
                result_tryed: dict = self.__create_ss_dir()
                path_dir = result_tryed["path_created"]

            if save_with_date:  # use date on file name
                image = pyautogui.screenshot()
                file_name = f'{file_name}_{datetime.today().strftime("%d_%m_%Y-%H_%M_%S")}.png'
                path_file_screenshoted = os.path.join(path_dir, file_name)

                image.save(path_file_screenshoted)

                if display_message:
                    success_print(path_file_screenshoted)

                return path_file_screenshoted

            else:  # not use date on file name
                image = pyautogui.screenshot()
                file_name = f"{file_name}.png"
                path_file_screenshoted = os.path.join(path_dir, file_name)

                image.save(path_file_screenshoted)

                if display_message:
                    success_print(path_file_screenshoted)

                return path_file_screenshoted

        except Exception as e:

            error_print(f"Error to execute function:{self.screen_shot.__name__}! Error: {str(e)}")
            return None

    def flag_create(
        self,
        name_file: str = "running.flag",
        path_to_create: str | None = None,
        display_message: bool = True,
    ) -> None:
        """
        Cria um arquivo de sinalização indicando que o robô está em execução.
        """

        try:
            if path_to_create is None:
                path_origin: str = os.getcwd()
                full_path_with_name = rf"{path_origin}/{name_file}"
            else:
                full_path_with_name = rf"{path_to_create}/{name_file}"

            with open(full_path_with_name, "w", encoding="utf-8") as file:
                file.write("[RPA Suite] - Running Flag File")
            if display_message:
                success_print("Flag file created.")

        except Exception as e:
            error_print(f"Erro na função file_scheduling_create: {str(e)}")

    def flag_delete(
        self,
        name_file: str = "running.flag",
        path_to_delete: str | None = None,
        display_message: bool = True,
    ) -> None:
        """
        Deleta o arquivo de sinalização indicando que o robô terminou a execução.
        """

        try:

            if path_to_delete is None:
                path_origin: str = os.getcwd()
                full_path_with_name = rf"{path_origin}/{name_file}"
            else:
                full_path_with_name = rf"{path_to_delete}/{name_file}"

            if os.path.exists(full_path_with_name):
                os.remove(full_path_with_name)
                if display_message:
                    success_print("Flag file deleted.")
            else:
                alert_print("Flag file not found.")

        except Exception as e:
            error_print(f"Erro na função file_scheduling_delete: {str(e)}")
            time.sleep(1)

    def count_files(
        self,
        dir_to_count: List[str] = ["."],
        type_extension: str = "*",
        display_message: bool = False,
    ) -> Dict[str, Union[bool, int]]:
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
        result: dict = {"success": False, "qt": 0}

        # Process
        try:
            for directory in dir_to_count:
                for _, _, files in os.walk(directory):
                    for file in files:
                        if type_extension == "*" or file.endswith(f".{type_extension}"):
                            result["qt"] += 1
            result["success"] = True

            if display_message:
                success_print(f'Function: {self.count_files.__name__} counted {result["qt"]} files.')

        except Exception as e:
            result["success"] = False
            error_print(f"Error when trying to count files! Error: {str(e)}")

        return result
