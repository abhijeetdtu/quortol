"""Short-form feature package."""

from .api.routes import short_form_bp


def create_short_form_blueprint():
    """Factory for the short-form feature blueprint."""
    return short_form_bp
