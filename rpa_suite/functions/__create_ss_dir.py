# rpa_suite/functions/__create_ss_dir.py

# imports internal
# imports third-party
import os
from typing import Union

from rpa_suite.functions._printer import success_print


class CreateSSDirError(Exception):
    """Custom exception for Validate errors."""

    def __init__(self, message):
        clean_message = message.replace("CreateSSDirError:", "").strip()
        super().__init__(f"CreateSSDirError: {clean_message}")


# pylint: disable=duplicate-code
def __create_ss_dir(
    path_to_create: str = "default", name_ss_dir: str = "screenshots"
) -> dict[str, Union[bool, str, None]]:
    """
    Function responsible for creating a screenshots directory to work with your screenshot files. \n

    Parameters:
    ----------
    ``path_to_create: str`` - should be a string with the full path pointing to the folder where the screenshots folder should be created, if it is empty the ``default`` value will be used which will create a folder in the current directory where the file containing this function was called.

    ``name_ss_dir: str`` - should be a string representing the name of the logger directory to be created. If it is empty, the ``temp`` value will be used as the default directory name.

    Return:
    ----------
    >>> type:dict
        * 'success': bool - represents case the action was performed successfully
        * 'path_created': str - path of the directory that was created on the process

    Description: pt-br
    ----------
    Função responsavel por criar diretório de screenshots para trabalhar com seus arquivos de sreenshot. \n

    Parametros:
    ----------
    ``path_to_create: str`` - deve ser uma string com o path completo apontando para a pasta onde deve ser criada a pasta temporaria, se estiver vazio sera usado valor ``default`` que criará pasta no diretório atual onde o arquivo contendo esta função foi chamada.

    ``name_ss_dir: str`` - deve ser uma string representando o nome do diretório de screenshots a ser criado. Se estiver vazio, o valor ``screenshots`` será usado como o nome padrão do diretório.

    Retorno:
    ----------
    >>> type:dict
        * 'success': bool - representa se ação foi realizada com sucesso
        * 'path_created': str - path do diretório que foi criado no processo
    """

    # Variáveis locais
    result: dict = {  # pylint: disable=duplicate-code
        "success": False,
        "path_created": None,
    }

    try:
        # por padrão, define o path para o diretório de execução do script
        if path_to_create == "default":  # pylint: disable=duplicate-code
            path_to_create = os.getcwd()

        # Monta o caminho para o novo diretório
        full_path: str = os.path.join(path_to_create, name_ss_dir)

        # Tenta criar o diretório
        try:
            os.makedirs(full_path, exist_ok=False)
            result["success"] = True
            result["path_created"] = rf"{full_path}"
            success_print(f"Diretório:'{full_path}' foi criado com sucesso.")

        except FileExistsError:
            result["success"] = False
            result["path_created"] = full_path
            # alert_print(f"Diretório:'{full_path}' já existe.")

        except PermissionError as e:
            result["success"] = False
            result["path_created"] = None
            raise CreateSSDirError(f"Permissão negada: não é possível criar o diretório '{full_path}'.") from e

    except Exception as e:
        result["success"] = False
        result["path_created"] = None
        raise CreateSSDirError(
            f"Erro ao capturar o caminho atual para criar o diretório de screenshots! Erro: {str(e)}"
        ) from e

    return result
