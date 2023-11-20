from typing import Callable, Any
import time
from rpa_suite.log.loggin import logging_decorator

@logging_decorator
def wait_for_exec(
                wait_time: int,
                fn_to_exec: Callable[..., Any],
                *args,
                **kwargs
                ) -> dict:
    
    """
    Função temporizadora, aguarda um valor em segundos para executar a função que é passada como argumento. \n
    
    use no formato wait_for_exec(time_seconds, my_function_execute, args_function)
    
    Retorno sendo (dicionário):
        - 'success': bool
    """
    # Variaveis locais
    waiter_result: dict = {
        'success': bool
    }
    # Pré Tratamento
    
    # Processo
    try:
        time.sleep(wait_time)
        fn_to_exec(*args, **kwargs)
        waiter_result['success'] = True
    except Exception as e:
        print(f'Erro ao tentar aguardar para executar a função! Mensagem: {str(e)}')
        waiter_result['success'] = False
    
    # Pós Tratamento
    
    # Retorno
    return waiter_result
