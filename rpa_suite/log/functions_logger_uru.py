# /functions_logger_uru.py

from loguru import logger
from rpa_suite.log.printer import error_print, alert_print
import inspect, os

def log_start_run_debug(msg_start_loggin: str) -> None: # represent start application

    """
    Function responsable to generate ``start run log level debug``, in file and print on terminal the same log captured on this call.
    """

    file_h: False

    try:

        from .logger_uru import config_logger
        file_h = config_logger()

    except Exception as e:

        error_print(f'Para usar o log_start_run_debug é necessario instanciar file_handler usando o arquivo "logger_uru" em algum arquivo de configuração do seu projeto primeiramente! Error: {str(e)}')

    try:
        try:
            if file_h:
                with open(file_h, 'a') as f:
                    f.write('\n')

        except Exception as e:
            alert_print(f'Não foi possivel gerar break_row para log inicial!')

        # logger.debug(f'{msg_start_loggin}')
        frame = inspect.currentframe().f_back
        full_path_filename = frame.f_code.co_filename

        # Obtenha o nome do arquivo e o nome da pasta
        filename = os.path.basename(full_path_filename)
        foldername = os.path.basename(os.path.dirname(full_path_filename))

        # Combine o nome da pasta e o nome do arquivo
        filename = os.path.join(foldername, filename)
        lineno = frame.f_lineno

        # Vincule o nome do arquivo e a linha à mensagem de log
        logger.bind(filename=filename, lineno=lineno).debug(f'{msg_start_loggin}')

    except Exception as e:
        error_print(f'Erro durante a função: {log_start_run_debug.__name__}! Error: {str(e)}')


def log_debug(msg) -> None:

    """
    Function responsable to generate log level ``debug``, in file and print on terminal the same log captured on this call.
    """

    try:
        frame = inspect.currentframe().f_back
        full_path_filename = frame.f_code.co_filename

        # Obtenha o nome do arquivo e o nome da pasta
        filename = os.path.basename(full_path_filename)
        foldername = os.path.basename(os.path.dirname(full_path_filename))

        # Combine o nome da pasta e o nome do arquivo
        filename = os.path.join(foldername, filename)
        lineno = frame.f_lineno

        # Vincule o nome do arquivo e a linha à mensagem de log
        logger.bind(filename=filename, lineno=lineno).debug(msg)

    except Exception as e:
        error_print(f'Erro durante a função: {log_debug.__name__}! Error: {str(e)}')

def log_info(msg) -> None:

    """
    Function responsable to generate log level ``info``, in file and print on terminal the same log captured on this call.
    """

    try:
        frame = inspect.currentframe().f_back
        full_path_filename = frame.f_code.co_filename

        # Obtenha o nome do arquivo e o nome da pasta
        filename = os.path.basename(full_path_filename)
        foldername = os.path.basename(os.path.dirname(full_path_filename))

        # Combine o nome da pasta e o nome do arquivo
        filename = os.path.join(foldername, filename)
        lineno = frame.f_lineno

        # Vincule o nome do arquivo e a linha à mensagem de log
        logger.bind(filename=filename, lineno=lineno).info(msg)

    except Exception as e:
        error_print(f'Erro durante a função: {log_info.__name__}! Error: {str(e)}')

def log_warning(msg) -> None:

    """
    Function responsable to generate log level ``warning``, in file and print on terminal the same log captured on this call.
    """

    try:
        frame = inspect.currentframe().f_back
        full_path_filename = frame.f_code.co_filename

        # Obtenha o nome do arquivo e o nome da pasta
        filename = os.path.basename(full_path_filename)
        foldername = os.path.basename(os.path.dirname(full_path_filename))

        # Combine o nome da pasta e o nome do arquivo
        filename = os.path.join(foldername, filename)
        lineno = frame.f_lineno

        # Vincule o nome do arquivo e a linha à mensagem de log
        logger.bind(filename=filename, lineno=lineno).warning(msg)

    except Exception as e:
        error_print(f'Erro durante a função: {log_warning.__name__}! Error: {str(e)}')


def log_error(msg) -> None:

    """
    Function responsable to generate log level ``error``, in file and print on terminal the same log captured on this call.
    """

    try:
        frame = inspect.currentframe().f_back
        full_path_filename = frame.f_code.co_filename

        # Obtenha o nome do arquivo e o nome da pasta
        filename = os.path.basename(full_path_filename)
        foldername = os.path.basename(os.path.dirname(full_path_filename))

        # Combine o nome da pasta e o nome do arquivo
        filename = os.path.join(foldername, filename)
        lineno = frame.f_lineno

        # Vincule o nome do arquivo e a linha à mensagem de log
        logger.bind(filename=filename, lineno=lineno).error(msg)

    except Exception as e:
        error_print(f'Erro durante a função: {log_error.__name__}! Error: {str(e)}')


def log_critical(msg) -> None:

    """
    Function responsable to generate log level ``critical``, in file and print on terminal the same log captured on this call.
    """

    try:
        frame = inspect.currentframe().f_back
        full_path_filename = frame.f_code.co_filename

        # Obtenha o nome do arquivo e o nome da pasta
        filename = os.path.basename(full_path_filename)
        foldername = os.path.basename(os.path.dirname(full_path_filename))

        # Combine o nome da pasta e o nome do arquivo
        filename = os.path.join(foldername, filename)
        lineno = frame.f_lineno

        # Vincule o nome do arquivo e a linha à mensagem de log
        logger.bind(filename=filename, lineno=lineno).critical(msg)

    except Exception as e:
        error_print(f'Erro durante a função: {log_critical.__name__}! Error: {str(e)}')
