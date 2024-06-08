from colorama import Fore

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
    call_fn   = f'{Fore.LIGHTMAGENTA_EX}'
    retur_fn  = f'{Fore.LIGHTYELLOW_EX}'


def success_print(string_text: str, color=Colors.green, ending="\n") -> None:
    """
    Print that indicates ``SUCCESS``. Customized with the color Green \n

    Return:
    ----------
        >>> type:None

    pt-br
    ----------
    Print  que indica ``SUCESSO``. Personalizado com a cor Verde \n

    Retorno:
    ----------
        >>> type:None
    """
    print(f'{color} {string_text} {Colors.default}', end=ending) 


def alert_print(string_text: str, color=Colors.yellow, ending="\n") -> None:
    """
    Print that indicates ``ALERT``. Customized with the color Yellow \n

    Return:
    ----------
        >>> type:None

    pt-br
    ----------
    Print que indica ``ALERTA``. Personalizado com a cor Amarelo \n
    Retorno:
    ----------
        >>> type:None
    """
    print(f'{color} {string_text} {Colors.default}', end=ending) 


def info_print(string_text: str, color=Colors.cyan, ending="\n") -> None:
    """
    Print that indicates ``INFORMATION``. Customized with the color Cyan \n

    Return:
    ----------
        >>> type:None

    pt-br
    ----------
    Print que indica ``INFORMATIVO``. Personalizado com a cor Ciano \n
    Retorno:
    ----------
        >>> type:None
    """
    print(f'{color} {string_text} {Colors.default}', end=ending) 


def error_print(string_text: str, color=Colors.red, ending="\n") -> None:
    """
    Print that indicates ``ERROR``. Customized with the color Red \n

    Return:
    ----------
        >>> type:None

    pt-br
    ----------
    Print que indica ``ERRO``. Personalizado com a cor Vermelho \n
    Retorno:
    ----------
        >>> type:None
    """
    print(f'{color} {string_text} {Colors.default}', end=ending) 


def magenta_print(string_text: str, color=Colors.magenta, ending="\n") -> None:
    """
    Print customized with the color Magenta \n

    Return:
    ----------
        >>> type:None

    pt-br
    ----------
    Print personalizado com a cor Magenta \n
    Retorno:
    ----------
        >>> type:None
    """
    print(f'{color} {string_text} {Colors.default}', end=ending) 


def blue_print(string_text: str, color=Colors.blue, ending="\n") -> None:
    """
    Print customized with the color Blue \n

    Return:
    ----------
        >>> type:None

    pt-br
    ----------
    Print personalizado com a cor Azul \n
    Retorno:
    ----------
        >>> type:None
    """
    print(f'{color} {string_text} {Colors.default}', end=ending)


def print_call_fn(string_text: str, color=Colors.call_fn, ending="\n") -> None:
    """
    Print customized for function called (log) \n
    Color: Magenta Light
    Return:
    ----------
        >>> type:None

    pt-br
    ----------
    Print personalizado para log de chamada de função. \n
    Cor: Magenta Light
    Retorno:
    ----------
        >>> type:None
    """
    print(f'{color} {string_text} {Colors.default}', end=ending)


def print_retur_fn(string_text: str, color=Colors.retur_fn, ending="\n") -> None:
    """
    Print customized for function return (log) \n
    Color: Yellow Light
    Return:
    ----------
        >>> type:None

    pt-br
    ----------
    Print personalizado para log de chamada de função. \n
    Cor: Yellow Light
    Retorno:
    ----------
        >>> type:None
    """
    print(f'{color} {string_text} {Colors.default}', end=ending)
