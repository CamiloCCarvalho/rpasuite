import os, shutil
from rpa_suite.log.printer import error_print, alert_print, success_print

def create_temp_dir(path_to_create: str = 'default') -> dict:
    
    """
    Function responsible for creating a temporary directory to work with files and etc. \n
    
    Parameters:
    ----------
    ``path_to_create: str`` - should be a string with the full path pointing to the folder where the temporary folder should be created, if it is empty the ``default`` value will be used which will create a folder in the current directory where the file containing this function was called.
    
    Return:
    ----------
    >>> type:dict
        * 'success': bool - represents if the action was performed successfully
        * 'path_created': str - path of the directory that was created in the process
        
    Description: pt-br
    ----------
    Função responsavel por criar diretório temporário para trabalhar com arquivos e etc. \n
    
    Parametros:
    ----------
    ``path_to_create: str`` - deve ser uma string com o path completo apontando para a pasta onde deve ser criada a pasta temporaria, se estiver vazio sera usado valor ``default`` que criará pasta no diretório atual onde o arquivo contendo esta função foi chamada.
    
    Retorno:
    ----------
    >>> type:dict
        * 'success': bool - representa se ação foi realizada com sucesso
        * 'path_created': str - path do diretório que foi criado no processo
    """
    
    # Local Variables
    result: dict = {
        'success': bool,
        'path_created': str
    }
    
    # Preprocessing
    default_dir: str
    try:
        if path_to_create == 'default':
            default_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            default_dir = path_to_create
    except Exception as e:
        result['success'] = False
        error_print(f'Error capturing current path to create temporary directory! Error: {str(e)}')
        
    # Process
    try:
        if not os.path.exists(fr'{default_dir}\temp'):
            try:
                os.mkdir(fr'{default_dir}\temp')
                if os.path.exists(fr'{default_dir}\temp'):
                    result['success'] = True
                    success_print(fr'Directory created in: {default_dir}\temp')
                else:
                    result['success'] = False
                    raise Exception
            except Exception as e:
                error_print(f'Unable to create temporary directory! Error: {str(e)}')
        else:
            result['success'] = True
            alert_print(fr'NOTICE! directory already exists in: {default_dir}\temp ')
    except Exception as e:
        error_print(f'Error when trying to create temporary directory in: {default_dir} - Error: {str(e)}')
        
    # Postprocessing
    result['path_created'] = fr'{default_dir}\temp'
    
    return result


def delete_temp_dir(path_to_delete: str = 'default') -> dict:
    
    """
    Function responsible for deleting temporary directory at the specified path. \n
    
    Parameters:
    ----------
    ``path_to_delete: str`` - should be a string with the full path pointing to the folder where the temporary folder should be deleted, if it is empty the ``default`` value will be used which will search for a folder in the current directory where the file containing this function was called.
    
    Return:
    ----------
    >>> type:dict
        * 'success': bool - represents if the action was performed successfully
        * 'path_deleted': str - path of the directory that was deleted in the process
        
    Description: pt-br
    ----------
    Função responsavel por deletar diretório temporário no caminho especificado. \n
    
    Parametros:
    ----------
    ``path_to_delete: str`` - deve ser uma string com o path completo apontando para a pasta onde deve ser deletada a pasta temporaria, se estiver vazio sera usado valor ``default`` que buscará pasta no diretório atual onde o arquivo contendo esta função foi chamada.
    
    Retorno:
    ----------
    >>> type:dict
        * 'success': bool - representa se ação foi realizada com sucesso
        * 'path_deleted': str - path do diretório que foi excluido no processo
    """
    
    # Local Variables
    temp_dir_result: dict = {
        'success': bool,
        'path_deleted': str
    }
    
    # Preprocessing
    default_dir: str
    try:
        if path_to_delete == 'default':
            default_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            default_dir = path_to_delete
    except Exception as e:
        temp_dir_result['success'] = False
        error_print(f'Unable to capture current path to delete temporary folder! Error: {str(e)}')
        
    # Process
    try:
        if os.path.exists(fr'{default_dir}\temp'):
            try:
                shutil.rmtree(fr'{default_dir}\temp')
                if not os.path.exists(fr'{default_dir}\temp'):
                    temp_dir_result['success'] = True
                    success_print(fr'Directory deleted in: {default_dir}\temp')
                else:
                    temp_dir_result['success'] = False
                    raise Exception
            except Exception as e:
                error_print(f'Unable to delete temporary directory! Error: {str(e)}')
        else:
            temp_dir_result['success'] = True
            alert_print(fr'Directory does not exist in: {default_dir}\temp. ')
            
    except Exception as e:
        error_print(fr'Error when trying to delete temporary directory in: {default_dir}\temp - Error: {str(e)}')
        
    # Postprocessing
    temp_dir_result['path_deleted'] = fr'{default_dir}\temp'
    
    return temp_dir_result
