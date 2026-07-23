# rpa_suite/core/file.py

# imports standard
import os
import time
from datetime import datetime
from typing import Dict, List, Union

# imports third party
from colorama import Fore

from rpa_suite.functions.__create_ss_dir import __create_ss_dir as create_ss_dir

# imports internal
from rpa_suite.functions._printer import alert_print, success_print


class FileError(Exception):
    """Custom exception for File errors."""

    def __init__(self, message):
        clean_message = message.replace("FileError:", "").strip()
        super().__init__(f"FileError: {clean_message}")


class File:
    """
    Class for file management utilities: create/delete flag files, count files in directories, and take screenshots.

    Example:
        >>> from rpa_suite.core.file import File
        >>> file_util = File()
        >>> file_util.screen_shot('example')

    """

    def __init__(self):
        """
        Class for file management utilities: create/delete flag files, count files in directories, and take screenshots.

        Example:
            >>> from rpa_suite.core.file import File
            >>> file_util = File()
            >>> file_util.screen_shot('example')

        """
        try:
            self.__create_ss_dir = create_ss_dir
        except Exception as e:
            raise FileError(f"Error trying execute: {self.__init__.__name__}! {str(e)}.") from e

    def screen_shot(  # pylint: disable=too-many-positional-arguments
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
        Takes a screenshot and saves it to a directory. By default, uses the current date in the filename.

        Example:
            >>> file_util = File()
            >>> file_util.screen_shot('my_screenshot', save_with_date=True)

        """

        # proccess
        try:

            try:  # only to check if opencv, pillow allowed and installed
                import pyautogui  # pylint: disable=import-outside-toplevel
                import pyscreeze  # pylint: disable=unused-import,import-outside-toplevel

            except ImportError as e:
                raise ImportError(
                    f"\nThe 'pyautogui' e 'Pillow' libraries are necessary to use this module. {Fore.YELLOW}Please install them with: 'pip install pyautogui pillow'{Fore.WHITE}"
                ) from e

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

            # not use date on file name
            image = pyautogui.screenshot()
            file_name = f"{file_name}.png"
            path_file_screenshoted = os.path.join(path_dir, file_name)

            image.save(path_file_screenshoted)

            if verbose:
                success_print(path_file_screenshoted)
            return path_file_screenshoted

        except Exception as e:
            raise FileError(f"Error to execute function:{self.screen_shot.__name__}! Error: {str(e)}") from e

    def flag_create(
        self,
        name_file: str = "running.flag",
        path_to_create: str | None = None,
        verbose: bool = True,
    ) -> None:
        """
        Creates a flag file to indicate the robot is running.

        Example:
            >>> file_util = File()
            >>> file_util.flag_create('my.flag')

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
            raise FileError(f"Error in function file_scheduling_create: {str(e)}") from e

    def flag_delete(
        self,
        name_file: str = "running.flag",
        path_to_delete: str | None = None,
        verbose: bool = True,
    ) -> None:
        """
        Deletes the flag file to indicate the robot has finished.

        Example:
            >>> file_util = File()
            >>> file_util.flag_delete('my.flag')

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
        dir_to_count: List[str] | None = None,
        type_extension: str = "*",
        verbose: bool = False,
    ) -> Dict[str, Union[bool, int]]:
        """
        Counts files in one or more directories, optionally filtering by extension.

        Example:
            >>> file_util = File()
            >>> file_util.count_files(['./myfolder'], type_extension='txt')

        """

        # Local Variables
        result: dict = {"success": False, "qt": 0}

        # Process
        try:
            # by default, search in the current directory
            if not dir_to_count:
                dir_to_count = ["."]

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
            raise FileError(f"Error when trying to count files! Error: {str(e)}") from e

        return result
