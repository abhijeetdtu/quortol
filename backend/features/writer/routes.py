"""Public API routes for writing autocomplete."""

from __future__ import annotations

from collections import defaultdict, deque
import logging
import threading
import time

from flask import Blueprint, Response, current_app, jsonify, request, stream_with_context

from .service import (
    WriterAutocompleteService,
    WriterDependenciesUnavailable,
    writer_backend_available,
)
from .analysis import WriterAnalysisService

writer_bp = Blueprint('writer', __name__, url_prefix='/api/writer')
_requests: dict[str, deque[float]] = defaultdict(deque)
_rate_lock = threading.Lock()
_services = {}
_analysis_services = {}
_semaphores = {}


def _client_ip() -> str:
    return request.remote_addr or 'unknown'


def _is_rate_limited(ip: str, limit: int) -> bool:
    now = time.monotonic()
    with _rate_lock:
        window = _requests[ip]
        while window and now - window[0] >= 60:
            window.popleft()
        if len(window) >= limit:
            return True
        window.append(now)
        return False


def _runtime():
    app_key = id(current_app._get_current_object())
    service = _services.get(app_key)
    if service is None:
        service = WriterAutocompleteService(current_app.config)
        _services[app_key] = service
    semaphore = _semaphores.get(app_key)
    if semaphore is None:
        semaphore = threading.BoundedSemaphore(current_app.config['WRITER_MAX_CONCURRENT'])
        _semaphores[app_key] = semaphore
    return service, semaphore


def _analysis_runtime():
    app_key = id(current_app._get_current_object())
    service = _analysis_services.get(app_key)
    if service is None:
        service = WriterAnalysisService(current_app.config)
        _analysis_services[app_key] = service
    _, semaphore = _runtime()
    return service, semaphore


@writer_bp.get('/status')
def status():
    """Report writer readiness without exposing upstream connection details."""
    try:
        available = writer_backend_available(current_app.config)
    except Exception:
        available = False
    return jsonify({'available': available})


@writer_bp.post('/autocomplete')
def autocomplete():
    started = time.monotonic()
    limit = current_app.config['WRITER_RATE_LIMIT_PER_MINUTE']
    if _is_rate_limited(_client_ip(), limit):
        response = jsonify({'error': 'Too many autocomplete requests. Please try again shortly.'})
        response.status_code = 429
        response.headers['Retry-After'] = '60'
        return response

    if request.content_length and request.content_length > current_app.config['WRITER_MAX_CONTEXT_CHARS'] * 2 + 1024:
        return jsonify({'error': 'Request is too large.'}), 413

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'A JSON request body is required.'}), 400
    prefix, suffix, count = data.get('prefix'), data.get('suffix', ''), data.get('count', 3)
    conditioning = data.get('conditioning', '')
    conditioning_depth = data.get('conditioning_depth', 0)
    base_recommendations = data.get('base_recommendations', [])
    if not isinstance(prefix, str) or not prefix.strip():
        return jsonify({'error': 'prefix must be a non-empty string.'}), 400
    if not isinstance(suffix, str):
        return jsonify({'error': 'suffix must be a string.'}), 400
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 5:
        return jsonify({'error': 'count must be an integer from 1 to 5.'}), 400
    if not isinstance(conditioning, str) or len(conditioning) > 200:
        return jsonify({'error': 'conditioning must be a string up to 200 characters.'}), 400
    if isinstance(conditioning_depth, bool) or not isinstance(conditioning_depth, int) or conditioning_depth < 0:
        return jsonify({'error': 'conditioning_depth must be a non-negative integer.'}), 400
    if not isinstance(base_recommendations, list) or not all(
        isinstance(value, str) for value in base_recommendations
    ):
        return jsonify({'error': 'base_recommendations must be an array of strings.'}), 400
    if conditioning and not base_recommendations:
        return jsonify({'error': 'base_recommendations are required with conditioning.'}), 400
    if len(base_recommendations) > 5 or any(len(value) > 1000 for value in base_recommendations):
        return jsonify({'error': 'base_recommendations are too large.'}), 413

    max_context = current_app.config['WRITER_MAX_CONTEXT_CHARS']
    if len(prefix) + len(suffix) > max_context:
        return jsonify({'error': 'Writing context is too large.'}), 413

    service, semaphore = _runtime()
    if not semaphore.acquire(blocking=False):
        response = jsonify({'error': 'Autocomplete is busy. Please retry shortly.'})
        response.status_code = 429
        response.headers['Retry-After'] = '2'
        return response

    status = 200
    try:
        result = service.autocomplete(prefix, suffix, count, conditioning, base_recommendations)
        return jsonify(result)
    except WriterDependenciesUnavailable:
        status = 503
        return jsonify({'error': 'Writing autocomplete is not installed on this server.'}), status
    except TimeoutError:
        status = 504
        return jsonify({'error': 'The autocomplete model timed out.'}), status
    except Exception as exc:
        message = str(exc).lower()
        if 'timeout' in message:
            status = 504
            error = 'The autocomplete model timed out.'
        elif 'loading' in message or '503' in message:
            status = 503
            error = 'The autocomplete model is still loading.'
        else:
            status = 502
            error = 'Could not reach the autocomplete model.'
        return jsonify({'error': error}), status
    finally:
        semaphore.release()
        logging.getLogger(__name__).info(
            'writer autocomplete status=%s count=%s prefix_chars=%s suffix_chars=%s '
            'cursor_ratio=%.3f conditioning_depth=%s duration_ms=%d',
            status,
            count,
            len(prefix),
            len(suffix),
            len(prefix) / max(len(prefix) + len(suffix), 1),
            conditioning_depth,
            (time.monotonic() - started) * 1000,
        )


