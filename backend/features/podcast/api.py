"""Flask blueprints for podcast serving."""

from __future__ import annotations

from flask import Blueprint, Response, jsonify, send_file

from .config import get_podcast_config
from .repository import (
    get_podcast_episode,
    load_podcast_episodes,
    serialize_podcast_detail,
    serialize_podcast_summary,
)
from .rss import build_podcast_feed_xml


podcast_api_bp = Blueprint("podcast_api", __name__, url_prefix="/api/podcasts")
podcast_public_bp = Blueprint("podcast_public", __name__)


@podcast_api_bp.get("/")
def get_podcasts():
    config = get_podcast_config()
    payload = [serialize_podcast_summary(episode, config=config) for episode in load_podcast_episodes()]
    return jsonify({"podcasts": payload}), 200


@podcast_api_bp.get("/<string:slug>")
def get_podcast(slug: str):
    config = get_podcast_config()
    episode = get_podcast_episode(slug)
    if episode is None:
        return jsonify({"error": "Podcast episode not found"}), 404
    return jsonify({"podcast": serialize_podcast_detail(episode, config=config)}), 200


@podcast_api_bp.get("/<string:slug>/audio")
def get_podcast_audio(slug: str):
    episode = get_podcast_episode(slug)
    if episode is None:
        return jsonify({"error": "Podcast episode not found"}), 404
    return send_file(
        episode.audio_path,
        mimetype=episode.audio_mimetype,
        conditional=True,
        download_name=f"{episode.slug}.wav",
        as_attachment=False,
    )


@podcast_public_bp.get("/podcasts/rss.xml")
def get_podcast_feed():
    config = get_podcast_config()
    payload = build_podcast_feed_xml(load_podcast_episodes(), config=config)
    return Response(payload, mimetype="application/rss+xml")
