from typing import Callable
from loguru import logger

def logging_decorator(
                    fn: Callable
                    ) -> Callable:

    """
    Function responsible for displaying log message in the console for functions that are called. \n
    Displays function name, and the result of the function in case of return, without return returns None.

    Return:
    ----------
    A ``wrapper`` function with python decoration ``@logger.catch`` that received:
        * ``*args and **kwargs`` in the call parameters as an argument to result in the Log.

    Description: pt-br
    ----------
    Função responsavel por exibir mensagem de log no console para funções que são chamadas. \n
    Exibe nome da função, e o resultado da função em caso de retorno, sem retorno devolve None.

    Retorno:
    ----------
    Uma função ``wrapper`` com decoração ``@logger.catch`` do python que recebeu:
        * ``*args e **kwargs`` nos parametros de chamada como argumento para resultar no Log.
    """

    @logger.catch
    def wrapper(*args, **kwargs):
        logger.info('Function Called: {}', fn.__name__)
        result = fn(*args, **kwargs)
        logger.info('Function {} returned: {}', fn.__name__, result)
        return result

    return wrapper
