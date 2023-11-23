from colorama import Fore, Back, Style
from typing import Any

# Windows bash colors
class Colors():
    black     = f'{Fore.BLACK}'
    blue      = f'{Fore.BLUE}'
    green     = f'{Fore.GREEN}'
    cyan      = f'{Fore.CYAN}'
    red       = f'{Fore.RED}'
    magenta   = f'{Fore.MAGENTA}'
    yellow    = f'{Fore.YELLOW}'
    white     = f'{Fore.WHITE}'
    default   = f'{Fore.WHITE}'


def success_print(string_text: str, color=Colors.green) -> None:
    """
    Print  que indica ``SUCESSO``. Personalizado com a cor Verde \n
    
    Retorno:
    ----------
        >>> type:None
    """
    return print(f'{color} {string_text} {Colors.default}') 

def alert_print(string_text: str, color=Colors.yellow) -> None:
    """
    Print que indica ``ALERTA``. Personalizado com a cor Amarelo \n
    Retorno:
    ----------
        >>> type:None
    """
    return print(f'{color} {string_text} {Colors.default}') 

def info_print(string_text: str, color=Colors.cyan) -> None:
    """
    Print que indica ``INFORMATIVO``. Personalizado com a cor Ciano \n
    Retorno:
    ----------
        >>> type:None
    """
    return print(f'{color} {string_text} {Colors.default}') 

def error_print(string_text: str, color=Colors.red) -> None:
    """
    Print que indica ``ERRO``. Personalizado com a cor Vermelho \n
    Retorno:
    ----------
        >>> type:None
    """
    return print(f'{color} {string_text} {Colors.default}') 

def magenta_print(string_text: str, color=Colors.magenta) -> None:
    """
    Print personalizado com a cor Magenta \n
    Retorno:
    ----------
        >>> type:None
    """
    return print(f'{color} {string_text} {Colors.default}') 

def blue_print(string_text: str, color=Colors.blue) -> None:
    """
    Print personalizado com a cor Azul \n
    Retorno:
    ----------
        >>> type:None
    """
    return print(f'{color} {string_text} {Colors.default}') 
