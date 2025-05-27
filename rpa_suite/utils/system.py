# rpa_suite/utils/system.py

# imports internal
from rpa_suite.functions._printer import error_print, success_print

# imports third-party
import sys, os, ctypes, traceback


class Utils:
    """
    Classe utilitária para gerenciamento de configurações de sistema e diretórios.

    Fornece métodos para manipulação de caminhos de importação e configurações do sistema.
    """
    
    def __init__(self): 
        """
        Inicializa a classe Utils.

        Não requer parâmetros de inicialização específicos.
        """
        try:
            pass
        except Exception as e:
            error_print(f"Erro durante a inicialização da classe Utils: {str(e)}")


    def set_importable_dir(self, display_message: bool = False) -> None:
        """
        Configura o diretório atual como importável, adicionando-o ao caminho do sistema.

        Adiciona o diretório pai do módulo atual ao sys.path, permitindo importações 
        dinâmicas de módulos locais.

        Parâmetros:
        ----------
        display_message : bool, opcional
            Se True, exibe uma mensagem de sucesso após definir o diretório. 
            Por padrão é False.

        Retorna:
        --------
        None

        Exceções:
        ---------
        Captura e registra quaisquer erros durante o processo de configuração.
        """

        try:
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            if display_message:
                success_print("Diretório configurado com sucesso para importação!")

        except Exception as e:
            error_print(
                f"Erro ao configurar diretório importável: {str(e)}"
            )


class KeepSessionActive:
    """
    Gerenciador de contexto avançado para prevenir bloqueio de tela no Windows.

    Utiliza chamadas de API do Windows para manter o sistema ativo durante 
    execução de tarefas críticas, impedindo suspensão ou bloqueio de tela.

    Atributos de Classe:
    -------------------
    ES_CONTINUOUS : int
        Flag para manter o estado de execução atual do sistema.
    ES_SYSTEM_REQUIRED : int
        Flag para prevenir a suspensão do sistema.
    ES_DISPLAY_REQUIRED : int
        Flag para manter o display ativo.

    Exemplo de Uso:
    --------------
    with KeepSessionActive():
        # Código que requer que o sistema permaneça ativo
        realizar_tarefa_longa()
    """

    def __init__(self) -> None:
        """
        Inicializa as configurações de estado de execução do sistema.

        Configura constantes específicas do Windows para controle de energia 
        e gerenciamento de estado do sistema operacional.
        """
        try:
            self.ES_CONTINUOUS = 0x80000000
            self.ES_SYSTEM_REQUIRED = 0x00000001
            self.ES_DISPLAY_REQUIRED = 0x00000002
        except Exception as e:
            error_print(f"Erro ao inicializar KeepSessionActive: {str(e)}")
    

    def __enter__(self) -> None:
        """
        Configura o estado de execução para prevenir bloqueio de tela.

        Utiliza chamada de API do Windows para manter sistema e display ativos 
        durante a execução do bloco de código.

        Retorna:
        --------
        KeepSessionActive
            A própria instância do gerenciador de contexto.

        Exceções:
        ---------
        Captura e registra quaisquer erros durante a configuração de estado.
        """
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(
                self.ES_CONTINUOUS | self.ES_SYSTEM_REQUIRED | self.ES_DISPLAY_REQUIRED
            )
            return self
        except Exception as e:
            error_print(f"Erro ao configurar estado de execução: {str(e)}")
            return self
    

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Restaura as configurações padrão de energia do sistema.

        Método chamado automaticamente ao sair do bloco de contexto, 
        revertendo as configurações de estado de execução para o padrão.

        Parâmetros:
        ----------
        exc_type : type, opcional
            Tipo de exceção que pode ter ocorrido.
        exc_val : Exception, opcional
            Valor da exceção que pode ter ocorrido.
        exc_tb : traceback, opcional
            Traceback da exceção que pode ter ocorrido.

        Exceções:
        ---------
        Captura e registra quaisquer erros durante a restauração do estado.
        """
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(self.ES_CONTINUOUS)
        except Exception as e:
            error_print(f"Erro ao restaurar estado de execução: {str(e)}")
