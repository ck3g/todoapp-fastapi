from contextlib import asynccontextmanager

from fastapi import FastAPI

from todoapp.api.routers import auth, tasks
from todoapp.database.base import create_db_and_tables
from todoapp.models import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome!"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
