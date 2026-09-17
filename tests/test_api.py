from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}


def test_query_endpoint_returns_plan_and_results():
    with TestClient(app) as client:
        response = client.post("/query", params={"question": "How many tickets are currently open?"})
        assert response.status_code == 200
        payload = response.json()
        assert payload["plan"]["filters"][0]["value"] == "Open"
        assert payload["results"] == [{"value": 111}]
