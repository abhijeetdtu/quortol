from datetime import datetime, timedelta

import pytest

from backend.app import create_app
from backend.extensions import db
from backend.models import BlogPost, Tag


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("DATABASE_URI", "sqlite:///:memory:")
    app = create_app(enable_dash=False)
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()
        baseline = datetime(2026, 1, 1)
        for index in range(25):
            db.session.add(
                BlogPost(
                    title=f"Post {index}",
                    slug=f"post-{index}",
                    content=f"Content {index}",
                    excerpt=f"Excerpt {index}",
                    published_at=baseline + timedelta(days=index),
                    updated_at=baseline + timedelta(days=index),
                )
            )
        db.session.commit()

    return app.test_client()


def test_paginated_blog_contract_and_stable_order(client):
    response = client.get("/api/blog/?page=2&limit=12")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["pagination"] == {
        "current_page": 2,
        "total_pages": 3,
        "total_posts": 25,
        "posts_per_page": 12,
    }
    assert len(payload["posts"]) == 12
    assert payload["posts"][0]["slug"] == "post-12"
    assert payload["posts"][-1]["slug"] == "post-1"


def test_final_and_out_of_range_blog_pages(client):
    final_payload = client.get("/api/blog/?page=3&limit=12").get_json()
    out_of_range = client.get("/api/blog/?page=4&limit=12").get_json()

    assert [post["slug"] for post in final_payload["posts"]] == ["post-0"]
    assert out_of_range["posts"] == []
    assert out_of_range["pagination"]["total_pages"] == 3


@pytest.mark.parametrize(
    "query",
    ["page=0&limit=12", "page=nope&limit=12", "page=1&limit=0", "page=1&limit=101"],
)
def test_invalid_blog_pagination_returns_400(client, query):
    assert client.get(f"/api/blog/?{query}").status_code == 400


def test_unpaginated_blog_response_remains_legacy_array(client):
    payload = client.get("/api/blog/").get_json()

    assert isinstance(payload, list)
    assert len(payload) == 25


@pytest.mark.parametrize(
    ("field", "value", "query"),
    [
        ("title", "A Nebula Field Guide", "NEBULA"),
        ("excerpt", "A story about quasars", "quasars"),
        ("content", "Markdown about pulsars", "pulsars"),
    ],
)
def test_blog_search_matches_text_fields_case_insensitively(client, field, value, query):
    with client.application.app_context():
        post = BlogPost.query.filter_by(slug="post-0").one()
        setattr(post, field, value)
        db.session.commit()

    payload = client.get("/api/blog/", query_string={"page": 1, "limit": 12, "q": query}).get_json()

    assert [post["slug"] for post in payload["posts"]] == ["post-0"]
    assert payload["pagination"]["total_posts"] == 1


def test_blog_search_matches_tags_and_paginates_filtered_results(client):
    with client.application.app_context():
        tag = Tag(name="Astronomy", slug="astronomy")
        for index in range(13):
            BlogPost.query.filter_by(slug=f"post-{index}").one().tags.append(tag)
        db.session.commit()

    payload = client.get(
        "/api/blog/", query_string={"page": 2, "limit": 12, "q": "astronomy"}
    ).get_json()

    assert payload["pagination"] == {
        "current_page": 2,
        "total_pages": 2,
        "total_posts": 13,
        "posts_per_page": 12,
    }
    assert [post["slug"] for post in payload["posts"]] == ["post-0"]


@pytest.mark.parametrize("query", ["%", "_", "\\"])
def test_blog_search_treats_sql_wildcards_as_literal_text(client, query):
    payload = client.get(
        "/api/blog/", query_string={"page": 1, "limit": 12, "q": query}
    ).get_json()

    assert payload["posts"] == []
    assert payload["pagination"]["total_posts"] == 0


def test_blank_blog_search_is_ignored(client):
    payload = client.get(
        "/api/blog/", query_string={"page": 1, "limit": 12, "q": "   "}
    ).get_json()

    assert payload["pagination"]["total_posts"] == 25
