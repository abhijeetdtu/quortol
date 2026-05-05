from flask import Blueprint, current_app, jsonify, request

from ..services.pokhi_wikipedia import (
    WikipediaService,
    WikipediaServiceError,
    WikipediaUnavailableError,
)

pokhi_wikipedia_bp = Blueprint("pokhi_wikipedia", __name__)
_wikipedia_service = None


def _error_response(message, status_code):
    return jsonify({"success": False, "data": None, "error": message}), status_code


def _get_service():
    global _wikipedia_service

    if _wikipedia_service is None:
        _wikipedia_service = WikipediaService(
            lang=current_app.config.get("POKHI_WIKIPEDIA_LANG", "en"),
            timeout=current_app.config.get("POKHI_WIKIPEDIA_TIMEOUT", 8),
            retries=current_app.config.get("POKHI_WIKIPEDIA_RETRIES", 2),
            retry_delay=current_app.config.get("POKHI_WIKIPEDIA_RETRY_DELAY", 0.25),
            max_images=current_app.config.get("POKHI_WIKIPEDIA_MAX_IMAGES", 8),
            max_content_chars=current_app.config.get("POKHI_WIKIPEDIA_MAX_CONTENT_CHARS", 8000),
        )

    return _wikipedia_service


@pokhi_wikipedia_bp.route("/page", methods=["POST"])
def get_wikipedia_page():
    payload = request.get_json(silent=True) or {}
    topic = str(payload.get("topic", "")).strip()
    if not topic:
        return _error_response("Field `topic` is required", 400)

    try:
        item = _get_service().fetch_page(topic)
        return jsonify({"success": True, "data": item, "error": None})
    except WikipediaUnavailableError as exc:
        return _error_response(str(exc), 503)
    except WikipediaServiceError as exc:
        return _error_response(str(exc), 502)
    except KeyError as exc:
        return _error_response(f"Wikipedia response missing field: {exc}", 502)
    except Exception as exc:  # pragma: no cover - defensive
        return _error_response(f"Unexpected error: {exc}", 500)


@pokhi_wikipedia_bp.route("/feed", methods=["POST"])
def get_wikipedia_feed():
    payload = request.get_json(silent=True) or {}
    count_raw = payload.get("count", 10)
    seed_topic = payload.get("seed_topic")
    seed_topic = seed_topic.strip() if isinstance(seed_topic, str) else None

    try:
        count = int(count_raw)
    except (TypeError, ValueError):
        return _error_response("Field `count` must be an integer", 400)

    max_count = int(current_app.config.get("POKHI_WIKIPEDIA_MAX_FEED_COUNT", 20))
    count = max(1, min(count, max_count))

    try:
        feed = _get_service().generate_feed(count=count, seed_topic=seed_topic)
        return jsonify({"success": True, "data": feed, "error": None})
    except WikipediaUnavailableError as exc:
        return _error_response(str(exc), 503)
    except WikipediaServiceError as exc:
        return _error_response(str(exc), 502)
    except KeyError as exc:
        return _error_response(f"Wikipedia response missing field: {exc}", 502)
    except Exception as exc:  # pragma: no cover - defensive
        return _error_response(f"Unexpected error: {exc}", 500)
