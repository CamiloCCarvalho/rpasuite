# rpa_suite/core/dir.py

# imports standard
import os
import shutil
from contextlib import contextmanager
from typing import Iterator, Union

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

    def _resolve_base_path(self, path: str | None) -> str:
        if path is None or path in ("default", ""):
            return os.getcwd()
        return path

    def ensure_dir(self, path: str, display_message: bool = False) -> str:
        """
        Create ``path`` (and parents) if it does not exist. Safe to call when it already exists.

        Returns the absolute path created/ensured.
        """
        try:
            full_path = os.path.abspath(path)
            os.makedirs(full_path, exist_ok=True)
            if display_message:
                success_print(f"Directory:'{full_path}' is ready.")
            return full_path
        except Exception as e:
            raise DirectoryError(f"Error trying execute: {self.ensure_dir.__name__}! {str(e)}.") from e

    def create_temp_dir(
        self,
        path_to_create: str = "default",
        name_temp_dir: str = "temp",
        display_message: bool = False,
        exist_ok: bool = True,
    ) -> dict[str, Union[bool, str, None]]:
        """
        Function responsible for creating a temporary directory to work with files and etc.

        Parameters:
        ----------
        ``path_to_create: str`` - should be a string with the full path pointing to the folder where the temporary folder should be created, if it is empty the ``default`` value will be used which will create a folder in the current directory where the file containing this function was called.

        ``name_temp_dir: str`` - should be a string representing the name of the temporary directory to be created. If it is empty, the ``temp`` value will be used as the default directory name.

        ``display_message: bool`` - should be a bool to display messages on terminal, by default False.

        ``exist_ok: bool`` - if True (default), reuse the directory when it already exists.
            Pass False to restore the previous fail-if-exists behaviour.

        Return:
        ----------
        >>> type:dict
            * 'success': bool - represents case the action was performed successfully
            * 'path_created': str - path of the directory that was created on the process
        """

        result: dict = {  # pylint: disable=duplicate-code
            "success": False,
            "path_created": None,
        }

        try:
            path_to_create = self._resolve_base_path(path_to_create)
            full_path: str = os.path.join(path_to_create, name_temp_dir)

            try:
                os.makedirs(full_path, exist_ok=exist_ok)

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

        except DirectoryError:
            raise
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
        Function responsible for deleting a temporary directory.

        Parameters:
        ----------
        ``path_to_delete: str`` - should be a string with the full path pointing to the folder where the temporary folder should be deleted, if it is empty the ``default`` value will be used which will delete a folder in the current directory where the file containing this function was called.

        ``name_temp_dir: str`` - should be a string representing the name of the temporary directory to be deleted. If it is empty, the ``temp`` value will be used as the default directory name.

        ``delete_files: bool`` - should be a boolean indicating whether to delete files in the directory. If it is False, files in the directory will not be deleted.

        Return:
        ----------
        >>> type:dict
            * 'success': bool - represents case the action was performed successfully
            * 'path_deleted': str - path of the directory that was deleted on the process
        """

        result: dict = {  # pylint: disable=duplicate-code
            "success": False,
            "path_deleted": None,
        }

        try:
            path_to_delete = self._resolve_base_path(path_to_delete)

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

    def clear_dir(self, path: str, display_message: bool = False) -> dict[str, Union[bool, str, int]]:
        """
        Remove files and subfolders inside ``path`` but keep the directory itself.

        Returns:
            dict with ``success``, ``path`` and ``removed`` (number of entries deleted).
        """
        result: dict[str, Union[bool, str, int]] = {"success": False, "path": path, "removed": 0}
        try:
            full_path = os.path.abspath(path)
            if not os.path.isdir(full_path):
                raise DirectoryError(f"Directory does not exist: '{full_path}'.")

            removed = 0
            for name in os.listdir(full_path):
                entry = os.path.join(full_path, name)
                if os.path.isdir(entry) and not os.path.islink(entry):
                    shutil.rmtree(entry)
                else:
                    os.remove(entry)
                removed += 1

            result["success"] = True
            result["path"] = full_path
            result["removed"] = removed
            if display_message:
                success_print(f"Directory:'{full_path}' cleared ({removed} entries).")
            return result
        except DirectoryError:
            raise
        except Exception as e:
            raise DirectoryError(f"Error trying execute: {self.clear_dir.__name__}! {str(e)}.") from e

    @contextmanager
    def temp_dir(
        self,
        path_to_create: str = "default",
        name_temp_dir: str = "temp",
        delete_on_exit: bool = True,
        exist_ok: bool = True,
        display_message: bool = False,
    ) -> Iterator[str]:
        """
        Context manager: create a temp folder, yield its path, then optionally delete it.

        Example:
            >>> from rpa_suite import rpa
            >>> with rpa.directory.temp_dir() as path:
            ...     # download PDFs into `path`
            ...     pass
        """
        created = self.create_temp_dir(
            path_to_create=path_to_create,
            name_temp_dir=name_temp_dir,
            display_message=display_message,
            exist_ok=exist_ok,
        )
        path = created.get("path_created")
        if not path:
            raise DirectoryError("Failed to create temporary directory.")
        try:
            yield str(path)
        finally:
            if delete_on_exit:
                self.delete_temp_dir(
                    path_to_delete=path_to_create,
                    name_temp_dir=name_temp_dir,
                    delete_files=True,
                    display_message=display_message,
                )
