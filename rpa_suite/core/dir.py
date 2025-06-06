# rpa_suite/core/dir.py

# imports standard
import os
import shutil
from typing import Union

# imports internal
from rpa_suite.functions._printer import error_print, alert_print, success_print


class Directory:
    """
    Class that provides utilities for directory management, including creating, deleting, and manipulating directories.

    This class offers functionalities for:
        - Creating temporary directories
        - Deleting directories
        - Checking if a directory exists
        - Listing files in a directory

    Methods:
        create_temp_dir: Creates a temporary directory for file operations.

    The Directory class is part of RPA Suite and can be accessed through the rpa object:
        >>> from rpa_suite import rpa
        >>> rpa.directory.create_temp_dir(path_to_create='my_folder', name_temp_dir='temp_dir')

    Parameters:
        path_to_create (str): The full path where the temporary directory should be created. Default is 'default', which creates it in the current directory.
        name_temp_dir (str): The name of the temporary directory to be created. Default is 'temp'.

    pt-br
    ----------
    Classe que fornece utilitários para gerenciamento de diretórios, incluindo criação, exclusão e manipulação de diretórios.

    Esta classe oferece funcionalidades para:
        - Criar diretórios temporários
        - Excluir diretórios
        - Verificar se um diretório existe
        - Listar arquivos em um diretório

    Métodos:
        create_temp_dir: Cria um diretório temporário para operações com arquivos.

    A classe Directory é parte do RPA Suite e pode ser acessada através do objeto rpa:
        >>> from rpa_suite import rpa
        >>> rpa.directory.create_temp_dir(path_to_create='minha_pasta', name_temp_dir='temp_dir')

    Parâmetros:
        path_to_create (str): O caminho completo onde o diretório temporário deve ser criado. O padrão é 'default', que o cria no diretório atual.
        name_temp_dir (str): O nome do diretório temporário a ser criado. O padrão é 'temp'.
    """

    def __init__(self): 
        """
        Função construtora da Classe que fornece utilitários para gerenciamento de:\n
        diretórios, incluindo criação, exclusão e manipulação de diretórios.
        """
        ...

    def create_temp_dir(
        self,
        path_to_create: str = "default",
        name_temp_dir: str = "temp",
        display_message: bool = False,
    ) -> dict[str, Union[bool, str, None]]:
        """
        Function responsible for creating a temporary directory to work with files and etc. \n

        Parameters:
        ----------
        ``path_to_create: str`` - should be a string with the full path pointing to the folder where the temporary folder should be created, if it is empty the ``default`` value will be used which will create a folder in the current directory where the file containing this function was called.

        ``name_temp_dir: str`` - should be a string representing the name of the temporary directory to be created. If it is empty, the ``temp`` value will be used as the default directory name.

        ``display_message: bool`` - should be a bool to display messages on terminal, by default False.

        Return:
        ----------
        >>> type:dict
            * 'success': bool - represents case the action was performed successfully
            * 'path_created': str - path of the directory that was created on the process

        Description: pt-br
        ----------
        Função responsavel por criar diretório temporário para trabalhar com arquivos e etc. \n

        Parametros:
        ----------
        ``path_to_create: str`` - deve ser uma string com o path completo apontando para a pasta onde deve ser criada a pasta temporaria, se estiver vazio sera usado valor ``default`` que criará pasta no diretório atual onde o arquivo contendo esta função foi chamada.

        ``name_temp_dir: str`` - deve ser uma string representando o nome do diretório temporário a ser criado. Se estiver vazio, o valor ``temp`` será usado como o nome padrão do diretório.

        ``display_message: bool`` - deve ser um bool para exibir mensagens no terminal, por padrão False.

        Retorno:
        ----------
        >>> type:dict
            * 'success': bool - representa se ação foi realizada com sucesso
            * 'path_created': str - path do diretório que foi criado no processo
        """

        # Local Variables
        result: dict = {
            "success": bool,
            "path_created": str,
        }

        try:
            # by 'default', defines path to local script execution path
            if path_to_create == "default":
                path_to_create: str = os.getcwd()

            # Build path to new dir
            full_path: str = os.path.join(path_to_create, name_temp_dir)

            # Create dir in this block
            try:

                # Successefully created
                os.makedirs(full_path, exist_ok=False)

                result["success"] = True
                result["path_created"] = rf"{full_path}"

                if display_message:
                    success_print(f"Directory:'{full_path}' successfully created.")

            except FileExistsError:
                result["success"] = False
                result["path_created"] = None
                if display_message:
                    alert_print(f"Directory:'{full_path}' already exists.")

            except PermissionError:
                result["success"] = False
                result["path_created"] = None
                alert_print(f"Permission denied: Not possible to create Directory '{full_path}'.")

        except Exception as e:
            result["success"] = False
            result["path_created"] = None
            error_print(f"Error capturing current path to create temporary directory! Error: {str(e)}")

        return result

    def delete_temp_dir(
        self,
        path_to_delete: str = "default",
        name_temp_dir: str = "temp",
        delete_files: bool = False,
        display_message: bool = False,
    ) -> dict[str, Union[bool, str, None]]:
        """
        Function responsible for deleting a temporary directory. \n

        Parameters:
        ----------
        ``path_to_delete: str`` - should be a string with the full path pointing to the folder where the temporary folder should be deleted, if it is empty the ``default`` value will be used which will delete a folder in the current directory where the file containing this function was called.

        ``name_temp_dir: str`` - should be a string representing the name of the temporary directory to be deleted. If it is empty, the ``temp`` value will be used as the default directory name.

        ``delete_files: bool`` - should be a boolean indicating whether to delete files in the directory. If it is False, files in the directory will not be deleted.

        Return:
        ----------
        >>> type:dict
            * 'success': bool - represents case the action was performed successfully
            * 'path_deleted': str - path of the directory that was deleted on the process

        Description: pt-br
        ----------
        Função responsavel por deletar diretório temporário. \n

        Parametros:
        ----------
        ``path_to_delete: str`` - deve ser uma string com o path completo apontando para a pasta onde deve ser deletada a pasta temporaria, se estiver vazio sera usado valor ``default`` que deletará pasta no diretório atual onde o arquivo contendo esta função foi chamada.

        ``name_temp_dir: str`` - deve ser uma string representando o nome do diretório temporário a ser deletado. Se estiver vazio, o valor ``temp`` será usado como o nome padrão do diretório.

        ``delete_files: bool`` - deve ser um booleano indicando se deve deletar arquivos no diretório. Se for False, arquivos no diretório não serão deletados.

        Retorno:
        ----------
        >>> type:dict
            * 'success': bool - representa se ação foi realizada com sucesso
            * 'path_deleted': str - path do diretório que foi deletado no processo
        """

        # Local Variables
        result: dict = {
            "success": bool,
            "path_deleted": str,
        }

        try:
            # by 'default', defines path to local script execution path
            if path_to_delete == "default":
                path_to_delete: str = os.getcwd()

            # Build path to new dir
            full_path: str = os.path.join(path_to_delete, name_temp_dir)

            # Delete dir in this block
            try:

                # Check if directory exists
                if os.path.exists(full_path):

                    # Check if delete_files is True
                    if delete_files:
                        # Delete all files in the directory
                        shutil.rmtree(full_path)

                    else:
                        # Delete the directory only
                        os.rmdir(full_path)

                    result["success"] = True
                    result["path_deleted"] = rf"{full_path}"

                    if display_message:
                        success_print(f"Directory:'{full_path}' successfully delete.")
                else:
                    result["success"] = False
                    result["path_deleted"] = None
                    if display_message:
                        alert_print(f"Directory:'{full_path}' don't exists.")

            except PermissionError:
                result["success"] = False
                result["path_deleted"] = None
                alert_print(f"Permission denied: Not possible to delete Directory '{full_path}'.")

        except Exception as e:
            result["success"] = False
            result["path_deleted"] = None
            error_print(f"Error capturing current path to delete temporary directory! Error: {str(e)}.")

        return result
