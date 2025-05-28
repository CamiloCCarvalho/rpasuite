# rpa_suite/core/log.py

# imports internal
from rpa_suite.functions._printer import error_print, alert_print, success_print

# imports external
from loguru import logger

# imports third-party
from typing import Optional as Op
import sys, os, inspect


class Filters:
    word_filter: Op[list[str]]

    def __call__(self, record):
        if self.word_filter and len(self.word_filter) > 0:
            for words in self.word_filter:
                string_words: list[str] = [str(word) for word in words]
                for word in string_words:
                    if word in record["message"]:
                        record["message"] = "Log Alterado devido a palavra Filtrada!"
                        return True
        return True


class CustomHandler:
    def __init__(self, formatter):
        self.formatter = formatter

    def write(self, message):
        frame = inspect.currentframe().f_back.f_back
        log_msg = self.formatter.format(message, frame)
        sys.stderr.write(log_msg)


class CustomFormatter:
    def format(self, record):
        # Use the info from record["extra"] which is set in Log._log to the caller's file and line
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


class Log:
    filters: Filters
    custom_handler: CustomHandler
    custom_formatter: CustomFormatter
    path_dir: str | None = None
    name_file_log: str | None = None
    full_path: str | None = None
    file_handler = None

    def __init__(self):
        self.logger = logger

    def config_logger(
        self,
        path_dir: str = "default",
        name_log_dir: str = "Logs",
        name_file_log: str = "log",
        filter_words: list[str] = None,
    ):
        try:
            self.path_dir = path_dir
            self.name_file_log = name_file_log

            if self.path_dir == "default":
                self.path_dir = os.getcwd()

            full_path = os.path.join(self.path_dir, name_log_dir)
            self.full_path = full_path

            try:
                os.makedirs(self.full_path, exist_ok=True)
                success_print(f"Diretório:'{self.full_path}' foi criado com sucesso.")
            except FileExistsError:
                alert_print(f"Diretório:'{self.full_path}' já existe.")
            except PermissionError:
                alert_print(
                    f"Permissão negada: não é possível criar o diretório '{self.full_path}'."
                )

            new_filter = None
            if filter_words is not None:
                new_filter = Filters()
                new_filter.word_filter = [filter_words]

            file_handler = os.path.join(self.full_path, f"{self.name_file_log}.log")
            self.logger.remove()

            log_format = "<green>{time:DD.MM.YY.HH:mm}</green> <level>{level: <8}</level> <green>{extra[filename]}</green>:<cyan>{extra[lineno]: <4}</cyan> <level>{message}</level>"

            formatter = CustomFormatter()

            if new_filter:
                self.logger.add(
                    file_handler, filter=new_filter, level="DEBUG", format=log_format
                )
            else:
                self.logger.add(file_handler, level="DEBUG", format=log_format)

            self.logger.add(sys.stderr, level="DEBUG", format=formatter.format)
            self.file_handler = file_handler
            return file_handler

        except Exception as e:
            error_print(
                f"Houve um erro durante a execução da função: {self.config_logger.__name__}! Error: {str(e)}."
            )
            return None

    def _log(self, level: str, msg: str):
        """
        docstring
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

            # Normalize path to use os.sep
            full_path_filename = os.path.normpath(full_path_filename)

            # Get the last two components: parent folder and filename
            parent_folder = os.path.basename(os.path.dirname(full_path_filename))
            file_name = os.path.basename(full_path_filename)
            display_filename = f"{parent_folder}/{file_name}"

            lineno = frame.f_lineno

            self.logger.bind(filename=display_filename, lineno=lineno).log(level, msg)
        except Exception as e:
            error_print(f"Erro durante a função de log! Error: {str(e)}")

    def log_start_run_debug(self, msg_start_loggin: str) -> None:
        try:
            with open(self.file_handler, "a") as log_file:
                log_file.write(
                    "\n"
                )  # Add a blank line before logging the start message
            self._log("DEBUG", msg_start_loggin)
        except Exception as e:
            error_print(
                f"Erro fn: {self.log_start_run_debug.__name__} ao tentar acessar o arquivo de log Confira se foi criado a configuração de log correta com a função config_logger e se a pasta e arquivo estão nos diretório desejado! Error: {str(e)}."
            )

    def log_debug(self, msg: str) -> None:
        self._log("DEBUG", msg)

    def log_info(self, msg: str) -> None:
        self._log("INFO", msg)

    def log_warning(self, msg: str) -> None:
        self._log("WARNING", msg)

    def log_error(self, msg: str) -> None:
        self._log("ERROR", msg)

    def log_critical(self, msg: str) -> None:
        self._log("CRITICAL", msg)
