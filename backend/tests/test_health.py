from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_healthz():
    response = client.get("/api/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz():
    response = client.get("/api/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
