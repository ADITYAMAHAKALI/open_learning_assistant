def test_health_ping(client):
    resp = client.get("/api/v1/health/ping")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
