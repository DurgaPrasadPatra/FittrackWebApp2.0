import os
import json
from datetime import date
from fastapi import FastAPI
from sqlalchemy import create_engine, text
import redis

DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 60))

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

app = FastAPI(title="summary-worker")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/summary/today")
def summary_today():
    today = str(date.today())
    cache_key = f"summary:{today}"

    # 1. Check Redis first (the fast path)
    cached = r.get(cache_key)
    if cached:
        data = json.loads(cached)
        data["source"] = "cache"
        return data

    # 2. Cache miss — compute the summary from Postgres directly
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT
                    COALESCE(SUM(water_ml), 0) AS total_water_ml,
                    COALESCE(SUM(steps), 0)    AS total_steps,
                    COALESCE(AVG(sleep_hours), 0) AS avg_sleep_hours,
                    COUNT(*) AS entries
                FROM logs
                WHERE log_date = :today
            """),
            {"today": today},
        ).mappings().first()

    summary = {
        "date": today,
        "total_water_ml": row["total_water_ml"],
        "total_steps": row["total_steps"],
        "avg_sleep_hours": round(float(row["avg_sleep_hours"]), 1),
        "entries": row["entries"],
        "source": "database",
    }

    # 3. Store the result in Redis so the NEXT request is fast,
    # automatically expiring after CACHE_TTL_SECONDS
    r.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(summary))
    return summary

@app.get("/streak")
def streak():
    # Demonstrates Redis as a fast counter store.
    # Increments once per calendar day, no matter how many times called.
    today = str(date.today())
    last_seen_key = "streak:lastseen"
    counter_key = "streak:count"

    last_seen = r.get(last_seen_key)
    if last_seen != today:
        r.incr(counter_key)
        r.set(last_seen_key, today)

    count = int(r.get(counter_key) or 0)
    return {"streak_days": count}
