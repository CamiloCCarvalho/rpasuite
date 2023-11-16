from loguru import logger

def logging_decorator(fn):
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
