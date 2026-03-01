"""
Flask application for GradCafe database analysis – Module 6 (microservice edition).

Buttons (Pull Data / Update Analysis) publish tasks to RabbitMQ
and immediately return HTTP 202 "request queued" instead of doing
synchronous work.  The worker container processes those tasks.
"""
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
    # When loaded as the app/ package, __name__ == 'app' and root_path is
    # the app/ directory itself, so templates/ and static/ are direct children.
    app = Flask(__name__, template_folder="templates", static_folder="static")

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
        resp = render_template(
            "results.html",
            results=results,
            current_db=dbname,
            db_info=DATABASE_INFO,
        )
        from flask import make_response  # noqa: PLC0415  # pylint: disable=import-outside-toplevel
        response = make_response(resp)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        return response

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
            return jsonify(
                {"ok": False, "message": f"Could not enqueue task: {exc}"}
            ), 503

        return (
            jsonify(
                {
                    "ok": True,
                    "queued": True,
                    "message": (
                        "Scrape task queued – worker is running now; "
                        "UI will wait until completion."
                    ),
                }
            ),
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
            return jsonify(
                {"ok": False, "message": f"Could not enqueue task: {exc}"}
            ), 503

        return (
            jsonify(
                {
                    "ok": True,
                    "queued": True,
                    "message": "Analytics recompute queued – refresh the page shortly.",
                }
            ),
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

    @app.route("/worker_status", methods=["GET"])
    def worker_status():
        """
        Report the current database row count and last ingestion watermark.
        The frontend polls this to show a live status banner.
        """
        try:
            from query_data import get_db_connection  # noqa: PLC0415  # pylint: disable=import-outside-toplevel
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM gradcafe_main;")
            total_records = cur.fetchone()[0]

            cur.execute(
                "SELECT source, last_seen, updated_at FROM ingestion_watermarks "
                "ORDER BY updated_at DESC LIMIT 1;"
            )
            wm = cur.fetchone()

            cur.execute(
                "SELECT last_seen, updated_at FROM ingestion_watermarks WHERE source = %s;",
                ("gradcafe_scraped",),
            )
            scrape_wm = cur.fetchone()

            cur.execute(
                "SELECT last_seen, updated_at FROM ingestion_watermarks WHERE source = %s;",
                ("recompute",),
            )
            recompute_wm = cur.fetchone()
            cur.close()
            conn.close()

            return jsonify({
                "ok": True,
                "total_records": total_records,
                "last_updated": wm[2].isoformat() if wm else None,
                "last_seen": wm[1] if wm else None,
                "last_source": wm[0] if wm else None,
                "scrape_last_seen": scrape_wm[0] if scrape_wm else None,
                "scrape_last_updated": (
                    scrape_wm[1].isoformat() if scrape_wm else None
                ),
                "recompute_last_seen": recompute_wm[0] if recompute_wm else None,
                "recompute_last_updated": (
                    recompute_wm[1].isoformat() if recompute_wm else None
                ),
                "seeded": total_records > 0,
            })
        except Exception as exc:  # pylint: disable=broad-exception-caught
            return jsonify(
                {"ok": False, "error": str(exc), "total_records": 0, "seeded": False}
            )

    return app


# Default app instance (used by run.py)
application = create_app()

