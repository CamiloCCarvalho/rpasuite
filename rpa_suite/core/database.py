# rpa_suite/core/database.py

# imports standard
import atexit
import inspect
import json
import os
import signal
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# imports third party
try:
    import mysql.connector  # type: ignore
    from mysql.connector import pooling  # type: ignore

    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import psycopg2  # type: ignore
    from psycopg2 import pool  # type: ignore

    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

# imports internal
from rpa_suite.functions._printer import alert_print, success_print

# Import condicional para evitar dependência circular
try:
    from .log import Log

    LOG_AVAILABLE = True
except ImportError:
    LOG_AVAILABLE = False
    Log = None  # type: ignore


# ========== ENUMS E CONSTANTES ==========


class DatabaseType(Enum):
    """Tipos de banco de dados suportados."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


# Constantes de confirmação para limpeza protegida
CONFIRMATION_CODES = {
    "DELETE_SUCCESS": "DELETE_SUCCESS",
    "DELETE_FAILED": "DELETE_FAILED",
    "DELETE_SUCCESS_EXECUTIONS": "DELETE_SUCCESS_EXECUTIONS",
    "DELETE_FAILED_EXECUTIONS": "DELETE_FAILED_EXECUTIONS",
    "CLEAR_TABLE": "CLEAR_TABLE",
    "CLEAR_DATABASE": "CLEAR_DATABASE",
}

# Nomes padrão baseados em Athena
DEFAULT_DB_NAME = "athena_executions.db"
DEFAULT_EXECUTIONS_TABLE = "athena_executions"
DEFAULT_ITEMS_TABLE = "athena_items"
DEFAULT_LOGS_TABLE = "athena_logs"

# Constantes de nível de log para evitar texto livre
LOG_LEVEL_DEBUG = "debug"
LOG_LEVEL_INFO = "info"
LOG_LEVEL_WARNING = "warning"
LOG_LEVEL_ERROR = "error"
LOG_LEVEL_CRITICAL = "critical"
LOG_LEVEL_SUCCESS = "success"
VALID_LOG_LEVELS = (
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_CRITICAL,
    LOG_LEVEL_SUCCESS,
)
VALID_LOG_LEVELS_SQL = "', '".join(VALID_LOG_LEVELS)

# Palavras-chave para classificar falhas transitórias (reprocessáveis)
TRANSIENT_ERROR_KEYWORDS = (
    "timeout",
    "timed out",
    "temporar",
    "temporarily",
    "connection reset",
    "connection aborted",
    "connection refused",
    "network",
    "rate limit",
    "too many requests",
    "429",
    "500",
    "502",
    "503",
    "504",
    "lock",
    "deadlock",
)


# ========== EXCEÇÕES CUSTOMIZADAS ==========


class DatabaseError(Exception):
    """Custom exception for Database errors."""

    def __init__(self, message: str):
        if not message:
            message = "Generic error raised!"
        clean_message = message.replace("DatabaseError:", "").strip()
        super().__init__(f"DatabaseError: {clean_message}")


# ========== ABSTRAÇÃO DE BANCO (ADAPTERS) ==========


class DatabaseAdapter(ABC):
    """Classe abstrata para adaptadores de banco de dados."""

    @abstractmethod
    def connect(self) -> Any:
        """Cria conexão com o banco."""

    @abstractmethod
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> Any:
        """Executa query e retorna cursor."""

    @abstractmethod
    def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Executa query múltiplas vezes."""

    @abstractmethod
    def commit(self) -> None:
        """Confirma transação."""

    @abstractmethod
    def rollback(self) -> None:
        """Reverte transação."""

    @abstractmethod
    def close(self) -> None:
        """Fecha conexão."""

    @abstractmethod
    def get_last_insert_id(self, cursor: Any, table_name: str) -> int:
        """Retorna o último ID inserido."""

    @abstractmethod
    def get_table_exists_query(self, table_name: str) -> str:
        """Query para verificar se tabela existe."""

    @abstractmethod
    def escape_table_name(self, table_name: str) -> str:
        """Escapa nome de tabela para uso em queries."""


class SQLiteAdapter(DatabaseAdapter):
    """Adaptador para SQLite."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    def connect(self) -> sqlite3.Connection:
        """Cria conexão SQLite."""
        try:
            self.connection = sqlite3.connect(  # type: ignore
                self.db_path, check_same_thread=False, isolation_level=None
            )
            self.connection.row_factory = sqlite3.Row  # type: ignore
            return self.connection  # type: ignore
        except Exception as e:
            raise DatabaseError(f"Erro ao conectar ao SQLite: {str(e)}.") from e

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> sqlite3.Cursor:
        """Executa query SQLite."""
        try:
            cursor = self.connection.cursor()  # type: ignore
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except Exception as e:
            raise DatabaseError(f"Erro ao executar query SQLite: {str(e)}.") from e

    def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Executa query múltiplas vezes."""
        try:
            cursor = self.connection.cursor()  # type: ignore
            cursor.executemany(query, params_list)
        except Exception as e:
            raise DatabaseError(f"Erro ao executar executemany SQLite: {str(e)}.") from e

    def commit(self) -> None:
        """SQLite auto-commit está habilitado."""

    def rollback(self) -> None:
        """SQLite auto-commit está habilitado."""

    def close(self) -> None:
        """Fecha conexão SQLite."""
        if self.connection:
            self.connection.close()

    def get_last_insert_id(self, cursor: sqlite3.Cursor, table_name: str) -> int:
        """SQLite usa lastrowid."""
        return cursor.lastrowid  # type: ignore

    def get_table_exists_query(self, table_name: str) -> str:
        """Query para verificar se tabela existe no SQLite."""
        return f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"

    def escape_table_name(self, table_name: str) -> str:
        """SQLite não precisa escapar com backticks."""
        return table_name


class PostgreSQLAdapter(DatabaseAdapter):
    """Adaptador para PostgreSQL."""

    def __init__(
        self, host: str, port: int, database: str, user: str, password: str, use_pool: bool = True, pool_size: int = 5
    ):
        if not POSTGRESQL_AVAILABLE:
            raise DatabaseError("PostgreSQL não está disponível. Instale: pip install psycopg2-binary")

        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.use_pool = use_pool
        self.pool_size = pool_size
        self.pool = None
        self.connection = None

    def connect(self) -> Any:
        """Cria conexão PostgreSQL."""
        try:
            if self.use_pool and self.pool is None:
                self.pool = pool.SimpleConnectionPool(
                    1,
                    self.pool_size,
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                )

            if self.use_pool:
                self.connection = self.pool.getconn()  # type: ignore
            else:
                self.connection = psycopg2.connect(
                    host=self.host, port=self.port, database=self.database, user=self.user, password=self.password
                )

            return self.connection
        except Exception as e:
            raise DatabaseError(f"Erro ao conectar ao PostgreSQL: {str(e)}.") from e

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> Any:
        """Executa query PostgreSQL."""
        try:
            cursor = self.connection.cursor()  # type: ignore
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except Exception as e:
            raise DatabaseError(f"Erro ao executar query PostgreSQL: {str(e)}.") from e

    def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Executa query múltiplas vezes."""
        try:
            cursor = self.connection.cursor()  # type: ignore
            cursor.executemany(query, params_list)
        except Exception as e:
            raise DatabaseError(f"Erro ao executar executemany PostgreSQL: {str(e)}.") from e

    def commit(self) -> None:
        """Confirma transação PostgreSQL."""
        if self.connection:
            self.connection.commit()

    def rollback(self) -> None:
        """Reverte transação PostgreSQL."""
        if self.connection:
            self.connection.rollback()

    def close(self) -> None:
        """Fecha conexão PostgreSQL."""
        if self.connection:
            if self.use_pool and self.pool:
                self.pool.putconn(self.connection)
            else:
                self.connection.close()

    def get_last_insert_id(self, cursor: Any, table_name: str) -> int:
        """PostgreSQL usa RETURNING ou cursor.fetchone()[0]."""
        # Se a query não tem RETURNING, usar uma query separada
        try:
            cursor.execute(f"SELECT CURRVAL(pg_get_serial_sequence('{table_name}', 'id'))")
            result = cursor.fetchone()
            return result[0] if result else None  # type: ignore
        except Exception:
            # Fallback: tentar lastrowid se disponível
            return getattr(cursor, "lastrowid", None)  # type: ignore

    def get_table_exists_query(self, table_name: str) -> str:
        """Query para verificar se tabela existe no PostgreSQL."""
        return f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{table_name}'
            )
        """

    def escape_table_name(self, table_name: str) -> str:
        """PostgreSQL usa aspas duplas."""
        return f'"{table_name}"'


