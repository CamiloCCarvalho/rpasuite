# rpa_suite/core/dir.py

# imports standard
import os
import shutil
from typing import Union

# imports internal
from rpa_suite.functions._printer import alert_print, success_print


class DirectoryError(Exception):
    """Custom exception for Directory errors."""

    def __init__(self, message):
        clean_message = message.replace("DirectoryError:", "").strip()
        super().__init__(f"DirectoryError: {clean_message}")


class Directory:
    """
    Class that provides utilities for directory management, including creating, deleting, and manipulating directories.

    This class offers functionalities for:
        - Creating temporary directories
        - Deleting directories
        - Checking if a directory exists
        - Listing files in a directory

    Methods:
        create_temp_dir: Creates a temporary directory for file operations.

    The Directory class is part of RPA Suite and can be accessed through the rpa object:
        >>> from rpa_suite import rpa
        >>> rpa.directory.create_temp_dir(path_to_create='my_folder', name_temp_dir='temp_dir')

    Parameters:
        path_to_create (str): The full path where the temporary directory should be created. Default is 'default', which creates it in the current directory.
        name_temp_dir (str): The name of the temporary directory to be created. Default is 'temp'.
    """

    def __init__(self):
        """
        Constructor function of the Class that provides utilities for directory management,
        including creation, deletion and manipulation of directories.
        """
        try:
            pass
        except Exception as e:
            raise DirectoryError(f"Error trying execute: {self.__init__.__name__}! {str(e)}.") from e

    def create_temp_dir(
        self,
        path_to_create: str = "default",
        name_temp_dir: str = "temp",
        display_message: bool = False,
    ) -> dict[str, Union[bool, str, None]]:
        """
        Creates a temporary directory for file operations.

        Parameters:
        -----------
        path_to_create : str, optional
            Full path pointing to the folder where the temporary folder should be created.
            If "default" (or empty), creates the folder in the current directory.
            Default: "default".

        name_temp_dir : str, optional
            Name of the temporary directory to be created. Default: "temp".

        display_message : bool, optional
            Whether to display success messages on terminal. Default: False.

        Returns:
        --------
        dict[str, Union[bool, str, None]]
            Dictionary containing:
            - 'success' (bool): Indicates if the action was performed successfully
            - 'path_created' (str | None): Path of the directory that was created, or None if failed
        """

        # Local Variables
        result: dict = {  # pylint: disable=duplicate-code
            "success": bool,
            "path_created": str,
        }

        try:
            # by 'default', defines path to local script execution path
            if path_to_create == "default":  # pylint: disable=duplicate-code
                path_to_create: str = os.getcwd()

            # Build path to new dir
            full_path: str = os.path.join(path_to_create, name_temp_dir)

            # Create dir in this block
            try:
                # Successefully created
                os.makedirs(full_path, exist_ok=False)

                result["success"] = True
                result["path_created"] = rf"{full_path}"

                if display_message:
                    success_print(f"Directory:'{full_path}' successfully created.")

            except FileExistsError as e:
                result["success"] = False
                result["path_created"] = None
                if display_message:
                    raise DirectoryError(f"Directory:'{full_path}' already exists.") from e

            except PermissionError as e:
                result["success"] = False
                result["path_created"] = None
                if display_message:
                    raise DirectoryError(f"Permission denied: Not possible to create Directory '{full_path}'.") from e

        except Exception as e:
            result["success"] = False
            result["path_created"] = None
            raise DirectoryError(f"Error trying execute: {self.create_temp_dir.__name__}! {str(e)}.") from e

        return result

    def delete_temp_dir(
        self,
        path_to_delete: str = "default",
        name_temp_dir: str = "temp",
        delete_files: bool = False,
        display_message: bool = False,
    ) -> dict[str, Union[bool, str, None]]:
        """
        Deletes a temporary directory.

        Parameters:
        -----------
        path_to_delete : str, optional
            Full path pointing to the folder where the temporary folder should be deleted.
            If "default" (or empty), deletes the folder in the current directory.
            Default: "default".

        name_temp_dir : str, optional
            Name of the temporary directory to be deleted. Default: "temp".

        delete_files : bool, optional
            Whether to delete files in the directory. If False, only the empty directory is deleted.
            Default: False.

        display_message : bool, optional
            Whether to display success messages on terminal. Default: False.

        Returns:
        --------
        dict[str, Union[bool, str, None]]
            Dictionary containing:
            - 'success' (bool): Indicates if the action was performed successfully
            - 'path_deleted' (str | None): Path of the directory that was deleted, or None if failed
        """

        # Local Variables
        result: dict = {  # pylint: disable=duplicate-code
            "success": bool,
            "path_deleted": str,
        }

        try:
            # by 'default', defines path to local script execution path
            if path_to_delete == "default":  # pylint: disable=duplicate-code
                path_to_delete: str = os.getcwd()

            # Build path to new dir
            full_path: str = os.path.join(path_to_delete, name_temp_dir)

            # Delete dir in this block
            try:
                # Check if directory exists
                if os.path.exists(full_path):

                    # Check if delete_files is True
                    if delete_files:
                        # Delete all files in the directory
                        shutil.rmtree(full_path)

                    else:
                        # Delete the directory only
                        os.rmdir(full_path)

                    result["success"] = True
                    result["path_deleted"] = rf"{full_path}"

                    if display_message:
                        success_print(f"Directory:'{full_path}' successfully deleted.")
                else:
                    result["success"] = False
                    result["path_deleted"] = None
                    if display_message:
                        alert_print(f"Directory:'{full_path}' doesn't exist.")

            except PermissionError as e:
                result["success"] = False
                result["path_deleted"] = None
                if display_message:
                    raise DirectoryError(f"Permission denied: Not possible to delete Directory '{full_path}'.") from e

            except OSError as e:
                result["success"] = False
                result["path_deleted"] = None
                if display_message:
                    raise DirectoryError(f"OS error occurred while deleting directory '{full_path}': {str(e)}") from e

        except Exception as e:
            result["success"] = False
            result["path_deleted"] = None
            raise DirectoryError(f"Error trying execute: {self.delete_temp_dir.__name__}! {str(e)}.") from e

        return result
