# rpa_suite/core/__init__.py

"""
The Core module is where we can import all Sub-Objects used by the rpa_suite module separately, categorized by their respective classes based on functionality. However, we can also use them through the main rpa object using the following syntax:
>>> from rpa_suite import rpa
>>> rpa.clock.wait_for_exec(foo)
>>> rpa.file.screen_shot() ...
or
>>> from rpa_suite.core.clock import Clock
>>> clock = Clock()
>>> clock.wait_for_exec()

pt-br
----------
O módulo Core é de onde podemos importar todos os Sub-Objetos usados pelo módulo rpa_suite de forma separada, categorizados por suas respectivas classes com base na funcionalidade. No entanto, também podemos usá-los através do objeto principal rpa usando a seguinte sintaxe:
>>> from rpa_suite import rpa
>>> rpa.clock.wait_for_exec()
>>> rpa.file.screen_shot() ...
ou
>>> from rpa_suite.core.clock import Clock
>>> clock = Clock()
>>> clock.wait_for_exec(foo)

"""

# On this case, we are importing the (Browser|Iris|Artemis) class only if the (selenium and webdriver_manager| docling| pyautogui) modules are installed.
# This is useful to avoid unnecessary imports and dependencies if the user does not need the (Browser|Iris|Artemis) functionality.
import importlib.util

from .asyncrun import AsyncRunner
from .clock import Clock
from .database import Database
from .date import Date
from .dir import Directory
from .email import Email
from .file import File
from .log import Log
from .parallel import ParallelRunner
from .print import Print
from .regex import Regex
from .validate import Validate

# from .browser import Browser
if importlib.util.find_spec("selenium") and importlib.util.find_spec("webdriver_manager"):
    from .browser import Browser

# from .iris import Iris
if importlib.util.find_spec("docling"):
    from .iris import Iris

# from .iris import Artemis
if importlib.util.find_spec("pyautogui"):
    from .artemis import Artemis

__version__ = "1.6.5"
