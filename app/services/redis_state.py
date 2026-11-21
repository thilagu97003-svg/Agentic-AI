import json
import redis
from app.config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)


def load_session(session_id: str) -> dict:
    raw = r.get(f"session:{session_id}")
    return json.loads(raw) if raw else {}


def save_session(session_id: str, data: dict, ttl: int = 3600):
    r.setex(f"session:{session_id}", ttl, json.dumps(data))


def cache_get(key: str):
    raw = r.get(key)
    return json.loads(raw) if raw else None


def cache_set(key: str, value, ttl: int = 600):
    r.setex(key, ttl, json.dumps(value))