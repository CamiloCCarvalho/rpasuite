# rpa_suite/core/print.py

# imports third party
from colorama import Fore

class PrintError(Exception):
    """Custom exception for Print errors."""
    def __init__(self, message):
        super().__init__(f'Print Error: {message}')

# Windows bash colors
class Colors:
    """Color constants for console output formatting."""
    black = f"{Fore.BLACK}"
    blue = f"{Fore.BLUE}"
    green = f"{Fore.GREEN}"
    cyan = f"{Fore.CYAN}"
    red = f"{Fore.RED}"
    magenta = f"{Fore.MAGENTA}"
    yellow = f"{Fore.YELLOW}"
    white = f"{Fore.WHITE}"
    default = f"{Fore.WHITE}"
    call_fn = f"{Fore.LIGHTMAGENTA_EX}"
    retur_fn = f"{Fore.LIGHTYELLOW_EX}"


class Print:
    """
    Class that provides methods for formatted printing in the console, allowing for different types of messages to be displayed with specific colors.

    This class offers functionalities for:
        - Printing success messages in green
        - Printing alert messages in yellow
        - Printing information messages in cyan
        - Printing error messages in red
        - Additional printing methods for other message types

    The Print class is part of the RPA Suite and can be used to enhance the visibility of console outputs.

    Example:
    ----------
        >>> from rpa_suite import rpa
        >>> rpa.alert_print('Hello World')
    """

    colors: Colors = Colors

    def __init__(self) -> None:
        """Initialize the Print class.""" 
        pass

    def success_print(self, string_text: str, color=Colors.green, ending="\n") -> None:
        """
        Print that indicates SUCCESS. Customized with the color Green.

        Parameters:
        -----------
        ``string_text: str``
            The text to be printed.
        
        ``color``
            The color to use for printing. Default is green.
        
        ``ending: str``
            The string appended after the text. Default is newline.

        Return:
        ----------
            >>> type: None
        """
        print(f"{color}{string_text}{Colors.default}", end=ending)

    def alert_print(self, string_text: str, color=Colors.yellow, ending="\n") -> None:
        """
        Print that indicates ALERT. Customized with the color Yellow.

        Parameters:
        -----------
        ``string_text: str``
            The text to be printed.
        
        ``color``
            The color to use for printing. Default is yellow.
        
        ``ending: str``
            The string appended after the text. Default is newline.

        Return:
        ----------
            >>> type: None
        """
        print(f"{color}{string_text}{Colors.default}", end=ending)

    def info_print(self, string_text: str, color=Colors.cyan, ending="\n") -> None:
        """
        Print that indicates INFORMATION. Customized with the color Cyan.

        Parameters:
        -----------
        ``string_text: str``
            The text to be printed.
        
        ``color``
            The color to use for printing. Default is cyan.
        
        ``ending: str``
            The string appended after the text. Default is newline.

        Return:
        ----------
            >>> type: None
        """
        print(f"{color}{string_text}{Colors.default}", end=ending)

    def error_print(self, string_text: str, color=Colors.red, ending="\n") -> None:
        """
        Print that indicates ERROR. Customized with the color Red.

        Parameters:
        -----------
        ``string_text: str``
            The text to be printed.
        
        ``color``
            The color to use for printing. Default is red.
        
        ``ending: str``
            The string appended after the text. Default is newline.

        Return:
        ----------
            >>> type: None
        """
        print(f"{color}{string_text}{Colors.default}", end=ending)

    def magenta_print(self, string_text: str, color=Colors.magenta, ending="\n") -> None:
        """
        Print customized with the color Magenta.

        Parameters:
        -----------
        ``string_text: str``
            The text to be printed.
        
        ``color``
            The color to use for printing. Default is magenta.
        
        ``ending: str``
            The string appended after the text. Default is newline.

        Return:
        ----------
            >>> type: None
        """
        print(f"{color}{string_text}{Colors.default}", end=ending)

    def blue_print(self, string_text: str, color=Colors.blue, ending="\n") -> None:
        """
        Print customized with the color Blue.

        Parameters:
        -----------
        ``string_text: str``
            The text to be printed.
        
        ``color``
            The color to use for printing. Default is blue.
        
        ``ending: str``
            The string appended after the text. Default is newline.

        Return:
        ----------
            >>> type: None
        """
        print(f"{color}{string_text}{Colors.default}", end=ending)

    def print_call_fn(self, string_text: str, color=Colors.call_fn, ending="\n") -> None:
        """
        Print customized for function called (log).
        Color: Light Magenta

        Parameters:
        -----------
        ``string_text: str``
            The text to be printed.
        
        ``color``
            The color to use for printing. Default is light magenta.
        
        ``ending: str``
            The string appended after the text. Default is newline.

        Return:
        ----------
            >>> type: None
        """
        print(f"{color}{string_text}{Colors.default}", end=ending)

    def print_retur_fn(self, string_text: str, color=Colors.retur_fn, ending="\n") -> None:
        """
        Print customized for function return (log).
        Color: Light Yellow

        Parameters:
        -----------
        ``string_text: str``
            The text to be printed.
        
        ``color``
            The color to use for printing. Default is light yellow.
        
        ``ending: str``
            The string appended after the text. Default is newline.

        Return:
        ----------
            >>> type: None
        """
        print(f"{color}{string_text}{Colors.default}", end=ending)
