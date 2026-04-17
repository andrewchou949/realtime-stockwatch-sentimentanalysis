import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.alerts import router as alerts_router
from app.api.dev import router as dev_router
from app.api.health import router as health_router
from app.api.prices import router as prices_router
from app.api.refresh import router as refresh_router
from app.api.watchlist import router as watchlist_router
from app.db import engine
from app.models import Base  # imports model so meta data exists

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Stock Watch API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(watchlist_router)
app.include_router(prices_router)
app.include_router(alerts_router)
app.include_router(refresh_router)
app.include_router(dev_router)


@app.get("/", include_in_schema=False)
def read_dashboard():
    return {
        "service": "stock-watch-api",
        "frontend": "Run the Vite app from v0/frontend on http://127.0.0.1:5173",
        "docs": "/docs",
        "dev_tools_enabled": os.getenv("STOCK_WATCH_ENABLE_DEV_TOOLS", "true").strip().lower()
        in {"1", "true", "yes", "on"},
    }
