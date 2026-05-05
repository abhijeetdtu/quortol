import pytest

from backend.app import create_app
import backend.routes.pokhi_wikipedia as pokhi_route_module
from backend.services.pokhi_wikipedia import WikipediaServiceError, WikipediaUnavailableError


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REGISTRATION_ENABLED = True
    POKHI_WIKIPEDIA_MAX_FEED_COUNT = 20


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app
    pokhi_route_module._wikipedia_service = None


@pytest.fixture
def client(app):
    return app.test_client()


def test_page_requires_topic(client):
    response = client.post("/api/pokhi/wikipedia/page", json={})
    assert response.status_code == 400
    payload = response.get_json()
    assert payload["success"] is False
    assert payload["error"] == "Field `topic` is required"


def test_page_success(client):
    class StubService:
        def fetch_page(self, topic):
            return {
                "topic": topic,
                "title": "Test Title",
                "summary": "Summary",
                "content": "Content",
                "images": [],
                "source_url": "https://example.com",
                "retrieved_at": "2026-01-01T00:00:00+00:00",
            }

    pokhi_route_module._wikipedia_service = StubService()

    response = client.post("/api/pokhi/wikipedia/page", json={"topic": "OpenAI"})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["error"] is None
    assert payload["data"]["title"] == "Test Title"


def test_feed_count_validation(client):
    response = client.post("/api/pokhi/wikipedia/feed", json={"count": "oops"})
    assert response.status_code == 400
    payload = response.get_json()
    assert payload["success"] is False
    assert payload["error"] == "Field `count` must be an integer"


def test_feed_count_clamps_to_max(client):
    recorded = {"count": None}

    class StubService:
        def generate_feed(self, count=10, seed_topic=None):
            recorded["count"] = count
            return {"items": [], "count": 0, "requested_count": count, "seed_topic": seed_topic}

    pokhi_route_module._wikipedia_service = StubService()

    response = client.post("/api/pokhi/wikipedia/feed", json={"count": 999, "seed_topic": "space"})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert recorded["count"] == 20
    assert payload["data"]["requested_count"] == 20


def test_feed_maps_upstream_service_error(client):
    class StubService:
        def generate_feed(self, count=10, seed_topic=None):
            raise WikipediaServiceError("Upstream failed")

    pokhi_route_module._wikipedia_service = StubService()

    response = client.post("/api/pokhi/wikipedia/feed", json={"count": 5})
    assert response.status_code == 502
    payload = response.get_json()
    assert payload["success"] is False
    assert payload["error"] == "Upstream failed"


def test_page_maps_unavailable_dependency(client):
    class StubService:
        def fetch_page(self, topic):
            raise WikipediaUnavailableError("Dependency missing")

    pokhi_route_module._wikipedia_service = StubService()

    response = client.post("/api/pokhi/wikipedia/page", json={"topic": "OpenAI"})
    assert response.status_code == 503
    payload = response.get_json()
    assert payload["success"] is False
    assert payload["error"] == "Dependency missing"

