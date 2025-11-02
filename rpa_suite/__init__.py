# rpa_suite/__init__.py

"""
RPA Suite is a Python module that provides a set of tools for process automation.

To use the module, import it as follows:
    >>> from rpa_suite import rpa

Example of usage:
    >>> from rpa_suite import rpa
    >>> rpa.email.send_smtp(
    ...     email_user="your@email.com",
    ...     email_password="123",
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
    ...     email_password="123",
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

__version__ = "1.6.5"

# allows importing the rpa_suite module without the package name
from .suite import rpa
