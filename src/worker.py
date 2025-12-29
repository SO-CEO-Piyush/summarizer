import asyncio
import os
import tempfile
import requests
import logging
import time
from urllib.parse import urlparse

import dotenv

from src.ai import AiSummarizer
from src.db import get_next_todo, init_pool, update_result, update_status
from src.parse import Parser
from src.scraper import scrape
from src.cache import cache_key, set_cache
from src.docs import extract_text
from src.config import WORD_LIMIT, FILE_SIZE_LIMIT

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()
parser = Parser()
ai_summarizer = AiSummarizer()

DOC_EXTENSIONS = ['.pdf', '.pptx', '.ppt', '.docx', '.doc', '.txt', '.xlsx', '.xls']

def is_document_url(url: str) -> bool:
    parsed = urlparse(url)
    path = parsed.path.lower().rstrip('/')
    if not path:
        return False
    path_ext = os.path.splitext(path)[1]
    return path_ext in DOC_EXTENSIONS

async def process_job(job_id: int, url: str, text: str, custom_instructions: str):
    logger.info(f"processing job {job_id}")
    start_time = time.perf_counter()
    try:
        await update_status(job_id, "in_progress")
        if url:
            logger.info(f"processing url: {url}")
            if is_document_url(url):
                logger.info("detected document url, downloading...")
                response = requests.get(url)
                logger.info(f"downloaded {len(response.content)} bytes")
                if len(response.content) > FILE_SIZE_LIMIT:
                    logger.error(f"file size {len(response.content)} exceeds limit {FILE_SIZE_LIMIT}")
                    raise ValueError(f"file size {len(response.content)} bytes exceeds limit of {FILE_SIZE_LIMIT} bytes")
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(url)[1]) as tmp:
                    tmp.write(response.content)
                    tmp_path = tmp.name
                logger.info(f"saved to temp file: {tmp_path}")
                content = extract_text(tmp_path)
                os.unlink(tmp_path)
                logger.info("temp file deleted")
            else:
                logger.info("processing as web page")
                html = scrape(url)
                content = parser.parse(html)
        else:
            logger.info("processing raw text")
            content = text
        word_count = len(content.split())
        logger.info(f"content: {len(content)} characters, {word_count} words")
        if word_count > WORD_LIMIT:
            logger.error(f"word count {word_count} exceeds limit {WORD_LIMIT}")
            raise ValueError(f"content has {word_count} words, exceeds limit of {WORD_LIMIT} words")
        logger.info("generating summary...")
        summary = ai_summarizer.summarize(content, custom_instructions)
        logger.info(f"summary generated: {len(summary)} characters")
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)
        await update_result(job_id, "success", summary, processing_time_ms)
        key = cache_key(url, text, custom_instructions)
        set_cache(key, summary)
        logger.info(f"job {job_id} completed successfully in {processing_time_ms}ms")
    except Exception as e:
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)
        logger.error(f"job {job_id} failed after {processing_time_ms}ms: {str(e)}", exc_info=True)
        await update_result(job_id, "failed", str(e), processing_time_ms)


async def main():
    logger.info("worker starting...")
    await init_pool()
    logger.info("database pool initialized")
    while True:
        job_id, url, text, custom_instructions = await get_next_todo()
        if job_id:
            logger.info(f"found job {job_id} to process")
            await process_job(job_id, url, text, custom_instructions)
        else:
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
