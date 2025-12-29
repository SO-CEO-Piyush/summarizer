import os

import dotenv

dotenv.load_dotenv()
PG_CONN_STR = os.getenv("PG_CONN_STR")
REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", 3600))
WORD_LIMIT = int(os.getenv("WORD_LIMIT", 10_000))
FILE_SIZE_LIMIT = int(os.getenv("FILE_SIZE_LIMIT", 2 * 1024 * 1024))  # 2 MB
