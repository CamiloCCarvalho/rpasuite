# rpa_suite/core/log.py

# imports internal
from rpa_suite.functions._printer import alert_print, success_print

# imports third party
from loguru import logger

# imports standard
from typing import Optional as Op
import sys
import os
import inspect
import traceback

class LogFiltersError(Exception):
    """Custom exception for LogFilters errors."""
    def __init__(self, message):
        clean_message = message.replace("LogFilters Error:", "").strip()
        super().__init__(f'LogFilters Error: {clean_message}')

class LogCustomHandlerError(Exception):
    """Custom exception for LogCustomHandler errors."""
    def __init__(self, message):
        clean_message = message.replace("LogCustomHandler Error:", "").strip()
        super().__init__(f'LogCustomHandler Error: {clean_message}')

class LogCustomFormatterError(Exception):
    """Custom exception for LogCustomFormatter errors."""
    def __init__(self, message):
        clean_message = message.replace("LogCustomFormatter Error:", "").strip()
        super().__init__(f'LogCustomFormatter Error: {clean_message}')

class LogError(Exception):
    """Custom exception for Log errors."""
    def __init__(self, message):
        clean_message = message.replace("Log Error:", "").strip()
        super().__init__(f'Log Error: {clean_message}')

class Filters:
    """
    Filter class for log messages based on word filtering.
    """
    word_filter: Op[list[str]]

    def __call__(self, record: dict[str, str]):
        try:
            if self.word_filter and len(self.word_filter) > 0:
                message = record["message"]
                for words in self.word_filter:
                    string_words: list[str] = [str(word) for word in words]
                    for word in string_words:
                        if word in message:
                            record["message"] = message.replace(word, "***")
                return True
            return True
        except Exception as e:
            raise LogFiltersError(f"Error trying execute: {self.__call__.__name__}! {str(e)}.")

class CustomHandler:
    """
    Custom handler for log messages with formatting capabilities.
    """
    def __init__(self, formatter):
        self.formatter = formatter

    def write(self, message):
        try:
            frame = inspect.currentframe().f_back.f_back
            log_msg = self.formatter.format(message, frame)
            sys.stderr.write(log_msg)
        except Exception as e:
            raise LogCustomHandlerError(f"Error trying execute: {self.write.__name__}! {str(e)}.")

class CustomFormatter:
    """
    Custom formatter for log messages with specific formatting rules.
    """
    def format(self, record):
        try:
            filename = record["extra"].get("filename", "")
            lineno = record["extra"].get("lineno", "")
            format_string = "<green>{time:DD.MM.YY.HH:mm}</green> <level>{level: <8}</level> <green>{filename}</green>:<cyan>{lineno: <4}</cyan> <level>{message}</level>\n"
            log_msg = format_string.format(
                time=record["time"],
                level=record["level"].name,
                filename=filename,
                lineno=lineno,
                message=record["message"],
            )
            return log_msg
        except Exception as e:
            raise LogCustomFormatterError(f"Error trying execute: {self.format.__name__}! {str(e)}.")

