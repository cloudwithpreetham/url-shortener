import pytest
from unittest.mock import patch, MagicMock

import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        yield client


@pytest.fixture
def mock_redis():
    with patch.object(app_module, "r") as mock_r:
        yield mock_r


def test_health_ok(client, mock_redis):
    mock_redis.ping.return_value = True
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["redis"] == "connected"


def test_health_redis_down(client, mock_redis):
    import redis
    mock_redis.ping.side_effect = redis.exceptions.ConnectionError
    resp = client.get("/health")
    assert resp.status_code == 503
    data = resp.get_json()
    assert data["status"] == "error"


def test_shorten_missing_url(client, mock_redis):
    resp = client.post("/shorten", json={})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_shorten_success(client, mock_redis):
    mock_redis.exists.return_value = False
    resp = client.post("/shorten", json={"url": "example.com"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert "code" in data
    assert data["long_url"] == "https://example.com"
    assert data["short_url"].endswith(data["code"])
    mock_redis.set.assert_called_once()


def test_shorten_preserves_scheme(client, mock_redis):
    mock_redis.exists.return_value = False
    resp = client.post("/shorten", json={"url": "http://example.com"})
    data = resp.get_json()
    assert data["long_url"] == "http://example.com"


def test_resolve_not_found(client, mock_redis):
    mock_redis.get.return_value = None
    resp = client.get("/abc123")
    assert resp.status_code == 404


def test_resolve_success(client, mock_redis):
    mock_redis.get.return_value = "https://example.com"
    resp = client.get("/abc123", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"] == "https://example.com"


def test_stats_not_found(client, mock_redis):
    mock_redis.get.return_value = None
    resp = client.get("/stats/abc123")
    assert resp.status_code == 404


def test_stats_success(client, mock_redis):
    mock_redis.get.return_value = "https://example.com"
    resp = client.get("/stats/abc123")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["code"] == "abc123"
    assert data["long_url"] == "https://example.com"
