# rpa_suite/core/parallel.py

# imports third-party
from multiprocessing import Process, Manager
from typing import Any, Callable, Dict, Optional, TypeVar, Generic
import time
import traceback

# Define a generic type for the function return
T = TypeVar('T')


class ParallelRunner(Generic[T]):
    
    """
    Class to execute functions in parallel while maintaining the main application flow.
    
    Allows starting a function in a separate process and retrieving its result later.
    
    pt-br
    ------
    Classe para executar funções em paralelo mantendo o fluxo principal da aplicação.
    
    Permite iniciar uma função em um processo separado e obter seu resultado posteriormente.
    """
    
    display_message = None
    
    def __init__(self, display_message: bool = False):
        """
        Initializes the ParallelRunner.

        Args:
            display_message (bool): If True, displays debug messages during execution.

        pt-br
        ------
        Inicializa o ParallelRunner.

        Args:
            display_message (bool): Se True, exibe mensagens de debug durante a execução.
        """
        
        self._manager = Manager()
        self._result_dict = self._manager.dict()
        self._process = None
        self._start_time = None
        self.display_message = display_message
        
    @staticmethod
    def _execute_function(function, args, kwargs, result_dict):
        """
        Static method that executes the target function and stores the result.
        This function needs to be defined at the module level to be "picklable".

        pt-br
        ------
        Função estática que executa a função alvo e armazena o resultado.
        Esta função precisa ser definida no nível do módulo para ser "picklable".
        """
        try:
            # Executa a função do usuário com os argumentos fornecidos
            result = function(*args, **kwargs)
            
            # Armazena o resultado no dicionário compartilhado
            result_dict['status'] = 'success'
            result_dict['result'] = result
            
            # Para debug
            #print(f"[Processo Filho] Resultado calculado: {result}")
            #print(f"[Processo Filho] Dicionário de resultados: {dict(result_dict)}")
            
        except Exception as e:
            # Em caso de erro, armazena informações sobre o erro
            result_dict['status'] = 'error'
            result_dict['error'] = str(e)
            result_dict['traceback'] = traceback.format_exc()
            
            # Para debug
            print(f"[Processo Filho] Erro ocorrido: {str(e)}")
        
    @staticmethod
    def _execute_function_w_disp_msg(function, args, kwargs, result_dict):
        """
        Static method that executes the target function and stores the result.
        This function needs to be defined at the module level to be "picklable".

        pt-br
        ------
        Função estática que executa a função alvo e armazena o resultado.
        Esta função precisa ser definida no nível do módulo para ser "picklable".
        """
        try:
            # Executa a função do usuário com os argumentos fornecidos
            result = function(*args, **kwargs)
            
            # Armazena o resultado no dicionário compartilhado
            result_dict['status'] = 'success'
            result_dict['result'] = result
            
            # Para debug
            print(f"[Processo Filho] Resultado calculado: {result}")
            print(f"[Processo Filho] Dicionário de resultados: {dict(result_dict)}")
            
        except Exception as e:
            # Em caso de erro, armazena informações sobre o erro
            result_dict['status'] = 'error'
            result_dict['error'] = str(e)
            result_dict['traceback'] = traceback.format_exc()
            
            # Para debug
            print(f"[Processo Filho] Erro ocorrido: {str(e)}")   
    
    
    def run(self, function: Callable[..., T], *args, **kwargs) -> 'ParallelRunner[T]':
        """
        Starts the execution of the function in a parallel process.
        
        Args:
            function: Function to be executed in parallel
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            self: Returns the instance itself to allow chained calls

        pt-br
        ------
        Inicia a execução da função em um processo paralelo.
        
        Args:
            function: Função a ser executada em paralelo
            *args: Argumentos posicionais para a função
            **kwargs: Argumentos nomeados para a função
            
        Returns:
            self: Retorna a própria instância para permitir chamadas encadeadas
        """
        # Limpar resultado anterior, se houver
        if self._result_dict:
            self._result_dict.clear()
        
        # Configura valores iniciais no dicionário compartilhado
        self._result_dict['status'] = 'running'
        
        # Inicia o processo com a função auxiliar estática
        if self.display_message:
            self._process = Process(
                target=ParallelRunner._execute_function_w_disp_msg, 
                args=(function, args, kwargs, self._result_dict)
            )
        else:
            self._process = Process(
                target=ParallelRunner._execute_function, 
                args=(function, args, kwargs, self._result_dict)
            )
        
        self._process.daemon = True  # Processo filho termina quando o principal termina
        self._process.start()
        self._start_time = time.time()
        
        return self

    def is_running(self) -> bool:
        """
        Checks if the process is still running.
        
        Returns:
            bool: True if the process is still running, False otherwise
        
        pt-br
        ------
        Verifica se o processo ainda está em execução.
        
        Retorna:
            bool: True se o processo ainda estiver em execução, False caso contrário
        """
        if self._process is None:
            return False
        return self._process.is_alive()
    
    def get_result(self, timeout: Optional[float] = 60, terminate_on_timeout: bool = True) -> Dict[str, Any]:
        """
        Retrieves the result of the parallel execution.
        
        Args:
            timeout: Maximum time (in seconds) to wait for the process to finish.
            None means wait indefinitely.
            terminate_on_timeout: If True, terminates the process if the timeout is reached.
            
        Returns:
            - Dict containing:
            - success: bool indicating if the operation was successful.
            - result: result of the function (if successful).
            - error: error message (if any).
            - traceback: full stack trace (if an error occurred).
            - execution_time: execution time in seconds.
            - terminated: True if the process was terminated due to timeout.
        
        pt-br
        ------
        
        Recupera o resultado da execução paralela.
        
        Args:
            timeout: Tempo máximo (em segundos) para aguardar o término do processo.
            None significa aguardar indefinidamente.
            terminate_on_timeout: Se True, termina o processo se o tempo limite for atingido.
            
        Retorna:
            - Dicionário contendo:
            - success: bool indicando se a operação foi bem-sucedida.
            - result: resultado da função (se bem-sucedida).
            - error: mensagem de erro (se houver).
            - traceback: rastreamento completo da pilha (se ocorreu um erro).
            - execution_time: tempo de execução em segundos.
            - terminated: True se o processo foi terminado devido ao tempo limite.
        """
        
        if self._process is None:
            return {
                'success': False, 
                'error': 'Nenhum processo foi iniciado',
                'execution_time': 0,
                'terminated': False
            }
        
        # Aguarda o processo terminar com tempo limite
        self._process.join(timeout=timeout)
        execution_time = time.time() - self._start_time
        
        # Preparamos o dicionário de resposta
        result = {
            'execution_time': execution_time,
            'terminated': False
        }
        
        # Debug - mostra o dicionário compartilhado
        if self.display_message: print(f"[Processo Principal] Dicionário compartilhado: {dict(self._result_dict)}")
        
        # Verifica se o processo terminou ou se atingiu o timeout
        if self._process.is_alive():
            if terminate_on_timeout:
                self._process.terminate()
                self._process.join(timeout=1)  # Pequeno timeout para garantir que o processo termine
                result['terminated'] = True
                result['success'] = False
                result['error'] = f'Operação cancelada por timeout após {execution_time:.2f} segundos'
            else:
                result['success'] = False
                result['error'] = f'Operação ainda em execução após {execution_time:.2f} segundos'
        else:
            # Processo terminou normalmente - verificamos o status
            status = self._result_dict.get('status', 'unknown')
            
            if status == 'success':
                result['success'] = True
                # Garantimos que o resultado está sendo copiado corretamente
                if 'result' in self._result_dict:
                    result['result'] = self._result_dict['result']
                else:
                    result['success'] = False
                    result['error'] = 'Resultado não encontrado no dicionário compartilhado'
            else:
                result['success'] = False
                result['error'] = self._result_dict.get('error', 'Erro desconhecido')
                if 'traceback' in self._result_dict:
                    result['traceback'] = self._result_dict['traceback']
        
        # Finaliza o Manager se o processo terminou e não estamos mais esperando resultado
        if not self._process.is_alive() and (result.get('success', False) or result.get('terminated', False)):
            self._cleanup()
        
        return result
    
    def terminate(self) -> None:
        """
        Terminates the running process.

        pt-br
        ------
        Termina o processo em execução.
        """
        if self._process and self._process.is_alive():
            self._process.terminate()
            self._process.join(timeout=1)
            self._cleanup()
    
    def _cleanup(self) -> None:
        """
        Cleans up resources used by the process.

        pt-br
        ------
        Limpa os recursos utilizados pelo processo.
        """
        if hasattr(self, '_manager') and self._manager is not None:
            try:
                self._manager.shutdown()
            except Exception:
                pass
            self._manager = None
        self._process = None

    def __del__(self):
        """
        Destructor of the class, ensures resources are released.

        pt-br
        ------
        Destrutor da classe, garante que recursos sejam liberados.
        """
        self.terminate()
