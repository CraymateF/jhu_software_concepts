"""
RabbitMQ worker / consumer for the GradCafe application.

Connects to RabbitMQ, declares durable AMQP entities, and processes
incoming task messages.  Supported task kinds:
  - scrape_new_data       → handle_scrape_new_data(conn, payload)
  - recompute_analytics   → handle_recompute_analytics(conn, payload)

Design constraints:
  - basic_qos(prefetch_count=1)  – one message at a time
  - Database transaction per message; commit → ack, exception → nack
  - Watermark table tracks the "last_seen" key for idempotent scraping
"""
import json
import logging
import os
import sys
import time
import re
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import execute_values
import pika
from dotenv import load_dotenv

# ── ETL helpers ─────────────────────────────────────────────────────────────
# The etl/ directory sits alongside consumer.py in the worker context.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "etl"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "etl", "module_2_code"))

from scrape import GradCafeScraper          # noqa: E402  (added to sys.path above)
from clean import GradCafeDataCleaner       # noqa: E402

load_dotenv(override=False)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [worker] %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

# ── AMQP constants ───────────────────────────────────────────────────────────
EXCHANGE    = "tasks"
QUEUE       = "tasks_q"
ROUTING_KEY = "tasks"

# ── Database connection ──────────────────────────────────────────────────────

def get_db_connection():
    """Return a new psycopg2 connection using DATABASE_URL or DB_* env vars."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)

    conn_params = {
        "dbname": os.getenv("DB_NAME", "gradcafe"),
        "user":   os.getenv("DB_USER"),
        "host":   os.getenv("DB_HOST"),
        "port":   os.getenv("DB_PORT", "5432"),
    }
    db_password = os.getenv("DB_PASSWORD")
    if db_password:
        conn_params["password"] = db_password
    return psycopg2.connect(**conn_params)


def ensure_watermark_table(conn):
    """Create the ingestion_watermarks table if it does not exist."""
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ingestion_watermarks (
            source      TEXT PRIMARY KEY,
            last_seen   TEXT,
            updated_at  TIMESTAMPTZ DEFAULT now()
        );
    """)
    conn.commit()
    cur.close()


# ── Data helpers shared with load_data ──────────────────────────────────────

def _parse_date(date_str):
    """Return a datetime.date object, or None if unparseable."""
    if not date_str or not isinstance(date_str, str):
        return None
    date_str = date_str.strip()
    for fmt in (
        "%d/%m/%Y",   # 31/01/2026  (legacy gradcafe)
        "%m/%d/%Y",   # 01/31/2026  (US format)
        "%B %d, %Y",  # January 31, 2026
        "%Y-%m-%d",   # 2026-01-31  (ISO)
        "%y-%m-%d",   # 26-01-31    (2-digit year ISO)
        "%d-%m-%Y",   # 31-01-2026
        "%d-%m-%y",   # 31-01-26
    ):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            pass
    return None


def _extract_numeric(value_str, prefix=""):
    if not value_str:
        return None
    if isinstance(value_str, (int, float)):
        return float(value_str)
    if isinstance(value_str, str):
        try:
            return float(value_str.replace(prefix, "").strip())
        except ValueError:
            return None
    return None


def _clean_str(value):
    if isinstance(value, str):
        return value.replace("\x00", "").replace("\u0000", "")
    return value


