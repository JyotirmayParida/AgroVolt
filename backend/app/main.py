import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import crop, solar, irrigation, weather, farms
from app.database.db import create_tables

logger = logging.getLogger("agrovolt")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create DB tables automatically so init_db.py is optional."""
    logger.info("AgroVolt starting up — creating database tables...")
    try:
        create_tables()
        logger.info("Database tables ready.")
    except Exception as e:
        logger.error("Database initialization failed: %s", e)
    yield
    logger.info("AgroVolt shutting down.")


app = FastAPI(
    title="AgroVolt API",
    description="Smart Agrovoltaic Management System API",
    version="1.0.0",
    lifespan=lifespan,
)

import os

# CORS — allow local React dev server, production frontend, and optional env overrides
cors_origins_env = os.getenv("CORS_ORIGINS", "")
custom_origins = [orig.strip() for orig in cors_origins_env.split(",") if orig.strip()]

default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://agrovolt.vercel.app",
]
allowed_origins = list(dict.fromkeys(default_origins + custom_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crop.router,       prefix="/api/crop",       tags=["Crop Yield"])
app.include_router(solar.router,      prefix="/api/solar",      tags=["Solar Forecast"])
app.include_router(irrigation.router, prefix="/api/irrigation", tags=["Irrigation"])
app.include_router(weather.router,    prefix="/api/weather",    tags=["Weather"])
app.include_router(farms.router,      prefix="/api/farms",      tags=["Farms"])


@app.get("/")
def root():
    return {"message": "AgroVolt API is running ✅", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}
