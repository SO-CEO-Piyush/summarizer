import fastapi
import os
import logging
from scalar_fastapi import get_scalar_api_reference
from src.db import create_job, create_job_with_result, init_pool
from src.db import get_result as db_get_result
from src.db import get_status as db_get_status
from src.models import SummaryRequest
from src.cache import cache_key, get_cache, set_cache

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = fastapi.FastAPI()


@app.on_event("startup")
async def startup():
    await init_pool()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        scalar_proxy_url="https://proxy.scalar.com",
    )


@app.post("/submit")
async def submit(request: SummaryRequest):
    logger.info(f"received submit request: url={request.url}, text_len={len(request.text) if request.text else 0}")
    key = cache_key(request.url, request.text, request.custom_instructions)
    cached_result = get_cache(key)
    if cached_result:
        logger.info("cache hit, creating job with cached result")
        job_id = await create_job_with_result(request.url, request.text, request.custom_instructions, cached_result)
        return {"job_id": job_id, "is_cached": True}
    logger.info("cache miss, creating new job")
    job_id = await create_job(request.url, request.text, request.custom_instructions)
    return {"job_id": job_id, "is_cached": False}


@app.get("/status/{job_id}")
async def get_status(job_id: int):
    status = await db_get_status(job_id)
    if not status:
        raise fastapi.HTTPException(status_code=404, detail="job not found")
    return {"status": status}


@app.get("/result/{job_id}")
async def get_result(job_id: int):
    status, result, processing_time_ms = await db_get_result(job_id)
    if not status:
        raise fastapi.HTTPException(status_code=404, detail="job not found")
    if status == "todo" or status == "in_progress":
        raise fastapi.HTTPException(status_code=400, detail="job not completed yet")
    if status == "failed":
        raise fastapi.HTTPException(status_code=503, detail="job failed")
    if not result:
        raise fastapi.HTTPException(status_code=500, detail="result is null")
    return {"result": result, "processing_time_ms": processing_time_ms}
