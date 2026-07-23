# rpa_suite/core/database/core.py

from __future__ import annotations

import os

from rpa_suite.functions._printer import alert_print, success_print

from .adapters import DatabaseAdapter, MySQLAdapter, PostgreSQLAdapter, SQLiteAdapter
from .constants import (
    CONFIRMATION_CODES,
    DEFAULT_DB_NAME,
    DEFAULT_EXECUTIONS_TABLE,
    DEFAULT_ITEMS_TABLE,
    DEFAULT_LOGS_TABLE,
    LOG_LEVEL_CRITICAL,
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_INFO,
    LOG_LEVEL_SUCCESS,
    LOG_LEVEL_WARNING,
    TRANSIENT_ERROR_KEYWORDS,
    VALID_LOG_LEVELS,
    DatabaseType,
)
from .exceptions import DatabaseError
from .helpers import extract_row_id, row_to_dict, rows_to_dicts
from .item_dedup import (
    extract_item_unique_value,
    json_extract_sql,
    resolve_item_identifier_for_storage,
)
from .retention import RetentionPolicy
from .schema_migrations import run_schema_migrations
from .signals import register_database, unregister_database
from .sql_generator import SQLGenerator
from .validation import (
    validate_days,
    validate_limit,
    validate_table_name,
    validate_unique_item_field,
)

try:
    from ..log import Log

    LOG_AVAILABLE = True
except ImportError:
    LOG_AVAILABLE = False
    Log = None  # type: ignore

from .mixins import (
    CleanupMixin,
    DashboardQueriesMixin,
    ExecutionsMixin,
    ItemsMixin,
    LogsMixin,
    ProcessQueueMixin,
    ReprocessMixin,
    RetentionMixin,
    StatisticsMixin,
)


