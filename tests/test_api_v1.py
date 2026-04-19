from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_v1() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_report_v1_has_summary() -> None:
    response = client.get("/api/v1/report")
    assert response.status_code == 200
    payload = response.json()
    assert "summary" in payload
    assert "sessions" in payload


def test_result_v1_has_expected_keys() -> None:
    response = client.get("/api/v1/result")
    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == {"final_sum", "valid_entries", "total_entries"}


def test_sessions_filters_v1() -> None:
    response = client.get("/api/v1/sessions", params={"department": "MDR", "valid_only": "true"})
    assert response.status_code == 200
    sessions = response.json()
    assert isinstance(sessions, list)
    assert all(session["department"] == "MDR" for session in sessions)
    assert all(session["valid_entries"] > 0 for session in sessions)


def test_session_not_found_v1() -> None:
    response = client.get("/api/v1/sessions/UNKNOWN-SESSION")
    assert response.status_code == 404
