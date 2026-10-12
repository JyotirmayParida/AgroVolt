import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import (
    Column, DateTime, Float, ForeignKey, Integer, String, create_engine,
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

load_dotenv()

IS_VERCEL = os.getenv("VERCEL") == "1"
DATABASE_URL = os.getenv("DATABASE_URL")

if IS_VERCEL and not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be configured for Vercel; SQLite is local-only.")

DATABASE_URL = DATABASE_URL or "sqlite:///./agrovolt.db"

# Supabase's pooler may provide the legacy postgres:// scheme.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL.removeprefix("postgres://")

# Use check_same_thread only for SQLite
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine_options = {"connect_args": connect_args}

# Vercel functions are serverless; let Supavisor manage transaction pooling.
if IS_VERCEL and DATABASE_URL.startswith("postgresql://"):
    engine_options["poolclass"] = NullPool

engine = create_engine(DATABASE_URL, **engine_options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Modern SQLAlchemy 2.0 declarative base."""
    pass


# ─── ORM Models ──────────────────────────────────────────────────────────────

class Farm(Base):
    __tablename__ = "farms"
    id             = Column(Integer, primary_key=True, index=True)
    name           = Column(String(100))
    location       = Column(String(200))
    latitude       = Column(Float)
    longitude      = Column(Float)
    panel_count    = Column(Integer)
    crop_type      = Column(String(50))
    area_hectares  = Column(Float)
    created_at     = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Prediction(Base):
    __tablename__ = "predictions"
    id                    = Column(Integer, primary_key=True, index=True)
    farm_id               = Column(Integer, ForeignKey("farms.id"))
    predicted_yield       = Column(Float)
    predicted_solar_kwh   = Column(Float)
    irrigation_recommendation = Column(String(50))
    timestamp             = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SensorData(Base):
    __tablename__ = "sensor_data"
    id            = Column(Integer, primary_key=True, index=True)
    farm_id       = Column(Integer, ForeignKey("farms.id"))
    soil_moisture = Column(Float)
    temperature   = Column(Float)
    shading_pct   = Column(Float)
    timestamp     = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def get_db():
    """Dependency to get DB session in routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
