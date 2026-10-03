import os
from datetime import date
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, Float, Date
from sqlalchemy.orm import sessionmaker, declarative_base

# Build the connection string from environment variables —
# these come from docker-compose.yml, never hardcoded here
DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Table definition — SQLAlchemy creates this automatically on startup
class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    log_date = Column(Date, default=date.today)
    water_ml = Column(Integer, default=0)
    steps = Column(Integer, default=0)
    sleep_hours = Column(Float, default=0)
    target_weight_kg = Column(Float, nullable=True)

Base.metadata.create_all(bind=engine)   # creates the table if missing

app = FastAPI(title="tracker-service")

class LogEntry(BaseModel):
    water_ml: int = Field(0, ge=0)
    steps: int = Field(0, ge=0)
    sleep_hours: float = Field(0, ge=0, le=24)
    target_weight_kg: float | None = Field(None, gt=0)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/log")
def create_log(entry: LogEntry):
    db = SessionLocal()
    row = Log(log_date=date.today(), **entry.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    db.close()
    return {"id": row.id, "log_date": str(row.log_date), **entry.model_dump()}

@app.get("/logs")
def list_logs():
    db = SessionLocal()
    rows = db.query(Log).order_by(Log.id.desc()).limit(20).all()
    db.close()
    return [
        {
            "id": r.id, "log_date": str(r.log_date), "water_ml": r.water_ml,
            "steps": r.steps, "sleep_hours": r.sleep_hours,
            "target_weight_kg": r.target_weight_kg,
        } for r in rows
    ]
