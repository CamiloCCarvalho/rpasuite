# rpa_suite/core/iris.py

"""
Iris (OCR-IA) módulo para conversão de documentos usando DocLing.

Este módulo fornece uma interface simplificada para converter documentos
em vários formatos, otimizado para uso em automação RPA.
"""

# imports externos
try:
    from docling.document_converter import DocumentConverter
except ImportError as e:
    raise ImportError("Iris - Error: Não foi possível importar 'docling.document_converter'. Certifique-se de que a biblioteca 'docling' está instalada.") from e

# imports de terceiros
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# imports internos
from rpa_suite.functions._printer import alert_print, error_print, success_print

class IrisError(Exception):
    """Exceção personalizada para erros do Iris."""
    def __init__(self, message):
        super().__init__(f'Iris - Error: {message}')

class ExportFormats(Enum):
    """Formatos de exportação suportados para conversão de documentos."""
    MARKDOWN = "markdown"
    DICT = "dict"
    DOCTAGS = "doctags"
    HTML = "html"
    TEXT = "text"

class Iris:
    """
    Iris (OCR-IA)
    Conversor de documentos usando a biblioteca DocLing.

    Esta classe fornece uma interface simplificada para converter documentos
    em vários formatos (PDF, imagens, texto) para formatos estruturados como
    Markdown, HTML, texto simples, entre outros.

    Atributos:
        engine: Instância do DocumentConverter do DocLing.
        last_result: Último resultado de conversão processado.

    Exemplo:
        >>> iris = Iris()
        >>> content = iris.read_document("document.pdf", ExportFormats.MARKDOWN)
        >>> print(content)
    """

    engine: Optional[DocumentConverter]

    def __init__(self) -> None:
        """
        Inicializa a classe Iris com o conversor de documentos.

        Levanta:
            IrisError: Se a biblioteca DocLing não estiver instalada.
        """
        try:
            self.iris_converter = DocumentConverter()
            self.engine = self.iris_converter
            self.path_file = None
            self.result_converted = None
            self.result_formatted = None
        except Exception as e:
            error_print("Iris - Error: Falha ao inicializar o DocumentConverter.")
            raise IrisError(f"Falha ao inicializar o DocumentConverter: {e}")

    def __convert_document(self, path_file: str = None):
        """
        Converte o documento informado pelo caminho.

        Levanta:
            IrisError: Se ocorrer erro na conversão do documento.
        """
        try:
            if not path_file:
                raise IrisError("Caminho do arquivo não informado para conversão.")
            self.result_converted = self.iris_converter.convert(path_file)
        except Exception as e:
            error_print(f"Iris - Error: Falha ao converter o documento: {e}")
            raise IrisError(f"Falha ao converter o documento: {e}")

    def read_document(self, file_path: str = None, result_format=ExportFormats.MARKDOWN, verbose: bool = False) -> Optional[Union[str, dict]]:
        """
        Lê e converte um documento para o formato especificado.

        Args:
            file_path: Caminho para o arquivo do documento.
            result_format: Formato de exportação desejado.
            verbose: Se True, exibe mensagens de sucesso.

        Retorna:
            Documento convertido para o formato especificado, ou None se falhar.

        Levanta:
            IrisError: Se ocorrer erro durante validação, conversão ou exportação.

        Exemplo:
            >>> iris = Iris()
            >>> content = iris.read_document("doc.pdf", ExportFormats.TEXT)
            >>> print(content)
        """
        try:
            self.__convert_document(file_path)

            if not self.result_converted or not hasattr(self.result_converted, 'document'):
                raise IrisError("Conversão falhou ou objeto retornado inválido.")

            if result_format == ExportFormats.MARKDOWN:
                self.result_formatted = self.result_converted.document.export_to_markdown()
            elif result_format == ExportFormats.DICT:
                self.result_formatted = self.result_converted.document.export_to_dict()
            elif result_format == ExportFormats.DOCTAGS:
                self.result_formatted = self.result_converted.document.export_to_doctags()
            elif result_format == ExportFormats.HTML:
                self.result_formatted = self.result_converted.document.export_to_html()
            elif result_format == ExportFormats.TEXT:
                self.result_formatted = self.result_converted.document.export_to_text()
            else:
                alert_print(f'Iris - Error: Formato não suportado: {result_format}.')
                raise IrisError(f"Formato não suportado: {result_format}.")

            if verbose:
                success_print('Irir - Convertido com sucesso!')

            return self.result_formatted

        except IrisError as ie:
            error_print(str(ie))
            return None
        except Exception as e:
            error_print(f"Iris - Error: Erro inesperado ao ler o documento: {e}")
            raise IrisError(f"Erro inesperado ao ler o documento: {e}")
