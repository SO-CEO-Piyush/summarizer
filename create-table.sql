
DO $$ BEGIN
    CREATE TYPE STATUS AS ENUM ('todo', 'in_progress', 'success', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS JOBS (
    id SERIAL PRIMARY KEY,
    url TEXT,
    text TEXT,
    status STATUS NOT NULL,
    result TEXT,
    custom_instructions TEXT,
    processing_time_ms INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_jobs_status ON JOBS(status);