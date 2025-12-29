import asyncpg
from src.config import PG_CONN_STR

pool = None

async def init_pool():
    global pool
    pool = await asyncpg.create_pool(PG_CONN_STR)

async def create_job(url: str = None, text: str = None, custom_instructions: str = None) -> int:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("INSERT INTO jobs (url, text, status, custom_instructions) VALUES ($1, $2, 'todo', $3) RETURNING id", url, text, custom_instructions)
        return row['id']

async def create_job_with_result(url: str = None, text: str = None, custom_instructions: str = None, result: str = None) -> int:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("INSERT INTO jobs (url, text, status, custom_instructions, result) VALUES ($1, $2, 'success', $3, $4) RETURNING id", url, text, custom_instructions, result)
        return row['id']

async def get_status(job_id: int) -> str:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT status FROM jobs WHERE id = $1", job_id)
        return row['status'] if row else None

async def get_result(job_id: int) -> tuple:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT status, result, processing_time_ms FROM jobs WHERE id = $1", job_id)
        return (row['status'], row['result'], row['processing_time_ms']) if row else (None, None, None)

async def get_next_todo() -> tuple:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            UPDATE jobs SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP
            WHERE id = (
                SELECT id FROM jobs
                WHERE status = 'todo'
                ORDER BY created_at
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            )
            RETURNING id, url, text, custom_instructions
        """)
        return (row['id'], row['url'], row['text'], row['custom_instructions']) if row else (None, None, None, None)

async def update_status(job_id: int, status: str):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE jobs SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2", status, job_id)

async def update_result(job_id: int, status: str, result: str, processing_time_ms: int = None):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE jobs SET status = $1, result = $2, processing_time_ms = $3, updated_at = CURRENT_TIMESTAMP WHERE id = $4", status, result, processing_time_ms, job_id)
