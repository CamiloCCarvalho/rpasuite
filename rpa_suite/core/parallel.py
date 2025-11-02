# rpa_suite/core/parallel.py

# imports standard
import time
import traceback
from multiprocessing import Manager, Process
from typing import Any, Callable, Dict, Generic, Optional, TypeVar

from rpa_suite.functions._printer import alert_print, error_print, success_print

# Define a generic type for the function return
T = TypeVar("T")


class ParallelRunnerError(Exception):
    """
    Custom exception for ParallelRunner errors.

    Example:
    ----------
    >>> raise ParallelRunnerError("Some error")
    Traceback (most recent call last):
        ...
    ParallelRunnerError: ParallelRunner Error: Some error

    Exceção personalizada para erros do ParallelRunner.

    Exemplo:
    ----------
    >>> raise ParallelRunnerError("Algum erro")
    Traceback (most recent call last):
        ...
    ParallelRunnerError: ParallelRunner Error: Algum erro
    """

    def __init__(self, message):
        clean_message = message.replace("ParallelRunnerError:", "").strip()
        super().__init__(f"ParallelRunnerError: {clean_message}")


class ParallelRunner(Generic[T]):
    """
    Class responsible for executing functions in parallel processes, allowing the main application flow to continue while the function runs in the background.

    This class allows you to start a function in a separate process, check if it is still running, retrieve its result (with timeout and error handling), and clean up resources. It is useful for running time-consuming or blocking operations without freezing the main program.

    Example:
    ----------
    >>> def slow_add(a, b):
    ...     import time; time.sleep(2)
    ...     return a + b
    >>> runner = ParallelRunner(verbose=True)
    >>> runner.run(slow_add, 2, 3)
    >>> result = runner.get_result(timeout=5)
    >>> print(result['result'])
    5

    Classe responsável por executar funções em processos paralelos, permitindo que o fluxo principal da aplicação continue enquanto a função é executada em segundo plano.

    Esta classe permite iniciar uma função em um processo separado, verificar se ainda está em execução, obter seu resultado (com timeout e tratamento de erros) e liberar recursos. É útil para executar operações demoradas ou bloqueantes sem travar o programa principal.

    Exemplo:
    ----------
    >>> def soma_lenta(a, b):
    ...     import time; time.sleep(2)
    ...     return a + b
    >>> runner = ParallelRunner(verbose=True)
    >>> runner.run(soma_lenta, 2, 3)
    >>> resultado = runner.get_result(timeout=5)
    >>> print(resultado['result'])
    5
    """

    verbose = None

    def __init__(self, verbose: bool = False) -> None:
        """
        Class responsible for executing functions in parallel processes, allowing the main application flow to continue while the function runs in the background.

        This class allows you to start a function in a separate process, check if it is still running, retrieve its result (with timeout and error handling), and clean up resources. It is useful for running time-consuming or blocking operations without freezing the main program.

        Args:
        ----------
            verbose (bool): If True, displays debug messages during execution.

        Example:
        ----------
        >>> def slow_add(a, b):
        ...     import time; time.sleep(2)
        ...     return a + b
        >>> runner = ParallelRunner(verbose=True)
        >>> runner.run(slow_add, 2, 3)
        >>> result = runner.get_result(timeout=5)
        >>> print(result['result'])
        5

        Classe responsável por executar funções em processos paralelos, permitindo que o fluxo principal da aplicação continue enquanto a função é executada em segundo plano.

        Esta classe permite iniciar uma função em um processo separado, verificar se ainda está em execução, obter seu resultado (com timeout e tratamento de erros) e liberar recursos. É útil para executar operações demoradas ou bloqueantes sem travar o programa principal.

        Parâmetros:
        ----------
            verbose (bool): Se True, exibe mensagens de depuração durante a execução.

        Exemplo:
        ----------
        >>> def soma_lenta(a, b):
        ...     import time; time.sleep(2)
        ...     return a + b
        >>> runner = ParallelRunner(verbose=True)
        >>> runner.run(soma_lenta, 2, 3)
        >>> resultado = runner.get_result(timeout=5)
        >>> print(resultado['result'])
        5
        """
        try:
            self._manager = Manager()
            self._result_dict = self._manager.dict()
            self._process = None
            self._start_time = None
            self.verbose = verbose

            if self.verbose:
                success_print("ParallelRunner initialized successfully")

        except Exception as e:
            raise ParallelRunnerError(f"Error initializing ParallelRunner: {str(e)}") from e

    @staticmethod
    def _execute_function(function, args, kwargs, result_dict):
        """
        Static method that executes the target function and stores the result.

        This function is used internally to run the user function in a separate process and store its result or error in a shared dictionary.

        Example:
        ----------
        (Internal use only)

        Método estático que executa a função alvo e armazena o resultado.

        Esta função é usada internamente para executar a função do usuário em um processo separado e armazenar seu resultado ou erro em um dicionário compartilhado.

        Exemplo:
        ----------
        (Uso interno apenas)
        """
        try:
            # Execute the user function with the provided arguments
            result = function(*args, **kwargs)

            # Store the result in the shared dictionary
            result_dict["status"] = "success"
            result_dict["result"] = result

        except Exception as e:
            # In case of error, store information about the error
            result_dict["status"] = "error"
            result_dict["error"] = str(e)
            result_dict["traceback"] = traceback.format_exc()

            # For debug
            error_print(f"[Child Process] Error occurred: {str(e)}")

    @staticmethod
    def _execute_function_w_disp_msg(function, args, kwargs, result_dict):
        """
        Static method that executes the target function and stores the result, displaying debug messages.

        This function is used internally to run the user function in a separate process, store its result or error in a shared dictionary, and print debug messages.

        Example:
        ----------
        (Internal use only)

        Método estático que executa a função alvo e armazena o resultado, exibindo mensagens de depuração.

        Esta função é usada internamente para executar a função do usuário em um processo separado, armazenar seu resultado ou erro em um dicionário compartilhado e imprimir mensagens de depuração.

        Exemplo:
        ----------
        (Uso interno apenas)
        """
        try:
            # Execute the user function with the provided arguments
            result = function(*args, **kwargs)

            # Store the result in the shared dictionary
            result_dict["status"] = "success"
            result_dict["result"] = result

            # For debug
            success_print(f"[Child Process] Result calculated: {result}")
            success_print(f"[Child Process] Result dictionary: {dict(result_dict)}")

        except Exception as e:
            # In case of error, store information about the error
            result_dict["status"] = "error"
            result_dict["error"] = str(e)
            result_dict["traceback"] = traceback.format_exc()

            # For debug
            error_print(f"[Child Process] Error occurred: {str(e)}")

    def run(self, function: Callable[..., T], *args, **kwargs) -> "ParallelRunner[T]":
        """
        Starts the execution of the given function in a parallel process.

        This method launches the specified function in a separate process, allowing the main program to continue running. The result can be retrieved later using `get_result()`.

        Parameters:
        ----------
            function: Function to be executed in parallel.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
        ----------
            self: Returns the instance itself to allow chained calls.

        Example:
        ----------
        >>> def slow_add(a, b):
        ...     import time; time.sleep(2)
        ...     return a + b
        >>> runner = ParallelRunner()
        >>> runner.run(slow_add, 2, 3)

        Inicia a execução da função fornecida em um processo paralelo.

        Este método executa a função especificada em um processo separado, permitindo que o programa principal continue rodando. O resultado pode ser obtido depois usando `get_result()`.

        Parâmetros:
        ----------
            function: Função a ser executada em paralelo.
            *args: Argumentos posicionais para a função.
            **kwargs: Argumentos nomeados para a função.

        Retorno:
        ----------
            self: Retorna a própria instância para permitir chamadas encadeadas.

        Exemplo:
        ----------
        >>> def soma_lenta(a, b):
        ...     import time; time.sleep(2)
        ...     return a + b
        >>> runner = ParallelRunner()
        >>> runner.run(soma_lenta, 2, 3)
        """
        try:
            # Clear previous result, if any
            if self._result_dict:
                self._result_dict.clear()

            # Configure initial values in the shared dictionary
            self._result_dict["status"] = "running"

            # Start the process with the static helper function
            if self.verbose:
                self._process = Process(
                    target=ParallelRunner._execute_function_w_disp_msg,
                    args=(function, args, kwargs, self._result_dict),
                )
            else:
                self._process = Process(
                    target=ParallelRunner._execute_function,
                    args=(function, args, kwargs, self._result_dict),
                )

            self._process.daemon = True  # Child process terminates when main terminates
            self._process.start()
            self._start_time = time.time()

            if self.verbose:
                success_print("Parallel process started successfully")

            return self

        except Exception as e:
            raise ParallelRunnerError(f"Error starting parallel process: {str(e)}") from e

    def is_running(self) -> bool:
        """
        Checks if the parallel process is still running.

        Returns:
        ----------
            bool: True if the process is still running, False otherwise.

        Example:
        ----------
        >>> runner.is_running()
        True

        Verifica se o processo paralelo ainda está em execução.

        Retorno:
        ----------
            bool: True se o processo ainda está rodando, False caso contrário.

        Exemplo:
        ----------
        >>> runner.is_running()
        True
        """
        try:
            if self._process is None:
                return False
            return self._process.is_alive()
        except Exception as e:
            if self.verbose:
                error_print(f"Error checking process status: {str(e)}")
            return False

    def get_result(  # pylint: disable=too-many-branches
        self, timeout: Optional[float] = 60, terminate_on_timeout: bool = True
    ) -> Dict[str, Any]:
        """
        Retrieves the result of the parallel execution, waiting up to the specified timeout.

        This method waits for the parallel process to finish, up to the given timeout. If the process does not finish in time and `terminate_on_timeout` is True, it will be terminated. The result includes success status, result or error, execution time, and whether the process was terminated.

        Parameters:
        ----------
            timeout: Maximum time (in seconds) to wait for the process to finish. None means wait indefinitely.
            terminate_on_timeout: If True, terminates the process if the timeout is reached.

        Returns:
        ----------
            dict: Contains:
                * 'success': bool - True if the operation was successful.
                * 'result': result of the function (if successful).
                * 'error': error message (if any).
                * 'traceback': full stack trace (if an error occurred).
                * 'execution_time': execution time in seconds.
                * 'terminated': True if the process was terminated due to timeout.

        Example:
        ----------
        >>> result = runner.get_result(timeout=5)
        >>> print(result['success'], result.get('result'))

        Obtém o resultado da execução paralela, aguardando até o tempo limite especificado.

        Este método espera o processo paralelo terminar, até o tempo limite informado. Se o processo não terminar a tempo e `terminate_on_timeout` for True, ele será encerrado. O resultado inclui status de sucesso, resultado ou erro, tempo de execução e se o processo foi terminado.

        Parâmetros:
        ----------
            timeout: Tempo máximo (em segundos) para aguardar o término do processo. None significa aguardar indefinidamente.
            terminate_on_timeout: Se True, encerra o processo se o tempo limite for atingido.

        Retorno:
        ----------
            dict: Contém:
                * 'success': bool - True se a operação foi bem-sucedida.
                * 'result': resultado da função (se bem-sucedida).
                * 'error': mensagem de erro (se houver).
                * 'traceback': stack trace completo (se ocorreu erro).
                * 'execution_time': tempo de execução em segundos.
                * 'terminated': True se o processo foi encerrado por timeout.

        Exemplo:
        ----------
        >>> resultado = runner.get_result(timeout=5)
        >>> print(resultado['success'], resultado.get('result'))
        """
        try:
            if self._process is None:
                return {
                    "success": False,
                    "error": "No process was started",
                    "execution_time": 0,
                    "terminated": False,
                }

            # Wait for the process to finish with timeout
            self._process.join(timeout=timeout)
            execution_time = time.time() - self._start_time

            # Prepare the response dictionary
            result = {"execution_time": execution_time, "terminated": False}

            # Debug - show the shared dictionary
            if self.verbose:
                success_print(f"[Main Process] Shared dictionary: {dict(self._result_dict)}")

            # Check if the process finished or reached timeout
            if self._process.is_alive():
                if terminate_on_timeout:
                    try:
                        self._process.terminate()
                        self._process.join(timeout=1)  # Small timeout to ensure process terminates
                        result["terminated"] = True
                        result["success"] = False
                        result["error"] = "Operation cancelled due to timeout after {execution_time:.2f} seconds"

                        if self.verbose:
                            alert_print("Process terminated due to timeout")

                    except Exception as e:
                        result["success"] = False
                        result["error"] = f"Error terminating process: {str(e)}"
                        if self.verbose:
                            error_print(f"Error terminating process: {str(e)}")
                else:
                    result["success"] = False
                    result["error"] = f"Operation still running after {execution_time:.2f} seconds"
            else:
                # Process finished normally - check the status
                try:
                    status = self._result_dict.get("status", "unknown")

                    if status == "success":
                        result["success"] = True
                        # Ensure the result is being copied correctly
                        if "result" in self._result_dict:
                            result["result"] = self._result_dict["result"]
                            if self.verbose:
                                success_print("Result retrieved successfully")
                        else:
                            result["success"] = False
                            result["error"] = "Result not found in shared dictionary"
                            if self.verbose:
                                error_print("Result not found in shared dictionary")
                    else:
                        result["success"] = False
                        result["error"] = self._result_dict.get("error", "Unknown error")
                        if "traceback" in self._result_dict:
                            result["traceback"] = self._result_dict["traceback"]
                        if self.verbose:
                            error_print(f"Process failed with error: {result['error']}")

                except Exception as e:
                    result["success"] = False
                    result["error"] = f"Error retrieving result from shared dictionary: {str(e)}"
                    if self.verbose:
                        error_print(f"Error retrieving result: {str(e)}")

            # Finalize the Manager if the process finished and we're no longer waiting for result
            if not self._process.is_alive() and (result.get("success", False) or result.get("terminated", False)):
                self._cleanup()

            return result

        except Exception as e:
            error_message = f"Error getting result from parallel process: {str(e)}"
            if self.verbose:
                error_print(error_message)
            return {
                "success": False,
                "error": error_message,
                "execution_time": 0,
                "terminated": False,
            }

    def terminate(self) -> None:
        """
        Terminates the running parallel process, if any.

        This method forcibly stops the process if it is still running and cleans up resources.

        Example:
        ----------
        >>> runner.terminate()

        Encerra o processo paralelo em execução, se houver.

        Este método interrompe o processo caso ainda esteja rodando e libera os recursos.

        Exemplo:
        ----------
        >>> runner.terminate()
        """
        try:
            if self._process and self._process.is_alive():
                self._process.terminate()
                self._process.join(timeout=1)
                self._cleanup()

                if self.verbose:
                    success_print("Process terminated successfully")

        except Exception as e:
            if self.verbose:
                error_print(f"Error terminating process: {str(e)}")

    def _cleanup(self) -> None:
        """
        Cleans up resources used by the process.

        This method is called internally to release resources after the process finishes or is terminated.

        Example:
        ----------
        (Internal use only)

        Limpa os recursos utilizados pelo processo.

        Este método é chamado internamente para liberar recursos após o término ou encerramento do processo.

        Exemplo:
        ----------
        (Uso interno apenas)
        """
        try:
            if hasattr(self, "_manager") and self._manager is not None:
                try:
                    self._manager.shutdown()
                except Exception as e:
                    if self.verbose:
                        error_print(f"Error shutting down manager: {str(e)}")
                self._manager = None
            self._process = None

            if self.verbose:
                success_print("Resources cleaned up successfully")

        except Exception as e:
            if self.verbose:
                error_print(f"Error during cleanup: {str(e)}")

    def __del__(self):
        """
        Destructor of the class, ensures resources are released.

        This method is called when the object is destroyed to guarantee that all resources are properly cleaned up.

        Example:
        ----------
        (Internal use only)

        Destrutor da classe, garante que os recursos sejam liberados.

        Este método é chamado quando o objeto é destruído para garantir que todos os recursos sejam liberados corretamente.

        Exemplo:
        ----------
        (Uso interno apenas)
        """
        try:
            self.terminate()
        except Exception:
            # Silently handle any errors during destruction
            pass
