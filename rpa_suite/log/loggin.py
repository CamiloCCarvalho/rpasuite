from typing import Callable
from loguru import logger

def logging_decorator(
                    fn: Callable
                    ) -> Callable:
    
    """
    Função responsavel por exibir mensagem de log no console para funções que são chamadas. \n
    Exibe nome da função, e o resultado da função em caso de retorno, sem retorno devolve None.
    
    Retorno:
    ----------
    Uma função ``wrapper`` com decoração ``@logger.catch`` do python que recebeu:
        * ``*args e **kwargs`` nos parametros de chamada como argumento para resultar no Log.
    """
    
    @logger.catch
    def wrapper(*args, **kwargs):
        logger.info('Chamando função: {}', fn.__name__)
        result = fn(*args, **kwargs)
        logger.info('Função {} retornou: {}', fn.__name__, result)
        return result
    return wrapper


'''
Exemplo de uso com teste

@logging_decorator
def add(x, y):
    return x + y

add(1, 2)
'''
