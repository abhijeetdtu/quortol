import json
import threading

import pytest

from backend.app import create_app
from backend.features.writer import routes
from backend.features.writer.service import WriterDependenciesUnavailable


@pytest.fixture
def writer_client(monkeypatch):
    monkeypatch.setenv('DATABASE_URI', 'sqlite:///:memory:')
    app = create_app(enable_dash=False)
    app.config.update(
        TESTING=True, WRITER_RATE_LIMIT_PER_MINUTE=100,
        WRITER_MAX_CONTEXT_CHARS=100, WRITER_MAX_CONCURRENT=1,
        WRITER_ANALYSIS_MAX_CHARS=100, WRITER_ANALYSIS_RATE_LIMIT_PER_MINUTE=100,
    )
    routes._requests.clear()
    routes._services.pop(id(app), None)
    routes._analysis_services.pop(id(app), None)
    routes._semaphores.pop(id(app), None)
    return app, app.test_client()


def _events(response):
    frames = response.get_data(as_text=True).strip().split('\n\n')
    return [json.loads(frame.removeprefix('data: ')) for frame in frames]


@pytest.mark.parametrize('available', [True, False])
def test_writer_status_has_stable_public_shape(writer_client, monkeypatch, available):
    _, client = writer_client
    monkeypatch.setattr(routes, 'writer_backend_available', lambda config: available)
    response = client.get('/api/writer/status')
    assert response.status_code == 200
    assert response.get_json() == {'available': available}


def test_writer_status_sanitizes_probe_failures(writer_client, monkeypatch):
    _, client = writer_client

    def fail(config):
        raise RuntimeError('secret upstream URL and credential')

    monkeypatch.setattr(routes, 'writer_backend_available', fail)
    response = client.get('/api/writer/status')
    assert response.status_code == 200
    assert response.get_json() == {'available': False}
    assert 'secret' not in response.get_data(as_text=True)


def test_public_autocomplete_still_works(writer_client, monkeypatch):
    _, client = writer_client
    monkeypatch.setattr(
        'backend.features.writer.service.WriterAutocompleteService.autocomplete',
        lambda *args, **kwargs: {'recommendations': ['next'], 'emotional_angles': ['playful']},
    )
    response = client.post('/api/writer/autocomplete', json={'prefix': 'Once'})
    assert response.status_code == 200
    assert response.get_json()['recommendations'] == ['next']


@pytest.mark.parametrize('payload', [
    {}, {'body': ''}, {'body': '   '}, {'body': 12}, {'title': 12, 'body': 'text'},
])
def test_analysis_stream_validates_payload(writer_client, payload):
    _, client = writer_client
    assert client.post('/api/writer/analyze/stream', json=payload).status_code == 400


def test_analysis_stream_rejects_excessive_draft(writer_client):
    _, client = writer_client
    response = client.post('/api/writer/analyze/stream', json={'title': '', 'body': 'x' * 101})
    assert response.status_code == 413


def test_analysis_stream_returns_ordered_events_and_headers(writer_client, monkeypatch):
    _, client = writer_client
    monkeypatch.setattr('backend.features.writer.analysis.WriterAnalysisService.check_dependencies', lambda self: None)
    monkeypatch.setattr(
        'backend.features.writer.analysis.WriterAnalysisService.stream',
        lambda self, title, body: iter([
            {'type': 'start', 'schema_version': '2.0'},
            {'type': 'block', 'block': {'id': 'depth', 'title': 'Depth', 'content': 'Plain prose'}},
            {'type': 'complete', 'completed_ids': ['depth'], 'failed_ids': []},
        ]),
    )
    response = client.post('/api/writer/analyze/stream', json={'title': 'Draft', 'body': 'Prose'})
    assert response.status_code == 200
    assert response.mimetype == 'text/event-stream'
    assert response.headers['Cache-Control'] == 'no-cache'
    assert response.headers['X-Accel-Buffering'] == 'no'
    assert [event['type'] for event in _events(response)] == ['start', 'block', 'complete']


def test_analysis_stream_sanitizes_partial_failure(writer_client, monkeypatch):
    _, client = writer_client
    monkeypatch.setattr('backend.features.writer.analysis.WriterAnalysisService.check_dependencies', lambda self: None)
    monkeypatch.setattr(
        'backend.features.writer.analysis.WriterAnalysisService.stream',
        lambda self, title, body: (_ for _ in ()).throw(ConnectionError('secret host')),
    )
    response = client.post('/api/writer/analyze/stream', json={'body': 'Prose'})
    text = response.get_data(as_text=True)
    assert 'secret' not in text
    assert 'ended unexpectedly' in text


def test_analysis_dependency_failure_is_pre_stream_json(writer_client, monkeypatch):
    _, client = writer_client
    def fail(self):
        raise WriterDependenciesUnavailable('secret dependency')
    monkeypatch.setattr('backend.features.writer.analysis.WriterAnalysisService.check_dependencies', fail)
    response = client.post('/api/writer/analyze/stream', json={'body': 'Prose'})
    assert response.status_code == 503
    assert response.is_json
    assert 'secret' not in response.get_data(as_text=True)


def test_analysis_rate_limit_counts_whole_stream_once(writer_client, monkeypatch):
    app, client = writer_client
    app.config['WRITER_ANALYSIS_RATE_LIMIT_PER_MINUTE'] = 1
    monkeypatch.setattr('backend.features.writer.analysis.WriterAnalysisService.check_dependencies', lambda self: None)
    monkeypatch.setattr(
        'backend.features.writer.analysis.WriterAnalysisService.stream',
        lambda self, title, body: iter([{'type': 'complete', 'completed_ids': [], 'failed_ids': []}]),
    )
    first = client.post('/api/writer/analyze/stream', json={'body': 'First'})
    first.get_data()
    response = client.post('/api/writer/analyze/stream', json={'body': 'Second'})
    assert response.status_code == 429
    assert response.headers['Retry-After'] == '60'


def test_analysis_releases_semaphore_after_stream_consumption(writer_client, monkeypatch):
    app, client = writer_client
    monkeypatch.setattr('backend.features.writer.analysis.WriterAnalysisService.check_dependencies', lambda self: None)
    monkeypatch.setattr(
        'backend.features.writer.analysis.WriterAnalysisService.stream',
        lambda self, title, body: iter([{'type': 'complete', 'completed_ids': [], 'failed_ids': []}]),
    )
    response = client.post('/api/writer/analyze/stream', json={'body': 'First'})
    response.get_data()
    semaphore = routes._semaphores[id(app)]
    assert semaphore.acquire(blocking=False)
    semaphore.release()


def test_analysis_busy_response_is_pre_stream_json(writer_client, monkeypatch):
    _, client = writer_client
    class BusySemaphore:
        def acquire(self, blocking=False): return False
    service = object()
    monkeypatch.setattr(routes, '_analysis_runtime', lambda: (service, BusySemaphore()))
    response = client.post('/api/writer/analyze/stream', json={'body': 'Prose'})
    assert response.status_code == 429
    assert response.is_json
