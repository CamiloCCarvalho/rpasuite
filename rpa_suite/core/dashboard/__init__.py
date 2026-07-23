# rpa_suite/core/dashboard/__init__.py

"""
Local HTML dashboard for the RPA Suite Database.

The dashboard is an optional feature that requires Flask. Users install it
alongside the suite (e.g. `pip install flask`) and launch either via the
CLI (`python -m rpa_suite dashboard <db.db>`) or programmatically:

    >>> from rpa_suite.core import Database
    >>> from rpa_suite.core.dashboard import create_app, run_dashboard
    >>> db = Database(db_path="my.db")
    >>> run_dashboard(db, host="127.0.0.1", port=5001)

Because Flask is an optional dep, the actual imports happen inside
`create_app`/`run_dashboard`; importing this module does not require Flask.
"""

from .server import DashboardError, create_app, run_dashboard

__all__ = ["DashboardError", "create_app", "run_dashboard"]