class Database(
    RetentionMixin,
    ProcessQueueMixin,
    DashboardQueriesMixin,
    ExecutionsMixin,
    ItemsMixin,
    ReprocessMixin,
    CleanupMixin,
    StatisticsMixin,
    LogsMixin,
):
    """
    Main class for RPA execution management with multi-database support.

    Supports SQLite (default), PostgreSQL, and MySQL.
    """

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
        host: str | None = None,
        port: int | None = None,
        database: str | None = None,
        user: str | None = None,
        password: str | None = None,
        use_pool: bool = True,
        pool_size: int = 5,
        executions_table: str = DEFAULT_EXECUTIONS_TABLE,
        items_table: str = DEFAULT_ITEMS_TABLE,
        logs_table: str = DEFAULT_LOGS_TABLE,
        allow_reprocess_interrupted_items: bool = False,
        allow_reprocess_interrupted_executions: bool = False,
        auto_detect_interruptions: bool = True,
        mark_stale_on_init: bool = False,
        auto_generate_execution_id: bool = True,
        prevent_duplicate_items: bool = False,
        unique_item_field: str = "item_identifier",
        duplicate_item_behavior: str = "skip",
        log_instance: Log | None = None,
        verbose: bool = False,
        retention_policy: RetentionPolicy | dict | None = None,
    ):
        """
        Initialize the database manager.

        Parameters:
        -----------
        db_type : DatabaseType
            Database backend: SQLITE, POSTGRESQL, or MYSQL.
            Default: DatabaseType.SQLITE

        db_path : str
            SQLite file name (SQLite only).
            Combined with db_dir when db_dir is set.
            Default: "athena_executions.db"

        db_dir : str
            Directory for the SQLite database file (SQLite only).
            Use "default" for the current working directory.
            Created automatically when missing.
            Default: "default"

        host : Optional[str]
            Server host (PostgreSQL/MySQL).

        port : Optional[int]
            Server port (PostgreSQL: 5432, MySQL: 3306).

        database : Optional[str]
            Database name (PostgreSQL/MySQL).

        user : Optional[str]
            Database user (PostgreSQL/MySQL).

        password : Optional[str]
            Database password (PostgreSQL/MySQL).

        use_pool : bool
            Enable connection pooling (PostgreSQL/MySQL).
            Default: True

        pool_size : int
            Connection pool size.
            Default: 5

        executions_table : str
            Executions table name.
            Default: "athena_executions"

        items_table : str
            Items table name.
            Default: "athena_items"

        logs_table : str
            Logs table name.
            Default: "athena_logs"

        allow_reprocess_interrupted_items : bool
            Allow reprocessing interrupted/failed items.
            Default: False

        allow_reprocess_interrupted_executions : bool
            Allow reprocessing interrupted executions.
            Default: False

        auto_detect_interruptions : bool
            Register signal handlers to detect interruptions automatically.
            Default: True

        mark_stale_on_init : bool
            When True, mark stale running executions/items as interrupted on init.
            Default: False

        auto_generate_execution_id : bool
            Generate a UUID for execution_id when not provided to start_execution().
            Default: True

        prevent_duplicate_items : bool
            Enable global item deduplication.
            Default: False

        unique_item_field : str
            Field used for deduplication: "item_identifier" or "item_data.<key>".
            Default: "item_identifier"

        duplicate_item_behavior : str
            Behavior on duplicate: "skip" (return existing id) or "error".
            Default: "skip"

        log_instance : Optional[Log]
            Optional RPA Suite Log instance. When set, database logs are also
            forwarded to the Log object.
            Default: None

        verbose : bool
            Print informational messages during initialization.
            Default: False

        retention_policy : RetentionPolicy | dict | None
            Automatic table retention (TTL + row caps). Pass a dict or
            ``RetentionPolicy`` instance. Use ``enabled=True`` to activate.
            Default: disabled.
        """
        try:
            if isinstance(retention_policy, RetentionPolicy):
                self.retention_policy = retention_policy
            else:
                self.retention_policy = RetentionPolicy.from_mapping(retention_policy)
            self.db_type = db_type
            # Validar nomes de tabelas para prevenir SQL injection
            self.executions_table = validate_table_name(executions_table)
            self.items_table = validate_table_name(items_table)
            self.logs_table = validate_table_name(logs_table)
            self.allow_reprocess_items = allow_reprocess_interrupted_items
            self.allow_reprocess_executions = allow_reprocess_interrupted_executions
            self.auto_detect = auto_detect_interruptions
            self._current_execution_id = None
            self._interrupted_flag = False
            self._closed = False
            self.mark_stale_on_init = mark_stale_on_init
            self.auto_generate_execution_id = auto_generate_execution_id
            self.prevent_duplicate_items = prevent_duplicate_items
            self.unique_item_field = validate_unique_item_field(unique_item_field)
            if duplicate_item_behavior not in ("skip", "error"):
                raise DatabaseError("Invalid duplicate_item_behavior. Use 'skip' or 'error'.")
            self.duplicate_item_behavior = duplicate_item_behavior

            # Armazena instância do Log se fornecida
            if log_instance is not None:
                if not LOG_AVAILABLE:
                    raise DatabaseError("Log object is not available. " "Ensure rpa_suite.core.log is importable.")
                if not hasattr(log_instance, "log_debug"):
                    raise DatabaseError(
                        "The provided object is not a valid Log instance. "
                        "It must expose log_debug, log_info, and related methods"
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
                    raise DatabaseError(f"Permission denied: cannot create directory '{base_dir}'! {str(e)}.") from e

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

            if auto_detect_interruptions:
                register_database(self)
                if mark_stale_on_init:
                    self.detect_and_mark_interrupted_executions(scope="all")
                    self.detect_and_mark_interrupted_items(scope="all")

            if self.retention_policy.enabled and self.retention_policy.auto_on_init:
                self.apply_retention_policy(dry_run=False)

        except Exception as e:
            raise DatabaseError(f"Failed to initialize Database: {str(e)}.") from e

    def close(self) -> None:
        """Close the database connection and unregister interruption handlers."""
        if self._closed:
            return
        unregister_database(self)
        self._adapter.close()
        self._closed = True

    def __enter__(self) -> Database:
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager and close the connection."""
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def _ensure_open(self) -> None:
        """Raise if the database connection has already been closed."""
        if self._closed:
            raise DatabaseError("Database connection is already closed. Create a new Database instance.")

    def _create_adapter(self, **kwargs) -> DatabaseAdapter:
        """Factory that creates the adapter for the configured database type."""
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
            raise DatabaseError(f"Unsupported database type: {db_type}")

    def _create_tables(self) -> None:
        """Create tables and indexes using the active adapter."""
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
                except Exception:
                    pass

            if self.prevent_duplicate_items:
                self._sync_unique_item_index()

            run_schema_migrations(
                self.db_type,
                self._adapter,
                self.items_table,
            )

            self._adapter.commit()

        except Exception as e:
            raise DatabaseError(f"Failed to create tables: {str(e)}.") from e

    def _sync_unique_item_index(self) -> None:
        """
        Sync the unique item_identifier index with the current configuration.

        The index exists only when deduplication uses ``item_identifier``.
        When the unique field changes (e.g. item_data.order_id), any legacy index
        is dropped so inserts with the same item_identifier are not blocked.
        """
        index_name = f"idx_{self.items_table}_unique_item_identifier"
        try:
            self._adapter.execute_query(f"DROP INDEX IF EXISTS {index_name}")
        except Exception:
            pass

        if not self.prevent_duplicate_items:
            return
        if self.unique_item_field != "item_identifier":
            return

        index_sql = (
            f"CREATE UNIQUE INDEX IF NOT EXISTS {index_name} "
            f"ON {self.items_table}(item_identifier) "
            f"WHERE item_identifier IS NOT NULL AND item_identifier != ''"
        )
        try:
            self._adapter.execute_query(index_sql)
        except Exception:
            pass
