# for registering router

from fastapi import FastAPI
from app.api.health import router as health_router
from app.db import engine
from app.models import Base #imports model so meta data exists

app = FastAPI(title="Stock Watch API")
app.include_router(health_router)

@app.on_event("startup")
def on_startup():
    # create tables if they don't exist
    Base.metadata.create_all(bind=engine)