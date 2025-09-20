# rpa_suite/core/clock.py

# imports standard
import time
from typing import Callable, Any
from datetime import datetime as dt

# imports internal
from rpa_suite.functions._printer import success_print

class ClockError(Exception):
    """Custom exception for Clock errors."""
    def __init__(self, message):
        super().__init__(f'ClockError: {message}')

class Clock:
    """
    Class that provides utilities for time manipulation and stopwatch.

    This class offers functionalities for:
        - Timed function execution
        - Execution time control
        - Task scheduling

    Methods:
        exec_at_hour: Executes a function at a specific time

    The Clock class is part of RPA Suite and can be accessed through the rpa object:
        >>> from rpa_suite import rpa
        >>> rpa.clock.exec_at_hour("14:30", my_function)

    pt-br
    ----------
    Classe que fornece utilitários para manipulação de tempo e cronômetro.

    Esta classe oferece funcionalidades para:
        - Execução temporizada de funções
        - Controle de tempo de execução
        - Agendamento de tarefas

    Métodos:
        exec_at_hour: Executa uma função em um horário específico

    A classe Clock é parte do RPA Suite e pode ser acessada através do objeto rpa:
        >>> from rpa_suite import rpa
        >>> rpa.clock.exec_at_hour("14:30", minha_funcao)
    """

    def __init__(self) -> None:
        """
        Class that provides utilities for time manipulation and stopwatch.

        This class offers functionalities for:
            - Timed function execution
            - Execution time control
            - Task scheduling

        Methods:
            exec_at_hour: Executes a function at a specific time

        The Clock class is part of RPA Suite and can be accessed through the rpa object:
            >>> from rpa_suite import rpa
            >>> rpa.clock.exec_at_hour("14:30", my_function)

        pt-br
        ----------
        Classe que fornece utilitários para manipulação de tempo e cronômetro.

        Esta classe oferece funcionalidades para:
            - Execução temporizada de funções
            - Controle de tempo de execução
            - Agendamento de tarefas

        Métodos:
            exec_at_hour: Executa uma função em um horário específico

        A classe Clock é parte do RPA Suite e pode ser acessada através do objeto rpa:
            >>> from rpa_suite import rpa
            >>> rpa.clock.exec_at_hour("14:30", minha_funcao)
        """
        pass

    def exec_at_hour(
        self,
        hour_to_exec: str | None,
        fn_to_exec: Callable[..., Any],
        *args,
        **kwargs,
    ) -> dict[str, bool]:
        """
        Timed function, executes the function at the specified time, by ``default`` it executes at runtime, optionally you can choose the time for execution.

        Parameters:
        ----------
            `hour_to_exec: 'xx:xx'` - time for function execution, if not passed the value will be by ``default`` at runtime at the time of this function call by the main code.

            ``fn_to_exec: function`` - (function) to be called by the handler, if there are parameters in this function they can be passed as next arguments in ``*args`` and ``**kwargs``

        Return:
        ----------
        >>> type:dict
            * 'tried': bool - represents if it tried to execute the function passed in the argument
            * 'success': bool - represents if there was success in trying to execute the requested function

        Example:
        ---------
        Let's execute the function ``sum`` responsible for adding the values of a and b and return x``sum(a, b) -> x`` and we want the code to wait for the specific time to be executed at ``11:00``
        >>> exec_at_hour("11:00", sum, 10, 5) -> 15 \n
            * NOTE:  `exec_at_hour` receives as first parameter the function that should be executed, then it can receive the arguments of the function, and explicitly we can define the time for execution.

        Description: pt-br
        ----------
        Função temporizada, executa a função no horário especificado, por ``default`` executa no momento da chamada em tempo de execução, opcionalmente pode escolher o horário para execução.

        Parâmetros:
        ----------
            `hour_to_exec: 'xx:xx'` - horário para execução da função, se não for passado o valor será por ``default`` em tempo de execução no momento da chamada desta função pelo cógido principal.

            ``fn_to_exec: function`` - (função) a ser chamada pelo handler, se houver parâmetros nessa função podem ser passados como próximos argumentos em ``*args`` e ``**kwargs``

        Retorno:
        ----------
        >>> type:dict
            * 'tried': bool - representa se tentou executar a função passada no argumento
            * 'success': bool - representa se houve sucesso ao tentar executar a função solicitada

        Exemplo:
        ---------
        Vamos executar a função ``soma`` responsável por somar os valores de a e b e retornar x``soma(a, b) -> x`` e queremos que o código aguarde o horário especifico para ser executado de ``11:00``
        >>> exec_at_hour("11:00", sum, 10, 5) -> 15 \n
            * OBS.:  `exec_at_hour` recebe como primeiro parâmetro a função que deve ser executada, em seguida pode receber os argumentos da função, e de forma explicitada podemos definir o horário para execução.
        """

        # Local Variables
        result: dict = {"tried": bool, "successs": bool}
        run: bool
        now: dt
        hours: str
        minutes: str
        moment_now: str

        try:
            # Preprocessing
            run = True
            now = dt.now()
            hours = str(now.hour) if now.hour >= 10 else f"0{now.hour}"
            minutes = str(now.minute) if now.minute >= 10 else f"0{now.minute}"
            moment_now = f"{hours}:{minutes}"

            if hour_to_exec is None:

                # Process
                while run:
                    try:
                        fn_to_exec(*args, **kwargs)
                        run = False
                        result["tried"] = not run
                        result["success"] = True
                        success_print(f"{fn_to_exec.__name__}: Successfully executed!")
                        break

                    except Exception as e:
                        run = False
                        result["tried"] = not run
                        result["success"] = False
                        break
            else:
                # Executes the function call only at the time provided in the argument.
                while run:
                    if moment_now == hour_to_exec:
                        try:
                            fn_to_exec(*args, **kwargs)
                            run = False
                            result["tried"] = not run
                            result["success"] = True
                            success_print(f"{fn_to_exec.__name__}: Successfully executed!")
                            break

                        except Exception as e:
                            run = False
                            result["tried"] = not run
                            result["success"] = False
                            ClockError(
                                f"An error occurred that prevented the function from executing: {fn_to_exec.__name__} correctly. Error: {str(e)}"
                            )
                    else:
                        time.sleep(30)
                        now = dt.now()
                        hours = str(now.hour) if now.hour >= 10 else f"0{now.hour}"
                        minutes = str(now.minute) if now.minute >= 10 else f"0{now.minute}"
                        moment_now = f"{hours}:{minutes}"

            return result

        except Exception as e:
            result["success"] = False
            raise ClockError(str(e)) from e

    def wait_for_exec(self, wait_time: int, fn_to_exec: Callable[..., Any], *args, **kwargs) -> dict[str, bool]:
        """
        Timer function, wait for a value in ``seconds`` to execute the function of the argument.

        Parameters:
        ----------
            `wait_time: int` - (seconds) represents the time that should wait before executing the function passed as an argument.

            ``fn_to_exec: function`` - (function) to be called after the waiting time, if there are parameters in this function they can be passed as next arguments of this function in ``*args`` and ``**kwargs``

        Return:
        ----------
        >>> type:dict
            * 'success': bool - represents if the action was performed successfully

        Example:
        ---------
        We have a sum function in the following format ``sum(a, b) -> return x``, where ``x`` is the result of the sum. We want to wait `30 seconds` to execute this function, so:
        >>> wait_for_exec(30, sum, 10, 5) -> 15 \n
            * NOTE:  `wait_for_exec` receives as first argument the time to wait (sec), then the function `sum` and finally the arguments that the function will use.


        pt-br
        ----------
        Função temporizadora, aguardar um valor em ``segundos`` para executar a função do argumento.

        Parametros:
        ----------
            `wait_time: int` - (segundos) representa o tempo que deve aguardar antes de executar a função passada como argumento.

            ``fn_to_exec: function`` - (função) a ser chamada depois do tempo aguardado, se houver parametros nessa função podem ser passados como próximos argumentos desta função em ``*args`` e ``**kwargs``

        Retorno:
        ----------
        >>> type:dict
            * 'success': bool - representa se ação foi realizada com sucesso

        Exemplo:
        ---------
        Temos uma função de soma no seguinte formato ``soma(a, b) -> return x``, onde ``x`` é o resultado da soma. Queremos aguardar `30 segundos` para executar essa função, logo:
        >>> wait_for_exec(30, soma, 10, 5) -> 15 \n
            * OBS.:  `wait_for_exec` recebe como primeiro argumento o tempo a aguardar (seg), depois a função `soma` e por fim os argumentos que a função ira usar.
        """

        # Local Variables
        result: dict = {"success": bool}

        # Process
        try:
            time.sleep(wait_time)
            fn_to_exec(*args, **kwargs)
            result["success"] = True
            success_print(f"Function: {self.wait_for_exec.__name__} executed the function: {fn_to_exec.__name__}.")

        except Exception as e:
            result["success"] = False
            ClockError(
                f"Error while trying to wait to execute the function: {fn_to_exec.__name__} \nMessage: {str(e)}"
            )

        return result

    def exec_and_wait(self, wait_time: int, fn_to_exec: Callable[..., Any], *args, **kwargs) -> dict[str, bool]:
        """
        Timer function, executes a function and waits for the time in ``seconds``

        Parameters:
        ----------
            `wait_time: int` - (seconds) represents the time that should wait after executing the requested function

            ``fn_to_exec: function`` - (function) to be called before the time to wait, if there are parameters in this function they can be passed as an argument after the function, being: ``*args`` and ``**kwargs``

        Return:
        ----------
        >>> type:dict
            * 'success': bool - represents if the action was performed successfully

        Example:
        ---------
        We have a sum function in the following format ``sum(a, b) -> return x``, where ``x`` is the result of the sum. We want to execute the sum and then wait `30 seconds` to continue the main code:
        >>> wait_for_exec(30, sum, 10, 5) -> 15 \n
            * NOTE:  `wait_for_exec` receives as first argument the time to wait (sec), then the function `sum` and finally the arguments that the function will use.


        pt-br
        ----------
        Função temporizadora, executa uma função e aguarda o tempo em ``segundos``

        Parametros:
        ----------
            `wait_time: int` - (segundos) representa o tempo que deve aguardar após executar a função solicitada

            ``fn_to_exec: function`` - (função) a ser chamada antes do tempo para aguardar, se houver parametros nessa função podem ser passados como argumento depois da função, sendo: ``*args`` e ``**kwargs``

        Retorno:
        ----------
        >>> type:dict
            * 'success': bool - representa se ação foi realizada com sucesso

        Exemplo:
        ---------
        Temos uma função de soma no seguinte formato ``soma(a, b) -> return x``, onde ``x`` é o resultado da soma. Queremos executar a soma e então aguardar `30 segundos` para continuar o código principal:
        >>> wait_for_exec(30, soma, 10, 5) -> 15 \n
            * OBS.:  `wait_for_exec` recebe como primeiro argumento o tempo a aguardar (seg), depois a função `soma` e por fim os argumentos que a função ira usar.
        """

        # Local Variables
        result: dict = {"success": bool}

        # Process
        try:
            fn_to_exec(*args, **kwargs)
            time.sleep(wait_time)
            result["success"] = True
            success_print(f"Function: {self.wait_for_exec.__name__} executed the function: {fn_to_exec.__name__}.")

        except Exception as e:
            result["success"] = False
            raise ClockError(
                f"Error while trying to wait to execute the function: {fn_to_exec.__name__} \nMessage: {str(e)}"
            ) from e

        return result
