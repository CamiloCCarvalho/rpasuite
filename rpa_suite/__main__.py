# rpa_suite/__main__.py

# imports standard
import argparse
import json
import os
import sys

from . import __version__
from .core.database import Database, DatabaseType


def _open_sqlite(path: str) -> Database:
    """Open an existing SQLite database file with sensible defaults for CLI use."""
    db_dir = os.path.dirname(os.path.abspath(path)) or "."
    db_file = os.path.basename(path)
    return Database(
        db_type=DatabaseType.SQLITE,
        db_path=db_file,
        db_dir=db_dir,
        auto_detect_interruptions=False,
        verbose=False,
    )


def _cmd_version(_args: argparse.Namespace) -> int:
    print(__version__)
    return 0


def _cmd_db_stats(args: argparse.Namespace) -> int:
    """Print storage stats for a SQLite database created by `Database`.

    Opens the database read-only-ish (schema is created with
    `CREATE TABLE IF NOT EXISTS`, so existing files are not disturbed).
    """
    db = _open_sqlite(args.path)
    try:
        stats = db.get_storage_stats()
    finally:
        try:
            db.close()
        except Exception:  # noqa: BLE001
            pass

    if args.json:
        print(json.dumps(stats, indent=2, default=str))
        return 0

    print(f"Database: {args.path}")
    for section, values in stats.items():
        print(f"\n[{section}]")
        if isinstance(values, dict):
            for key, val in values.items():
                print(f"  {key}: {val}")
        else:
            print(f"  {values}")
    return 0


def _cmd_dashboard(args: argparse.Namespace) -> int:
    """Launch the local HTML dashboard against a SQLite database file."""
    from .core.dashboard import run_dashboard  # lazy: requires flask

    db = _open_sqlite(args.path)
    try:
        print(f"Serving dashboard for {args.path} at http://{args.host}:{args.port}")
        run_dashboard(
            db,
            host=args.host,
            port=args.port,
            debug=args.debug,
            title=args.title,
        )
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        try:
            db.close()
        except Exception:  # noqa: BLE001
            pass
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rpa_suite",
        description="rpa_suite command-line utilities.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    version_parser = subparsers.add_parser(
        "version", help="Show the installed rpa_suite version."
    )
    version_parser.set_defaults(func=_cmd_version)

    stats_parser = subparsers.add_parser(
        "db-stats",
        help="Print retention/storage statistics for a SQLite Database file.",
    )
    stats_parser.add_argument("path", help="Path to the SQLite .db file.")
    stats_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of a plain summary.",
    )
    stats_parser.set_defaults(func=_cmd_db_stats)

    dashboard_parser = subparsers.add_parser(
        "dashboard",
        help="Serve an HTML dashboard for a SQLite Database file (requires flask).",
    )
    dashboard_parser.add_argument("path", help="Path to the SQLite .db file.")
    dashboard_parser.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1).")
    dashboard_parser.add_argument("--port", type=int, default=5001, help="Bind port (default 5001).")
    dashboard_parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode.")
    dashboard_parser.add_argument(
        "--title", default="RPA Suite Dashboard", help="Dashboard title (browser tab + header)."
    )
    dashboard_parser.set_defaults(func=_cmd_dashboard)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    sys.exit(main())
