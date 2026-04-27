from config import REDIS_DB, REDIS_HOST, REDIS_PORT, WOLFRAM_CACHE_TTL_SECONDS

try:
    import redis
except ImportError:
    redis = None


def create_redis_client():
    if redis is None:
        return None
    try:
        client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        client.ping()
        return client
    except Exception:
        return None


redis_client = create_redis_client()


def get_cached_wolfram_answer(question: str):
    if redis_client is None:
        return None
    cache_key = f"wolfram:{question}"
    try:
        cached_value = redis_client.get(cache_key)
        if not cached_value:
            return None
        if isinstance(cached_value, bytes):
            return cached_value.decode("utf-8")
        return str(cached_value)
    except Exception:
        return None


def set_cached_wolfram_answer(question: str, answer: str) -> None:
    if redis_client is None:
        return
    cache_key = f"wolfram:{question}"
    try:
        redis_client.setex(cache_key, WOLFRAM_CACHE_TTL_SECONDS, answer)
    except Exception:
        return
