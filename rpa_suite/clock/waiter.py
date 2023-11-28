from typing import Callable, Any
import time
from rpa_suite.log.printer import error_print, success_print

def wait_for_exec(
                wait_time: int,
                fn_to_exec: Callable[..., Any],
                *args,
                **kwargs
                ) -> dict:
    
    """
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
    >>> wait_for_exec(30, soma, a, b) -> x \n
        * OBS.:  `wait_for_exec` recebe como primeiro argumento o tempo a aguardar (seg), depois a função `soma` e por fim os argumentos que a função ira usar.
    """
    
    # Variaveis locais
    result: dict = {
        'success': bool
    }
    # Pré Tratamento
    
    # Processo
    try:
        time.sleep(wait_time)
        fn_to_exec(*args, **kwargs)
        result['success'] = True
        success_print(f'A função:: {wait_for_exec.__name__} executou a função: {fn_to_exec.__name__}.')
        
    except Exception as e:
        result['success'] = False
        error_print(f'Erro ao tentar aguardar para executar a função: {fn_to_exec.__name__} \nMensagem: {str(e)}')
        
    
    # Pós Tratamento
    ...
    
    return result