def _record_to_row(r):
    """Convert a raw scraped/cleaned dict to a gradcafe_main insert tuple."""
    is_new_format = any(k in r for k in ("applicant_status", "citizenship", "semester_year_start"))
    if is_new_format:
        combined_program  = r.get("program", "")
        comments          = r.get("comments")
        date_added        = _parse_date(r.get("date_added"))
        url               = r.get("url")
        status_map        = {
            "Accepted": "Accepted", "Rejected": "Rejected",
            "Interview": "Interview", "Wait listed": "Wait listed", "Waitlisted": "Wait listed",
        }
        status            = status_map.get(r.get("applicant_status", ""), r.get("applicant_status"))
        term              = r.get("semester_year_start")
        citizenship_map   = {"American": "American", "International": "International",
                             "U": "American", "I": "International"}
        us_or_intl        = citizenship_map.get(r.get("citizenship", ""), r.get("citizenship"))
        gpa               = _extract_numeric(r.get("gpa"), "GPA")
        gre               = _extract_numeric(r.get("gre"), "GRE")
        gre_v_raw         = r.get("gre_v")
        gre_v             = float(gre_v_raw) if isinstance(gre_v_raw, (int, float)) else None
        gre_aw_raw        = r.get("gre_aw")
        gre_aw            = float(gre_aw_raw) if isinstance(gre_aw_raw, (int, float)) else None
        degree            = r.get("masters_or_phd")
        llm_program       = r.get("llm-generated-program")
        llm_university    = r.get("llm-generated-university")
    else:
        acceptance_date = r.get("Acceptance Date")
        rejection_date  = r.get("Rejection Date")
        if acceptance_date:
            status, date_added = "Accepted", _parse_date(acceptance_date)
        elif rejection_date:
            status, date_added = "Rejected", _parse_date(rejection_date)
        else:
            status, date_added = None, None
        university       = r.get("University", "")
        program_name     = r.get("Program", "")
        combined_program = (f"{university} - {program_name}"
                            if university and program_name else university or program_name)
        comments         = r.get("Notes")
        url              = r.get("Url")
        term             = r.get("Term")
        us_or_intl       = r.get("US/International")
        gpa              = r.get("GPA") if isinstance(r.get("GPA"), (int, float)) else None
        gre              = r.get("GRE General") if isinstance(r.get("GRE General"), (int, float)) else None
        gre_v            = r.get("GRE Verbal") if isinstance(r.get("GRE Verbal"), (int, float)) else None
        gre_aw           = r.get("GRE Analytical Writing") if isinstance(r.get("GRE Analytical Writing"), (int, float)) else None
        degree           = r.get("Degree")
        llm_program      = r.get("LLM Generated Program")
        llm_university   = r.get("LLM Generated University") or r.get("University")

    return (
        _clean_str(combined_program),
        _clean_str(comments) if isinstance(comments, str) else None,
        date_added,
        _clean_str(url) if isinstance(url, str) else None,
        _clean_str(status),
        _clean_str(term) if isinstance(term, str) else None,
        _clean_str(us_or_intl) if isinstance(us_or_intl, str) else None,
        gpa, gre, gre_v, gre_aw,
        _clean_str(degree) if isinstance(degree, str) else None,
        _clean_str(llm_program),
        _clean_str(llm_university),
        json.dumps(r).replace("\x00", "").replace("\\u0000", ""),
    )


def seed_from_json():
    """
    On first startup, populate gradcafe_main from SEED_JSON if the table is empty.

    SEED_JSON is set via the docker-compose worker environment to the path of
    the mounted applicant_data.json (e.g. /data/applicant_data.json).
    Skipped silently when the file is absent or the table already has rows.
    """
    seed_file = os.getenv("SEED_JSON")
    if not seed_file or not os.path.exists(seed_file):
        log.info("seed_from_json: SEED_JSON not set or file not found (%s) – skipping", seed_file)
        return

    conn = get_db_connection()
    try:
        ensure_watermark_table(conn)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM gradcafe_main;")
        count = cur.fetchone()[0]
        if count > 0:
            log.info("seed_from_json: table already has %d rows – skipping seed", count)
            # Ensure there is at least one watermark row so /worker_status shows a timestamp
            cur.execute("SELECT COUNT(*) FROM ingestion_watermarks WHERE source = %s;", ("seed_json",))
            if cur.fetchone()[0] == 0:
                cur.execute(
                    """INSERT INTO ingestion_watermarks (source, last_seen, updated_at)
                       VALUES (%s, %s, now())
                       ON CONFLICT (source) DO UPDATE
                       SET last_seen = EXCLUDED.last_seen, updated_at = now();""",
                    ("seed_json", seed_file),
                )
                conn.commit()
                log.info("seed_from_json: wrote watermark for pre-existing seed")
            cur.close()
            return

        log.info("seed_from_json: loading from %s …", seed_file)
        with open(seed_file, encoding="utf-8") as f:
            raw = f.read().strip()

        # Support both JSON array and newline-delimited JSON
        try:
            records = json.loads(raw)
            if not isinstance(records, list):
                records = [records]
        except json.JSONDecodeError:
            records = []
            for line in raw.splitlines():
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

        if not records:
            log.warning("seed_from_json: no records parsed from %s", seed_file)
            cur.close()
            return

        target_table = os.getenv("TARGET_TABLE", "gradcafe_main")
        id_key       = os.getenv("ID_KEY", "url")

        # Dedup against existing rows. Records may use either lower-case 'url'
        # (new format) or 'Url' (legacy module_2 format), so try all casings.
        def _get_id(record):
            return (record.get(id_key)
                    or record.get(id_key.capitalize())
                    or record.get(id_key.upper()))

        cur.execute(f"SELECT {id_key} FROM {target_table} WHERE {id_key} IS NOT NULL;")
        existing = {row[0] for row in cur.fetchall()}
        records = [r for r in records if _get_id(r) and _get_id(r) not in existing]

        if not records:
            log.info("seed_from_json: all records already present – skipping")
            cur.close()
            return

        rows = []
        for r in records:
            try:
                rows.append(_record_to_row(r))
            except Exception as row_exc:  # pylint: disable=broad-exception-caught
                log.warning("seed_from_json: skipping record – %s", row_exc)

        INSERT_SQL = f"""INSERT INTO {target_table} (
                   program, comments, date_added, url, status, term, us_or_international,
                   gpa, gre, gre_v, gre_aw, degree, llm_generated_program,
                   llm_generated_university, raw_data
               ) VALUES %s
               ON CONFLICT DO NOTHING"""

        # Insert in batches of 500 so one bad row only skips that batch,
        # not the entire dataset.
        BATCH = 500
        inserted = 0
        for start in range(0, len(rows), BATCH):
            batch = rows[start : start + BATCH]
            try:
                execute_values(cur, INSERT_SQL, batch)
                conn.commit()
                inserted += len(batch)
            except Exception as batch_exc:  # pylint: disable=broad-exception-caught
                log.warning("seed_from_json: batch %d-%d failed (%s) – trying row-by-row",
                            start, start + len(batch), batch_exc)
                conn.rollback()
                for row in batch:
                    try:
                        execute_values(cur, INSERT_SQL, [row])
                        conn.commit()
                        inserted += 1
                    except Exception as single_exc:  # pylint: disable=broad-exception-caught
                        log.warning("seed_from_json: skipping row – %s", single_exc)
                        conn.rollback()

        log.info("seed_from_json: inserted %d / %d rows from %s", inserted, len(rows), seed_file)

        # Update watermark so /worker_status shows a meaningful timestamp
        cur.execute(
            """INSERT INTO ingestion_watermarks (source, last_seen, updated_at)
               VALUES (%s, %s, now())
               ON CONFLICT (source) DO UPDATE
               SET last_seen = EXCLUDED.last_seen, updated_at = now();""",
            ("seed_json", seed_file),
        )
        conn.commit()
        cur.close()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        log.exception("seed_from_json: failed – %s", exc)
        conn.rollback()
    finally:
        conn.close()


