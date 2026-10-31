from typing import Annotated, Literal

import httpx
from fastapi import APIRouter, Depends, Request, Response
from neo4j import AsyncDriver
from pydantic import BaseModel

from app.config import Settings, get_settings

router = APIRouter(tags=["health"])


class DependencyStatus(BaseModel):
    ok: bool
    detail: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    neo4j: DependencyStatus
    ollama: DependencyStatus


async def check_neo4j(driver: AsyncDriver) -> DependencyStatus:
    try:
        info = await driver.get_server_info()
        return DependencyStatus(ok=True, detail=info.agent)
    except Exception as e:
        return DependencyStatus(ok=False, detail=str(e))


async def check_ollama(base_url: str) -> DependencyStatus:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(f"{base_url}/api/version")
            r.raise_for_status()

            return DependencyStatus(ok=True, detail=r.json()["version"])
    except Exception as e:
        return DependencyStatus(ok=False, detail=str(e))


@router.get("/health")
async def health(
    request: Request, response: Response, settings: Annotated[Settings, Depends(get_settings)]
) -> HealthResponse:
    driver = request.app.state.neo4j_driver
    base_url = settings.ollama_base_url

    neo4j_check = await check_neo4j(driver=driver)
    ollama_check = await check_ollama(base_url=base_url)

    if not (neo4j_check.ok and ollama_check.ok):
        response.status_code = 503

    return HealthResponse(
        status="ok" if neo4j_check.ok and ollama_check.ok else "degraded",
        neo4j=neo4j_check,
        ollama=ollama_check,
    )
