import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_schedule_scraping_job():
    payload = {
        "target_urls": ["https://example.com/item1", "https://example.com/item2"],
        "proxy_tier": "rotating_residential"
    }
    res = client.post("/api/v1/jobs/collect", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["target_count"] == 2
    assert "job_id" in data

    # Verify query status
    job_id = data["job_id"]
    status_res = client.get(f"/api/v1/jobs/{job_id}")
    assert status_res.status_code == 200
    assert len(status_res.json()["items"]) == 2
