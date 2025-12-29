# Async Content Summarizer

## Overview

A service that accepts URLs or text, processes them asynchronously, and returns AI-generated summaries.
The system supports asynchronous job processing, multi-worker architecture, caching, and document handling.

## System Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────────────────────────┐
│         FastAPI Application             │
│  ┌──────────┐  ┌──────────┐            │
│  │ /submit  │  │ /status  │            │
│  │ /result  │  │ /scalar  │            │
│  └──────────┘  └──────────┘            │
└────┬────────────────────────────────┬──┘
     │                                │
     │                                │
┌────▼─────┐                    ┌────▼─────┐
│  NeonDB  │                    │  Redis   │
│ Database │                    │  Cache   │
└────▲─────┘                    └────▲─────┘
     │                                │
     │                                │
┌────┴────────────────────────────────┴───┐
│         Background Workers              │
│  ┌──────────┐  ┌──────────┐             │
│  │ Worker 1 │  │ Worker 2 │  ...        │
│  └──────────┘  └──────────┘             │
└────┬────────────────────────────────────┘
     │
     │ External Services
     ▼
┌────────────────────────────────────────┐
│  • OpenAI API (Summarization)          │
│  • Spider CLI (Web Scraping)           │
│  • LangChain Unstructured (Document Processing)
└────────────────────────────────────────┘
```

## Database Schema

**JOBS Table**

- `id`: Primary key
- `url` / `text`: Input source (mutually exclusive)
- `status`: `todo`, `in_progress`, `success`, `failed`
- `result`: Summary or error message
- `processing_time_ms`: Duration in ms
- `custom_instructions`: Optional prompt instructions

```sql
CREATE TYPE STATUS AS ENUM ('todo', 'in_progress', 'success', 'failed');
CREATE TABLE JOBS (
    id SERIAL PRIMARY KEY,
    url TEXT,
    text TEXT,
    status STATUS NOT NULL,
    result TEXT,
    custom_instructions TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_jobs_status ON JOBS(status);
```

**Entity Relationship**

```
┌─────────────────────────────────────┐
│              JOBS                   │
├─────────────────────────────────────┤
│ PK  id                 SERIAL       │
│     url                TEXT         │
│     text               TEXT         │
│     status             STATUS       │
│     result             TEXT         │
│     custom_instructions TEXT        │
│     processing_time_ms INTEGER      │
│     created_at         TIMESTAMP    │
│     updated_at         TIMESTAMP    │
└─────────────────────────────────────┘
```

## Core Features

### 1. Processing Flow
1. **Submit**: Client posts URL/text via `/submit`.
2. **Cache Check**: Returns immediately if result exists (`is_cached: true`).
3. **Queue**: Creates job with status `todo`.
4. **Process**: Worker claims job, processes content, and saves result.

### 2. Multi-Worker Design
Workers concurrently claim jobs using atomic `FOR UPDATE SKIP LOCKED` to prevent race conditions. Each worker operates independently.

### 3. Caching
- **Redis**: Stores results with TTL (default 1h).
- **Key**: SHA256 hash of inputs.
- **Benefit**: Reduces API costs and latency.

### 4. Content Pipeline
- **Docs**: Downloads & extracts text (PDF, Office, etc.) via LangChain.
- **Web**: Scrapes HTML using Spider CLI, parses with BeautifulSoup.
- **Text**: Processes raw text directly.

**Pipeline Visualization**:
```
Input (URL or Text)
       │
       ▼
┌──────────────┐
│  URL Check   │ ──► Is Document? ──► Download ──► Extract Text
└──────────────┘
       │ No
       ▼
  Web Scraping ──► Parse HTML ───────────────────┐
                                                 │
                                                 ▼
                                          Validate Limits
                                                 │
                                                 ▼
                                          Summarize (OpenAI)
                                                 │
                                                 ▼
                                          Store & Cache
```

### 5. Validation
- **Size**: Max 2MB file size.
- **Length**: Max 10,000 words.
- **Type**: Checks extensions for supported formats.

### 6. Error Handling
- Failures are logged and stored with `status='failed'`.
- Processing time is recorded regardless of outcome.
- API returns 4xx/5xx codes as appropriate.

## API Endpoints

- **POST /submit**: Accepts `url` or `text`. Returns `job_id`.
- **GET /status/{id}**: Returns current status.
- **GET /result/{id}**: Returns summary & timing if successful.

## Components

- **config.py**: Env vars for DB, Redis, OpenAI, and limits.
- **db.py**: Asyncpg pool, job management queries.
- **cache.py**: Redis set/get operations.
- **scraper.py / parse.py / docs.py**: Content extraction logic.
- **ai.py**: OpenAI integration (GPT-4o-mini).
- **worker.py**: Background loop claiming and processing jobs.
- **main.py**: FastAPI server with validation and logging.
