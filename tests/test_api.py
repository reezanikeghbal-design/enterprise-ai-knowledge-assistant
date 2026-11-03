from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app


def test_health_is_public():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_operational_endpoint_rejects_missing_api_key():
    app.dependency_overrides[get_settings] = lambda: Settings(api_key="test-secret")
    try:
        response = TestClient(app).get("/documents")
        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_operational_endpoint_rejects_invalid_api_key():
    app.dependency_overrides[get_settings] = lambda: Settings(api_key="test-secret")
    try:
        response = TestClient(app).get("/documents", headers={"X-API-Key": "wrong"})
        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_operational_endpoint_accepts_valid_api_key():
    app.dependency_overrides[get_settings] = lambda: Settings(api_key="test-secret")
    try:
        response = TestClient(app).get("/documents", headers={"X-API-Key": "test-secret"})
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()


def test_operational_endpoint_fails_closed_when_api_key_unconfigured():
    app.dependency_overrides[get_settings] = lambda: Settings(api_key="")
    try:
        response = TestClient(app).get("/documents", headers={"X-API-Key": "anything"})
        assert response.status_code == 503
    finally:
        app.dependency_overrides.clear()