# ── Task handlers ────────────────────────────────────────────────────────────

def handle_scrape_new_data(conn, payload: dict):
    """
    Scrape new GradCafe entries and insert only those not yet in the DB.

    Reads last_seen watermark from ingestion_watermarks and advances it
    to the newest date_added value after a successful commit.
    """
    cur = conn.cursor()
    source    = "gradcafe_scraped"
    since     = payload.get("since")
    max_pages = int(payload.get("max_pages", 2))

    def _touch_scrape_watermark(last_seen_value=None):
        cur.execute(
            """INSERT INTO ingestion_watermarks (source, last_seen, updated_at)
               VALUES (%s, %s, now())
               ON CONFLICT (source) DO UPDATE
               SET last_seen  = COALESCE(EXCLUDED.last_seen, ingestion_watermarks.last_seen),
                   updated_at = now();""",
            (source, last_seen_value),
        )

    # ── Read watermark ───────────────────────────────────────────────────────
    if since is None:
        cur.execute("SELECT last_seen FROM ingestion_watermarks WHERE source = %s;", (source,))
        row   = cur.fetchone()
        since = row[0] if row else None
    log.info("scrape_new_data: since=%s  max_pages=%s", since, max_pages)

    # ── Scrape ───────────────────────────────────────────────────────────────
    scraper  = GradCafeScraper()
    raw_data = scraper.scrape_data(max_pages=max_pages)
    if not raw_data:
        log.info("scrape_new_data: scraper returned no data")
        _touch_scrape_watermark(since)
        conn.commit()
        cur.close()
        return

    # ── Clean ────────────────────────────────────────────────────────────────
    import tempfile  # pylint: disable=import-outside-toplevel
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(raw_data, tmp, ensure_ascii=False)
        tmp_path = tmp.name
    cleaner      = GradCafeDataCleaner()
    cleaned_data = cleaner.clean_data(tmp_path)
    os.unlink(tmp_path)
    if not cleaned_data:
        log.info("scrape_new_data: no data after cleaning")
        _touch_scrape_watermark(since)
        conn.commit()
        cur.close()
        return

    # ── Get existing URLs to skip duplicates ─────────────────────────────────
    cur.execute("SELECT url FROM gradcafe_main WHERE url IS NOT NULL;")
    existing_urls = {row[0] for row in cur.fetchall()}

    new_records = [r for r in cleaned_data if r.get("Url") not in existing_urls]
    if not new_records:
        log.info("scrape_new_data: no new records after dedup")
        _touch_scrape_watermark(since)
        conn.commit()
        cur.close()
        return

    # ── Insert with ON CONFLICT safety ───────────────────────────────────────
    rows = [_record_to_row(r) for r in new_records]
    execute_values(
        cur,
        """INSERT INTO gradcafe_main (
               program, comments, date_added, url, status, term, us_or_international,
               gpa, gre, gre_v, gre_aw, degree, llm_generated_program,
               llm_generated_university, raw_data
           ) VALUES %s
           ON CONFLICT DO NOTHING""",
        rows,
    )

    # ── Advance watermark ────────────────────────────────────────────────────
    cur.execute(
        "SELECT MAX(date_added::text) FROM gradcafe_main WHERE url IS NOT NULL;"
    )
    max_date = cur.fetchone()[0]
    if max_date:
        _touch_scrape_watermark(max_date)
    else:
        _touch_scrape_watermark(since)

    conn.commit()
    cur.close()
    log.info("scrape_new_data: inserted %d new records; watermark → %s", len(rows), max_date)


