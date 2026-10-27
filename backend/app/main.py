from contextlib import asynccontextmanager

from fastapi import FastAPI
from neo4j import AsyncGraphDatabase

from app.api import health
from app.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.neo4j_driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password.get_secret_value()),
        connection_timeout=5.0,
    )
    yield
    await app.state.neo4j_driver.close()

app = FastAPI(title="DART ONTOLOGY GRAPH RAG", lifespan=lifespan)
app.include_router(health.router)