class Log:
    """
    Main logging class providing comprehensive logging functionality.
    """
    filters: Filters
    custom_handler: CustomHandler
    custom_formatter: CustomFormatter
    path_dir: str | None = None
    name_file_log: str | None = None
    full_path: str | None = None
    file_handler = None
    enable_traceback: bool = False  # NEW PROPERTY

    def __init__(self):
        """
        Initialize the Log class with default loguru logger.
        """
        try:
            self.logger = logger
        except Exception as e:
            raise LogError(f"Error trying execute: {self.__init__.__name__}! {str(e)}.")

    def config_logger(
        self,
        path_dir: str = "default",
        name_log_dir: str = "logs",
        name_file_log: str = "log",
        filter_words: list[str] = None,
        display_message: bool = False,
        enable_traceback: bool = False,  # NEW PARAMETER
    ):
        """
        Configure the logger with specified parameters.
        
        Args:
            path_dir: Directory path for log files
            name_log_dir: Name of the log directory
            name_file_log: Name of the log file
            filter_words: List of words to filter from logs
            display_message: Whether to display configuration messages
            enable_traceback: Whether to include traceback in error logs
        """
        try:
            self.path_dir = path_dir
            self.name_file_log = name_file_log
            self.enable_traceback = enable_traceback  # CONFIGURE THE PROPERTY

            if self.path_dir == "default":
                self.path_dir = os.getcwd()

            full_path = os.path.join(self.path_dir, name_log_dir)
            self.full_path = full_path

            try:
                os.makedirs(self.full_path, exist_ok=True)
                if display_message:
                    success_print(f"Directory:'{self.full_path}' was created successfully.")
            except FileExistsError:
                if display_message:
                    alert_print(f"Directory:'{self.full_path}' already exists.")
            except PermissionError:
                LogError(f"Permission denied: cannot create directory '{self.full_path}'.")

            new_filter = None
            if filter_words is not None:
                new_filter = Filters()
                new_filter.word_filter = [filter_words]

            file_handler = os.path.join(self.full_path, f"{self.name_file_log}.log")
            self.logger.remove()

            log_format = "<green>{time:DD.MM.YY.HH:mm}</green> <level>{level: <8}</level> <green>{extra[filename]}</green>:<cyan>{extra[lineno]: <4}</cyan> <level>{message}</level>"

            formatter = CustomFormatter()

            if new_filter:
                self.logger.add(file_handler, filter=new_filter, level="DEBUG", format=log_format)
            else:
                self.logger.add(file_handler, level="DEBUG", format=log_format)

            self.logger.add(sys.stderr, level="DEBUG", format=formatter.format)
            self.file_handler = file_handler
            return file_handler

        except Exception as e:
            raise LogError(f"Error trying execute: {self.config_logger.__name__}! {str(e)}.")

    def _escape_traceback(self, tb_string: str) -> str:
        """
        Escape special characters in traceback to avoid conflicts with Loguru colorizer.
        """
        try:
        # Escape characters that might be interpreted as color tags
            escaped = tb_string.replace('<', '\\<').replace('>', '\\>')
            return escaped
        except Exception as e:
            raise LogError(f"Error trying execute: {self._escape_traceback.__name__}! {str(e)}.")
    
    def _log(self, level: str, msg: str):
        """
        Method to generate logs used from self.
        """
        try:
            # Find the first frame that's not from this log.py file
            frame = inspect.currentframe()
            current_file = os.path.normpath(__file__)

            while frame:
                frame = frame.f_back
                if frame and os.path.normpath(frame.f_code.co_filename) != current_file:
                    break

            if not frame:
                # Fallback if we can't find external caller
                frame = inspect.currentframe().f_back.f_back

            full_path_filename = frame.f_code.co_filename
            full_path_filename = os.path.normpath(full_path_filename)
            parent_folder = os.path.basename(os.path.dirname(full_path_filename))
            file_name = os.path.basename(full_path_filename)
            display_filename = f"{parent_folder}/{file_name}"
            lineno = frame.f_lineno

            # IF TRACEBACK IS ENABLED AND IT'S ERROR LEVEL, ADD TRACEBACK
            if self.enable_traceback and level in ["ERROR", "CRITICAL"]:
                try:
                    # Capture current traceback if there's an active exception
                    tb_string = traceback.format_exc()
                    if tb_string != "NoneType: None\n":  # Check if there's real traceback
                        # ESCAPE SPECIAL CHARACTERS IN TRACEBACK
                        escaped_traceback = self._escape_traceback(tb_string)
                        msg = f"{msg}\n{escaped_traceback}"
                except Exception:
                    # If can't capture traceback, continue normally
                    pass

            self.logger.bind(filename=display_filename, lineno=lineno).log(level, msg)
        except Exception as e:
            raise LogError(f"Error trying execute: {self._log.__name__}! {str(e)}.")

    def log_start_run_debug(self, msg_start_loggin: str) -> None:
        """
        Log a debug message to start a new run session.
        """
        try:
            with open(self.file_handler, "a") as log_file:
                log_file.write("\n")
            self._log("DEBUG", msg_start_loggin)
        except Exception as e:
            raise LogError(
                f"Error trying execute: {self.log_start_run_debug.__name__}! see log directory and configuration to config_logger: {str(e)}."
            )

    def log_debug(self, msg: str) -> None:
        """Log a debug level message."""
        self._log("DEBUG", msg)

    def log_info(self, msg: str) -> None:
        """Log an info level message."""
        self._log("INFO", msg)

    def log_warning(self, msg: str) -> None:
        """Log a warning level message."""
        self._log("WARNING", msg)

    def log_error(self, msg: str) -> None:
        """Log an error level message."""
        self._log("ERROR", msg)

    def log_critical(self, msg: str) -> None:
        """Log a critical level message."""
        self._log("CRITICAL", msg)