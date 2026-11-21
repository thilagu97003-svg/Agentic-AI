import redis
from sqlalchemy import text
from app.config import settings
from app.db.session import engine, Base
from app.db import models  # noqa

Base.metadata.create_all(bind=engine)
with engine.connect() as c:
    print("Postgres OK:", c.execute(text("select 1")).scalar())

r = redis.from_url(settings.REDIS_URL)
print("Redis OK:", r.ping())