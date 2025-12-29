import hashlib
import typing
import logging
import redis
from src.config import REDIS_CACHE_TTL

logger = logging.getLogger(__name__)
client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_key(url: typing.Optional[str], text: typing.Optional[str], custom_instructions: typing.Optional[str]) -> str:
    key_parts = []
    if url:
        key_parts.append(url)
    if text:
        key_parts.append(text)
    if custom_instructions:
        key_parts.append(custom_instructions)
    key = hashlib.sha256("".join(key_parts).encode()).hexdigest()
    logger.debug(f"generated cache key: {key}")
    return key

def set_cache(key: str, result: str):
    logger.info(f"caching result with key: {key}, ttl: {REDIS_CACHE_TTL}s")
    client.set(key, result, ex=REDIS_CACHE_TTL)

def get_cache(key: str) -> typing.Optional[str]:
    result = client.get(key)
    if result:
        logger.info(f"cache hit for key: {key}")
    else:
        logger.info(f"cache miss for key: {key}")
    return result
