"""Podcast feature package."""


def create_podcast_blueprints():
    """Factory for podcast API and public-feed blueprints."""
    from .api import podcast_api_bp, podcast_public_bp

    return podcast_api_bp, podcast_public_bp
