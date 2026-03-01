"""
RabbitMQ publisher for the GradCafe web service.

Publishes task messages to the 'tasks' exchange / 'tasks_q' queue
so the worker can process them asynchronously.
"""
import json
import os
from datetime import datetime, timezone

import pika

EXCHANGE = "tasks"
QUEUE = "tasks_q"
ROUTING_KEY = "tasks"


def _open_channel():
    """
    Open a RabbitMQ connection and channel, declaring durable AMQP entities.

    Returns:
        (connection, channel) pair.  Callers are responsible for closing
        the connection in a finally block.
    """
    url = os.environ["RABBITMQ_URL"]
    params = pika.URLParameters(url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    # Idempotent declarations – safe to call multiple times
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    ch.queue_declare(queue=QUEUE, durable=True)
    ch.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=ROUTING_KEY)

    return conn, ch


def publish_task(
    kind: str,
    payload: dict | None = None,
    headers: dict | None = None,
) -> None:
    """
    Publish a task message to the RabbitMQ tasks exchange.

    The message body is a compact JSON object with keys:
      - kind    task type identifier (e.g. 'scrape_new_data')
      - ts      UTC ISO-8601 timestamp
      - payload arbitrary dict (defaults to {})

    Messages are persistent (delivery_mode=2) so they survive broker restarts.

    Args:
        kind:    Task kind string.
        payload: Optional dict of task-specific parameters.
        headers: Optional AMQP message headers.

    Raises:
        Exception: Re-raised on any publish failure so the caller can return 503.
    """
    body = json.dumps(
        {
            "kind": kind,
            "ts": datetime.now(timezone.utc).isoformat(),
            "payload": payload or {},
        },
        separators=(",", ":"),
    ).encode("utf-8")

    conn, ch = _open_channel()
    try:
        ch.basic_publish(
            exchange=EXCHANGE,
            routing_key=ROUTING_KEY,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,          # persistent message
                content_type="application/json",
                headers=headers or {},
            ),
            mandatory=False,
        )
    finally:
        conn.close()
