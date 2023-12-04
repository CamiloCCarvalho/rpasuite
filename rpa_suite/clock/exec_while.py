import re
from typing import Callable, Any
from rpa_suite.date.date import get_hms
from rpa_suite.log.printer import error_print, success_print

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
    
        ``fn_to_exec: function`` - (função) a ser chamada (repetidas vezes) durante o temporizador, se houver parametros nessa função podem ser passados como próximos argumentos desta função em ``*args`` e ``**kwargs``
    
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
    
    # Variáveis locais
    result: dict = {
        'success': bool
    }
    run: bool
    timmer: int
    
    # Pré Tratamento
    timmer = while_time
    
    # Processo
    try:
        run = True
        hour, minute, second = get_hms()
        while run and timmer > 0:
            fn_to_exec(*args, **kwargs)
            hour_now, minute_now, second_now = get_hms()
            if second_now != second:
                second = second_now
                timmer =- 1
                if timmer <= 0:
                    run = False
                    break
        result['success'] = True
        success_print(f'Função {fn_to_exec.__name__} foi executada durante: {while_time} seg(s).')
        
    except Exception as e:
        result['success'] = False
        error_print(f'Ocorreu algum erro que impediu a execução da função: {exec_wtime.__name__} corretamente. Erro: {str(e)}')
        
    return result
