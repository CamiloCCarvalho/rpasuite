# /waiter.py

import time
from typing import Callable, Any
from rpa_suite.log.printer import error_print, success_print

def wait_for_exec(
                wait_time: int,
                fn_to_exec: Callable[..., Any],
                *args,
                **kwargs
                ) -> dict[str, bool]:
    
    """
    Timer function, wait for a value in ``seconds`` to execute the function of the argument.
    
    Parameters:
    ----------
        `wait_time: int` - (seconds) represents the time that should wait before executing the function passed as an argument.
    
        ``fn_to_exec: function`` - (function) to be called after the waiting time, if there are parameters in this function they can be passed as next arguments of this function in ``*args`` and ``**kwargs``
    
    Return:
    ----------
    >>> type:dict
        * 'success': bool - represents if the action was performed successfully
        
    Example:
    ---------
    We have a sum function in the following format ``sum(a, b) -> return x``, where ``x`` is the result of the sum. We want to wait `30 seconds` to execute this function, so:
    >>> wait_for_exec(30, sum, 10, 5) -> 15 \n
        * NOTE:  `wait_for_exec` receives as first argument the time to wait (sec), then the function `sum` and finally the arguments that the function will use.
        
    Description: pt-br
    ----------    
    Função temporizadora, aguardar um valor em ``segundos`` para executar a função do argumento.
    
    Parametros:
    ----------
        `wait_time: int` - (segundos) representa o tempo que deve aguardar antes de executar a função passada como argumento.
    
        ``fn_to_exec: function`` - (função) a ser chamada depois do tempo aguardado, se houver parametros nessa função podem ser passados como próximos argumentos desta função em ``*args`` e ``**kwargs``
    
    Retorno:
    ----------
    >>> type:dict
        * 'success': bool - representa se ação foi realizada com sucesso
        
    Exemplo:
    ---------
    Temos uma função de soma no seguinte formato ``soma(a, b) -> return x``, onde ``x`` é o resultado da soma. Queremos aguardar `30 segundos` para executar essa função, logo:
    >>> wait_for_exec(30, soma, 10, 5) -> 15 \n
        * OBS.:  `wait_for_exec` recebe como primeiro argumento o tempo a aguardar (seg), depois a função `soma` e por fim os argumentos que a função ira usar.
    """
    
    # Local Variables
    result: dict = {
        'success': bool
    }
    
    # Process
    try:
        time.sleep(wait_time)
        fn_to_exec(*args, **kwargs)
        result['success'] = True
        success_print(f'Function: {wait_for_exec.__name__} executed the function: {fn_to_exec.__name__}.')
        
    except Exception as e:
        result['success'] = False
        error_print(f'Error while trying to wait to execute the function: {fn_to_exec.__name__} \nMessage: {str(e)}')
    
    return result

def exec_and_wait(
                wait_time: int,
                fn_to_exec: Callable[..., Any],
                *args,
                **kwargs
                ) -> dict[str, bool]:
    
    """
    Timer function, executes a function and waits for the time in ``seconds``
    
    Parameters:
    ----------
        `wait_time: int` - (seconds) represents the time that should wait after executing the requested function
    
        ``fn_to_exec: function`` - (function) to be called before the time to wait, if there are parameters in this function they can be passed as an argument after the function, being: ``*args`` and ``**kwargs``
    
    Return:
    ----------
    >>> type:dict
        * 'success': bool - represents if the action was performed successfully
        
    Example:
    ---------
    We have a sum function in the following format ``sum(a, b) -> return x``, where ``x`` is the result of the sum. We want to execute the sum and then wait `30 seconds` to continue the main code:
    >>> wait_for_exec(30, sum, 10, 5) -> 15 \n
        * NOTE:  `wait_for_exec` receives as first argument the time to wait (sec), then the function `sum` and finally the arguments that the function will use.
        
    Description: pt-br
    ----------
    Função temporizadora, executa uma função e aguarda o tempo em ``segundos``
    
    Parametros:
    ----------
        `wait_time: int` - (segundos) representa o tempo que deve aguardar após executar a função solicitada
    
        ``fn_to_exec: function`` - (função) a ser chamada antes do tempo para aguardar, se houver parametros nessa função podem ser passados como argumento depois da função, sendo: ``*args`` e ``**kwargs``
    
    Retorno:
    ----------
    >>> type:dict
        * 'success': bool - representa se ação foi realizada com sucesso
        
    Exemplo:
    ---------
    Temos uma função de soma no seguinte formato ``soma(a, b) -> return x``, onde ``x`` é o resultado da soma. Queremos executar a soma e então aguardar `30 segundos` para continuar o código principal:
    >>> wait_for_exec(30, soma, 10, 5) -> 15 \n
        * OBS.:  `wait_for_exec` recebe como primeiro argumento o tempo a aguardar (seg), depois a função `soma` e por fim os argumentos que a função ira usar.
    """
    
    # Local Variables
    result: dict = {
        'success': bool
    }
    
    # Process
    try:
        fn_to_exec(*args, **kwargs)
        time.sleep(wait_time)
        result['success'] = True
        success_print(f'Function: {wait_for_exec.__name__} executed the function: {fn_to_exec.__name__}.')
        
    except Exception as e:
        result['success'] = False
        error_print(f'Error while trying to wait to execute the function: {fn_to_exec.__name__} \nMessage: {str(e)}')
    
    return result