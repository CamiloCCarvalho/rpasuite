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
            default_dir = fr'{path_to_create}'
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


def clear_temp_dir(path_to_clear: str = 'default', name_dir: str = '') -> dict:
    
    """
    Function responsible for cleaning the temporary directory at the specified path. \n
    
    Parameters:
    ----------
    ``path_to_cleaned: str`` - a string that points to the destination to be cleaned, which can be: \n
        - relative path - based on the file where this function is being called
        - absolute path - based on the local disk of the machine or server
            
    If not declared or if the argument is left empty, then the ``default`` value will be used, which will search for the folder in the current directory where the file containing this function was called.
    
    Return:
    ----------
    >>> type:dict
        * 'success': bool - represents if the action was performed successfully
        * 'path_cleaned': str - path of the directory that was cleaned in the process
        
    Description: pt-br
    ----------
    Função responsavel por limpar o diretório temporário no caminho especificado. \n
    
    Parametros:
    ----------
    ``path_to_cleaned: str`` - uma string que aponta para o destino a limpar podendo ser: \n
        - caminho relativo - com base no arquivo onde esta sendo chamada a função
        - caminho absoluto - com base no disco local da maquina ou servidor
        
    não declarar ou deixar o argumento vazio então será usado valor ``default`` que buscará a pasta no diretório atual onde o arquivo contendo esta função foi chamada.
    
    Retorno:
    ----------
    >>> type:dict
        * 'success': bool - representa se ação foi realizada com sucesso
        * 'path_cleaned': str - path do diretório que foi executada limpeza no processo
    """
    
    # Local Variables
    temp_dir_result: dict = {
        'success': bool,
        'path_cleaned': str
    }
    
    # Preprocessing
    default_dir: str
    personal_name_dir_clear: str = 'temp' if name_dir == '' else name_dir
    
    # Process
    try:
        if path_to_clear == 'default':
            default_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            default_dir = fr'{path_to_clear}'
    except Exception as e:
        temp_dir_result['success'] = False
        error_print(f'Unable to capture current path to clear temporary folder! Error: {str(e)}')
        
    try:
        if os.path.exists(fr'{default_dir}/{personal_name_dir_clear}'):
            for root, dirs, files in os.walk(fr'{default_dir}\{personal_name_dir_clear}', topdown=False):
                for name in files:
                    try:
                        os.remove(os.path.join(root, name))
                    except:
                        pass
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root, name))
                    except:
                        pass
            temp_dir_result['success'] = True
            success_print(fr'Directory cleaned: "{default_dir}\{personal_name_dir_clear}"')
        else:
            temp_dir_result['success'] = False
            temp_dir_result['path_cleaned'] = None
            alert_print(fr'Directory does not exist: "{default_dir}\{personal_name_dir_clear}"')
            
    except Exception as e:
        error_print(fr'Error when trying to clear temporary directory: "{default_dir}\{personal_name_dir_clear}" - Error: {str(e)}')
        
    # Postprocessing
    if temp_dir_result['success']:
        temp_dir_result['path_cleaned'] = fr'{default_dir}\{personal_name_dir_clear}'
    
    return temp_dir_result
