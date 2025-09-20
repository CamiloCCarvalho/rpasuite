# rpa_suite/core/file.py

# imports standard
import os, time
from datetime import datetime
from typing import Dict, List, Union

# imports third party
from colorama import Fore

# imports internal
from rpa_suite.functions._printer import success_print, alert_print
from rpa_suite.functions.__create_ss_dir import __create_ss_dir as create_ss_dir

class FileError(Exception):
    """Custom exception for File errors."""
    def __init__(self, message):
        super().__init__(f'FileError: {message}')

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
        """Initialize the File class."""
        try:
            self.__create_ss_dir = create_ss_dir
        except Exception as e:
            raise FileError(f"Error trying execute: {self.__init__.__name__}! {str(e)}.")

    def screen_shot(
        self,
        file_name: str = "screenshot",
        path_dir: str = None,
        save_with_date: bool = True,
        delay: int = 1,
        use_default_path_and_name: bool = True,
        name_ss_dir: str | None = None,
        verbose: bool = False,
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
        ``verbose`` - should be a boolean, by default `False`

        Return:
        ----------
        >>> type:str
            * 'screenshot_path': str - represents the absulute path created for this file

        Description: pt-br
        ----------
        Function responsible for creating a screenshot directory, and screenshot file and saving it in the directory to be created, if the directory exists, save it in the original directory. By default, uses date in the file name.

        Parameters:
        ----------
        ``file_name: str`` - should be a string, by default the name is `screenshot`.
        ``file_path: str`` - should be a string, has no default path.
        ``save_with_date: bool`` - should be a boolean, by default `True` saves the file name with date `foo_dd_mm_yyyy-hh_mm_ss.png`.
        ``delay: int`` - should be an int, by default 1 represented in second(s).
        ``use_default_path_and_name: bool`` - should be a boolean, by default `True`
        ``name_ss_dir: str`` - should be a string, by default of type `None`
        ``verbose`` - should be a boolean, by default `False`

        Return:
        ----------
        >>> type: str
            * 'screenshot_path': str - represents the absolute path of the created file
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

                if verbose:
                    success_print(path_file_screenshoted)
                return path_file_screenshoted

            else:  # not use date on file name
                image = pyautogui.screenshot()
                file_name = f"{file_name}.png"
                path_file_screenshoted = os.path.join(path_dir, file_name)

                image.save(path_file_screenshoted)

                if verbose:
                    success_print(path_file_screenshoted)
                return path_file_screenshoted

        except Exception as e:
            FileError(f"Error to execute function:{self.screen_shot.__name__}! Error: {str(e)}")

    def flag_create(
        self,
        name_file: str = "running.flag",
        path_to_create: str | None = None,
        verbose: bool = True,
    ) -> None:
        """
        Creates a flag file indicating that the robot is running.
        """

        try:
            if path_to_create is None:
                path_origin: str = os.getcwd()
                full_path_with_name = rf"{path_origin}/{name_file}"
            else:
                full_path_with_name = rf"{path_to_create}/{name_file}"

            with open(full_path_with_name, "w", encoding="utf-8") as file:
                file.write("[RPA Suite] - Running Flag File")
            if verbose:
                success_print("Flag file created.")

        except Exception as e:
            FileError(f"Error in function file_scheduling_create: {str(e)}")

    def flag_delete(
        self,
        name_file: str = "running.flag",
        path_to_delete: str | None = None,
        verbose: bool = True,
    ) -> None:
        """
        Deletes the flag file indicating that the robot has finished execution.
        """

        try:

            if path_to_delete is None:
                path_origin: str = os.getcwd()
                full_path_with_name = rf"{path_origin}/{name_file}"
            else:
                full_path_with_name = rf"{path_to_delete}/{name_file}"

            if os.path.exists(full_path_with_name):
                os.remove(full_path_with_name)
                if verbose:
                    success_print("Flag file deleted.")
            else:
                alert_print("Flag file not found.")

        except Exception as e:
            raise FileError(f"Error in function file_scheduling_delete: {str(e)}") from e

    def count_files(
        self,
        dir_to_count: List[str] = ["."],
        type_extension: str = "*",
        verbose: bool = False,
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

            if verbose:
                success_print(f'Function: {self.count_files.__name__} counted {result["qt"]} files.')

        except Exception as e:
            result["success"] = False
            FileError(f"Error when trying to count files! Error: {str(e)}")

        return result