@writer_bp.post('/analyze/stream')
def analyze_stream():
    started = time.monotonic()
    limit = current_app.config['WRITER_ANALYSIS_RATE_LIMIT_PER_MINUTE']
    rate_key = f"analysis:{_client_ip()}"
    if _is_rate_limited(rate_key, limit):
        response = jsonify({'error': 'Too many analysis requests. Please try again shortly.'})
        response.status_code = 429
        response.headers['Retry-After'] = '60'
        return response
    max_chars = current_app.config['WRITER_ANALYSIS_MAX_CHARS']
    if request.content_length and request.content_length > max_chars * 2 + 1024:
        return jsonify({'error': 'Request is too large.'}), 413
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'A JSON request body is required.'}), 400
    title, body = data.get('title', ''), data.get('body')
    if not isinstance(title, str):
        return jsonify({'error': 'title must be a string.'}), 400
    if not isinstance(body, str) or not body.strip():
        return jsonify({'error': 'body must be a non-empty string.'}), 400
    if len(title) + len(body) > max_chars:
        return jsonify({'error': 'Draft is too large to analyze.'}), 413
    service, semaphore = _analysis_runtime()
    if not semaphore.acquire(blocking=False):
        response = jsonify({'error': 'Writing analysis is busy. Please retry shortly.'})
        response.status_code = 429
        response.headers['Retry-After'] = '2'
        return response
    try:
        service.check_dependencies()
    except WriterDependenciesUnavailable:
        semaphore.release()
        return jsonify({'error': 'Writing analysis is not installed on this server.'}), 503

    @stream_with_context
    def generate():
        status = 200
        try:
            for event in service.stream(title, body):
                from .analysis import sse_event
                yield sse_event(event)
        except GeneratorExit:
            status = 499
            raise
        except Exception:
            status = 502
            from .analysis import sse_event
            yield sse_event({
                'type': 'step_error', 'id': 'analysis',
                'message': 'The analysis stream ended unexpectedly.',
            })
            yield sse_event({'type': 'complete', 'completed_ids': [], 'failed_ids': ['analysis']})
        finally:
            semaphore.release()
            logging.getLogger(__name__).info(
                'writer analysis stream status=%s title_chars=%s body_chars=%s duration_ms=%d',
                status, len(title), len(body), (time.monotonic() - started) * 1000,
            )

    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Connection'] = 'keep-alive'
    return response
