"""
Flask application for GradCafe database analysis.

Buttons (Pull Data / Update Analysis) now publish tasks to RabbitMQ
and immediately return HTTP 202 "request queued" instead of doing
synchronous work.  The worker container processes those tasks.
"""
import os

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from query_data import run_all_queries
from publisher import publish_task

load_dotenv(override=False)

DATABASE_INFO = {
    "gradcafe": {
        "name": "gradcafe",
        "display_name": "GradCafe Dataset",
        "file_path": "src/data/applicant_data.json",
    },
}


def create_app(query_func=None, config=None):
    """
    Application factory.

    Args:
        query_func: Overridable query function (for testing).
        config:     Optional dict of Flask config overrides.
    """
    app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

    if config:
        app.config.update(config)

    _query_func = query_func or run_all_queries

    # ------------------------------------------------------------------ #
    #  Routes                                                              #
    # ------------------------------------------------------------------ #

    @app.route("/")
    @app.route("/analysis")
    def index():
        """Main analysis page – runs all SQL queries and renders results."""
        dbname = request.args.get("db", "gradcafe")
        if dbname not in DATABASE_INFO:
            dbname = "gradcafe"

        results = _query_func(dbname=dbname)
        return render_template(
            "results.html",
            results=results,
            current_db=dbname,
            db_info=DATABASE_INFO,
        )

    @app.route("/pull-data", methods=["POST"])
    @app.route("/pull_data", methods=["POST"])
    def pull_data():
        """
        Enqueue a scrape-new-data task.
        Returns HTTP 202 immediately; the worker does the actual work.
        """
        dbname = "gradcafe"
        if request.is_json:
            dbname = request.json.get("dbname", "gradcafe")
            max_pages = request.json.get("max_pages", 2)
        else:
            max_pages = 2

        if dbname not in DATABASE_INFO:
            dbname = "gradcafe"

        try:
            publish_task(
                "scrape_new_data",
                payload={"dbname": dbname, "max_pages": max_pages},
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            return jsonify({"ok": False, "message": f"Could not enqueue task: {exc}"}), 503

        return (
            jsonify({"ok": True, "queued": True, "message": "Scrape task queued – results will appear shortly."}),
            202,
        )

    @app.route("/update-analysis", methods=["POST"])
    def update_analysis():
        """
        Enqueue a recompute-analytics task.
        Returns HTTP 202 immediately; the worker refreshes summaries.
        """
        try:
            publish_task("recompute_analytics", payload={})
        except Exception as exc:  # pylint: disable=broad-exception-caught
            return jsonify({"ok": False, "message": f"Could not enqueue task: {exc}"}), 503

        return (
            jsonify({"ok": True, "queued": True, "message": "Analytics recompute queued – refresh the page shortly."}),
            202,
        )

    @app.route("/scraping_status", methods=["GET"])
    def scraping_status():
        """
        Lightweight status endpoint.
        In the async model, status is managed by the worker;
        this endpoint always returns 'idle' from the web side.
        """
        return jsonify(
            {
                "is_running": False,
                "status_message": "Ready (tasks handled by worker)",
                "records_added": 0,
            }
        )

    return app


# Default app instance (used by run.py)
application = create_app()