def handle_recompute_analytics(conn, payload: dict):  # pylint: disable=unused-argument
    """
    Refresh analytics summaries used by the UI.

    Runs ANALYZE on gradcafe_main so the query planner uses
    up-to-date statistics, then writes a watermark so the frontend
    can detect when the recompute has finished.
    """
    cur = conn.cursor()
    log.info("recompute_analytics: running ANALYZE gradcafe_main")
    cur.execute("ANALYZE gradcafe_main;")
    cur.execute(
        """INSERT INTO ingestion_watermarks (source, last_seen, updated_at)
           VALUES ('recompute', now()::text, now())
           ON CONFLICT (source) DO UPDATE
           SET last_seen = EXCLUDED.last_seen, updated_at = now();"""
    )
    conn.commit()
    cur.close()
    log.info("recompute_analytics: complete")


# ── Task dispatch map ────────────────────────────────────────────────────────
TASK_MAP = {
    "scrape_new_data":     handle_scrape_new_data,
    "recompute_analytics": handle_recompute_analytics,
}


# ── Consumer loop ────────────────────────────────────────────────────────────

def _open_channel():
    """Connect to RabbitMQ and return (connection, channel)."""
    url    = os.environ["RABBITMQ_URL"]
    params = pika.URLParameters(url)
    conn   = pika.BlockingConnection(params)
    ch     = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    ch.queue_declare(queue=QUEUE, durable=True)
    ch.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=ROUTING_KEY)
    ch.basic_qos(prefetch_count=1)
    return conn, ch


def on_message(ch, method, _properties, body):
    """
    Callback invoked for each RabbitMQ message.

    Opens a fresh DB connection per message, routes by kind, commits on
    success, nacks (no requeue) on failure.
    """
    delivery_tag = method.delivery_tag
    try:
        message = json.loads(body)
        kind    = message.get("kind", "")
        payload = message.get("payload", {})
        log.info("Received task: kind=%s ts=%s", kind, message.get("ts"))

        handler = TASK_MAP.get(kind)
        if handler is None:
            log.warning("Unknown task kind '%s' – discarding.", kind)
            ch.basic_nack(delivery_tag=delivery_tag, requeue=False)
            return

        db_conn = get_db_connection()
        try:
            ensure_watermark_table(db_conn)
            handler(db_conn, payload)
            db_conn.commit()
            ch.basic_ack(delivery_tag=delivery_tag)
            log.info("Task '%s' completed and acked.", kind)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            log.exception("Handler '%s' failed: %s – rolling back and nacking.", kind, exc)
            db_conn.rollback()
            ch.basic_nack(delivery_tag=delivery_tag, requeue=False)
        finally:
            db_conn.close()

    except Exception as exc:  # pylint: disable=broad-exception-caught
        log.exception("Failed to decode/dispatch message: %s", exc)
        ch.basic_nack(delivery_tag=delivery_tag, requeue=False)


def run():
    """Start the long-running consumer with automatic reconnect."""
    seed_from_json()
    retry_delay = 5
    while True:
        try:
            log.info("Connecting to RabbitMQ …")
            rmq_conn, ch = _open_channel()
            ch.basic_consume(queue=QUEUE, on_message_callback=on_message)
            log.info("Worker ready – waiting for tasks on '%s'.", QUEUE)
            ch.start_consuming()
        except pika.exceptions.AMQPConnectionError as exc:
            log.error("RabbitMQ connection lost: %s – retrying in %ss", exc, retry_delay)
            time.sleep(retry_delay)
        except KeyboardInterrupt:
            log.info("Shutting down.")
            break


if __name__ == "__main__":
    run()
