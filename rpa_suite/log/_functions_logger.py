# /_functions_logger.py

import logging
from ._logger import file_handler
from rpa_suite.log.printer import error_print, success_print


def log_start_run_debug(msg_start_loggin: str) -> None: # represent start application

    """
    Function responsable to generate ``start run log level debug``, in file and print on terminal the same log captured on this call.
    """

    try:
        global file_handler
        file_handler.stream.write(f'\n{msg_start_loggin}\n')
        success_print(f'{msg_start_loggin}')

    except Exception as e:
        error_print(f'Erro durante a função: {log_start_run_debug.__name__}! Error: {str(e)}')


def log_debug(msg) -> None:

    """
    Function responsable to generate log level ``debug``, in file and print on terminal the same log captured on this call.
    """

    try:
        logging.debug(msg)

    except Exception as e:
        error_print(f'Erro durante a função: {log_debug.__name__}! Error: {str(e)}')

def log_info(msg) -> None:

    """
    Function responsable to generate log level ``info``, in file and print on terminal the same log captured on this call.
    """

    try:
        logging.info(msg)

    except Exception as e:
        error_print(f'Erro durante a função: {log_debug.__name__}! Error: {str(e)}')
        
def log_info(msg) -> None:

    """
    Function responsable to generate log level ``info``, in file and print on terminal the same log captured on this call.
    """

    try:
        logging.info(msg)

    except Exception as e:
        error_print(f'Erro durante a função: {log_info.__name__}! Error: {str(e)}')


def log_warning(msg) -> None:

    """
    Function responsable to generate log level ``warning``, in file and print on terminal the same log captured on this call.
    """

    try:
        logging.warning(msg)

    except Exception as e:
        error_print(f'Erro durante a função: {log_warning.__name__}! Error: {str(e)}')


def log_error(msg) -> None:

    """
    Function responsable to generate log level ``error``, in file and print on terminal the same log captured on this call.
    """

    try:
        logging.error(msg)

    except Exception as e:
        error_print(f'Erro durante a função: {log_error.__name__}! Error: {str(e)}')


def log_critical(msg) -> None:

    """
    Function responsable to generate log level ``critical``, in file and print on terminal the same log captured on this call.
    """

    try:
        logging.critical(msg)

    except Exception as e:
        error_print(f'Erro durante a função: {log_critical.__name__}! Error: {str(e)}')
