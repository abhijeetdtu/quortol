import json
from pathlib import Path

import pytest

from backend.app import create_app
from backend.features.short_form.infra.loader import clear_posts_cache


@pytest.fixture
def short_form_env(tmp_path, monkeypatch):
    data_dir = tmp_path / 'data' / 'short_form'
    media_dir = tmp_path / 'static' / 'short_form'
    images_dir = media_dir / 'images'
    videos_dir = media_dir / 'videos'

    data_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    videos_dir.mkdir(parents=True, exist_ok=True)

    # Valid image fixture for one post.
    (images_dir / 'post_001.jpg').write_bytes(b'\xff\xd8\xff')

    posts = [
        {
            'id': 'post-1',
            'text': 'IPL final thriller',
            'media_url': '/static/short_form/images/post_001.jpg',
            'video_url': None,
            'author': 'Desk',
            'timestamp': '2026-05-30T14:30:00Z',
            'tags': ['#ipl', '#final'],
            'created_at': '2026-05-30T14:25:00Z',
        },
        {
            'id': 'post-2',
            'text': 'Practice nets session',
            'media_url': '/static/short_form/images/missing.jpg',
            'video_url': None,
            'author': 'Coach Cam',
            'timestamp': '2026-05-30T13:00:00Z',
            'tags': ['#training'],
            'created_at': '2026-05-30T12:55:00Z',
        },
        {
            'id': 'post-3',
            'text': 'Team bus arrives at stadium',
            'media_url': None,
            'video_url': None,
            'author': 'Reporter',
            'timestamp': '2026-05-30T12:00:00Z',
            'tags': ['#ipl', '#arrival'],
            'created_at': '2026-05-30T11:58:00Z',
        },
    ]

    posts_path = data_dir / 'posts.json'
    posts_path.write_text(json.dumps(posts), encoding='utf-8')

    monkeypatch.setenv('SHORT_FORM_POSTS_JSON', str(posts_path))
    monkeypatch.setenv('SHORT_FORM_MEDIA_DIR', str(media_dir))
    monkeypatch.setenv('SHORT_FORM_MEDIA_URL_PREFIX', '/static/short_form/')
    monkeypatch.setenv('DATABASE_URI', 'sqlite:///:memory:')

    clear_posts_cache()
    yield {'posts_path': posts_path, 'media_dir': media_dir}
    clear_posts_cache()


@pytest.fixture
def client(short_form_env):
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()


def test_feed_pagination_contract(client):
    response = client.get('/api/short-form/feed?page=1&limit=2')
    assert response.status_code == 200

    payload = response.get_json()
    assert 'posts' in payload
    assert 'pagination' in payload
    assert 'available_tags' in payload
    assert payload['pagination']['current_page'] == 1
    assert payload['pagination']['posts_per_page'] == 2
    assert len(payload['posts']) == 2


def test_feed_supports_tag_and_keyword_filters(client):
    response = client.get('/api/short-form/feed?page=1&limit=20&tags=%23ipl&keyword=final')
    assert response.status_code == 200

    payload = response.get_json()
    assert len(payload['posts']) == 1
    assert payload['posts'][0]['id'] == 'post-1'


def test_post_detail_contract(client):
    response = client.get('/api/short-form/posts/post-1')
    assert response.status_code == 200

    payload = response.get_json()
    assert payload['post']['id'] == 'post-1'
    assert payload['post']['author'] == 'Desk'


def test_missing_media_keeps_post_visible_with_null_media(client):
    response = client.get('/api/short-form/feed?page=1&limit=20')
    payload = response.get_json()

    broken = next(post for post in payload['posts'] if post['id'] == 'post-2')
    assert broken['media_url'] is None


def test_old_short_form_endpoints_are_retired(client):
    assert client.get('/api/feed').status_code == 404
    assert client.get('/api/post/post-1').status_code == 404


def test_missing_json_returns_stable_empty_feed(monkeypatch, tmp_path):
    missing_path = tmp_path / 'does-not-exist.json'
    media_dir = tmp_path / 'static' / 'short_form'
    media_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv('SHORT_FORM_POSTS_JSON', str(missing_path))
    monkeypatch.setenv('SHORT_FORM_MEDIA_DIR', str(media_dir))
    monkeypatch.setenv('SHORT_FORM_MEDIA_URL_PREFIX', '/static/short_form/')
    monkeypatch.setenv('DATABASE_URI', 'sqlite:///:memory:')

    clear_posts_cache()
    app = create_app()
    app.config['TESTING'] = True
    test_client = app.test_client()

    response = test_client.get('/api/short-form/feed?page=1&limit=20')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['posts'] == []


def test_corrupt_json_returns_stable_empty_feed(monkeypatch, tmp_path):
    posts_path = tmp_path / 'posts.json'
    posts_path.write_text('{not-json', encoding='utf-8')
    media_dir = tmp_path / 'static' / 'short_form'
    media_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv('SHORT_FORM_POSTS_JSON', str(posts_path))
    monkeypatch.setenv('SHORT_FORM_MEDIA_DIR', str(media_dir))
    monkeypatch.setenv('SHORT_FORM_MEDIA_URL_PREFIX', '/static/short_form/')
    monkeypatch.setenv('DATABASE_URI', 'sqlite:///:memory:')

    clear_posts_cache()
    app = create_app()
    app.config['TESTING'] = True
    test_client = app.test_client()

    response = test_client.get('/api/short-form/feed?page=1&limit=20')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['posts'] == []
