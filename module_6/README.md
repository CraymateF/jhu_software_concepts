# Module 6 – Containerized Microservice Stack

This module runs the GradCafe analysis app as a 4-service Docker Compose stack:
- `db` (PostgreSQL)
- `rabbitmq` (task broker)
- `web` (Flask UI + publisher)
- `worker` (consumer + ETL)

## Project Structure

```text
module_6/
├── docker-compose.yml
├── setup.py
├── README.md
├── docs/
├── tests/
└── src/
    ├── web/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── run.py
    │   ├── publisher.py
    │   └── app/
    ├── worker/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── consumer.py
    │   └── etl/
    │       ├── incremental_scraper.py
    │       └── query_data.py
    ├── db/
    │   └── load_data.py
    └── data/
        └── applicant_data.json
```

## Run Instructions

From `module_6/`:

```bash
docker compose up --build
```

To run detached:

```bash
docker compose up --build -d
```

To stop:

```bash
docker compose down
```

To stop and remove DB volume:

```bash
docker compose down -v
```

## Ports

- Web UI: `http://localhost:8080`
- RabbitMQ Management UI: `http://localhost:15672`
- PostgreSQL: internal `5432` (container network)

## Docker Registry Links

Replace `<username>` with your DockerHub username:

- `docker.io/<username>/module_6-web:latest`
- `docker.io/<username>/module_6-worker:latest`

Example push commands:

```bash
docker build -t <username>/module_6-web:latest ./src/web
docker build -t <username>/module_6-worker:latest ./src/worker
docker push <username>/module_6-web:latest
docker push <username>/module_6-worker:latest
```

## Notes

- `docker-compose.yml` defines a named volume `pgdata` and health checks for `db` and `rabbitmq`.
- `src/data/applicant_data.json` is set to the LLM-cleaned applicant dataset.
- `web` publishes durable RabbitMQ messages; `worker` consumes with `prefetch_count=1`, ack/nack handling, and idempotent inserts.
