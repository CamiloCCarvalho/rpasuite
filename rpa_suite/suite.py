# rpa_suite/suite.py

# imports internal
from .core.clock import Clock
from .core.date import Date
from .core.email import Email
from .core.dir import Directory
from .core.file import File
from .core.log import Log
from .core.print import Print
from .core.regex import Regex
from .core.validate import Validate
from .core.parallel import ParallelRunner
from .core.asyncrun import AsyncRunner

# imports external
from colorama import Fore
from importlib.metadata import version

# imports third-party
import subprocess
import sys
import hashlib


# Windows bash colors
class Colors:
    """
    This class provides color constants based on the colorama library,
    allowing for visual formatting of texts in the Windows terminal.

    Attributes:
        black (str): Black color
        blue (str): Blue color
        green (str): Green color
        cyan (str): Cyan color
        red (str): Red color
        magenta (str): Magenta color
        yellow (str): Yellow color
        white (str): White color
        default (str): Default color (white)
        call_fn (str): Light magenta color (used for function calls)
        retur_fn (str): Light yellow color (used for function returns)

    pt-br
    ------

    Esta classe fornece constantes de cores baseadas na biblioteca colorama,
    permitindo a formatação visual de textos no terminal Windows.

    Atributos:
        black (str): Cor preta
        blue (str): Cor azul
        green (str): Cor verde
        cyan (str): Cor ciano
        red (str): Cor vermelha
        magenta (str): Cor magenta
        yellow (str): Cor amarela
        white (str): Cor branca
        default (str): Cor padrão (branca)
        call_fn (str): Cor magenta clara (usada para chamadas de função)
        retur_fn (str): Cor amarela clara (usada para retornos de função)
    """

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


