import os, shutil
import time

def create_temp_dir(path_to_create: str = 'default') -> dict:
    
    """
    Função responsavel por criar diretório temporário para trabalhar com arquivos e etc. \n
    
    Parametros:
    ----------
    ``path_to_create: str`` - deve ser uma string com o path completo apontando para a pasta onde deve ser criada a pasta temporaria, se estiver vazio sera usado valor ``default`` que criará pasta no diretório atual onde o arquivo contendo esta função foi chamada.
    
    Retorno:
    ----------
    >>> type:dict
        * 'success': bool - representa se ação foi realizada com sucesso
        * 'path_deleted': str - path do diretório que foi criado no processo
    
    """
    
    # Variaveis Locais
    temp_dir_result: dict = {
        'success': bool,
        'path_created': str
    }
    
    # Pré tratamento
    default_dir: str
    try:
        if path_to_create == 'default':
            default_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            default_dir = path_to_create
    except Exception as e:
        temp_dir_result['success'] = False
        print(f'Erro ao capturar caminho atual para criar pasta temporária! Erro: {str(e)}')
        
    # Processo
    try:
        if not os.path.exists(fr'{default_dir}\temp'):
            try:
                os.mkdir(fr'{default_dir}\temp')
                if os.path.exists(fr'{default_dir}\temp'):
                    temp_dir_result['success'] = True
                else:
                    raise Exception
            except Exception as e:
                temp_dir_result['success'] = False
                print(f'Não foi possivel criar diretório temporario! {str(e)}')
        else:
            temp_dir_result['success'] = True
            print(fr'Diretório já criado em: {default_dir}\temp ')
    except Exception as e:
        print(f'Erro ao tentar criar pasta temporaria em: {default_dir} - Erro: {str(e)}')
        
    # Pós tratamento
    temp_dir_result['path_created'] = fr'{default_dir}\temp'
    
    # Retorno
    return temp_dir_result


def delete_temp_dir(path_to_delete: str = 'default') -> dict:
    
    """
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
    
    # Variaveis Locais
    temp_dir_result: dict = {
        'success': bool,
        'path_deleted': str
    }
    
    # Pré tratamento
    default_dir: str
    try:
        if path_to_delete == 'default':
            default_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            default_dir = path_to_delete
    except Exception as e:
        temp_dir_result['success'] = False
        print(f'Erro ao capturar caminho atual para deletar pasta temporária! Erro: {str(e)}')
        
    # Processo
    try:
        if os.path.exists(fr'{default_dir}\temp'):
            try:
                shutil.rmtree(fr'{default_dir}\temp')
                if not os.path.exists(fr'{default_dir}\temp'):
                    temp_dir_result['success'] = True
                else:
                    raise Exception
            except Exception as e:
                temp_dir_result['success'] = False
                print(f'Não foi possivel excluir diretório temporario! {str(e)}')
        else:
            temp_dir_result['success'] = True
            print(fr'Diretório já excluido: {default_dir}\temp. ')
            
    except Exception as e:
        print(fr'Erro ao tentar deletar pasta temporaria de arquivos em: {default_dir}\temp - Erro: {str(e)}')
        
    # Pós tratamento
    temp_dir_result['path_deleted'] = fr'{default_dir}\temp'
    
    # Retorno
    return temp_dir_result
        
create_temp_dir()
time.sleep(30)
delete_temp_dir()