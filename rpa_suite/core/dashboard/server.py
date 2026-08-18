# rpa_suite/core/dashboard/server.py

"""
Flask-based HTML dashboard for the RPA Suite Database.

Flask is imported lazily inside `create_app`/`run_dashboard` so the rest of
`rpa_suite` keeps working when Flask is not installed. See `__init__.py` for
usage examples.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

if TYPE_CHECKING:  # pragma: no cover - typing-only
    from flask import Flask


class DashboardError(Exception):
    """Raised when the dashboard cannot start or handle a request."""

    def __init__(self, message: str) -> None:
        clean_message = message.replace("DashboardError:", "").strip()
        super().__init__(f"DashboardError: {clean_message}")


def _require_flask():
    """Import Flask lazily and give a clear error when missing."""
    try:
        import flask  # type: ignore[import-not-found]  # noqa: F401
    except ImportError as e:  # pragma: no cover - depends on env
        raise DashboardError("Flask is required to run the dashboard. Install with: pip install rpa-suite[dashboard]") from e
    return flask


def _int_arg(value: Any, default: int) -> int:
    """Best-effort int parse for query args (returns `default` on failure)."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


def _dashboard_paths() -> dict[str, str]:
    """
    Resolve and validate dashboard template/static directories.

    Returns:
        dict with keys ``here``, ``templates`` and ``static``.

    Raises:
        DashboardError: when required HTML/CSS/JS assets are missing from the
            installed package (typical when package-data was not included).
    """
    here = os.path.dirname(os.path.abspath(__file__))
    templates = os.path.join(here, "templates")
    static = os.path.join(here, "static")
    required = (
        os.path.join(templates, "overview.html"),
        os.path.join(templates, "error.html"),
        os.path.join(static, "dashboard.css"),
        os.path.join(static, "dashboard.js"),
    )
    missing = [path for path in required if not os.path.isfile(path)]
    if missing:
        raise DashboardError(
            "Dashboard assets missing. Reinstall rpa-suite with templates included "
            f"(missing: {', '.join(os.path.basename(p) for p in missing)})."
        )
    return {"here": here, "templates": templates, "static": static}


