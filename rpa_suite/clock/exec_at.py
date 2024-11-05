# /exec_at.py

import time
from typing import Callable, Any
from datetime import datetime as dt
from rpa_suite.log.printer import error_print, success_print

def exec_at_hour(
                time_waiting: int,
                hour_to_exec: str,
                fn_to_exec: Callable[..., Any],
                *args,
                **kwargs) -> dict[str, bool]:
    
    """
    Timed function, executes the function at the specified time, by ``default`` it executes at runtime, optionally you can choose the time for execution.
    
    Parameters:
    ----------
        `hour_to_exec: 'xx:xx'` - time for function execution, if not passed the value will be by ``default`` at runtime at the time of this function call by the main code.
    
        ``fn_to_exec: function`` - (function) to be called by the handler, if there are parameters in this function they can be passed as next arguments in ``*args`` and ``**kwargs``
    
    Return:
    ----------
    >>> type:dict
        * 'tried': bool - represents if it tried to execute the function passed in the argument
        * 'success': bool - represents if there was success in trying to execute the requested function
        
    Example:
    ---------
    Let's execute the function ``sum`` responsible for adding the values of a and b and return x``sum(a, b) -> x`` and we want the code to wait for the specific time to be executed at ``11:00``
    >>> exec_at_hour("11:00", sum, 10, 5) -> 15 \n
        * NOTE:  `exec_at_hour` receives as first parameter the function that should be executed, then it can receive the arguments of the function, and explicitly we can define the time for execution.
        
    Description: pt-br
    ----------    
    Função temporizada, executa a função no horário especificado, por ``default`` executa no momento da chamada em tempo de execução, opcionalmente pode escolher o horário para execução.
    
    Parâmetros:
    ----------
        `hour_to_exec: 'xx:xx'` - horário para execução da função, se não for passado o valor será por ``default`` em tempo de execução no momento da chamada desta função pelo cógido principal.
    
        ``fn_to_exec: function`` - (função) a ser chamada pelo handler, se houver parâmetros nessa função podem ser passados como próximos argumentos em ``*args`` e ``**kwargs``
    
    Retorno:
    ----------
    >>> type:dict
        * 'tried': bool - representa se tentou executar a função passada no argumento
        * 'success': bool - representa se houve sucesso ao tentar executar a função solicitada
        
    Exemplo:
    ---------
    Vamos executar a função ``soma`` responsável por somar os valores de a e b e retornar x``soma(a, b) -> x`` e queremos que o código aguarde o horário especifico para ser executado de ``11:00``
    >>> exec_at_hour("11:00", sum, 10, 5) -> 15 \n
        * OBS.:  `exec_at_hour` recebe como primeiro parâmetro a função que deve ser executada, em seguida pode receber os argumentos da função, e de forma explicitada podemos definir o horário para execução.
    """
    
    # Local Variables
    result: dict = {
        'tried': bool,
        'successs': bool
    }
    run: bool
    now: dt
    hours: str
    minutes: str
    moment_now: str
    
    try:
        # Preprocessing
        run = True
        now = dt.now()
        hours = str(now.hour) if now.hour >= 10 else f"0{now.hour}"
        minutes = str(now.minute) if now.minute >= 10 else f"0{now.minute}"
        moment_now = f'{hours}:{minutes}'
        
        if hour_to_exec == None:
            
            # Process
            while run:
                try:
                    fn_to_exec(*args, **kwargs)
                    run = False
                    result['tried'] = not run
                    result['success'] = True
                    success_print(f'{fn_to_exec.__name__}: Successfully executed!')
                    break
                    
                except Exception as e:
                    run = False
                    result['tried'] = not run
                    result['success'] = False
                    error_print(f'An error occurred that prevented the function from executing: {fn_to_exec.__name__} correctly. Error: {str(e)}')
                    break
        else:
            # Executes the function call only at the time provided in the argument.
            while run:
                if moment_now == hour_to_exec:
                    try:
                        fn_to_exec(*args, **kwargs)
                        run = False
                        result['tried'] = not run
                        result['success'] = True
                        success_print(f'{fn_to_exec.__name__}: Successfully executed!')
                        break
                        
                    except Exception as e:
                        run = False
                        result['tried'] = not run
                        result['success'] = False
                        error_print(f'An error occurred that prevented the function from executing: {fn_to_exec.__name__} correctly. Error: {str(e)}')
                        break
                else:
                    
                    # interval to new validate hour
                    if time_waiting:
                        time.sleep(time_waiting)
                    else:
                        time.sleep(9)
                        
                    now = dt.now()
                    hours = str(now.hour) if now.hour >= 10 else f"0{now.hour}"
                    minutes = str(now.minute) if now.minute >= 10 else f"0{now.minute}"
                    moment_now = f'{hours}:{minutes}'

        return result
    
    except Exception as e:
        
        result['success'] = False
        error_print(f'An error occurred on function from executing: {fn_to_exec.__name__}. Error: {str(e)}')
        return result
