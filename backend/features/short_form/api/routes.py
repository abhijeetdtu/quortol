"""Short-form feed API endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..domain.filter import filter_posts, paginate_posts
from ..infra.config import get_short_form_config
from ..infra.loader import get_post_by_id, load_posts
from ..infra.validators import validate_media_url, validate_video_duration


short_form_bp = Blueprint("short_form", __name__, url_prefix="/short-form")


def _sanitize_post_media(post):
    """Keep post visible even when one media file is broken."""
    payload = post.to_dict()

    if payload.get("media_url"):
        valid, _ = validate_media_url(payload["media_url"])
        if not valid:
            payload["media_url"] = None

    if payload.get("video_url"):
        valid, _ = validate_video_duration(payload["video_url"])
        if not valid:
            payload["video_url"] = None

    return payload


@short_form_bp.get("/feed")
def get_feed():
    config = get_short_form_config()

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", config.default_page_size, type=int)

    if page is None or page < 1:
        return (
            jsonify(
                {
                    "error": "Invalid query parameters",
                    "details": {"message": "Page must be >= 1"},
                }
            ),
            400,
        )

    if limit is None or limit < 1 or limit > config.max_page_size:
        return (
            jsonify(
                {
                    "error": "Invalid query parameters",
                    "details": {
                        "message": f"Limit must be between 1 and {config.max_page_size}"
                    },
                }
            ),
            400,
        )

    tags = request.args.getlist("tags")
    keyword = request.args.get("keyword", "").strip()

    posts = load_posts()
    filtered_posts = filter_posts(
        posts,
        tags=tags if tags else None,
        keyword=keyword if keyword else None,
    )

    paginated_posts, pagination = paginate_posts(filtered_posts, page=page, limit=limit)
    post_payloads = [_sanitize_post_media(post) for post in paginated_posts]

    available_tags = sorted({tag for post in filtered_posts for tag in post.tags})

    return (
        jsonify(
            {
                "posts": post_payloads,
                "pagination": pagination,
                "empty_state": len(post_payloads) == 0,
                "available_tags": available_tags,
            }
        ),
        200,
    )


@short_form_bp.get("/posts/<string:post_id>")
def get_post(post_id: str):
    post = get_post_by_id(post_id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    payload = _sanitize_post_media(post)
    return jsonify({"post": payload}), 200
