from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import run_migrations
from app.routes import pages, api


@asynccontextmanager
async def lifespan(app):
    run_migrations()
    yield


app = FastAPI(
    title="Veerless Kanban",
    lifespan=lifespan,
    root_path="/kanban/supplier-risk-tool",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(pages.router)
app.include_router(api.router)
