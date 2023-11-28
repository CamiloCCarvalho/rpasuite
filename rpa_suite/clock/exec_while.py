from typing import Callable, Any
import time
from rpa_suite.log.printer import alert_print, error_print, success_print

def exec_wtime(
                while_time: int,
                fn_to_exec: Callable[..., Any],
                *args,
                **kwargs
                ) -> dict:
    
    """
    Função temporizada, executa uma função enquanto o tempo (em segundos) da condição não foi atendido.
    
    Parametros:
    ----------
        `while_time: int` - (segundos) representa o tempo que deve persistir a execução da função passada no argumento ``fn_to_exec``
    
        ``fn_to_exec: function`` - (função) a ser chamada durante o temporizador, se houver parametros nessa função podem ser passados como próximos argumentos desta função em ``*args`` e ``**kwargs``
    
    Retorno:
    ----------
    >>> type:dict
        * 'success': bool - representa se ação foi realizada com sucesso
        
    Exemplo:
    ---------
    Temos uma função de soma no seguinte formato ``soma(a, b) -> return x``, onde ``x`` é o resultado da soma. Supondo que temos o valor de `a` mas não de `b` podemos executar a função por um tempo `y` até obtermos valor de `b` para saber o resultado da soma:
    >>> exec_wtime(60, soma, a, b) -> x \n
        * OBS.:  `exec_wtime` recebe como primeiro argumento o tempo a aguardar (seg), depois a função `soma` e por fim os argumentos que a função ira usar.
    """
    
    # Variaveis locais
    result: dict = {
        'success': bool
    }
    # Pré Tratamento
    ...
    
    # Processo
    alert_print(f'Função ainda não implementada!')
    
    
    # Pós Tratamento
    ...
    
    return result
