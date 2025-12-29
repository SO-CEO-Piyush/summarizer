## Setup

1. Start PostgreSQL:

```bash
podman run --name pg-main -e POSTGRES_PASSWORD=123456 -v pg-main-data:/var/lib/postgresql/data -p 5432:5432 -d docker.io/library/postgres
```

2. Start Redis:

```bash
podman run --name redis-main -p 6379:6379 -d docker.io/library/redis
```

3. Create database and table:

```bash
podman exec -it pg-main psql -U postgres -c "CREATE DATABASE piyush;"
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

API docs available at: [http://localhost:8000/scalar](http://localhost:8000/scalar)