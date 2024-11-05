# /_logger.py

import logging
from logging import DEBUG
from logging import FileHandler, StreamHandler, Filter
from colorlog import ColoredFormatter
from typing import Optional as Op
from ._variables import file_handler, stream_handler
from .__create_log_dir import _create_log_dir
from rpa_suite.log.printer import error_print


class Filters(Filter):

    word_filter: Op[list[str]]

    def filter(self, record):

        if len(self.word_filter) > 0:

            for words in self.word_filter:


                string_words: list[str] = [str(word) for word in words]
                """print(words)
                print(type(words))
                print(string_words)
                print(type(string_words))
                input()"""
                for word in string_words:
                    if word in record.msg:
                        record.msg = 'Log with filtered words!'
                        return True

        return True


def config_logger(name_app:str = 'Logger', path_dir:str = None, name_log_dir:str = None, name_file_log: str = 'log', use_default_path_and_name: bool = True, filter_words: list[str] = None) -> Op[FileHandler]:

    """
    Function responsible for create a object logger with fileHandler and streamHandler
    """

    global file_handler, stream_handler

    try:


        if not use_default_path_and_name:
            result_tryed: dict = _create_log_dir(path_dir, name_log_dir)
            path_dir = result_tryed['path_created']
        else:
            if path_dir == None and name_log_dir == None:
                result_tryed: dict = _create_log_dir()
                path_dir = result_tryed['path_created']


        # configuração de objetos logger
        file_handler = FileHandler(
            filename=fr'{path_dir}\{name_file_log}.log',
            mode='a',
            encoding='utf-8'
        )
        stream_handler = StreamHandler()

        # Crie um formatador
        formatter = ColoredFormatter(
            "%(log_color)s%(levelname)s ->%(reset)s %(log_color)s%(message)s%(reset)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red',
            },
            force_color=True
        )
        stream_handler.setFormatter(formatter)

        # ATRIBUIÇÕES
        new_filter: Op[Filters] = None
        if filter_words is not None:
            new_filter: Filters = Filters()
            new_filter.word_filter = [filter_words]

        if new_filter is not None:
            file_handler.addFilter(new_filter)

        file_handler.setLevel(DEBUG)
        
        # Obtenha o logger
        logger = logging.getLogger(__name__)

        # Adicione o manipulador de stream ao logger
        logger.addHandler(stream_handler)

        # terminando de inplementar configuração para o logger
        FORMAT = '%(levelname)s!%(asctime)s: %(message)s'
        logging.basicConfig(
            level=DEBUG, # level from stream_handler
            #format='%(levelname)s - %(asctime)s - %(message)s',
            format=FORMAT,
            handlers=[file_handler, stream_handler],
            datefmt='%d.%m.%y %H:%M',
        )
        return file_handler

    except Exception as e:

        error_print(f'Error to execute function:{config_logger.__name__}! Error: {str(e)}.')
        return None
