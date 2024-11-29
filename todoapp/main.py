from fastapi import FastAPI
from todoapp.api.routers import tasks

app = FastAPI()
app.include_router(tasks.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome!"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
