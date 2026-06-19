<img width="1743" height="644" alt="Screenshot from 2026-06-19 17-26-27" src="https://github.com/user-attachments/assets/8aac7ae1-cecd-4727-a7eb-2d0873096203" />


# WorkFinder


An automated ETL pipeline that collects job/training postings from multiple career sites, stores them in a versioned PostgreSQL database, and sends a daily digest of new postings to Telegram. Orchestrated with **Apache Airflow**, with a data lake layer in **MinIO** (S3-compatible) and a **Metabase** dashboard for analysis.

Built to track open IT training, internship, and job postings (e.g. EPAM, SoftServe) automatically instead of checking each career site manually.

## What it does

```
fetch sources → save raw JSON to MinIO → parse & normalize → upsert into PostgreSQL → notify (Telegram) → analyze (Metabase)
```

1. **Fetch** — pulls raw data from each configured source's career API on a daily schedule.
2. **Store raw** — saves the untouched JSON response to MinIO (S3-compatible object storage) and records file metadata (bucket, key, etag, status) in PostgreSQL for traceability.
3. **Parse & normalize** — source-specific adapters convert each provider's raw JSON into a single unified `Course` data model.
4. **Upsert with history** — instead of overwriting records, each course is versioned: when a posting changes, the old row is marked inactive (`active_to` is set) and a new active row is inserted. Active rows are always the ones with `active_to IS NULL`, enforced with a partial unique index on `(source, source_id)`.
5. **Notify** — once a day, a digest of newly added postings is sent to a Telegram chat.
6. **Analyze** — PostgreSQL is connected to Metabase for ad-hoc dashboards and trend analysis over time.

## Architecture

- **Orchestration**: Apache Airflow 3 (TaskFlow API), with dynamic task mapping (`.expand()`) to fetch all configured sources in parallel, each with its own retries and timeout.
- **Object storage**: MinIO, accessed via `boto3`'s S3 client — raw JSON payloads are kept as the source of truth.
- **Database**: PostgreSQL via SQLAlchemy ORM, with two core tables:
  - `file_record` — tracks every ingested file (`pending → processing → done/error`)
  - `courses` — the normalized, versioned postings table
- **Adapters**: a small `BaseAdapter` interface (`adapters/`) so adding a new source means writing one `parse()` method, not touching the rest of the pipeline.
- **Notifications**: Telegram Bot API.
- **Dashboards**: Metabase, connected directly to the PostgreSQL instance.
- **Containerization**: the entire stack (Airflow webserver, scheduler, dag-processor, PostgreSQL ×2, MinIO, Metabase) runs via Docker Compose for fully reproducible local development.

## Tech stack

Python · Apache Airflow 3 · PostgreSQL · SQLAlchemy · MinIO (S3 API) · boto3 · Docker / Docker Compose · Metabase · Telegram Bot API · curl_cffi

## Project structure

```
adapters/        # Source-specific parsers (EPAM, SoftServe, ...) implementing BaseAdapter
core/            # DB session, ORM models, repositories, settings
dags/            # Airflow DAG definitions
storage/         # MinIO client + pending-file processing logic
notify/          # Telegram digest / notification logic
utils/           # Shared utilities (logging, etc.)
fetch.py         # Source fetching + raw file persistence
docker-compose.yml
Dockerfile       # Airflow image with project dependencies
```

## Pipeline flow (Airflow DAG)

```python
sources = get_sources()                          # read configured source URLs from env
fetch_task = fetch_one_source.expand(source=sources)  # fetch all sources in parallel
load_task = load_all_to_db()                      # parse + upsert pending files into Postgres
notify_task = notify_new_courses_task()            # send Telegram digest

fetch_task >> load_task >> notify_task
```

Runs daily on a schedule (`30 8 * * *`), with per-source retries (`retries=3`, 2-minute delay) so a single failing source doesn't block the rest of the pipeline.

## Data model highlights

- **Idempotent ingestion**: each raw file is tracked by S3 key + etag, with a status field, so re-runs and partial failures are safe to retry.
- **Versioned records, not overwrites**: course postings keep history instead of being mutated in place — useful for tracking when a posting opened, changed, or closed over time.
- **Source-agnostic core**: the database and notification layers don't know anything about EPAM or SoftServe specifically — they only deal with the unified `Course` model produced by the adapters.

## Running locally

```bash
docker compose up -d
```

This spins up Airflow (webserver on `:8081`), PostgreSQL, pgAdmin (`:8080`), MinIO (`:9000` API / `:9001` console), and Metabase (`:3000`).

## Possible extensions

- Add new sources by implementing a new `BaseAdapter` subclass
- Swap the daily schedule for near-real-time polling
- Add data-quality checks before upsert (schema validation, deduplication thresholds)
