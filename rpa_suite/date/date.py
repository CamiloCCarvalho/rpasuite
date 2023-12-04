import datetime as dt
from rpa_suite.log.printer import error_print


        
def get_hms() -> tuple:
    """
    Função para retornar hora, minuto e segundo. O retorno é em forma de tupla com strings podendo armazenar e usar os valores de forma individual.
    
    Tratamento:
    ----------
    A função já faz o tratamento para valores abaixo de 10 mantendo sempre 2 casas decimais em todos resultados, os valores individuais são sempre em formato string
    
    Retorno:
    ----------
    >>> type:tuple
        * tuple('hh', 'mm', 'ss') - tupla com os valores de hora, minuto e segundo podendo ser armazenados individualmente, os valores são em string
        
    Exemplo:
    ---------
    >>> hora, minuto, segundo = get_hms() \n
        * OBS.:  Note que é possivel desestruturar o retorno para armazenar de forma simultânea.
    """
    
    # Variáiveis locais
    hours: str
    minutes: str
    seconds: str
    
    # Pré tratamento
    now = dt.datetime.now()
    hours: str = str(now.hour) if now.hour > 10 else f"0{now.hour}"
    minutes: str = str(now.minute) if now.minute > 10 else f"0{now.minute}"
    seconds: str = str(now.second) if now.second > 10 else f"0{now.second}"
    
    # Processo
    try:
        if len(hours) == 3 or len(minutes) == 3 or len(seconds) == 3:
            if len(seconds) == 3:
                seconds[1:]
            elif len(minutes) == 3:
                minutes[1:]
            elif len(hours) == 3:
                hours[1:]
                
        return hours, minutes, seconds
    except Exception as e:
        return error_print(f'Não foi possivel capturar o horário. Erro: {str(e)}')

def get_dma() -> tuple:
    """
    Função para retornar dia, mes e ano. O retorno é em forma de tupla com strings podendo armazenar e usar os valores de forma individual.
    
    Retorno:
    ----------
    >>> type:tuple
        * tuple('dd', 'mm', 'yy') - tupla com os valores de dia, mes e ano podendo ser armazenados individualmente
        
    Exemplo:
    ---------
    >>> dia, mes, ano = get_hms() \n
        * OBS.:  Note que é possivel desestruturar o retorno para armazenar de forma simultânea.
    """
    
    # Variáiveis locais
    day_got: str
    month_got: str
    year_got: str
    
    # Pré tratamento
    now = dt.datetime.now()
    
    # Processo
    try:
        day_got: str = str(now.day) if now.day > 10 else f"0{now.day}"
        month_got: str = str(now.month) if now.month > 10 else f"0{now.month}"
        year_got: str = str(now.year) if now.year > 10 else f"0{now.year}"
    
        return day_got, month_got, year_got
    
    except Exception as e:
        return error_print(f'Não foi possivel capturar o horário. Erro: {str(e)}')
