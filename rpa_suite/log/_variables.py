from logging import FileHandler, StreamHandler
from typing import Optional

# Variável global para o manipulador de arquivo
file_handler: Optional[FileHandler] = None

# Variável global para o manipulador de stream stdout/stdin/buffer
stream_handler: Optional[StreamHandler] = None
