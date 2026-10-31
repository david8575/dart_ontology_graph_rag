from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api import health as health_module
from app.api.health import DependencyStatus
from app.config import Settings, get_settings
from app.main import app


class FakeDriver:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    async def get_server_info(self) -> SimpleNamespace:
        if self.error:
            raise self.error
        return SimpleNamespace(agent="Neo4j/test")


def fake_settings() -> Settings:
    return Settings(
        neo4j_uri="bolt://test:7687",
        neo4j_user="neo4j",
        neo4j_password="test",
        ollama_base_url="http://test:11434",
        dart_api_key="test",
    )


@pytest.fixture
def client():
    app.dependency_overrides[get_settings] = fake_settings
    yield TestClient(app)
    app.dependency_overrides.clear()


def patch_ollama(monkeypatch, ok: bool) -> None:
    async def fake_check(base_url: str) -> DependencyStatus:
        return DependencyStatus(ok=ok, detail="test")

    monkeypatch.setattr(health_module, "check_ollama", fake_check)


def test_health_ok(client, monkeypatch):
    app.state.neo4j_driver = FakeDriver()
    patch_ollama(monkeypatch, ok=True)

    r = client.get("/health")

    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health_neo4j_down(client, monkeypatch):
    app.state.neo4j_driver = FakeDriver(error=RuntimeError("down"))
    patch_ollama(monkeypatch, ok=True)

    r = client.get("/health")

    assert r.status_code == 503
    assert r.json()["status"] == "degraded"
    assert r.json()["neo4j"]["ok"] is False


def test_health_ollama_down(client, monkeypatch):
    app.state.neo4j_driver = FakeDriver()
    patch_ollama(monkeypatch, ok=False)

    r = client.get("/health")

    assert r.status_code == 503
    assert r.json()["status"] == "degraded"
    assert r.json()["ollama"]["ok"] is False
