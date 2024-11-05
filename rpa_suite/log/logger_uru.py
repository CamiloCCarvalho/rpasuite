# /logger_uru.py

from typing import Optional as Op
from .__create_log_dir import _create_log_dir
from rpa_suite.log.printer import error_print
from loguru import logger
import sys, os, inspect

class Filters:
    word_filter: Op[list[str]]

    def __call__(self, record):

        if len(self.word_filter) > 0:

            for words in self.word_filter:

                string_words: list[str] = [str(word) for word in words]

                for word in string_words:
                    if word in record["message"]:
                        record["message"] = 'Log with filtered words!'
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

        frame = inspect.currentframe().f_back
        full_path_filename = frame.f_code.co_filename

        # Obtenha o nome do arquivo e o nome da pasta
        filename = os.path.basename(full_path_filename)
        foldername = os.path.basename(os.path.dirname(full_path_filename))

        # Combine o nome da pasta e o nome do arquivo
        filename = os.path.join(foldername, filename)
        lineno = frame.f_lineno

        # Formate a mensagem de log TERMINAL
        format_string = "<green>{time:DD.MM.YY.HH:mm}</green> <level>{level: <8}</level> <level>{message}</level>\n"

        log_msg = format_string.format(
            time=record["time"],
            level=record["level"].name,
            filename=filename,
            lineno=lineno,
            message=record["message"]
        )
        return log_msg

def config_logger(path_dir:str = None, name_log_dir:str = None, name_file_log: str = 'log', use_default_path_and_name: bool = True, filter_words: list[str] = None):

    """
    Function responsible for create a object logger with fileHandler and streamHandler
    """

    try:

        if not use_default_path_and_name:
            result_tryed: dict = _create_log_dir(path_dir, name_log_dir)
            path_dir = result_tryed['path_created']
        else:
            if path_dir == None and name_log_dir == None:
                result_tryed: dict = _create_log_dir()
                path_dir = result_tryed['path_created']


        # ATRIBUIÇÕES
        new_filter: Op[Filters] = None
        if filter_words is not None:
            new_filter: Filters = Filters()
            new_filter.word_filter = [filter_words]


        # configuração de objetos logger
        file_handler = fr'{path_dir}\{name_file_log}.log'
        logger.remove()

        # Formate a mensagem de log FILE
        log_format: str = "<green>{time:DD.MM.YY.HH:mm}</green> <level>{level: <8}</level> <green>{extra[filename]}</green>:{extra[lineno]: <4} <level>{message}</level>"


        formatter = CustomFormatter()
        if new_filter is not None:
            logger.add(file_handler, filter=new_filter, level="DEBUG", format=log_format)
        else:
            logger.add(file_handler, level="DEBUG", format=log_format)

        # Adicione sys.stderr como um manipulador
        logger.add(sys.stderr, level="DEBUG", format=formatter.format)

        return file_handler

    except Exception as e:

        error_print(f'Error to execute function:{config_logger.__name__}! Error: {str(e)}.')
        return None
