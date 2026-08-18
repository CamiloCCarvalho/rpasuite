# rpa_suite/core/file.py

# imports standard
import csv
import os
import shutil
import time
import zipfile
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union
from urllib.parse import unquote, urlparse

# imports third party
import requests
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

            try:  # pyautogui (screenshot) and Pillow/pyscreeze
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

    def wait_for_file(
        self,
        file_path: str,
        timeout: float = 60.0,
        poll_interval: float = 0.5,
        stable_for: float = 1.0,
        verbose: bool = False,
    ) -> Dict[str, Union[bool, str, int, float]]:
        """
        Wait for a file to exist and have a stable size (useful for downloads).

        Parameters:
        ----------
        file_path : str
            Absolute or relative path to the file being monitored.
        timeout : float
            Maximum seconds to wait before giving up. Must be > 0.
        poll_interval : float
            Seconds between checks. Must be > 0.
        stable_for : float
            The file size must remain unchanged for at least this many seconds
            before we consider the file "ready" (avoids reading half-written
            downloads). Set to 0 to skip stability checks.
        verbose : bool
            If True, prints a success/timeout summary.

        Returns:
        ----------
        dict with:
            * 'success' (bool): whether the file appeared and stabilized in time.
            * 'path' (str): the path checked.
            * 'size' (int): last observed file size in bytes (0 if not found).
            * 'waited' (float): seconds actually waited.
        """
        if timeout <= 0 or poll_interval <= 0:
            raise FileError("`timeout` and `poll_interval` must be > 0")

        start = time.time()
        result: Dict[str, Union[bool, str, int, float]] = {
            "success": False,
            "path": file_path,
            "size": 0,
            "waited": 0.0,
        }

        last_size: Optional[int] = None
        stable_since: Optional[float] = None
        try:
            while (time.time() - start) < timeout:
                if os.path.isfile(file_path):
                    try:
                        current = os.path.getsize(file_path)
                    except OSError:
                        current = None
                    if current is not None:
                        result["size"] = current
                        if stable_for <= 0:
                            result["success"] = True
                            break
                        now = time.time()
                        if last_size is None or current != last_size:
                            last_size = current
                            stable_since = now
                        elif stable_since is not None and (now - stable_since) >= stable_for:
                            result["success"] = True
                            break
                time.sleep(poll_interval)

            result["waited"] = time.time() - start

            if verbose:
                if result["success"]:
                    success_print(
                        f"File ready: {file_path} ({result['size']} bytes, " f"waited {result['waited']:.2f}s)"
                    )
                else:
                    alert_print(f"Timed out waiting for file: {file_path} (waited {result['waited']:.2f}s)")

            return result

        except Exception as e:
            raise FileError(f"Error waiting for file '{file_path}': {str(e)}") from e

    def read_csv(
        self,
        file_path: str,
        delimiter: str = ",",
        encoding: str = "utf-8",
        as_dict: bool = True,
        **reader_kwargs: Any,
    ) -> List[Dict[str, str] | List[str]]:
        """
        Read a CSV file using the stdlib `csv` module (no pandas required).

        Parameters:
        ----------
        file_path : str
            Path to the CSV file.
        delimiter : str
            Field delimiter (default ",").
        encoding : str
            File encoding (default "utf-8").
        as_dict : bool
            If True (default), use `csv.DictReader` and return `list[dict]`
            keyed by the header row. If False, return `list[list[str]]`.
        **reader_kwargs :
            Extra keyword arguments forwarded to the underlying reader.

        Returns:
        ----------
        list of rows (dicts or lists depending on `as_dict`).
        """
        try:
            with open(file_path, encoding=encoding, newline="") as f:
                if as_dict:
                    reader = csv.DictReader(f, delimiter=delimiter, **reader_kwargs)
                    return [dict(row) for row in reader]
                reader = csv.reader(f, delimiter=delimiter, **reader_kwargs)
                return [list(row) for row in reader]
        except Exception as e:
            raise FileError(f"Error reading CSV '{file_path}': {str(e)}") from e

    def write_csv(
        self,
        file_path: str,
        rows: Iterable[Dict[str, Any] | Sequence[Any]],
        headers: Optional[Sequence[str]] = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
        append: bool = False,
    ) -> str:
        """
        Write rows to a CSV file using the stdlib `csv` module.

        Parameters:
        ----------
        file_path : str
            Destination path.
        rows : iterable
            Iterable of dicts (uses `csv.DictWriter`) or sequences
            (uses `csv.writer`). If both `headers` are provided and rows are
            sequences, `headers` is written as the first line.
        headers : sequence of str, optional
            Column names. Required when rows are dicts (unless the first row's
            keys are used) or when writing a header for sequence rows.
        delimiter : str
            Field delimiter (default ",").
        encoding : str
            File encoding (default "utf-8").
        append : bool
            If True, appends to the file (headers are only written for a new file).

        Returns:
        ----------
        The absolute path of the written file.
        """
        mode = "a" if append else "w"
        file_is_new = not (append and os.path.isfile(file_path))
        try:
            rows = list(rows)
            with open(file_path, mode, encoding=encoding, newline="") as f:
                if rows and isinstance(rows[0], dict):
                    dict_headers = list(headers) if headers else list(rows[0].keys())
                    writer = csv.DictWriter(f, fieldnames=dict_headers, delimiter=delimiter)
                    if file_is_new:
                        writer.writeheader()
                    writer.writerows(rows)
                else:
                    writer = csv.writer(f, delimiter=delimiter)
                    if headers and file_is_new:
                        writer.writerow(list(headers))
                    writer.writerows(rows)
            return os.path.abspath(file_path)
        except Exception as e:
            raise FileError(f"Error writing CSV '{file_path}': {str(e)}") from e

    def copy(
        self,
        src: str,
        dst: str,
        overwrite: bool = True,
        verbose: bool = False,
    ) -> str:
        """
        Copy a file or directory to ``dst``. Directories are copied recursively.

        Returns the absolute destination path.
        """
        try:
            src_abs = os.path.abspath(src)
            dst_abs = os.path.abspath(dst)
            if not os.path.exists(src_abs):
                raise FileError(f"Source does not exist: '{src_abs}'.")

            if os.path.isdir(dst_abs):
                dst_abs = os.path.join(dst_abs, os.path.basename(src_abs))

            if os.path.exists(dst_abs) and not overwrite:
                raise FileError(f"Destination already exists: '{dst_abs}'.")

            parent = os.path.dirname(dst_abs)
            if parent:
                os.makedirs(parent, exist_ok=True)

            if os.path.isdir(src_abs):
                if os.path.exists(dst_abs):
                    shutil.rmtree(dst_abs)
                shutil.copytree(src_abs, dst_abs)
            else:
                shutil.copy2(src_abs, dst_abs)

            if verbose:
                success_print(f"Copied '{src_abs}' -> '{dst_abs}'.")
            return dst_abs
        except FileError:
            raise
        except Exception as e:
            raise FileError(f"Error copying '{src}' to '{dst}': {str(e)}") from e

    def move(
        self,
        src: str,
        dst: str,
        overwrite: bool = True,
        verbose: bool = False,
    ) -> str:
        """
        Move a file or directory to ``dst``.

        Returns the absolute destination path.
        """
        try:
            src_abs = os.path.abspath(src)
            dst_abs = os.path.abspath(dst)
            if not os.path.exists(src_abs):
                raise FileError(f"Source does not exist: '{src_abs}'.")

            if os.path.isdir(dst_abs):
                dst_abs = os.path.join(dst_abs, os.path.basename(src_abs))

            if os.path.exists(dst_abs):
                if not overwrite:
                    raise FileError(f"Destination already exists: '{dst_abs}'.")
                if os.path.isdir(dst_abs) and not os.path.islink(dst_abs):
                    shutil.rmtree(dst_abs)
                else:
                    os.remove(dst_abs)

            parent = os.path.dirname(dst_abs)
            if parent:
                os.makedirs(parent, exist_ok=True)

            shutil.move(src_abs, dst_abs)
            if verbose:
                success_print(f"Moved '{src_abs}' -> '{dst_abs}'.")
            return dst_abs
        except FileError:
            raise
        except Exception as e:
            raise FileError(f"Error moving '{src}' to '{dst}': {str(e)}") from e

    def zip_path(
        self,
        source: str,
        archive_path: str | None = None,
        verbose: bool = False,
    ) -> str:
        """
        Zip a file or folder. If ``archive_path`` is omitted, uses ``<source>.zip``.

        Returns the absolute path of the created archive.
        """
        try:
            source_abs = os.path.abspath(source)
            if not os.path.exists(source_abs):
                raise FileError(f"Source does not exist: '{source_abs}'.")

            if archive_path is None:
                archive_path = source_abs.rstrip("\\/") + ".zip"
            archive_abs = os.path.abspath(archive_path)
            parent = os.path.dirname(archive_abs)
            if parent:
                os.makedirs(parent, exist_ok=True)

            if os.path.isdir(source_abs):
                base, ext = os.path.splitext(archive_abs)
                if ext.lower() != ".zip":
                    base = archive_abs
                created = shutil.make_archive(
                    base,
                    "zip",
                    root_dir=os.path.dirname(source_abs),
                    base_dir=os.path.basename(source_abs),
                )
                created_abs = os.path.abspath(created)
                if created_abs != archive_abs:
                    if os.path.exists(archive_abs):
                        os.remove(archive_abs)
                    shutil.move(created_abs, archive_abs)
                    created_abs = archive_abs
            else:
                with zipfile.ZipFile(archive_abs, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                    zf.write(source_abs, arcname=os.path.basename(source_abs))
                created_abs = archive_abs

            if verbose:
                success_print(f"Archive created: '{created_abs}'.")
            return created_abs
        except FileError:
            raise
        except Exception as e:
            raise FileError(f"Error zipping '{source}': {str(e)}") from e

    def unzip_path(
        self,
        archive_path: str,
        dest_dir: str | None = None,
        verbose: bool = False,
    ) -> str:
        """
        Extract a zip archive. Default destination is the folder of the zip file.

        Returns the absolute extraction directory.
        """
        try:
            archive_abs = os.path.abspath(archive_path)
            if not os.path.isfile(archive_abs):
                raise FileError(f"Archive does not exist: '{archive_abs}'.")

            dest_abs = os.path.abspath(dest_dir) if dest_dir else os.path.dirname(archive_abs)
            os.makedirs(dest_abs, exist_ok=True)

            with zipfile.ZipFile(archive_abs, "r") as zf:
                for member in zf.infolist():
                    target = os.path.abspath(os.path.join(dest_abs, member.filename))
                    if target != dest_abs and not target.startswith(dest_abs + os.sep):
                        raise FileError(f"Unsafe zip entry blocked: '{member.filename}'.")
                zf.extractall(dest_abs)

            if verbose:
                success_print(f"Extracted '{archive_abs}' -> '{dest_abs}'.")
            return dest_abs
        except FileError:
            raise
        except Exception as e:
            raise FileError(f"Error unzipping '{archive_path}': {str(e)}") from e

    def download(
        self,
        url: str,
        dest: str | None = None,
        timeout: float = 60.0,
        chunk_size: int = 8192,
        verbose: bool = False,
    ) -> str:
        """
        Download ``url`` to disk with ``requests``.

        If ``dest`` is omitted or is a directory, the filename is taken from the URL path.

        Returns the absolute path of the saved file.
        """
        try:
            parsed = urlparse(url)
            url_name = unquote(os.path.basename(parsed.path)) or "download.bin"

            if dest is None:
                dest_abs = os.path.abspath(url_name)
            else:
                dest_abs = os.path.abspath(dest)
                if os.path.isdir(dest_abs) or dest.endswith(("/", "\\")):
                    dest_abs = os.path.join(dest_abs, url_name)

            parent = os.path.dirname(dest_abs)
            if parent:
                os.makedirs(parent, exist_ok=True)

            with requests.get(url, stream=True, timeout=timeout) as response:
                response.raise_for_status()
                with open(dest_abs, "wb") as out:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            out.write(chunk)

            if verbose:
                success_print(f"Downloaded '{url}' -> '{dest_abs}'.")
            return dest_abs
        except FileError:
            raise
        except Exception as e:
            raise FileError(f"Error downloading '{url}': {str(e)}") from e

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
