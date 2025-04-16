# /_variables_uru.py

from loguru import logger
from typing import Optional
from typing import Any

# Variável global para o manipulador de arquivo
file_handler: Optional[str] = None

# Variável global para o manipulador de stream stdout/stdin/buffer
stream_handler: Optional[Any] = logger