def create_app(database, title: str = "RPA Suite Dashboard") -> Flask:
    """
    Build a Flask app that serves the dashboard against `database`.

    Parameters:
        database: An open `rpa_suite.core.database.Database` instance.
        title: Displayed in the browser tab and page header.

    Returns:
        A ready-to-run Flask application.
    """
    _require_flask()
    from flask import Flask, Response, jsonify, render_template, request  # type: ignore[import-not-found]

    paths = _dashboard_paths()
    app = Flask(
        __name__,
        template_folder=paths["templates"],
        static_folder=paths["static"],
        static_url_path="/static",
    )
    app.config["TITLE"] = title
    app.config["DATABASE"] = database

    @app.context_processor
    def _inject_title() -> dict[str, Any]:
        return {"title": app.config["TITLE"]}

    def _base_qs_without_page() -> str:
        pairs = [(k, v) for k, v in request.args.items() if k != "page"]
        return urlencode(pairs)

    def _view_data(raw: dict[str, Any]) -> dict[str, Any]:
        """Wrap paginated query results using `rows` (Jinja-safe key)."""
        return {
            "rows": raw.get("items", []),
            "page": raw.get("page", 1),
            "page_size": raw.get("page_size", 25),
            "total": raw.get("total", 0),
            "pages": raw.get("pages", 1),
        }

    # -------- HTML pages ----------------------------------------------------

    @app.route("/")
    def index() -> Any:
        summary = database.dashboard_summary()
        return render_template(
            "overview.html",
            active="overview",
            summary=summary,
        )

    @app.route("/executions")
    def executions_page() -> Any:
        page = _int_arg(request.args.get("page"), 1)
        page_size = _int_arg(request.args.get("page_size"), 25)
        status = _optional_str(request.args.get("status"))
        automation_name = _optional_str(request.args.get("automation_name"))
        started_after = _optional_str(request.args.get("started_after"))
        started_before = _optional_str(request.args.get("started_before"))

        data = database.list_executions(
            status=status,
            automation_name=automation_name,
            started_after=started_after,
            started_before=started_before,
            page=page,
            page_size=page_size,
        )
        return render_template(
            "executions.html",
            active="executions",
            data=_view_data(data),
            base_qs=_base_qs_without_page(),
            filters={
                "status": status or "",
                "automation_name": automation_name or "",
                "started_after": started_after or "",
                "started_before": started_before or "",
                "page_size": data["page_size"],
            },
        )

    @app.route("/items")
    def items_page() -> Any:
        page = _int_arg(request.args.get("page"), 1)
        page_size = _int_arg(request.args.get("page_size"), 25)
        execution_id = _optional_int(request.args.get("execution_id"))
        status = _optional_str(request.args.get("status"))
        search = _optional_str(request.args.get("search"))

        data = database.list_items(
            execution_id=execution_id,
            status=status,
            search=search,
            page=page,
            page_size=page_size,
        )
        return render_template(
            "items.html",
            active="items",
            data=_view_data(data),
            base_qs=_base_qs_without_page(),
            filters={
                "execution_id": "" if execution_id is None else execution_id,
                "status": status or "",
                "search": search or "",
                "page_size": data["page_size"],
            },
        )

    @app.route("/logs")
    def logs_page() -> Any:
        page = _int_arg(request.args.get("page"), 1)
        page_size = _int_arg(request.args.get("page_size"), 50)
        execution_id = _optional_int(request.args.get("execution_id"))
        log_level = _optional_str(request.args.get("log_level"))
        search = _optional_str(request.args.get("search"))

        data = database.list_logs(
            execution_id=execution_id,
            log_level=log_level,
            search=search,
            page=page,
            page_size=page_size,
        )
        return render_template(
            "logs.html",
            active="logs",
            data=_view_data(data),
            base_qs=_base_qs_without_page(),
            filters={
                "execution_id": "" if execution_id is None else execution_id,
                "log_level": log_level or "",
                "search": search or "",
                "page_size": data["page_size"],
            },
        )

    # -------- JSON API (fed to Chart.js on the client) ----------------------

    @app.route("/api/summary")
    def api_summary() -> Any:
        return jsonify(database.dashboard_summary())

    @app.route("/api/executions/timeseries")
    def api_executions_timeseries() -> Any:
        days = _int_arg(request.args.get("days"), 14)
        return jsonify(database.executions_over_time(days=days))

    @app.route("/api/items/status")
    def api_items_status() -> Any:
        execution_id = _optional_int(request.args.get("execution_id"))
        return jsonify(database.item_status_distribution(execution_id=execution_id))

    @app.route("/api/logs/levels")
    def api_logs_levels() -> Any:
        execution_id = _optional_int(request.args.get("execution_id"))
        return jsonify(database.log_level_distribution(execution_id=execution_id))

    @app.route("/api/executions/top")
    def api_executions_top() -> Any:
        limit = _int_arg(request.args.get("limit"), 5)
        return jsonify(database.top_automations(limit=limit))

    @app.errorhandler(Exception)
    def _handle_error(exc: Exception) -> Any:  # noqa: ARG001
        # Keep this generic so we do not leak internal SQL details to callers.
        # Never raise from here — if error.html is missing, fall back to plain HTML.
        message = str(exc) or exc.__class__.__name__
        if request.path.startswith("/api/"):
            return jsonify({"error": message}), 500
        try:
            return render_template("error.html", message=message, active=""), 500
        except Exception:
            safe = (
                "<!doctype html><html><head><meta charset='utf-8'>"
                "<title>Dashboard error</title></head><body>"
                f"<h1>Dashboard error</h1><pre>{message}</pre></body></html>"
            )
            return Response(safe, status=500, mimetype="text/html")

    return app


def run_dashboard(
    database,
    host: str = "127.0.0.1",
    port: int = 5001,
    debug: bool = False,
    title: str = "RPA Suite Dashboard",
) -> None:
    """
    Convenience helper that builds and runs the dashboard app.

    Parameters:
        database: An open `Database` instance.
        host: Bind host (default `127.0.0.1` — local access only).
        port: Bind port.
        debug: Flask debug mode.
        title: Displayed in the browser tab and page header.
    """
    app = create_app(database, title=title)
    app.run(host=host, port=port, debug=debug, use_reloader=False)
