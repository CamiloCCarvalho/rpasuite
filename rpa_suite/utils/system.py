# rpa_suite/utils/system.py

# imports internal
from rpa_suite.functions._printer import error_print, success_print

# imports third-party
import sys, os


def set_importable_dir(display_message: bool = False):
    """
    Sets the directory to be importable by appending it to the system path.

    Parameters:
    ----------
        display_message: bool - If True, displays a success message after setting the directory.

    Returns:
    ----------
        None

    pt-br
    ----------
    Define o diretório para ser importável, adicionando-o ao caminho do sistema.

    Parâmetros:
    ----------
        display_message: bool - Se True, exibe uma mensagem de sucesso após definir o diretório.

    Retornos:
    ----------
        Nenhum
    """

    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        if display_message:
            success_print(f"Successfully set the directory for importation!")

    except Exception as e:
        error_print(
            f"An error occurred while executing the function: {set_importable_dir.__name__}! Error: {str(e)}."
        )
