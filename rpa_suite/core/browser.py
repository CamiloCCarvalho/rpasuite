# rpa_suite/core/browser.py

# imports internal
from rpa_suite.functions._printer import error_print, alert_print, success_print

# imports external
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# imports third-party
from time import sleep
import os, requests


class Browser():
    
    """
    Browser Object for Automation (Work in Progress)
    This class provides an interface for automating browser interactions using 
    Google Chrome with a debugging port. It includes methods for starting, 
    configuring, navigating, and interacting with the browser. The implementation 
    is still under development and may require further enhancements.
    
    Attributes:
        driver: The WebDriver instance used to control the browser.
        port (int): The debugging port used to connect to the browser. Default is 9393.
        path_driver (str): The path to the ChromeDriver executable.
        
    Methods:
        __init__(port: int = 9393, close_all_chrome_on_this_port: bool = False):
            Initializes the Browser object with the specified debugging port and 
            optionally closes all Chrome instances running on the same port.
        configure_browser() -> None:
            Configures the browser with debugging options and initializes the WebDriver.
        start_browser(close_chrome_on_this_port: bool = True, display_message: bool = False):
            Starts the Chrome browser with the specified debugging port and initializes 
            the WebDriver.
        find_ele(value, by=By.XPATH, timeout=12, display_message=True):
            Finds a single element on the page using the specified locator strategy.
        get(url: str, display_message: bool = False):
            Navigates the browser to the specified URL.
        _close_all_chrome():
            Closes all Chrome processes forcefully.
        close_browser(display_message: bool = False):
            Closes the browser instance and terminates the associated Chrome processes.
    
    pt-br
    ----------
    Objeto Browser para Automação (Em Desenvolvimento)
    Esta classe fornece uma interface para automação de interações com o navegador 
    Google Chrome utilizando uma porta de depuração. Inclui métodos para iniciar, 
    configurar, navegar e interagir com o navegador. A implementação ainda está em 
    desenvolvimento e pode requerer melhorias adicionais.
    
    Atributos:
        driver: A instância do WebDriver usada para controlar o navegador.
        port (int): A porta de depuração usada para conectar ao navegador. O padrão é 9393.
        path_driver (str): O caminho para o executável do ChromeDriver.
        
    Métodos:
        __init__(port: int = 9393, close_all_chrome_on_this_port: bool = False):
            Inicializa o objeto Browser com a porta de depuração especificada e, 
            opcionalmente, fecha todas as instâncias do Chrome que estão sendo executadas 
            na mesma porta.
        configure_browser() -> None:
            Configura o navegador com opções de depuração e inicializa o WebDriver.
        start_browser(close_chrome_on_this_port: bool = True, display_message: bool = False):
            Inicia o navegador Chrome com a porta de depuração especificada e inicializa 
            o WebDriver.
        find_ele(value, by=By.XPATH, timeout=12, display_message=True):
            Localiza um único elemento na página usando a estratégia de localização especificada.
        get(url: str, display_message: bool = False):
            Navega o navegador para a URL especificada.
        _close_all_chrome():
            Fecha todos os processos do Chrome de forma forçada.
        close_browser(display_message: bool = False):
            Fecha a instância do navegador e termina os processos associados do Chrome.
    """

    driver: None
    port: int = None
    path_driver = None
    
    def __init__(self, port: int = 9393, close_all_chrome_on_this_port: bool = False):
        self.port = port
        self.path_driver = ChromeDriverManager().install()

        if close_all_chrome_on_this_port: self._close_all_chrome()
        ...

    def configure_browser(self) -> None:
        """
        Configures the browser instance with specified options and initializes the WebDriver.
        This method sets up the browser with debugging options, maximized window, and disables notifications.
        It also verifies the existence of the ChromeDriver executable at the specified path before creating
        the WebDriver instance.
        Raises:
            FileNotFoundError: If the specified path to the ChromeDriver executable does not exist.
            Exception: For any other errors encountered during the browser configuration process.
        """
        
        try:
            # Use the absolute path from comment
            
            options = Options()
            options.add_experimental_option("debuggerAddress",
                                         f"127.0.0.1:{str(self.port)}")
            
            # Additional configs  
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")
            
            # Verifica se o caminho do driver está correto
            if not os.path.exists(self.path_driver):
                raise FileNotFoundError(f'O caminho do driver não foi encontrado: {self.path_driver}')
            
            # Create driver with options and chromedriver path
            self.driver = webdriver.Chrome(
                #service=self.path_driver,
                options=options,
                keep_alive=True
            )

        except Exception as e:
            error_print(f'Erro durante a função: {self.configure_browser.__name__}! Error: {str(e)}.')

    def start_browser(self, close_chrome_on_this_port: bool = True, display_message: bool = False):
        """
        Starts a Chrome browser instance with remote debugging enabled.
        Args:
            close_chrome_on_this_port (bool): If True, closes any existing Chrome instance using the specified debugging port before starting a new one. Defaults to True.
            display_message (bool): If True, displays a success message upon successfully starting the browser. Defaults to False.
        Raises:
            Exception: If an error occurs while starting the browser or connecting to the debugging port.
        Behavior:
            - Closes any existing Chrome instance on the specified debugging port if `close_chrome_on_this_port` is True.
            - Launches Chrome with the specified debugging port and user data directory.
            - Waits until Chrome is fully initialized and accessible via the debugging port.
            - Configures the browser instance using the `configure_browser` method.
            - Optionally displays a success message if `display_message` is True.
        """
        
        try:
            if close_chrome_on_this_port: self.close_browser()

            # Inicia o Chrome com debugging port
            os.system(f'start chrome.exe --remote-debugging-port={str(self.port)} --user-data-dir="C:/temp/chrome_profile"')

            # Aguardar até que o Chrome esteja realmente aberto
            while True:
                try:
                    # Tenta conectar ao Chrome na porta de depuração
                    response = requests.get(f'http://127.0.0.1:{self.port}/json')
                    if response.status_code == 200:
                        break  # O Chrome está aberto
                except requests.ConnectionError:
                    sleep(1)  # Espera um segundo antes de tentar novamente
            
            # Inicializa o Chrome com as opções
            self.configure_browser()
            
            if display_message: success_print(f'Browser: Iniciado com sucesso!')
            
        except Exception as e:
            error_print(f'Erro ao iniciar navegador: {str(e)}.')


    def find_ele(self, value: str, by:By=By.XPATH, timeout=12, display_message=True):
        """
        Locate and return a web element on the page using the specified locator strategy.
        Args:
            value (str): The locator value to identify the web element.
            by (selenium.webdriver.common.by.By, optional): The locator strategy to use. 
                Defaults to By.XPATH.
            timeout (int, optional): The maximum time to wait for the element to appear, in seconds. 
                Defaults to 12.
            display_message (bool, optional): Whether to display an error message if the element 
                is not found. Defaults to True.
        Returns:
            selenium.webdriver.remote.webelement.WebElement: The located web element if found.
            None: If the element is not found or an exception occurs.
        Raises:
            Exception: Propagates any exception encountered during the element search if 
                `display_message` is set to False.
        """
        
        try:
            sleep(2)
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            ); return element
        
        except Exception as e:

            if display_message:
                error_print(f'Erro durante a função: {self.find_ele.__name__}! Error: {str(e)}.')
                return None
            else: return None

    # find elements (needs implementation)
    ...
    
    # navigate
    def get(self, url: str, display_message: bool = False):
        """
        Navigates the browser to the specified URL.
        Args:
            url (str): The URL to navigate to.
            display_message (bool, optional): If True, displays a success message upon navigation. Defaults to False.
        Raises:
            Exception: If an error occurs while navigating to the URL, it logs the error message.
        """
        
        try:
            self.driver.get(url)
            if display_message: success_print(f'Browser: Navegando para: {url}')
            
        except Exception as e:
            error_print(f'Erro ao navegar para a URL: {url}. Error: {str(e)}.')


    def _close_all_browsers(self):
        """
        Forcefully closes all instances of Google Chrome running on the system.
        This method uses the `taskkill` command to terminate all processes with the name
        "chrome.exe". Any errors during the execution of the command are silently ignored.
        Note:
            This method is specific to Windows operating systems and will not work on other platforms.
        """

        try:
            os.system('taskkill /F /IM chrome.exe >nul 2>&1')
        except:
            pass


    def close_browser(self, display_message: bool = False):
        """
        Fecha o navegador controlado pelo Selenium e encerra os processos relacionados ao Chrome.
        Este método tenta fechar o navegador de forma ordenada utilizando os métodos `close` e `quit` do Selenium.
        Caso esses métodos falhem, ele força o encerramento do processo do Chrome associado à porta de depuração remota.
        Em último caso, pode encerrar todos os processos do Chrome relacionados à porta especificada.
        Args:
            display_message (bool): Indica se mensagens de status devem ser exibidas durante o processo de fechamento.
        Comportamento:
            - Tenta fechar o navegador utilizando `self.driver.close()` e `self.driver.quit()`.
            - Aguarda um momento para liberar o processo.
            - Força o encerramento do processo do Chrome associado à porta de depuração remota.
            - Verifica se o processo foi encerrado e tenta métodos mais agressivos, se necessário.
            - Em caso de falha crítica, tenta encerrar todos os processos do Chrome relacionados à porta especificada.
        Exceções:
            - Captura e exibe mensagens de erro caso ocorra falha ao fechar o navegador.
        Observação:
            Use com cautela, especialmente o encerramento extremo, pois pode afetar outros processos do Chrome em execução.
        """
        
        try:
            # Primeiro tenta fechar todas as janelas via Selenium
            try:
                self.driver.close()
            except:
                pass
                
            # Depois tenta encerrar a sessão
            try:
                self.driver.quit()
            except:
                pass
            
            # Aguarda um momento para o processo ser liberado
            sleep(1)
            
            # Força o fechamento do processo específico do Chrome
            os.system(f'taskkill /f /im chrome.exe /fi "commandline like *--remote-debugging-port={str(self.port)}*" >nul 2>&1')
            
            # Verifica se o processo foi realmente terminado
            check = os.system(f'tasklist /fi "imagename eq chrome.exe" /fi "commandline like *--remote-debugging-port={str(self.port)}*" >nul 2>&1')
            
            if check == 0:
                # Processo ainda existe, tenta método mais agressivo
                os.system(f'taskkill /f /im chrome.exe /fi "commandline like *--remote-debugging-port={str(self.port)}*" /t >nul 2>&1')
                if display_message: alert_print(f'Browser: Fechado via força!')
                
            else:
                if display_message: success_print(f'Browser: Fechado com sucesso!')
            
        except Exception as e:
            
            
            try:
                if display_message: alert_print(f'Erro ao fechar navegador: {str(e)}, Tentando meio mais forte!')

                # Último recurso - mata todos os processos do Chrome (use com cautela)
                os.system(f'taskkill /f /im chrome.exe /fi "commandline like *--remote-debugging-port={str(self.port)}*" /t >nul 2>&1')
                if display_message: alert_print(f'Browser: Fechado via força extrema!')
                
            except Exception as error_ultimate:
                if display_message: error_print(f'Falha crítica ao tentar fechar o navegador! Error: {str(error_ultimate)}!')