class Suite:
    """
    RPA Suite is a Python module that provides a set of tools for process automation.

    To use the module, import it as follows:
        >>> from rpa_suite import rpa

    Example of usage:
        >>> from rpa_suite import rpa
        >>> rpa.email.send_smtp(
        ...     email_user="your@email.com",
        ...     email_password="your_password",
        ...     email_to="destination@email.com",
        ...     subject_title="Test",
        ...     body_message="<p>Test message</p>"
        ... )
        >>> rpa.alert_print("Hello World")

    Available modules:
        ``clock``: Utilities for time and stopwatch manipulation
        ``date``: Functions for date manipulation
        ``email``: Functionalities for sending emails via SMTP
        ``directory``: Operations with directories
        ``file``: File manipulation
        ``log``: Logging system
        ``printer``: Functions for formatted output
        ``regex``: Operations with regular expressions
        ``validate``: Data validation functions
        ``ParallelRunner``: Object ParallelRunner functions to run in parallel
        ``AsyncRunner``: Object AsyncRunner functions to run in Assyncronous
        ``Browser``: Object Browser automation functions (neeeds Selenium and Webdriver_Manager)
        ``Iris``: Object Iris automation functions to convert documents with OCR + IA based on ``docling``

    pt-br
    -----
    RPA Suite é um módulo Python que fornece um conjunto de ferramentas para automação de processos.

    Para utilizar o módulo, importe-o da seguinte forma:
        >>> from rpa_suite import rpa

    Exemplo de uso:
        >>> from rpa_suite import rpa
        >>> rpa.email.send_smtp(
        ...     email_user="seu@email.com",
        ...     email_password="sua_senha",
        ...     email_to="destino@email.com",
        ...     subject_title="Teste",
        ...     body_message="<p>Mensagem de teste</p>"
        ... )
        >>> rpa.alert_print("Hello World")

    Módulos disponíveis:
        ``clock``: Utilitários para manipulação de tempo e cronômetro
        ``date``: Funções para manipulação de datas
        ``email``: Funcionalidades para envio de emails via SMTP
        ``directory``: Operações com diretórios
        ``file``: Manipulação de arquivos
        ``log``: Sistema de logging
        ``printer``: Funções para output formatado
        ``regex``: Operações com expressões regulares
        ``validate``: Funções de validação de dados
        ``ParallelRunner``: Objeto ParallelRunner funções para rodar processos em paralelo
        ``AsyncRunner``: Objeto AsyncRunner funções para rodar processos em assincronicidade
        ``Browser``: Objeto de Automação de Navegadores (necessario Selenium e Webdriver_Manager)
        ``Iris``: Objeto Iris Automação de funções para converter documentos com OCR + IA baseado em ``docling``
    """

    # SUBMODULES
    clock: Clock = Clock()
    date: Date = Date()
    email: Email = Email()
    directory: Directory = Directory()
    file: File = File()
    log: Log = Log()
    printer: Print = Print()
    regex: Regex = Regex()
    validate: Validate = Validate()
    Parallel: ParallelRunner = ParallelRunner
    Asyn: AsyncRunner = AsyncRunner

    # On this case, we are importing the (Browser | Iris) class only if the selenium and webdriver_manager modules are installed.
    # This is useful to avoid unnecessary imports and dependencies if the user does not need the (Browser | Iris) functionality.
    import importlib.util

    # from .browser import Browser
    if importlib.util.find_spec("selenium") and importlib.util.find_spec("webdriver_manager"):
        from .core.browser import Browser

        browser: Browser = Browser

    # from .iris import Iris
    if importlib.util.find_spec("docling"):
        from .core.iris import Iris

        iris: Iris = Iris
        
    # VARIABLES INTERNAL
    try:
        # old: __version__ = pkg_resources.get_distribution("rpa_suite").version

        __version__ = version("package_name")

    except Exception:
        __version__ = "unknown"

    __id_hash__ = "rpa_suite"

    def __init__(self):
        self.__id_hash__ = "rpa_suite"
        self.__id_hash__ = hashlib.sha256(self.__version__.encode()).hexdigest()

    def success_print(self, string_text: str, color=Colors.green, ending="\n") -> None:
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

        print(f"{color}{string_text}{Colors.default}", end=ending)

    def alert_print(self, string_text: str, color=Colors.yellow, ending="\n") -> None:
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
        print(f"{color}{string_text}{Colors.default}", end=ending)

    def info_print(self, string_text: str, color=Colors.cyan, ending="\n") -> None:
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
        print(f"{color}{string_text}{Colors.default}", end=ending)

    def error_print(self, string_text: str, color=Colors.red, ending="\n") -> None:
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
        print(f"{color}{string_text}{Colors.default}", end=ending)

    def magenta_print(self, string_text: str, color=Colors.magenta, ending="\n") -> None:
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
        print(f"{color}{string_text}{Colors.default}", end=ending)

    def blue_print(self, string_text: str, color=Colors.blue, ending="\n") -> None:
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
        print(f"{color}{string_text}{Colors.default}", end=ending)

    def print_call_fn(self, string_text: str, color=Colors.call_fn, ending="\n") -> None:
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
        print(f"{color}{string_text}{Colors.default}", end=ending)

    def print_retur_fn(self, string_text: str, color=Colors.retur_fn, ending="\n") -> None:
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
        print(f"{color}{string_text}{Colors.default}", end=ending)

    def __install_all_libs(self):
        """
        Method responsible for installing all libraries for advanced use of RPA-Suite, including all features such as OCR and AI agent.
        ----------
        Metodo responsavel por instalar todas libs para uso avançado do RPA-Suite com todas funcionalidades incluindo OCR e agente de IA
        """

        libs = [
            "setuptools",
            "wheel",
            "pyperclip",
            "pywin32"
            "colorama",
            "colorlog",
            "email_validator",
            "loguru",
            "openpyxl",
            "pandas",
            "pyautogui",
            "selenium",
            "typing",
            "webdriver_manager",
            "docling",
        ]

        for lib in libs:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                self.success_print(f"Suite RPA: Library {lib} installed successfully!")

            except subprocess.CalledProcessError:
                self.error_print(f"Suite RPA: Error installing library {lib}")


rpa = Suite()
