from typing import Callable, Any
import time

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