class MySQLAdapter(DatabaseAdapter):
    """Adaptador para MySQL."""

    def __init__(
        self, host: str, port: int, database: str, user: str, password: str, use_pool: bool = True, pool_size: int = 5
    ):
        if not MYSQL_AVAILABLE:
            raise DatabaseError("MySQL não está disponível. Instale: pip install mysql-connector-python")

        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.use_pool = use_pool
        self.pool_size = pool_size
        self.pool = None
        self.connection = None

    def connect(self) -> Any:
        """Cria conexão MySQL."""
        try:
            if self.use_pool and self.pool is None:
                self.pool = pooling.MySQLConnectionPool(
                    pool_name="rpa_pool",
                    pool_size=self.pool_size,
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                )

            if self.use_pool:
                self.connection = self.pool.get_connection()  # type: ignore
            else:
                self.connection = mysql.connector.connect(
                    host=self.host, port=self.port, database=self.database, user=self.user, password=self.password
                )

            return self.connection
        except Exception as e:
            raise DatabaseError(f"Erro ao conectar ao MySQL: {str(e)}.") from e

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> Any:
        """Executa query MySQL."""
        try:
            cursor = self.connection.cursor(dictionary=True)  # type: ignore
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except Exception as e:
            raise DatabaseError(f"Erro ao executar query MySQL: {str(e)}.") from e

    def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Executa query múltiplas vezes."""
        try:
            cursor = self.connection.cursor()  # type: ignore
            cursor.executemany(query, params_list)
        except Exception as e:
            raise DatabaseError(f"Erro ao executar executemany MySQL: {str(e)}.") from e

    def commit(self) -> None:
        """Confirma transação MySQL."""
        if self.connection:
            self.connection.commit()

    def rollback(self) -> None:
        """Reverte transação MySQL."""
        if self.connection:
            self.connection.rollback()

    def close(self) -> None:
        """Fecha conexão MySQL."""
        if self.connection:
            self.connection.close()

    def get_last_insert_id(self, cursor: Any, table_name: str) -> int:
        """MySQL usa lastrowid."""
        return cursor.lastrowid

    def get_table_exists_query(self, table_name: str) -> str:
        """Query para verificar se tabela existe no MySQL."""
        return f"""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = '{table_name}'
            )
        """

    def escape_table_name(self, table_name: str) -> str:
        """MySQL usa backticks."""
        return f"`{table_name}`"


# ========== GERADOR DE SQL ==========


class SQLGenerator:
    """Gera SQL compatível com diferentes bancos de dados."""

    def __init__(self, db_type: DatabaseType, executions_table: str, items_table: str, logs_table: str):
        self.db_type = db_type
        self.executions_table = executions_table
        self.items_table = items_table
        self.logs_table = logs_table

    def _get_pk_type(self) -> str:
        """Retorna tipo de PRIMARY KEY baseado no banco."""
        if self.db_type == DatabaseType.SQLITE:
            return "INTEGER PRIMARY KEY AUTOINCREMENT"
        elif self.db_type == DatabaseType.POSTGRESQL:
            return "SERIAL PRIMARY KEY"
        elif self.db_type == DatabaseType.MYSQL:
            return "INT AUTO_INCREMENT PRIMARY KEY"
        return "INTEGER PRIMARY KEY AUTOINCREMENT"

    def _get_text_type(self) -> str:
        """Retorna tipo de texto baseado no banco."""
        if self.db_type == DatabaseType.SQLITE:
            return "TEXT"
        elif self.db_type == DatabaseType.POSTGRESQL:
            return "VARCHAR(255)"
        elif self.db_type == DatabaseType.MYSQL:
            return "VARCHAR(255)"
        return "TEXT"

    def _get_long_text_type(self) -> str:
        """Retorna tipo de texto longo baseado no banco."""
        if self.db_type == DatabaseType.SQLITE:
            return "TEXT"
        elif self.db_type == DatabaseType.POSTGRESQL:
            return "TEXT"
        elif self.db_type == DatabaseType.MYSQL:
            return "TEXT"
        return "TEXT"

    def _get_boolean_type(self) -> str:
        """Retorna tipo booleano baseado no banco."""
        if self.db_type == DatabaseType.SQLITE:
            return "INTEGER"
        elif self.db_type == DatabaseType.POSTGRESQL:
            return "BOOLEAN"
        elif self.db_type == DatabaseType.MYSQL:
            return "BOOLEAN"
        return "INTEGER"

    def _get_datetime_type(self) -> str:
        """Retorna tipo datetime baseado no banco."""
        if self.db_type == DatabaseType.SQLITE:
            return "DATETIME"
        elif self.db_type == DatabaseType.POSTGRESQL:
            return "TIMESTAMP"
        elif self.db_type == DatabaseType.MYSQL:
            return "DATETIME"
        return "DATETIME"

    def _get_real_type(self) -> str:
        """Retorna tipo real baseado no banco."""
        if self.db_type == DatabaseType.SQLITE:
            return "REAL"
        elif self.db_type == DatabaseType.POSTGRESQL:
            return "DOUBLE PRECISION"
        elif self.db_type == DatabaseType.MYSQL:
            return "DOUBLE"
        return "REAL"

    def _get_integer_type(self) -> str:
        """Retorna tipo inteiro baseado no banco."""
        return "INTEGER"

    def create_executions_table(self) -> str:
        """Gera CREATE TABLE para executions."""
        pk_type = self._get_pk_type()
        text_type = self._get_text_type()
        long_text_type = self._get_long_text_type()
        bool_type = self._get_boolean_type()
        datetime_type = self._get_datetime_type()
        real_type = self._get_real_type()
        int_type = self._get_integer_type()

        if self.db_type == DatabaseType.SQLITE:
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"
        elif self.db_type == DatabaseType.POSTGRESQL:
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"
        elif self.db_type == DatabaseType.MYSQL:
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"
        else:
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"

        bool_default_false = "DEFAULT 0" if self.db_type == DatabaseType.SQLITE else "DEFAULT FALSE"

        sql = f"""
            CREATE TABLE IF NOT EXISTS {self.executions_table} (
                id {pk_type},
                execution_id {text_type} UNIQUE,
                automation_name {text_type} NOT NULL,
                status {text_type} NOT NULL DEFAULT 'running',
                finished_properly {bool_type} {bool_default_false},
                allow_reprocess {bool_type} DEFAULT 1,
                reprocess_count {int_type} DEFAULT 0,
                parent_execution_id {int_type},
                started_at {datetime_type} NOT NULL {default_timestamp},
                finished_at {datetime_type},
                execution_time_seconds {real_type},
                total_items {int_type} DEFAULT 0,
                successful_items {int_type} DEFAULT 0,
                failed_items {int_type} DEFAULT 0,
                interrupted_items {int_type} DEFAULT 0,
                error_message {long_text_type},
                metadata {long_text_type},
                created_at {datetime_type} NOT NULL {default_timestamp},
                FOREIGN KEY (parent_execution_id) REFERENCES {self.executions_table}(id) ON DELETE SET NULL,
                CHECK (status IN ('running', 'completed', 'failed', 'cancelled', 'interrupted'))
            )
        """

        if self.db_type == DatabaseType.MYSQL:
            sql += " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"

        return sql

    def create_items_table(self) -> str:
        """Gera CREATE TABLE para execution_items."""
        pk_type = self._get_pk_type()
        text_type = self._get_text_type()
        long_text_type = self._get_long_text_type()
        bool_type = self._get_boolean_type()
        datetime_type = self._get_datetime_type()
        real_type = self._get_real_type()
        int_type = self._get_integer_type()

        if self.db_type == DatabaseType.SQLITE:
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"
            cascade_delete = "ON DELETE CASCADE"
        elif self.db_type == DatabaseType.POSTGRESQL:
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"
            cascade_delete = "ON DELETE CASCADE"
        elif self.db_type == DatabaseType.MYSQL:
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"
            cascade_delete = "ON DELETE CASCADE"
        else:
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"
            cascade_delete = "ON DELETE CASCADE"

        sql = f"""
            CREATE TABLE IF NOT EXISTS {self.items_table} (
                id {pk_type},
                execution_id {int_type} NOT NULL,
                item_identifier {text_type},
                status {text_type} NOT NULL DEFAULT 'pending',
                priority {int_type} DEFAULT 0,
                queue_position {int_type},
                processing_schema {long_text_type},
                item_data {long_text_type},
                last_checkpoint {text_type},
                started_at {datetime_type},
                finished_at {datetime_type},
                execution_time_seconds {real_type},
                error_message {long_text_type},
                notes {long_text_type},
                retry_count {int_type} DEFAULT 0,
                max_retries {int_type} DEFAULT 0,
                allow_reprocess {bool_type} DEFAULT 1,
                created_at {datetime_type} NOT NULL {default_timestamp},
                FOREIGN KEY (execution_id) REFERENCES {self.executions_table}(id) {cascade_delete},
                CHECK (status IN ('pending', 'queued', 'processing', 'success', 'failed', 'skipped', 'interrupted', 'retrying'))
            )
        """

        if self.db_type == DatabaseType.MYSQL:
            sql += " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"

        return sql

    def create_logs_table(self) -> str:
        """Gera CREATE TABLE para execution_logs."""
        pk_type = self._get_pk_type()
        text_type = self._get_text_type()
        long_text_type = self._get_long_text_type()
        datetime_type = self._get_datetime_type()
        int_type = self._get_integer_type()

        if self.db_type == DatabaseType.SQLITE:
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"
            cascade_delete = "ON DELETE CASCADE"
        elif self.db_type == DatabaseType.POSTGRESQL:
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"
            cascade_delete = "ON DELETE CASCADE"
        elif self.db_type == DatabaseType.MYSQL:
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"
            cascade_delete = "ON DELETE CASCADE"
        else:
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"
            cascade_delete = "ON DELETE CASCADE"

        sql = f"""
            CREATE TABLE IF NOT EXISTS {self.logs_table} (
                id {pk_type},
                execution_id {int_type} NOT NULL,
                log_level {text_type} DEFAULT '{LOG_LEVEL_INFO}',
                step_name {text_type},
                message {long_text_type} NOT NULL,
                timestamp {datetime_type} NOT NULL {default_timestamp},
                created_at {datetime_type} NOT NULL {default_timestamp},
                FOREIGN KEY (execution_id) REFERENCES {self.executions_table}(id) {cascade_delete},
                CHECK (log_level IN ('{VALID_LOG_LEVELS_SQL}'))
            )
        """

        if self.db_type == DatabaseType.MYSQL:
            sql += " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"

        return sql

    def create_indexes(self) -> List[str]:
        """Gera CREATE INDEX para melhor performance."""
        indexes = [
            f"CREATE INDEX IF NOT EXISTS idx_{self.executions_table}_execution_id ON {self.executions_table}(execution_id)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.executions_table}_status ON {self.executions_table}(status)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.executions_table}_finished_properly ON {self.executions_table}(finished_properly)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.executions_table}_started_at ON {self.executions_table}(started_at)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.items_table}_execution_id ON {self.items_table}(execution_id)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.items_table}_status ON {self.items_table}(status)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.items_table}_queue ON {self.items_table}(execution_id, queue_position, status)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.items_table}_priority ON {self.items_table}(priority DESC, status)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.logs_table}_execution_id ON {self.logs_table}(execution_id)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.logs_table}_timestamp ON {self.logs_table}(timestamp)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.logs_table}_log_level ON {self.logs_table}(log_level)",
            f"CREATE INDEX IF NOT EXISTS idx_{self.logs_table}_execution_timestamp ON {self.logs_table}(execution_id, timestamp)",
        ]
        return indexes

    def get_last_id_query(self) -> str:
        """Retorna query para pegar último ID inserido."""
        if self.db_type == DatabaseType.SQLITE:
            return "SELECT last_insert_rowid()"
        elif self.db_type == DatabaseType.POSTGRESQL:
            return "SELECT LASTVAL()"
        elif self.db_type == DatabaseType.MYSQL:
            return "SELECT LAST_INSERT_ID()"
        return "SELECT last_insert_rowid()"


# ========== CLASSE PRINCIPAL DATABASE ==========


class Database:
    """
    Classe principal para gerenciamento de execuções RPA com suporte multi-banco.

    Suporta: SQLite (padrão), PostgreSQL, MySQL

    Example:
    --------
    >>> # SQLite (padrão)
    >>> from rpa_suite.core import Database, DatabaseType
    >>> register = Database()
    >>>
    >>> # PostgreSQL
    >>> register = Database(
    ...     db_type=DatabaseType.POSTGRESQL,
    ...     host="localhost",
    ...     database="rpa_db",
    ...     user="user",
    ...     password="pass"
    ... )
    >>>
    >>> exec_id = register.start_execution(automation_name="Meu Bot")
    >>> register.add_item(execution_id=exec_id, item_identifier="001")
    >>> register.finish_execution(exec_id)

    pt-br
    -----
    Classe principal para gerenciamento de execuções RPA com suporte multi-banco.

    Suporta: SQLite (padrão), PostgreSQL, MySQL

    Exemplo:
    --------
    >>> # SQLite (padrão)
    >>> from rpa_suite.core import Database, DatabaseType
    >>> register = Database()
    >>>
    >>> # PostgreSQL
    >>> register = Database(
    ...     db_type=DatabaseType.POSTGRESQL,
    ...     host="localhost",
    ...     database="rpa_db",
    ...     user="user",
    ...     password="pass"
    ... )
    >>>
    >>> exec_id = register.start_execution(automation_name="Meu Bot")
    >>> register.add_item(execution_id=exec_id, item_identifier="001")
    >>> register.finish_execution(exec_id)
    """

    # Constantes expostas na classe para facilitar descoberta via IDE/autocomplete
    LOG_LEVEL_DEBUG = LOG_LEVEL_DEBUG
    LOG_LEVEL_INFO = LOG_LEVEL_INFO
    LOG_LEVEL_WARNING = LOG_LEVEL_WARNING
    LOG_LEVEL_ERROR = LOG_LEVEL_ERROR
    LOG_LEVEL_CRITICAL = LOG_LEVEL_CRITICAL
    LOG_LEVEL_SUCCESS = LOG_LEVEL_SUCCESS
    VALID_LOG_LEVELS = VALID_LOG_LEVELS

    def __init__(
        self,
        db_type: DatabaseType = DatabaseType.SQLITE,
        db_path: str = DEFAULT_DB_NAME,
        db_dir: str = "default",
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        use_pool: bool = True,
        pool_size: int = 5,
        executions_table: str = DEFAULT_EXECUTIONS_TABLE,
        items_table: str = DEFAULT_ITEMS_TABLE,
        logs_table: str = DEFAULT_LOGS_TABLE,
        allow_reprocess_interrupted_items: bool = False,
        allow_reprocess_interrupted_executions: bool = False,
        auto_detect_interruptions: bool = True,
        log_instance: Log | None = None,
        verbose: bool = False,
    ):
        """
        Inicializa o gerenciador de banco de dados.

        Parameters:
        -----------
        db_type: DatabaseType
            Tipo de banco: SQLITE, POSTGRESQL ou MYSQL
            Default: DatabaseType.SQLITE

        db_path: str
            Nome do arquivo SQLite (apenas para SQLite)
            Se db_dir for especificado, será usado junto com db_dir
            Default: "athena_executions.db"

        db_dir: str
            Diretório onde o banco SQLite será criado (apenas para SQLite)
            Se "default", usa o diretório atual (os.getcwd())
            O diretório será criado automaticamente se não existir
            Default: "default"

        host: Optional[str]
            Host do servidor (PostgreSQL/MySQL)

        port: Optional[int]
            Porta do servidor (PostgreSQL: 5432, MySQL: 3306)

        database: Optional[str]
            Nome do banco de dados (PostgreSQL/MySQL)

        user: Optional[str]
            Usuário do banco (PostgreSQL/MySQL)

        password: Optional[str]
            Senha do banco (PostgreSQL/MySQL)

        use_pool: bool
            Usar pool de conexões (PostgreSQL/MySQL)
            Default: True

        pool_size: int
            Tamanho do pool de conexões
            Default: 5

        executions_table: str
            Nome da tabela de execuções
            Default: "athena_executions"

        items_table: str
            Nome da tabela de itens
            Default: "athena_items"

        logs_table: str
            Nome da tabela de logs
            Default: "athena_logs"

        log_instance: Optional[Log]
            Instância opcional do objeto Log do RPA Suite.
            Se fornecido, os logs adicionados no banco também serão
            disparados no objeto Log com os mesmos níveis.
            Default: None

        allow_reprocess_interrupted_items: bool
            Permite reprocessar itens interrompidos

        allow_reprocess_interrupted_executions: bool
            Permite reprocessar execuções interrompidas

        auto_detect_interruptions: bool
            Detecta interrupções automaticamente

        verbose: bool
            Displays informative messages about directory creation
            Default: False

        pt-br
        -----------
        Inicializa o gerenciador de banco de dados.

        Parâmetros:
        -----------
        db_type: DatabaseType
            Tipo de banco: SQLITE, POSTGRESQL ou MYSQL
            Padrão: DatabaseType.SQLITE

        db_path: str
            Nome do arquivo SQLite (apenas para SQLite)
            Se db_dir for especificado, será usado junto com db_dir
            Padrão: "athena_executions.db"

        db_dir: str
            Diretório onde o banco SQLite será criado (apenas para SQLite)
            Se "default", usa o diretório atual (os.getcwd())
            O diretório será criado automaticamente se não existir
            Padrão: "default"

        host: Optional[str]
            Host do servidor (PostgreSQL/MySQL)

        port: Optional[int]
            Porta do servidor (PostgreSQL: 5432, MySQL: 3306)

        database: Optional[str]
            Nome do banco de dados (PostgreSQL/MySQL)

        user: Optional[str]
            Usuário do banco (PostgreSQL/MySQL)

        password: Optional[str]
            Senha do banco (PostgreSQL/MySQL)

        use_pool: bool
            Usar pool de conexões (PostgreSQL/MySQL)
            Padrão: True

        pool_size: int
            Tamanho do pool de conexões
            Padrão: 5

        executions_table: str
            Nome da tabela de execuções
            Padrão: "athena_executions"

        items_table: str
            Nome da tabela de itens
            Padrão: "athena_items"

        logs_table: str
            Nome da tabela de logs
            Padrão: "athena_logs"

        log_instance: Optional[Log]
            Instância opcional do objeto Log do RPA Suite.
            Se fornecido, os logs adicionados no banco também serão
            disparados no objeto Log com os mesmos níveis.
            Padrão: None

        allow_reprocess_interrupted_items: bool
            Permite reprocessar itens interrompidos

        allow_reprocess_interrupted_executions: bool
            Permite reprocessar execuções interrompidas

        auto_detect_interruptions: bool
            Detecta interrupções automaticamente

        verbose: bool
            Exibe mensagens informativas sobre criação de diretórios
            Padrão: False
        """
        try:
            self.db_type = db_type
            self.executions_table = executions_table
            self.items_table = items_table
            self.logs_table = logs_table
            self.allow_reprocess_items = allow_reprocess_interrupted_items
            self.allow_reprocess_executions = allow_reprocess_interrupted_executions
            self.auto_detect = auto_detect_interruptions
            self._current_execution_id = None

            # Armazena instância do Log se fornecida
            if log_instance is not None:
                if not LOG_AVAILABLE:
                    raise DatabaseError(
                        "Objeto Log não está disponível. " "Certifique-se de que rpa_suite.core.log está disponível."
                    )
                if not hasattr(log_instance, "log_debug"):
                    raise DatabaseError(
                        "Objeto fornecido não é uma instância válida de Log. "
                        "O objeto deve ter os métodos log_debug, log_info, etc."
                    )
            self.log_instance = log_instance

            # Processa o caminho do banco de dados (apenas para SQLite)
            final_db_path = db_path
            if db_type == DatabaseType.SQLITE:
                # Determina o diretório base
                if db_dir == "default":
                    base_dir = os.getcwd()
                else:
                    base_dir = db_dir

                # Extrai apenas o nome do arquivo de db_path (remove diretórios se houver)
                db_filename = os.path.basename(db_path)

                # Constrói o caminho completo
                final_db_path = os.path.join(base_dir, db_filename)

                # Cria o diretório se não existir
                try:
                    os.makedirs(base_dir, exist_ok=True)
                    if verbose:
                        success_print(f"Diretório '{base_dir}' foi criado ou já existe.")
                except FileExistsError:
                    if verbose:
                        alert_print(f"Diretório '{base_dir}' já existe.")
                except PermissionError as e:
                    raise DatabaseError(
                        f"Permissão negada: não é possível criar o diretório '{base_dir}'! {str(e)}."
                    ) from e

            # Cria o adaptador baseado no tipo
            self._adapter = self._create_adapter(
                db_type=db_type,
                db_path=final_db_path,
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                use_pool=use_pool,
                pool_size=pool_size,
            )

            # Conecta e cria tabelas
            self._adapter.connect()
            self._create_tables()

            # Registra handlers para detectar interrupção
            if auto_detect_interruptions:
                atexit.register(self._handle_exit)
                signal.signal(signal.SIGTERM, self._handle_signal)
                signal.signal(signal.SIGINT, self._handle_signal)
                self.detect_and_mark_interrupted_executions()

        except Exception as e:
            raise DatabaseError(f"Erro ao inicializar Database: {str(e)}.") from e

    def _create_adapter(self, **kwargs) -> DatabaseAdapter:
        """Factory para criar o adaptador correto."""
        db_type = kwargs["db_type"]

        if db_type == DatabaseType.SQLITE:
            return SQLiteAdapter(db_path=kwargs["db_path"])

        elif db_type == DatabaseType.POSTGRESQL:
            return PostgreSQLAdapter(
                host=kwargs["host"],
                port=kwargs.get("port", 5432),
                database=kwargs["database"],
                user=kwargs["user"],
                password=kwargs["password"],
                use_pool=kwargs["use_pool"],
                pool_size=kwargs["pool_size"],
            )

        elif db_type == DatabaseType.MYSQL:
            return MySQLAdapter(
                host=kwargs["host"],
                port=kwargs.get("port", 3306),
                database=kwargs["database"],
                user=kwargs["user"],
                password=kwargs["password"],
                use_pool=kwargs["use_pool"],
                pool_size=kwargs["pool_size"],
            )

        else:
            raise DatabaseError(f"Tipo de banco não suportado: {db_type}")

    def _create_tables(self) -> None:
        """Cria as tabelas usando o adaptador."""
        try:
            sql_generator = SQLGenerator(
                db_type=self.db_type,
                executions_table=self.executions_table,
                items_table=self.items_table,
                logs_table=self.logs_table,
            )

            create_executions = sql_generator.create_executions_table()
            create_items = sql_generator.create_items_table()
            create_logs = sql_generator.create_logs_table()
            create_indexes = sql_generator.create_indexes()

            # Executa usando o adaptador
            self._adapter.execute_query(create_executions)
            self._adapter.execute_query(create_items)
            self._adapter.execute_query(create_logs)

            for index_sql in create_indexes:
                try:
                    self._adapter.execute_query(index_sql)
                except Exception:  # nosec B110
                    # Índice pode já existir, ignorar
                    pass

            self._adapter.commit()

        except Exception as e:
            raise DatabaseError(f"Erro ao criar tabelas: {str(e)}.") from e

    def _handle_exit(self) -> None:
        """Handler para detectar saída inesperada do programa."""
        if self._current_execution_id:
            try:
                self._mark_execution_interrupted(self._current_execution_id)
            except Exception:  # nosec B110
                pass

    def _handle_signal(self, signum, frame) -> None:
        """Handler para sinais de interrupção."""
        if self._current_execution_id:
            try:
                self._mark_execution_interrupted(self._current_execution_id)
            except Exception:  # nosec B110
                pass

    def _mark_execution_interrupted(self, execution_id: int) -> None:
        """Marca execução como interrompida."""
        try:
            query = f"""
                UPDATE {self.executions_table}
                SET status = 'interrupted', finished_properly = 0
                WHERE id = ? AND status = 'running'
            """
            self._adapter.execute_query(query, (execution_id,))
            self._adapter.commit()
        except Exception:  # nosec B110
            pass

    # ========== MÉTODOS DE EXECUÇÃO ==========

    def start_execution(
        self, automation_name: str, execution_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Inicia uma nova execução.

        Parameters:
        -----------
        automation_name: str
            Nome da automação/bot

        execution_id: Optional[str]
            ID opcional externo para a execução

        metadata: Optional[Dict[str, Any]]
            Metadados adicionais em formato JSON

        Returns:
        --------
        int: ID da execução criada

        pt-br
        -----------
        Inicia uma nova execução.

        Parâmetros:
        -----------
        automation_name: str
            Nome da automação/bot

        execution_id: Optional[str]
            ID opcional externo para a execução

        metadata: Optional[Dict[str, Any]]
            Metadados adicionais em formato JSON

        Retorna:
        --------
        int: ID da execução criada
        """
        try:
            metadata_str = json.dumps(metadata) if metadata else None
            now = datetime.now()

            query = f"""
                INSERT INTO {self.executions_table}
                (execution_id, automation_name, status, started_at, metadata)
                VALUES (?, ?, 'running', ?, ?)
            """

            cursor = self._adapter.execute_query(query, (execution_id, automation_name, now, metadata_str))

            exec_id = self._adapter.get_last_insert_id(cursor, self.executions_table)
            self._adapter.commit()

            self._current_execution_id = exec_id  # type: ignore
            return exec_id

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao iniciar execução: {str(e)}.") from e

    def finish_execution(
        self, execution_id: int, status: str = "completed", error_message: Optional[str] = None
    ) -> bool:
        """
        Finaliza uma execução.

        Parameters:
        -----------
        execution_id: int
            ID da execução

        status: str
            Status final: 'completed', 'failed', 'cancelled'
            Default: 'completed'

        error_message: Optional[str]
            Mensagem de erro se houver

        Returns:
        --------
        bool: True se sucesso

        pt-br
        -----------
        Finaliza uma execução.

        Parâmetros:
        -----------
        execution_id: int
            ID da execução

        status: str
            Status final: 'completed', 'failed', 'cancelled'
            Padrão: 'completed'

        error_message: Optional[str]
            Mensagem de erro se houver

        Retorna:
        --------
        bool: True se sucesso
        """
        try:
            if status not in ["completed", "failed", "cancelled"]:
                raise DatabaseError(f"Status inválido: {status}")

            # Busca dados da execução
            exec_data = self.get_execution(execution_id)
            if not exec_data:
                raise DatabaseError(f"Execução {execution_id} não encontrada")

            started_at = (
                datetime.fromisoformat(exec_data["started_at"])
                if isinstance(exec_data["started_at"], str)
                else exec_data["started_at"]
            )
            finished_at = datetime.now()
            execution_time = (finished_at - started_at).total_seconds()

            # Busca contadores de itens
            items_query = f"""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    SUM(CASE WHEN status = 'interrupted' THEN 1 ELSE 0 END) as interrupted
                FROM {self.items_table}
                WHERE execution_id = ?
            """
            items_cursor = self._adapter.execute_query(items_query, (execution_id,))
            items_result = items_cursor.fetchone()

            total_items = items_result[0] if items_result else 0
            successful_items = items_result[1] if items_result else 0
            failed_items = items_result[2] if items_result else 0
            interrupted_items = items_result[3] if items_result else 0

            query = f"""
                UPDATE {self.executions_table}
                SET status = ?,
                    finished_properly = 1,
                    finished_at = ?,
                    execution_time_seconds = ?,
                    total_items = ?,
                    successful_items = ?,
                    failed_items = ?,
                    interrupted_items = ?,
                    error_message = ?
                WHERE id = ?
            """

            self._adapter.execute_query(
                query,
                (
                    status,
                    finished_at,
                    execution_time,
                    total_items,
                    successful_items,
                    failed_items,
                    interrupted_items,
                    error_message,
                    execution_id,
                ),
            )

            self._adapter.commit()

            if self._current_execution_id == execution_id:
                self._current_execution_id = None

            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao finalizar execução: {str(e)}.") from e

    def get_execution(self, execution_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca execução por ID.

        Parameters:
        -----------
        execution_id: int
            ID da execução

        Returns:
        --------
        Optional[Dict[str, Any]]: Dados da execução ou None

        pt-br
        -----------
        Busca execução por ID.

        Parâmetros:
        -----------
        execution_id: int
            ID da execução

        Retorna:
        --------
        Optional[Dict[str, Any]]: Dados da execução ou None
        """
        try:
            query = f"SELECT * FROM {self.executions_table} WHERE id = ?"
            cursor = self._adapter.execute_query(query, (execution_id,))
            row = cursor.fetchone()

            if row:
                if self.db_type == DatabaseType.SQLITE:
                    return dict(row)
                else:
                    return dict(row) if hasattr(row, "keys") else row
            return None

        except Exception as e:
            raise DatabaseError(f"Erro ao buscar execução: {str(e)}.") from e

    def get_executions(
        self, status: Optional[str] = None, automation_name: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista execuções com filtros.

        Parameters:
        -----------
        status: Optional[str]
            Filtrar por status

        automation_name: Optional[str]
            Filtrar por nome da automação

        limit: Optional[int]
            Limitar número de resultados

        Returns:
        --------
        List[Dict[str, Any]]: Lista de execuções

        pt-br
        -----------
        Lista execuções com filtros.

        Parâmetros:
        -----------
        status: Optional[str]
            Filtrar por status

        automation_name: Optional[str]
            Filtrar por nome da automação

        limit: Optional[int]
            Limitar número de resultados

        Retorna:
        --------
        List[Dict[str, Any]]: Lista de execuções
        """
        try:
            query = f"SELECT * FROM {self.executions_table} WHERE 1=1"
            params = []

            if status:
                query += " AND status = ?"
                params.append(status)

            if automation_name:
                query += " AND automation_name = ?"
                params.append(automation_name)

            query += " ORDER BY started_at DESC"

            if limit:
                query += f" LIMIT {limit}"

            cursor = self._adapter.execute_query(query, tuple(params) if params else None)
            rows = cursor.fetchall()

            if self.db_type == DatabaseType.SQLITE:
                return [dict(row) for row in rows]
            else:
                return [dict(row) if hasattr(row, "keys") else row for row in rows]

        except Exception as e:
            raise DatabaseError(f"Erro ao listar execuções: {str(e)}.") from e

    def detect_and_mark_interrupted_executions(self) -> List[int]:
        """
        Detecta e marca execuções que não foram finalizadas corretamente.

        Returns:
        --------
        List[int]: Lista de IDs de execuções marcadas como interrompidas

        pt-br
        -----------
        Detecta e marca execuções que não foram finalizadas corretamente.

        Retorna:
        --------
        List[int]: Lista de IDs de execuções marcadas como interrompidas
        """
        try:
            query = f"""
                UPDATE {self.executions_table}
                SET status = 'interrupted', finished_properly = 0
                WHERE status = 'running' AND finished_properly = 0
            """

            self._adapter.execute_query(query)

            # Busca IDs atualizados
            query_ids = f"""
                SELECT id FROM {self.executions_table}
                WHERE status = 'interrupted' AND finished_properly = 0
            """
            cursor = self._adapter.execute_query(query_ids)
            rows = cursor.fetchall()

            interrupted_ids = [row[0] if isinstance(row, tuple) else row["id"] for row in rows]

            self._adapter.commit()
            return interrupted_ids

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao detectar interrupções: {str(e)}.") from e

    # ========== MÉTODOS DE ITENS ==========

    def add_item(
        self,
        execution_id: int,
        item_identifier: Optional[str] = None,
        item_data: Optional[Dict[str, Any]] = None,
        processing_schema: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        max_retries: int = 0,
    ) -> int:
        """
        Adiciona item à fila de processamento.

        Parameters:
        -----------
        execution_id: int
            ID da execução

        item_identifier: Optional[str]
            Identificador único do item

        item_data: Optional[Dict[str, Any]]
            Dados do item em formato JSON

        processing_schema: Optional[Dict[str, Any]]
            Schema/instruções de processamento em formato JSON

        priority: int
            Prioridade do item (maior = mais prioritário)
            Default: 0

        max_retries: int
            Número máximo de tentativas de reprocessamento.
            0 = sem limite (comportamento atual)
            Default: 0

        Returns:
        --------
        int: ID do item criado

        pt-br
        -----------
        Adiciona item à fila de processamento.

        Parâmetros:
        -----------
        execution_id: int
            ID da execução

        item_identifier: Optional[str]
            Identificador único do item

        item_data: Optional[Dict[str, Any]]
            Dados do item em formato JSON

        processing_schema: Optional[Dict[str, Any]]
            Schema/instruções de processamento em formato JSON

        priority: int
            Prioridade do item (maior = mais prioritário)
            Padrão: 0

        max_retries: int
            Número máximo de tentativas de reprocessamento.
            0 = sem limite (comportamento atual)
            Padrão: 0

        Retorna:
        --------
        int: ID do item criado
        """
        try:
            # Calcula próxima posição na fila
            queue_query = f"""
                SELECT COALESCE(MAX(queue_position), 0) + 1 as next_pos
                FROM {self.items_table}
                WHERE execution_id = ?
            """
            queue_cursor = self._adapter.execute_query(queue_query, (execution_id,))
            queue_result = queue_cursor.fetchone()
            queue_position = queue_result[0] if queue_result else 1

            item_data_str = json.dumps(item_data) if item_data else None
            schema_str = json.dumps(processing_schema) if processing_schema else None

            query = f"""
                INSERT INTO {self.items_table}
                (execution_id, item_identifier, status, priority, queue_position, 
                 processing_schema, item_data, max_retries)
                VALUES (?, ?, 'pending', ?, ?, ?, ?, ?)
            """

            cursor = self._adapter.execute_query(
                query, (execution_id, item_identifier, priority, queue_position, schema_str, item_data_str, max_retries)
            )

            item_id = self._adapter.get_last_insert_id(cursor, self.items_table)

            # Atualiza contador total de itens na execução
            update_query = f"""
                UPDATE {self.executions_table}
                SET total_items = total_items + 1
                WHERE id = ?
            """
            self._adapter.execute_query(update_query, (execution_id,))

            self._adapter.commit()
            return item_id

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao adicionar item: {str(e)}.") from e

    def add_items(
        self, execution_id: int, items: List[Dict[str, Any]], default_priority: int = 0, default_max_retries: int = 0
    ) -> List[int]:
        """
        Adiciona múltiplos itens à fila de processamento em lote (mais eficiente).

        Parameters:
        -----------
        execution_id: int
            ID da execução

        items: List[Dict[str, Any]]
            Lista de dicionários com dados dos itens. Cada dicionário deve conter:
            - item_identifier (Optional[str]): Identificador único do item
            - item_data (Optional[Dict[str, Any]]): Dados do item em formato JSON
            - processing_schema (Optional[Dict[str, Any]]): Schema/instruções de processamento
            - priority (Optional[int]): Prioridade do item (usa default_priority se não fornecido)
            - max_retries (Optional[int]): Máximo de tentativas (usa default_max_retries se não fornecido)

        default_priority: int
            Prioridade padrão para itens que não especificarem priority
            Default: 0

        default_max_retries: int
            Máximo de tentativas padrão para itens que não especificarem max_retries
            0 = sem limite
            Default: 0

        Returns:
        --------
        List[int]: Lista de IDs dos itens criados (na mesma ordem dos items fornecidos)

        Example:
        --------
        >>> items = [
        ...     {
        ...         "item_identifier": "001",
        ...         "item_data": {"nome": "Item 1"},
        ...         "priority": 1
        ...     },
        ...     {
        ...         "item_identifier": "002",
        ...         "item_data": {"nome": "Item 2"}
        ...     }
        ... ]
        >>> item_ids = register.add_items(execution_id=exec_id, items=items)

        pt-br
        -----------
        Adiciona múltiplos itens à fila de processamento em lote (mais eficiente).

        Parâmetros:
        -----------
        execution_id: int
            ID da execução

        items: List[Dict[str, Any]]
            Lista de dicionários com dados dos itens. Cada dicionário deve conter:
            - item_identifier (Optional[str]): Identificador único do item
            - item_data (Optional[Dict[str, Any]]): Dados do item em formato JSON
            - processing_schema (Optional[Dict[str, Any]]): Schema/instruções de processamento
            - priority (Optional[int]): Prioridade do item (usa default_priority se não fornecido)
            - max_retries (Optional[int]): Máximo de tentativas (usa default_max_retries se não fornecido)

        default_priority: int
            Prioridade padrão para itens que não especificarem priority
            Padrão: 0

        default_max_retries: int
            Máximo de tentativas padrão para itens que não especificarem max_retries
            0 = sem limite
            Padrão: 0

        Retorna:
        --------
        List[int]: Lista de IDs dos itens criados (na mesma ordem dos items fornecidos)

        Exemplo:
        --------
        >>> items = [
        ...     {
        ...         "item_identifier": "001",
        ...         "item_data": {"nome": "Item 1"},
        ...         "priority": 1
        ...     },
        ...     {
        ...         "item_identifier": "002",
        ...         "item_data": {"nome": "Item 2"}
        ...     }
        ... ]
        >>> item_ids = register.add_items(execution_id=exec_id, items=items)
        """
        try:
            if not items or len(items) == 0:
                return []

            # Calcula posição inicial na fila
            queue_query = f"""
                SELECT COALESCE(MAX(queue_position), 0) as max_pos
                FROM {self.items_table}
                WHERE execution_id = ?
            """
            queue_cursor = self._adapter.execute_query(queue_query, (execution_id,))
            queue_result = queue_cursor.fetchone()
            start_position = (queue_result[0] if queue_result else 0) + 1

            # Prepara dados para batch insert
            params_list = []
            for idx, item in enumerate(items):
                item_identifier = item.get("item_identifier")
                item_data = item.get("item_data")
                processing_schema = item.get("processing_schema")
                priority = item.get("priority", default_priority)
                max_retries = item.get("max_retries", default_max_retries)
                queue_position = start_position + idx

                item_data_str = json.dumps(item_data) if item_data else None
                schema_str = json.dumps(processing_schema) if processing_schema else None

                params_list.append(
                    (execution_id, item_identifier, priority, queue_position, schema_str, item_data_str, max_retries)
                )

            # Insere todos os itens em batch
            query = f"""
                INSERT INTO {self.items_table}
                (execution_id, item_identifier, status, priority, queue_position, 
                 processing_schema, item_data, max_retries)
                VALUES (?, ?, 'pending', ?, ?, ?, ?, ?)
            """

            self._adapter.execute_many(query, params_list)

            # Busca os IDs dos itens recém-inseridos usando queue_position
            # Busca todos os itens inseridos nesta execução com queue_position >= start_position
            id_query = f"""
                SELECT id FROM {self.items_table}
                WHERE execution_id = ? AND queue_position >= ?
                ORDER BY queue_position ASC
                LIMIT ?
            """
            id_cursor = self._adapter.execute_query(id_query, (execution_id, start_position, len(items)))
            id_results = id_cursor.fetchall()

            # Extrai IDs dos resultados
            if self.db_type == DatabaseType.SQLITE:
                item_ids = [row["id"] for row in id_results]
            else:
                item_ids = [(row[0] if isinstance(row, tuple) else row["id"]) for row in id_results]

            # Atualiza contador total de itens na execução (uma única vez)
            update_query = f"""
                UPDATE {self.executions_table}
                SET total_items = total_items + ?
                WHERE id = ?
            """
            self._adapter.execute_query(update_query, (len(items), execution_id))

            self._adapter.commit()
            return item_ids

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao adicionar itens em lote: {str(e)}.") from e

    def get_next_item_from_queue(
        self, execution_id: int, include_interrupted: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retorna próximo item da fila ordenado por priority e queue_position.

        Parameters:
        -----------
        execution_id: int
            ID da execução

        include_interrupted: Optional[bool]
            Se None, usa configuração da classe (allow_reprocess_items)
            Se True, inclui itens interrompidos
            Se False, não inclui itens interrompidos

        Returns:
        --------
        Optional[Dict[str, Any]]: Próximo item ou None

        pt-br
        -----------
        Retorna próximo item da fila ordenado por priority e queue_position.

        Parâmetros:
        -----------
        execution_id: int
            ID da execução

        include_interrupted: Optional[bool]
            Se None, usa configuração da classe (allow_reprocess_items)
            Se True, inclui itens interrompidos
            Se False, não inclui itens interrompidos

        Retorna:
        --------
        Optional[Dict[str, Any]]: Próximo item ou None
        """
        try:
            if include_interrupted is None:
                include_interrupted = self.allow_reprocess_items

            status_filter = "('pending', 'queued')"
            if include_interrupted:
                status_filter = "('pending', 'queued', 'interrupted')"

            query = f"""
                SELECT * FROM {self.items_table}
                WHERE execution_id = ? AND status IN {status_filter}
                ORDER BY priority DESC, queue_position ASC
                LIMIT 1
            """

            cursor = self._adapter.execute_query(query, (execution_id,))
            row = cursor.fetchone()

            if row:
                if self.db_type == DatabaseType.SQLITE:
                    return dict(row)
                else:
                    return dict(row) if hasattr(row, "keys") else row
            return None

        except Exception as e:
            raise DatabaseError(f"Erro ao buscar próximo item: {str(e)}.") from e

    def start_processing_item(self, item_id: int) -> bool:
        """
        Marca item como 'processing' e registra started_at.

        Parameters:
        -----------
        item_id: int
            ID do item

        Returns:
        --------
        bool: True se sucesso

        pt-br
        -----------
        Marca item como 'processing' e registra started_at.

        Parâmetros:
        -----------
        item_id: int
            ID do item

        Retorna:
        --------
        bool: True se sucesso
        """
        try:
            query = f"""
                UPDATE {self.items_table}
                SET status = 'processing', started_at = ?
                WHERE id = ? AND status IN ('pending', 'queued', 'interrupted')
            """

            self._adapter.execute_query(query, (datetime.now(), item_id))
            self._adapter.commit()
            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao iniciar processamento do item: {str(e)}.") from e

    def update_checkpoint(self, item_id: int, checkpoint: str) -> bool:
        """
        Atualiza last_checkpoint do item.

        Parameters:
        -----------
        item_id: int
            ID do item

        checkpoint: str
            Descrição do checkpoint atual

        Returns:
        --------
        bool: True se sucesso

        pt-br
        -----------
        Atualiza last_checkpoint do item.

        Parâmetros:
        -----------
        item_id: int
            ID do item

        checkpoint: str
            Descrição do checkpoint atual

        Retorna:
        --------
        bool: True se sucesso
        """
        try:
            query = f"""
                UPDATE {self.items_table}
                SET last_checkpoint = ?
                WHERE id = ?
            """

            self._adapter.execute_query(query, (checkpoint, item_id))
            self._adapter.commit()
            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao atualizar checkpoint: {str(e)}.") from e

    def finish_item(
        self, item_id: int, status: str = "success", error_message: Optional[str] = None, notes: Optional[str] = None
    ) -> bool:
        """
        Finaliza processamento do item.

        Parameters:
        -----------
        item_id: int
            ID do item

        status: str
            Status final: 'success', 'failed', 'skipped'
            Default: 'success'

        error_message: Optional[str]
            Mensagem de erro se houver

        notes: Optional[str]
            Observações adicionais

        Returns:
        --------
        bool: True se sucesso

        pt-br
        -----------
        Finaliza processamento do item.

        Parâmetros:
        -----------
        item_id: int
            ID do item

        status: str
            Status final: 'success', 'failed', 'skipped'
            Padrão: 'success'

        error_message: Optional[str]
            Mensagem de erro se houver

        notes: Optional[str]
            Observações adicionais

        Retorna:
        --------
        bool: True se sucesso
        """
        try:
            if status not in ["success", "failed", "skipped"]:
                raise DatabaseError(f"Status inválido: {status}")

            # Busca dados do item
            item_data = self.get_item(item_id)
            if not item_data:
                raise DatabaseError(f"Item {item_id} não encontrado")

            started_at = None
            if item_data.get("started_at"):
                started_at = (
                    datetime.fromisoformat(item_data["started_at"])
                    if isinstance(item_data["started_at"], str)
                    else item_data["started_at"]
                )

            finished_at = datetime.now()
            execution_time = None
            if started_at:
                execution_time = (finished_at - started_at).total_seconds()

            query = f"""
                UPDATE {self.items_table}
                SET status = ?,
                    finished_at = ?,
                    execution_time_seconds = ?,
                    error_message = ?,
                    notes = ?
                WHERE id = ?
            """

            self._adapter.execute_query(query, (status, finished_at, execution_time, error_message, notes, item_id))

            # Atualiza contadores na execução
            count_query = f"""
                UPDATE {self.executions_table}
                SET successful_items = (
                    SELECT COUNT(*) FROM {self.items_table}
                    WHERE execution_id = {self.items_table}.execution_id AND status = 'success'
                ),
                failed_items = (
                    SELECT COUNT(*) FROM {self.items_table}
                    WHERE execution_id = {self.items_table}.execution_id AND status = 'failed'
                )
                WHERE id = (SELECT execution_id FROM {self.items_table} WHERE id = ?)
            """
            self._adapter.execute_query(count_query, (item_id,))

            self._adapter.commit()
            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao finalizar item: {str(e)}.") from e

    def get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca item por ID.

        Parameters:
        -----------
        item_id: int
            ID do item

        Returns:
        --------
        Optional[Dict[str, Any]]: Dados do item ou None

        pt-br
        -----------
        Busca item por ID.

        Parâmetros:
        -----------
        item_id: int
            ID do item

        Retorna:
        --------
        Optional[Dict[str, Any]]: Dados do item ou None
        """
        try:
            query = f"SELECT * FROM {self.items_table} WHERE id = ?"
            cursor = self._adapter.execute_query(query, (item_id,))
            row = cursor.fetchone()

            if row:
                if self.db_type == DatabaseType.SQLITE:
                    return dict(row)
                else:
                    return dict(row) if hasattr(row, "keys") else row
            return None

        except Exception as e:
            raise DatabaseError(f"Erro ao buscar item: {str(e)}.") from e

    def get_items(self, execution_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lista itens de uma execução.

        Parameters:
        -----------
        execution_id: int
            ID da execução

        status: Optional[str]
            Filtrar por status

        Returns:
        --------
        List[Dict[str, Any]]: Lista de itens

        pt-br
        -----------
        Lista itens de uma execução.

        Parâmetros:
        -----------
        execution_id: int
            ID da execução

        status: Optional[str]
            Filtrar por status

        Retorna:
        --------
        List[Dict[str, Any]]: Lista de itens
        """
        try:
            query = f"SELECT * FROM {self.items_table} WHERE execution_id = ?"
            params = [execution_id]

            if status:
                query += " AND status = ?"
                params.append(status)  # type: ignore

            query += " ORDER BY queue_position ASC"

            cursor = self._adapter.execute_query(query, tuple(params))
            rows = cursor.fetchall()

            if self.db_type == DatabaseType.SQLITE:
                return [dict(row) for row in rows]
            else:
                return [dict(row) if hasattr(row, "keys") else row for row in rows]

        except Exception as e:
            raise DatabaseError(f"Erro ao listar itens: {str(e)}.") from e

    def detect_and_mark_interrupted_items(self) -> List[int]:
        """
        Detecta e marca itens que não foram finalizados corretamente.

        Returns:
        --------
        List[int]: Lista de IDs de itens marcados como interrompidos

        pt-br
        -----------
        Detecta e marca itens que não foram finalizados corretamente.

        Retorna:
        --------
        List[int]: Lista de IDs de itens marcados como interrompidos
        """
        try:
            query = f"""
                UPDATE {self.items_table}
                SET status = 'interrupted'
                WHERE status = 'processing'
            """

            self._adapter.execute_query(query)

            # Busca IDs atualizados
            query_ids = f"SELECT id FROM {self.items_table} WHERE status = 'interrupted'"
            cursor = self._adapter.execute_query(query_ids)
            rows = cursor.fetchall()

            interrupted_ids = [row[0] if isinstance(row, tuple) else row["id"] for row in rows]

            self._adapter.commit()
            return interrupted_ids

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao detectar itens interrompidos: {str(e)}.") from e

    # ========== MÉTODOS DE REPROCESSAMENTO ==========

    def is_reprocessable(
        self,
        item: Dict[str, Any],
        allow_failed: bool = True,
        allow_interrupted: bool = True,
        allow_pending_queued: bool = True,
        transient_only_for_failed: bool = True,
    ) -> bool:
        """
        Decide se um item é elegível para reprocessamento.

        Regras:
        - Exige allow_reprocess = 1
        - Exige retry_count < max_retries (quando max_retries > 0)
        - Itens interrupted são reprocessáveis (se habilitado)
        - Itens failed são reprocessáveis opcionalmente, com filtro de falha transitória
        - Itens pending/queued/retrying são reprocessáveis para retomada em nova execução
        """
        status = str(item.get("status", "")).lower()
        allow_reprocess = int(item.get("allow_reprocess", 1)) == 1
        retry_count = int(item.get("retry_count", 0) or 0)
        max_retries = int(item.get("max_retries", 0) or 0)
        error_message = str(item.get("error_message") or "").lower()

        if not allow_reprocess:
            return False

        # max_retries <= 0 significa "sem limite" para manter compatibilidade.
        if max_retries > 0 and retry_count >= max_retries:
            return False

        if status == "interrupted":
            return allow_interrupted

        if status == "failed":
            if not allow_failed:
                return False
            if not transient_only_for_failed:
                return True
            return any(keyword in error_message for keyword in TRANSIENT_ERROR_KEYWORDS)

        if status in ("pending", "queued", "retrying"):
            return allow_pending_queued

        return False

    def can_reprocess_execution(self, execution_id: int) -> bool:
        """
        Verifica se uma execução pode ser reprocessada.

        Parameters:
        -----------
        execution_id: int
            ID da execução

        Returns:
        --------
        bool: True se pode reprocessar

        pt-br
        -----------
        Verifica se uma execução pode ser reprocessada.

        Parâmetros:
        -----------
        execution_id: int
            ID da execução

        Retorna:
        --------
        bool: True se pode reprocessar
        """
        try:
            exec_data = self.get_execution(execution_id)
            if not exec_data:
                return False

            return (
                exec_data.get("status") in ("interrupted", "failed")
                and exec_data.get("allow_reprocess", 1) == 1
                and self.allow_reprocess_executions
            )
        except Exception:
            return False

    def reprocess_interrupted_execution(
        self, execution_id: int, keep_items: bool = True, reset_items_status: bool = False
    ) -> Optional[int]:
        """
        Cria uma nova execução baseada em uma execução interrompida/falha.

        Parameters:
        -----------
        execution_id: int
            ID da execução interrompida/falha

        keep_items: bool
            Se True, mantém os itens da execução original
            Default: True

        reset_items_status: bool
            Se True, reseta status dos itens para 'pending'
            Default: False

        Returns:
        --------
        Optional[int]: ID da nova execução ou None se não permitido

        pt-br
        -----------
        Cria uma nova execução baseada em uma execução interrompida/falha.

        Parâmetros:
        -----------
        execution_id: int
            ID da execução interrompida/falha

        keep_items: bool
            Se True, mantém os itens da execução original
            Padrão: True

        reset_items_status: bool
            Se True, reseta status dos itens para 'pending'
            Padrão: False

        Retorna:
        --------
        Optional[int]: ID da nova execução ou None se não permitido
        """
        try:
            if not self.can_reprocess_execution(execution_id):
                return None

            exec_data = self.get_execution(execution_id)
            if not exec_data:
                return None

            # Cria nova execução
            new_exec_id = self.start_execution(
                automation_name=exec_data["automation_name"],
                execution_id=None,  # Novo execution_id
                metadata=json.loads(exec_data["metadata"]) if exec_data.get("metadata") else None,
            )

            # Atualiza parent_execution_id e reprocess_count
            update_query = f"""
                UPDATE {self.executions_table}
                SET parent_execution_id = ?, reprocess_count = reprocess_count + 1
                WHERE id = ?
            """
            self._adapter.execute_query(update_query, (execution_id, new_exec_id))

            # Se manter itens, copia itens elegíveis para nova execução
            if keep_items:
                items = self.get_items(execution_id)
                for item in items:
                    should_copy = reset_items_status or self.is_reprocessable(
                        item, allow_failed=True, allow_interrupted=True, allow_pending_queued=True
                    )
                    if not should_copy:
                        continue

                    new_status = "pending"
                    item_id_query = f"""
                        INSERT INTO {self.items_table}
                        (execution_id, item_identifier, status, priority, queue_position,
                         processing_schema, item_data, allow_reprocess)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    self._adapter.execute_query(
                        item_id_query,
                        (
                            new_exec_id,
                            item.get("item_identifier"),
                            new_status,
                            item.get("priority", 0),
                            item.get("queue_position"),
                            item.get("processing_schema"),
                            item.get("item_data"),
                            item.get("allow_reprocess", 1),
                        ),
                    )

            self._adapter.commit()
            return new_exec_id

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao reprocessar execução: {str(e)}.") from e

    def can_reprocess_item(self, item_id: int) -> bool:
        """
        Verifica se um item pode ser reprocessado.

        Parameters:
        -----------
        item_id: int
            ID do item

        Returns:
        --------
        bool: True se pode reprocessar

        pt-br
        -----------
        Verifica se um item pode ser reprocessado.

        Parâmetros:
        -----------
        item_id: int
            ID do item

        Retorna:
        --------
        bool: True se pode reprocessar
        """
        try:
            item_data = self.get_item(item_id)
            if not item_data:
                return False

            if not self.allow_reprocess_items:
                return False
            return self.is_reprocessable(item_data)
        except Exception:
            return False

    def reprocess_interrupted_item(self, item_id: int) -> bool:
        """
        Reprocessa um item elegível (interrupted/failed/pending/queued).

        Parameters:
        -----------
        item_id: int
            ID do item

        Returns:
        --------
        bool: True se sucesso

        pt-br
        -----------
        Reprocessa um item elegível (interrupted/failed/pending/queued).

        Parâmetros:
        -----------
        item_id: int
            ID do item

        Retorna:
        --------
        bool: True se sucesso
        """
        try:
            if not self.can_reprocess_item(item_id):
                raise DatabaseError(f"Item {item_id} não pode ser reprocessado")

            query = f"""
                UPDATE {self.items_table}
                SET status = 'pending',
                    started_at = NULL,
                    finished_at = NULL,
                    execution_time_seconds = NULL,
                    error_message = NULL,
                    last_checkpoint = NULL,
                    retry_count = retry_count + 1
                WHERE id = ?
            """

            self._adapter.execute_query(query, (item_id,))
            self._adapter.commit()
            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao reprocessar item: {str(e)}.") from e

    def reprocess_items_from_execution(
        self,
        execution_id: int,
        statuses: Optional[List[str]] = None,
        transient_only_for_failed: bool = True,
        limit: Optional[int] = None,
    ) -> List[int]:
        """
        Reprocessa em lote itens elegíveis de uma execução.

        Parameters:
        -----------
        execution_id: int
            ID da execução origem

        statuses: Optional[List[str]]
            Filtra por status desejados (ex: ['failed', 'interrupted'])
            Se None, usa todos os status elegíveis pela regra de reprocessamento.

        transient_only_for_failed: bool
            Se True, reprocessa item failed apenas quando erro for transitório.

        limit: Optional[int]
            Limita quantidade de itens reprocessados.

        Returns:
        --------
        List[int]: IDs dos itens reprocessados
        """
        try:
            if not self.allow_reprocess_items:
                return []

            items = self.get_items(execution_id)
            reprocessed_ids: List[int] = []
            allowed_statuses = {s.lower() for s in statuses} if statuses else None

            for item in items:
                status = str(item.get("status", "")).lower()
                if allowed_statuses is not None and status not in allowed_statuses:
                    continue

                if not self.is_reprocessable(
                    item,
                    allow_failed=True,
                    allow_interrupted=True,
                    allow_pending_queued=True,
                    transient_only_for_failed=transient_only_for_failed,
                ):
                    continue

                item_id = int(item["id"])
                self.reprocess_interrupted_item(item_id)
                reprocessed_ids.append(item_id)

                if limit and len(reprocessed_ids) >= limit:
                    break

            return reprocessed_ids

        except Exception as e:
            raise DatabaseError(f"Erro ao reprocessar itens em lote: {str(e)}.") from e

    # ========== MÉTODOS DE LIMPEZA - SEGUROS ==========

    def clear_pending_items(self, execution_id: Optional[int] = None) -> int:
        """
        Remove itens com status 'pending' ou 'queued'.

        Parameters:
        -----------
        execution_id: Optional[int]
            ID da execução. Se não informado, tenta usar a execução atual iniciada
            com start_execution. Se não houver execução atual, limpa de todas.

        Returns:
        --------
        int: Número de itens removidos

        pt-br
        -----------
        Remove itens com status 'pending' ou 'queued'.

        Parâmetros:
        -----------
        execution_id: Optional[int]
            ID da execução. Se não informado, tenta usar a execução atual iniciada
            com start_execution. Se não houver execução atual, limpa de todas.

        Retorna:
        --------
        int: Número de itens removidos
        """
        try:
            if execution_id:
                query = f"""
                    DELETE FROM {self.items_table}
                    WHERE execution_id = ? AND status IN ('pending', 'queued')
                """
                cursor = self._adapter.execute_query(query, (execution_id,))
            else:
                query = f"""
                    DELETE FROM {self.items_table}
                    WHERE status IN ('pending', 'queued')
                """
                cursor = self._adapter.execute_query(query)

            count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            self._adapter.commit()
            return count

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao limpar itens pendentes: {str(e)}.") from e

    def clear_interrupted_items(self, execution_id: Optional[int] = None, allow_reprocess_check: bool = True) -> int:
        """
        Remove itens com status 'interrupted'.

        Parameters:
        -----------
        execution_id: Optional[int]
            ID da execução. Se None, limpa de todas.

        allow_reprocess_check: bool
            Se True, remove apenas os que NÃO podem ser reprocessados

        Returns:
        --------
        int: Número de itens removidos

        pt-br
        -----------
        Remove itens com status 'interrupted'.

        Parâmetros:
        -----------
        execution_id: Optional[int]
            ID da execução. Se None, limpa de todas.

        allow_reprocess_check: bool
            Se True, remove apenas os que NÃO podem ser reprocessados

        Retorna:
        --------
        int: Número de itens removidos
        """
        try:
            if allow_reprocess_check:
                filter_clause = " AND allow_reprocess = 0"
            else:
                filter_clause = ""

            if execution_id:
                query = f"""
                    DELETE FROM {self.items_table}
                    WHERE execution_id = ? AND status = 'interrupted'{filter_clause}
                """
                cursor = self._adapter.execute_query(query, (execution_id,))
            else:
                query = f"""
                    DELETE FROM {self.items_table}
                    WHERE status = 'interrupted'{filter_clause}
                """
                cursor = self._adapter.execute_query(query)

            count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            self._adapter.commit()
            return count

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao limpar itens interrompidos: {str(e)}.") from e

    def clear_interrupted_executions(self, allow_reprocess_check: bool = True) -> int:
        """
        Remove execuções com status 'interrupted'.

        Parameters:
        -----------
        allow_reprocess_check: bool
            Se True, remove apenas as que NÃO podem ser reprocessadas

        Returns:
        --------
        int: Número de execuções removidas

        pt-br
        -----------
        Remove execuções com status 'interrupted'.

        Parâmetros:
        -----------
        allow_reprocess_check: bool
            Se True, remove apenas as que NÃO podem ser reprocessadas

        Retorna:
        --------
        int: Número de execuções removidas
        """
        try:
            if allow_reprocess_check:
                filter_clause = " AND allow_reprocess = 0"
            else:
                filter_clause = ""

            query = f"""
                DELETE FROM {self.executions_table}
                WHERE status = 'interrupted'{filter_clause}
            """
            cursor = self._adapter.execute_query(query)

            count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            self._adapter.commit()
            return count

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao limpar execuções interrompidas: {str(e)}.") from e

    # ========== MÉTODOS DE LIMPEZA - PROTEGIDOS ==========

    def clear_successful_items(
        self, execution_id: Optional[int] = None, confirm: bool = False, confirmation_code: Optional[str] = None
    ) -> int:
        """
        Remove itens com status 'success'.

        PERIGO: Remove dados de sucesso permanentemente!
        Requer confirmação dupla para segurança.

        Parameters:
        -----------
        execution_id: Optional[int]
            ID da execução. Se None, limpa de todas.

        confirm: bool
            Deve ser True

        confirmation_code: Optional[str]
            Deve ser "DELETE_SUCCESS" para executar

        Returns:
        --------
        int: Número de itens removidos

        Raises:
        ------
        DatabaseError: Se confirmação não fornecida corretamente

        pt-br
        -----------
        Remove itens com status 'success'.

        PERIGO: Remove dados de sucesso permanentemente!
        Requer confirmação dupla para segurança.

        Parâmetros:
        -----------
        execution_id: Optional[int]
            ID da execução. Se None, limpa de todas.

        confirm: bool
            Deve ser True

        confirmation_code: Optional[str]
            Deve ser "DELETE_SUCCESS" para executar

        Retorna:
        --------
        int: Número de itens removidos

        Raises:
        ------
        DatabaseError: Se confirmação não fornecida corretamente
        """
        if not confirm:
            raise DatabaseError("Esta operação remove dados permanentemente! " "Passe confirm=True para executar.")

        if confirmation_code != CONFIRMATION_CODES["DELETE_SUCCESS"]:
            raise DatabaseError(
                f"Confirmação inválida! " f"Deve passar confirmation_code='{CONFIRMATION_CODES['DELETE_SUCCESS']}'"
            )

        try:
            if execution_id:
                query = f"""
                    DELETE FROM {self.items_table}
                    WHERE execution_id = ? AND status = 'success'
                """
                cursor = self._adapter.execute_query(query, (execution_id,))
            else:
                query = f"""
                    DELETE FROM {self.items_table}
                    WHERE status = 'success'
                """
                cursor = self._adapter.execute_query(query)

            count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            self._adapter.commit()
            return count

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao limpar itens de sucesso: {str(e)}.") from e

    def clear_failed_items(
        self, execution_id: Optional[int] = None, confirm: bool = False, confirmation_code: Optional[str] = None
    ) -> int:
        """
        Remove itens com status 'failed'.

        PERIGO: Remove dados de falha permanentemente!
        Requer confirmação dupla para segurança.

        Parameters:
        -----------
        execution_id: Optional[int]
            ID da execução. Se None, limpa de todas.

        confirm: bool
            Deve ser True

        confirmation_code: Optional[str]
            Deve ser "DELETE_FAILED" para executar

        Returns:
        --------
        int: Número de itens removidos

        pt-br
        -----------
        Remove itens com status 'failed'.

        PERIGO: Remove dados de falha permanentemente!
        Requer confirmação dupla para segurança.

        Parâmetros:
        -----------
        execution_id: Optional[int]
            ID da execução. Se None, limpa de todas.

        confirm: bool
            Deve ser True

        confirmation_code: Optional[str]
            Deve ser "DELETE_FAILED" para executar

        Retorna:
        --------
        int: Número de itens removidos
        """
        if not confirm:
            raise DatabaseError("Esta operação remove dados permanentemente! " "Passe confirm=True para executar.")

        if confirmation_code != CONFIRMATION_CODES["DELETE_FAILED"]:
            raise DatabaseError(
                f"Confirmação inválida! " f"Deve passar confirmation_code='{CONFIRMATION_CODES['DELETE_FAILED']}'"
            )

        try:
            if execution_id:
                query = f"""
                    DELETE FROM {self.items_table}
                    WHERE execution_id = ? AND status = 'failed'
                """
                cursor = self._adapter.execute_query(query, (execution_id,))
            else:
                query = f"""
                    DELETE FROM {self.items_table}
                    WHERE status = 'failed'
                """
                cursor = self._adapter.execute_query(query)

            count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            self._adapter.commit()
            return count

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao limpar itens de falha: {str(e)}.") from e

    def clear_successful_executions(self, confirm: bool = False, confirmation_code: Optional[str] = None) -> int:
        """
        Remove execuções com status 'completed'.

        PERIGO: Remove execuções de sucesso permanentemente!

        Parameters:
        -----------
        confirm: bool
            Deve ser True

        confirmation_code: Optional[str]
            Deve ser "DELETE_SUCCESS_EXECUTIONS" para executar

        Returns:
        --------
        int: Número de execuções removidas

        pt-br
        -----------
        Remove execuções com status 'completed'.

        PERIGO: Remove execuções de sucesso permanentemente!

        Parâmetros:
        -----------
        confirm: bool
            Deve ser True

        confirmation_code: Optional[str]
            Deve ser "DELETE_SUCCESS_EXECUTIONS" para executar

        Retorna:
        --------
        int: Número de execuções removidas
        """
        if not confirm:
            raise DatabaseError("Esta operação remove dados permanentemente! " "Passe confirm=True para executar.")

        if confirmation_code != CONFIRMATION_CODES["DELETE_SUCCESS_EXECUTIONS"]:
            raise DatabaseError(
                f"Confirmação inválida! "
                f"Deve passar confirmation_code='{CONFIRMATION_CODES['DELETE_SUCCESS_EXECUTIONS']}'"
            )

        try:
            query = f"""
                DELETE FROM {self.executions_table}
                WHERE status = 'completed'
            """
            cursor = self._adapter.execute_query(query)

            count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            self._adapter.commit()
            return count

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao limpar execuções de sucesso: {str(e)}.") from e

    def clear_failed_executions(self, confirm: bool = False, confirmation_code: Optional[str] = None) -> int:
        """
        Remove execuções com status 'failed'.

        PERIGO: Remove execuções de falha permanentemente!

        Parameters:
        -----------
        confirm: bool
            Deve ser True

        confirmation_code: Optional[str]
            Deve ser "DELETE_FAILED_EXECUTIONS" para executar

        Returns:
        --------
        int: Número de execuções removidas

        pt-br
        -----------
        Remove execuções com status 'failed'.

        PERIGO: Remove execuções de falha permanentemente!

        Parâmetros:
        -----------
        confirm: bool
            Deve ser True

        confirmation_code: Optional[str]
            Deve ser "DELETE_FAILED_EXECUTIONS" para executar

        Retorna:
        --------
        int: Número de execuções removidas
        """
        if not confirm:
            raise DatabaseError("Esta operação remove dados permanentemente! " "Passe confirm=True para executar.")

        if confirmation_code != CONFIRMATION_CODES["DELETE_FAILED_EXECUTIONS"]:
            raise DatabaseError(
                f"Confirmação inválida! "
                f"Deve passar confirmation_code='{CONFIRMATION_CODES['DELETE_FAILED_EXECUTIONS']}'"
            )

        try:
            query = f"""
                DELETE FROM {self.executions_table}
                WHERE status = 'failed'
            """
            cursor = self._adapter.execute_query(query)

            count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            self._adapter.commit()
            return count

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao limpar execuções de falha: {str(e)}.") from e

    # ========== MÉTODOS DE LIMPEZA - COMPLETOS ==========

    def clear_executions_table(self, confirm: bool = False) -> bool:
        """
        Remove TODA a tabela executions.

        PERIGO: Remove todas as execuções permanentemente!

        Parameters:
        -----------
        confirm: bool
            Deve ser True para executar

        Returns:
        --------
        bool: True se executado com sucesso

        pt-br
        -----------
        Remove TODA a tabela executions.

        PERIGO: Remove todas as execuções permanentemente!

        Parâmetros:
        -----------
        confirm: bool
            Deve ser True para executar

        Retorna:
        --------
        bool: True se executado com sucesso
        """
        if not confirm:
            raise DatabaseError(
                "Esta operação remove TODOS os dados permanentemente! " "Passe confirm=True para executar."
            )

        try:
            query = f"DELETE FROM {self.executions_table}"
            self._adapter.execute_query(query)
            self._adapter.commit()
            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao limpar tabela execuções: {str(e)}.") from e

    def clear_items_table(self, confirm: bool = False) -> bool:
        """
        Remove TODA a tabela items.

        PERIGO: Remove todos os itens permanentemente!

        Parameters:
        -----------
        confirm: bool
            Deve ser True para executar

        Returns:
        --------
        bool: True se executado com sucesso

        pt-br
        -----------
        Remove TODA a tabela items.

        PERIGO: Remove todos os itens permanentemente!

        Parâmetros:
        -----------
        confirm: bool
            Deve ser True para executar

        Retorna:
        --------
        bool: True se executado com sucesso
        """
        if not confirm:
            raise DatabaseError(
                "Esta operação remove TODOS os dados permanentemente! " "Passe confirm=True para executar."
            )

        try:
            query = f"DELETE FROM {self.items_table}"
            self._adapter.execute_query(query)
            self._adapter.commit()
            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao limpar tabela itens: {str(e)}.") from e

    def clear_logs_table(self, confirm: bool = False) -> bool:
        """
        Remove TODA a tabela logs.

        PERIGO: Remove todos os logs permanentemente!

        Parameters:
        -----------
        confirm: bool
            Deve ser True para executar

        Returns:
        --------
        bool: True se executado com sucesso

        pt-br
        -----------
        Remove TODA a tabela logs.

        PERIGO: Remove todos os logs permanentemente!

        Parâmetros:
        -----------
        confirm: bool
            Deve ser True para executar

        Retorna:
        --------
        bool: True se executado com sucesso
        """
        if not confirm:
            raise DatabaseError(
                "Esta operação remove TODOS os dados permanentemente! " "Passe confirm=True para executar."
            )

        try:
            query = f"DELETE FROM {self.logs_table}"
            self._adapter.execute_query(query)
            self._adapter.commit()
            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao limpar tabela logs: {str(e)}.") from e

    def clear_database(self, confirm: bool = False) -> bool:
        """
        Limpa TODO o banco de dados (todas as tabelas).

        PERIGO: Remove todos os dados permanentemente!

        Parameters:
        -----------
        confirm: bool
            Deve ser True para executar

        Returns:
        --------
        bool: True se executado com sucesso

        pt-br
        -----------
        Limpa TODO o banco de dados (todas as tabelas).

        PERIGO: Remove todos os dados permanentemente!

        Parâmetros:
        -----------
        confirm: bool
            Deve ser True para executar

        Retorna:
        --------
        bool: True se executado com sucesso
        """
        if not confirm:
            raise DatabaseError(
                "Esta operação remove TODOS os dados permanentemente! " "Passe confirm=True para executar."
            )

        try:
            self.clear_items_table(confirm=True)
            self.clear_logs_table(confirm=True)  # Limpa logs antes de execuções
            self.clear_executions_table(confirm=True)
            return True

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao limpar banco: {str(e)}.") from e

    # ========== UTILITÁRIOS ==========

    def get_statistics(self, execution_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Retorna estatísticas das execuções/itens.

        Parameters:
        -----------
        execution_id: Optional[int]
            ID da execução. Se None, retorna estatísticas gerais

        Returns:
        --------
        Dict[str, Any]: Estatísticas

        pt-br
        -----------
        Retorna estatísticas das execuções/itens.

        Parâmetros:
        -----------
        execution_id: Optional[int]
            ID da execução. Se None, retorna estatísticas gerais

        Retorna:
        --------
        Dict[str, Any]: Estatísticas
        """
        try:
            if execution_id:
                # Estatísticas de uma execução específica
                exec_data = self.get_execution(execution_id)
                if not exec_data:
                    return {}

                items = self.get_items(execution_id)

                return {
                    "execution": exec_data,
                    "total_items": len(items),
                    "items_by_status": {
                        status: len([i for i in items if i.get("status") == status])
                        for status in ["pending", "queued", "processing", "success", "failed", "interrupted"]
                    },
                }
            else:
                # Estatísticas gerais
                exec_query = f"""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                        SUM(CASE WHEN status = 'interrupted' THEN 1 ELSE 0 END) as interrupted
                    FROM {self.executions_table}
                """
                exec_cursor = self._adapter.execute_query(exec_query)
                exec_stats = exec_cursor.fetchone()

                items_query = f"""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                        SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                    FROM {self.items_table}
                """
                items_cursor = self._adapter.execute_query(items_query)
                items_stats = items_cursor.fetchone()

                if self.db_type == DatabaseType.SQLITE:
                    return {"executions": dict(exec_stats), "items": dict(items_stats)}
                else:
                    exec_dict = (
                        dict(exec_stats) if hasattr(exec_stats, "keys") else {i: v for i, v in enumerate(exec_stats)}
                    )
                    items_dict = (
                        dict(items_stats) if hasattr(items_stats, "keys") else {i: v for i, v in enumerate(items_stats)}
                    )
                    return {"executions": exec_dict, "items": items_dict}

        except Exception as e:
            raise DatabaseError(f"Erro ao buscar estatísticas: {str(e)}.") from e

    # ========== MÉTODOS DE LOGS ==========

    def add_log(
        self,
        message: str,
        execution_id: Optional[int] = None,
        log_level: str = LOG_LEVEL_INFO,
        step_name: Optional[str] = None,
    ) -> int:
        """
        Adiciona um log à execução.

        Parameters:
        -----------
        message: str
            Mensagem do log (pode ser texto longo)

        execution_id: Optional[int]
            ID da execução. Se não informado, usa a execução atual iniciada
            com start_execution.

        log_level: str
            Nível do log (use as constantes LOG_LEVEL_* da classe).
            Default: LOG_LEVEL_INFO

        step_name: Optional[str]
            Nome da etapa/step (ex: "Etapa 1", "Fase 2", "Validação")

        Returns:
        --------
        int: ID do log criado

        pt-br
        -----------
        Adiciona um log à execução.

        Parâmetros:
        -----------
        message: str
            Mensagem do log (pode ser texto longo)

        execution_id: Optional[int]
            ID da execução. Se não informado, usa a execução atual iniciada
            com start_execution.

        log_level: str
            Nível do log (use as constantes LOG_LEVEL_* da classe).
            Padrão: LOG_LEVEL_INFO

        step_name: Optional[str]
            Nome da etapa/step (ex: "Etapa 1", "Fase 2", "Validação")

        Retorna:
        --------
        int: ID do log criado
        """
        try:
            if log_level not in self.VALID_LOG_LEVELS:
                raise DatabaseError(f"Nível de log inválido: {log_level}")

            resolved_execution_id = execution_id or self._current_execution_id
            if not resolved_execution_id:
                raise DatabaseError(
                    "execution_id não informado e nenhuma execução ativa encontrada. "
                    "Execute start_execution() antes de adicionar logs ou informe execution_id."
                )

            now = datetime.now()

            query = f"""
                INSERT INTO {self.logs_table}
                (execution_id, log_level, step_name, message, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """

            cursor = self._adapter.execute_query(query, (resolved_execution_id, log_level, step_name, message, now))

            log_id = self._adapter.get_last_insert_id(cursor, self.logs_table)
            self._adapter.commit()

            # Se log_instance foi fornecido, dispara também no objeto Log
            if self.log_instance is not None:
                try:
                    # Formata mensagem incluindo step_name se fornecido
                    formatted_message = message
                    if step_name:
                        formatted_message = f"[{step_name}] {message}"

                    # Captura o frame do arquivo que chamou add_log() (não do database.py)
                    caller_frame = None
                    current_file = os.path.normpath(__file__)

                    # Percorre a pilha de chamadas para encontrar o primeiro frame que não é do database.py
                    # Começa do frame atual (add_log) e vai para trás
                    frame = inspect.currentframe()
                    # Pula o frame atual (add_log) e vai para quem chamou
                    while frame:
                        frame = frame.f_back
                        if frame:
                            frame_file = os.path.normpath(frame.f_code.co_filename)
                            # Se encontrou um frame que não é do database.py, usa ele
                            if frame_file != current_file:
                                caller_frame = frame
                                break

                    # Se encontrou o caller, extrai filename e lineno
                    if caller_frame:
                        full_path_filename = caller_frame.f_code.co_filename
                        full_path_filename = os.path.normpath(full_path_filename)
                        parent_folder = os.path.basename(os.path.dirname(full_path_filename))
                        file_name = os.path.basename(full_path_filename)
                        display_filename = f"{parent_folder}/{file_name}"
                        caller_lineno = caller_frame.f_lineno

                        # Mapeia níveis do Database para níveis do Log
                        log_level_mapping = {
                            self.LOG_LEVEL_DEBUG: "DEBUG",
                            self.LOG_LEVEL_INFO: "INFO",
                            self.LOG_LEVEL_WARNING: "WARNING",
                            self.LOG_LEVEL_ERROR: "ERROR",
                            self.LOG_LEVEL_CRITICAL: "CRITICAL",
                            self.LOG_LEVEL_SUCCESS: "INFO",  # success usa INFO no Log
                        }

                        # Usa _log_with_context para passar o contexto correto
                        log_level = log_level_mapping.get(log_level, "INFO")
                        self.log_instance._log_with_context(
                            level=log_level, msg=formatted_message, filename=display_filename, lineno=caller_lineno
                        )
                    else:
                        # Fallback: se não encontrou o caller, usa os métodos normais
                        log_level_mapping = {
                            self.LOG_LEVEL_DEBUG: self.log_instance.log_debug,  # type: ignore
                            self.LOG_LEVEL_INFO: self.log_instance.log_info,  # type: ignore
                            self.LOG_LEVEL_WARNING: self.log_instance.log_warning,  # type: ignore
                            self.LOG_LEVEL_ERROR: self.log_instance.log_error,  # type: ignore
                            self.LOG_LEVEL_CRITICAL: self.log_instance.log_critical,  # type: ignore
                            self.LOG_LEVEL_SUCCESS: self.log_instance.log_info,  # type: ignore # success usa info no Log
                        }

                        # Chama o método correspondente do Log
                        log_method = log_level_mapping.get(log_level, self.log_instance.log_info)
                        log_method(formatted_message)  # type: ignore

                except Exception as log_error:  # nosec B110
                    # Não falha se o log externo falhar, apenas registra silenciosamente
                    # Isso evita que problemas no Log externo quebrem o fluxo principal
                    pass

            return log_id

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao adicionar log: {str(e)}.") from e

    def add_log_debug(self, message: str, execution_id: Optional[int] = None, step_name: Optional[str] = None) -> int:
        """Adiciona log com nível DEBUG."""
        return self.add_log(
            message=message, execution_id=execution_id, log_level=self.LOG_LEVEL_DEBUG, step_name=step_name
        )

    def add_log_info(self, message: str, execution_id: Optional[int] = None, step_name: Optional[str] = None) -> int:
        """Adiciona log com nível INFO."""
        return self.add_log(
            message=message, execution_id=execution_id, log_level=self.LOG_LEVEL_INFO, step_name=step_name
        )

    def add_log_warn(self, message: str, execution_id: Optional[int] = None, step_name: Optional[str] = None) -> int:
        """Adiciona log com nível WARNING."""
        return self.add_log(
            message=message, execution_id=execution_id, log_level=self.LOG_LEVEL_WARNING, step_name=step_name
        )

    def add_log_warning(self, message: str, execution_id: Optional[int] = None, step_name: Optional[str] = None) -> int:
        """Alias de add_log_warn para nível WARNING."""
        return self.add_log_warn(message=message, execution_id=execution_id, step_name=step_name)

    def add_log_error(self, message: str, execution_id: Optional[int] = None, step_name: Optional[str] = None) -> int:
        """Adiciona log com nível ERROR."""
        return self.add_log(
            message=message, execution_id=execution_id, log_level=self.LOG_LEVEL_ERROR, step_name=step_name
        )

    def add_log_critical(
        self, message: str, execution_id: Optional[int] = None, step_name: Optional[str] = None
    ) -> int:
        """Adiciona log com nível CRITICAL."""
        return self.add_log(
            message=message, execution_id=execution_id, log_level=self.LOG_LEVEL_CRITICAL, step_name=step_name
        )

    def add_log_success(self, message: str, execution_id: Optional[int] = None, step_name: Optional[str] = None) -> int:
        """Adiciona log com nível SUCCESS."""
        return self.add_log(
            message=message, execution_id=execution_id, log_level=self.LOG_LEVEL_SUCCESS, step_name=step_name
        )

    def get_logs(
        self,
        execution_id: Optional[int] = None,
        log_level: Optional[str] = None,
        step_name: Optional[str] = None,
        limit: Optional[int] = None,
        order_desc: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Busca logs de uma execução.

        Parameters:
        -----------
        execution_id: Optional[int]
            ID da execução. Se não informado, usa a execução atual iniciada
            com start_execution.

        log_level: Optional[str]
            Filtrar por nível de log

        step_name: Optional[str]
            Filtrar por nome da etapa

        limit: Optional[int]
            Limitar número de resultados

        order_desc: bool
            Se True, ordena por timestamp DESC (mais recentes primeiro)
            Se False, ordena por timestamp ASC (mais antigos primeiro)
            Default: True

        Returns:
        --------
        List[Dict[str, Any]]: Lista de logs

        pt-br
        -----------
        Busca logs de uma execução.

        Parâmetros:
        -----------
        execution_id: Optional[int]
            ID da execução. Se não informado, usa a execução atual iniciada
            com start_execution.

        log_level: Optional[str]
            Filtrar por nível de log

        step_name: Optional[str]
            Filtrar por nome da etapa

        limit: Optional[int]
            Limitar número de resultados

        order_desc: bool
            Se True, ordena por timestamp DESC (mais recentes primeiro)
            Se False, ordena por timestamp ASC (mais antigos primeiro)
            Padrão: True

        Retorna:
        --------
        List[Dict[str, Any]]: Lista de logs
        """
        try:
            resolved_execution_id = execution_id or self._current_execution_id
            if not resolved_execution_id:
                raise DatabaseError(
                    "execution_id não informado e nenhuma execução ativa encontrada. "
                    "Execute start_execution() antes de buscar logs ou informe execution_id."
                )

            query = f"SELECT * FROM {self.logs_table} WHERE execution_id = ?"
            params = [resolved_execution_id]

            if log_level:
                query += " AND log_level = ?"
                params.append(log_level)  # type: ignore

            if step_name:
                query += " AND step_name = ?"
                params.append(step_name)  # type: ignore

            query += f" ORDER BY timestamp {'DESC' if order_desc else 'ASC'}"

            if limit:
                query += f" LIMIT {limit}"

            cursor = self._adapter.execute_query(query, tuple(params))
            rows = cursor.fetchall()

            if self.db_type == DatabaseType.SQLITE:
                return [dict(row) for row in rows]
            else:
                return [dict(row) if hasattr(row, "keys") else row for row in rows]

        except Exception as e:
            raise DatabaseError(f"Erro ao buscar logs: {str(e)}.") from e

    def clear_logs(
        self,
        execution_id: Optional[int] = None,
        log_level: Optional[str] = None,
        older_than_days: Optional[int] = None,
        confirm: bool = False,
    ) -> int:
        """
        Remove logs.

        Parameters:
        -----------
        execution_id: Optional[int]
            ID da execução. Se None, limpa de todas.

        log_level: Optional[str]
            Filtrar por nível de log

        older_than_days: Optional[int]
            Remove apenas logs mais antigos que X dias

        confirm: bool
            Deve ser True para executar (proteção contra limpeza acidental)

        Returns:
        --------
        int: Número de logs removidos

        pt-br
        -----------
        Remove logs.

        Parâmetros:
        -----------
        execution_id: Optional[int]
            ID da execução. Se None, limpa de todas.

        log_level: Optional[str]
            Filtrar por nível de log

        older_than_days: Optional[int]
            Remove apenas logs mais antigos que X dias

        confirm: bool
            Deve ser True para executar (proteção contra limpeza acidental)

        Retorna:
        --------
        int: Número de logs removidos
        """
        if not confirm:
            raise DatabaseError("Esta operação remove logs permanentemente! " "Passe confirm=True para executar.")

        try:
            query = f"DELETE FROM {self.logs_table} WHERE 1=1"
            params = []
            resolved_execution_id = execution_id or self._current_execution_id

            if resolved_execution_id:
                query += " AND execution_id = ?"
                params.append(resolved_execution_id)

            if log_level:
                query += " AND log_level = ?"
                params.append(log_level)  # type: ignore

            if older_than_days:
                if self.db_type == DatabaseType.SQLITE:
                    query += " AND timestamp < datetime('now', '-' || ? || ' days')"
                    params.append(older_than_days)
                elif self.db_type == DatabaseType.POSTGRESQL:
                    query += f" AND timestamp < NOW() - INTERVAL '{older_than_days} days'"
                elif self.db_type == DatabaseType.MYSQL:
                    query += f" AND timestamp < DATE_SUB(NOW(), INTERVAL {older_than_days} DAY)"

            cursor = self._adapter.execute_query(query, tuple(params) if params else None)

            count = cursor.rowcount if hasattr(cursor, "rowcount") else 0
            self._adapter.commit()
            return count

        except Exception as e:
            self._adapter.rollback()
            raise DatabaseError(f"Erro ao limpar logs: {str(e)}.") from e
