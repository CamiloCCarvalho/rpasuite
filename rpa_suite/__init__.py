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
    ``database``: RPA execution tracking (SQLite/PostgreSQL/MySQL/SQL Server)
    ``utils``: System utility helpers
    ``ParallelRunner``: Object ParallelRunner functions to run in parallel
    ``AsyncRunner``: Object AsyncRunner functions to run in Assyncronous
    ``Browser``: Object Browser automation functions (neeeds Selenium and Webdriver_Manager)
    ``Iris``: Object Iris automation functions to convert documents with OCR + IA based on ``docling``

"""

__version__ = "1.9.0"

# allows importing the rpa_suite module without the package name
from .suite import rpa
