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

- Repository: `https://hub.docker.com/repository/docker/fadetobiack/module_6/general`
- Web image tag: `fadetobiack/module_6:v1-web`
- Worker image tag: `fadetobiack/module_6:v1-worker`

Push commands:

```bash
docker build -t fadetobiack/module_6:v1-web ./src/web
docker build -t fadetobiack/module_6:v1-worker ./src/worker
docker push fadetobiack/module_6:v1-web
docker push fadetobiack/module_6:v1-worker
```

Pull commands:

```bash
docker pull fadetobiack/module_6:v1-web
docker pull fadetobiack/module_6:v1-worker
```

## Notes

- `docker-compose.yml` defines a named volume `pgdata` and health checks for `db` and `rabbitmq`.
- `src/data/applicant_data.json` is set to the LLM-cleaned applicant dataset.
- `web` publishes durable RabbitMQ messages; `worker` consumes with `prefetch_count=1`, ack/nack handling, and idempotent inserts.
