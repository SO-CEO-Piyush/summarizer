# Async Content Summarizer

## Overview

A service that accepts URLs or text, processes them asynchronously, and returns AI-generated summaries.
The system is designed with simplicity in mind, supporting asynchronous job processing, multi-worker architecture, caching, and document handling.

See [arch.md](arch.md) for detailed architecture information.

## Setup

1. PostgreSQL:
   
   Using NeonDB for PostgreSQL database. Ensure `PG_CONN_STR` in `.env` points to your NeonDB instance.

2. Start Redis:

```bash
podman run --name redis-main -p 6379:6379 -d docker.io/library/redis
```

3. Create database and table:

```bash
# Connect to your NeonDB instance using the connection string from .env
# Example: psql "postgres://user:pass@ep-xyz.region.aws.neon.tech/dbname?sslmode=require"
bash scripts/setup-db.sh
```

4. Add your OpenAI API key to `.env`

5. Install dependencies:

```bash
uv sync
```

## Run

Start the worker:

```bash
source .venv/bin/activate && python3 -m src.worker
```

Start the API server:

```bash
source .venv/bin/activate && uvicorn src.main:app --port 8000
```

### Start multiple workers (optional)

Multiple workers can be started for parallel processing:

```bash
# Terminal 1
python -m src.worker

# Terminal 2
python -m src.worker
```

API docs available at: [http://localhost:8000/scalar](http://localhost:8000/scalar)