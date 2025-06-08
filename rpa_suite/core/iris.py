# rpa_suite/core/iris.py
"""
Iris (OCR-IA) module for document conversion using DocLing.

This module provides a simplified interface for converting documents
into various formats, optimized for RPA automation use.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# imports internal
from rpa_suite.functions._printer import alert_print, error_print, success_print


class ExportFormat(Enum):
    """Supported export formats for document conversion."""
    
    MARKDOWN = "markdown"
    DICT = "dict"
    DOCTAGS = "doctags"
    HTML = "html"
    TEXT = "text"


class IrisError(Exception):
    """Custom exception for Iris class errors."""
    
    pass


class Iris:
    """
    Iris (OCR-IA)
    Document converter using the DocLing library.
    
    This class provides a simplified interface for converting documents
    in various formats (PDF, images, text) to structured formats such as
    Markdown, HTML, plain text, among others.
    
    Attributes:
        engine: Instance of DocLing's DocumentConverter.
        last_result: Last processed conversion result.
        
    Example:
        >>> iris = Iris()
        >>> content = iris.read_document("document.pdf", ExportFormat.MARKDOWN)
        >>> print(content)
    """
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        '.pdf', '.txt', '.docx', '.doc', '.png', '.jpg', '.jpeg', 
        '.tiff', '.bmp', '.webp', '.pptx', '.xlsx'
    }
    
    def __init__(self, display_message: bool = False) -> None:
        """
        Initializes the Iris class with the document converter.
        
        Raises:
            IrisError: If the DocLing library is not installed.
        """
        self._engine: Optional[Any] = None
        self._last_result: Optional[Any] = None
        self.display_message: bool = display_message
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """
        Initializes the DocumentConverter engine.
        
        Raises:
            IrisError: If the DocLing library is not available.
        """
        try:
            from docling.document_converter import DocumentConverter
            self._engine = DocumentConverter()
            if self.display_message: success_print("Iris engine initialized successfully")
        except ImportError as e:
            error_msg = (
                "The 'docling' library is not installed. "
                "Run: python -m pip install docling"
            )
            error_print(f"Iris - {error_msg}")
            error_print(f"Error importing DocLing: {e}")
            raise IrisError(error_msg) from e
    
    @property
    def engine(self) -> Any:
        """Returns the DocumentConverter engine instance."""
        return self._engine
    
    @property
    def last_result(self) -> Optional[Any]:
        """Returns the last processed conversion result."""
        return self._last_result
    
    def _validate_file_path(self, file_path: Union[str, Path]) -> Path:
        """
        Validates the file path and returns a Path object.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Path: Validated Path object.
            
        Raises:
            IrisError: If the file does not exist or is not supported.
        """
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            raise IrisError(f"File not found: {file_path}")
        
        if not path_obj.is_file():
            raise IrisError(f"Path does not point to a file: {file_path}")
        
        if path_obj.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            supported = ", ".join(sorted(self.SUPPORTED_EXTENSIONS))
            raise IrisError(
                f"Extension '{path_obj.suffix}' is not supported. "
                f"Supported extensions: {supported}"
            )
        
        return path_obj
    
    def _convert_document(self, file_path: Path) -> Any:
        """
        Converts the document using DocumentConverter.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Result of the DocLing conversion.
            
        Raises:
            IrisError: If the conversion fails.
        """
        try:
            if self.display_message: success_print(f"Starting conversion of file: {file_path}")
            result = self._engine.convert(str(file_path))
            self._last_result = result
            if self.display_message: success_print("Conversion completed successfully")
            return result
        except Exception as e:
            error_msg = f"Error converting document '{file_path}': {e}"
            error_print(f"Iris - {error_msg}")
            error_print(error_msg)
            raise IrisError(error_msg) from e
    
    def _export_to_format(self, document: Any, export_format: ExportFormat) -> Any:
        """
        Exports the document to the specified format.
        
        Args:
            document: Document converted by DocLing.
            export_format: Desired export format.
            
        Returns:
            Document in the specified format.
            
        Raises:
            IrisError: If the export fails.
        """
        export_methods = {
            ExportFormat.MARKDOWN: document.export_to_markdown,
            ExportFormat.DICT: document.export_to_dict,
            ExportFormat.DOCTAGS: document.export_to_doctags,
            ExportFormat.HTML: document.export_to_html,
            ExportFormat.TEXT: document.export_to_text,
        }
        
        try:
            export_method = export_methods[export_format]
            return export_method()
        except KeyError:
            available_formats = ", ".join([fmt.value for fmt in ExportFormat])
            raise IrisError(
                f"Format '{export_format.value}' is not supported. "
                f"Available formats: {available_formats}"
            )
        except Exception as e:
            error_msg = f"Error exporting to format '{export_format.value}': {e}"
            error_print(error_msg)
            raise IrisError(error_msg) from e
    
    def read_document(
        self,
        file_path: Union[str, Path],
        export_format: ExportFormat = ExportFormat.MARKDOWN,
        verbose: bool = False,
    ) -> Optional[Any]:
        """
        Reads and converts a document to the specified format.
        
        Args:
            file_path: Path to the document file.
            export_format: Desired export format.
            verbose: If True, displays success messages.
            
        Returns:
            Document converted to the specified format, or None if it fails.
            
        Raises:
            IrisError: If an error occurs during validation, conversion, or export.
            
        Example:
            >>> iris = Iris()
            >>> content = iris.read_document("doc.pdf", ExportFormat.TEXT)
            >>> print(content)
        """
        try:
            # File validation
            validated_path = self._validate_file_path(file_path)
            
            # Document conversion
            conversion_result = self._convert_document(validated_path)
            
            # Conversion result check
            if not conversion_result or not hasattr(conversion_result, 'document'):
                raise IrisError("Invalid conversion result or document not found")
            
            # Export to desired format
            formatted_result = self._export_to_format(
                conversion_result.document, 
                export_format
            )
            
            if verbose:
                success_print("Iris - Conversion completed successfully")
            
            success_print(
                f"Document '{validated_path.name}' converted to '{export_format.value}'"
            )
            
            return formatted_result
            
        except IrisError:
            # Re-raise exceptions from the class itself
            raise
        except Exception as e:
            error_msg = f"Unexpected error while processing document: {e}"
            error_print(f"Iris - {error_msg}")
            error_print(error_msg)
            raise IrisError(error_msg) from e
    
    def read_multiple_documents(
        self,
        file_paths: List[Union[str, Path]],
        export_format: ExportFormat = ExportFormat.MARKDOWN,
        verbose: bool = False,
    ) -> Dict[str, Optional[Any]]:
        """
        Reads and converts multiple documents.
        
        Args:
            file_paths: List of file paths.
            export_format: Desired export format.
            verbose: If True, displays detailed messages.
            
        Returns:
            Dictionary with the file name as key and converted content as value.
            
        Example:
            >>> iris = Iris()
            >>> files = ["doc1.pdf", "doc2.txt"]
            >>> results = iris.read_multiple_documents(files, ExportFormat.TEXT)
            >>> for filename, content in results.items():
            ...     print(f"{filename}: {len(content) if content else 0} characters")
        """
        results = {}
        successful_conversions = 0
        
        for file_path in file_paths:
            try:
                content = self.read_document(file_path, export_format, verbose=False)
                filename = Path(file_path).name
                results[filename] = content
                successful_conversions += 1
                
                if verbose:
                    if self.display_message: success_print(f"Iris - '{filename}' converted successfully")
                    
            except IrisError as e:
                filename = Path(file_path).name
                results[filename] = None
                if verbose:
                    error_print(f"Iris - Error converting '{filename}': {e}")
                alert_print(f"Failed to convert '{filename}': {e}")
        
        if verbose:
            total_files = len(file_paths)
            if self.display_message: success_print(
                f"Iris - Processing completed: {successful_conversions}/{total_files} "
                f"files converted successfully"
            )
        
        return results
    
    def get_supported_extensions(self) -> List[str]:
        """
        Returns the list of supported file extensions.
        
        Returns:
            Sorted list of supported extensions.
        """
        return sorted(list(self.SUPPORTED_EXTENSIONS))
    
    def is_file_supported(self, file_path: Union[str, Path]) -> bool:
        """
        Checks if a file is supported by the class.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            True if the file is supported, False otherwise.
        """
        try:
            path_obj = Path(file_path)
            return path_obj.suffix.lower() in self.SUPPORTED_EXTENSIONS
        except Exception:
            return False
