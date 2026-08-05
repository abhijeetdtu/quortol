"""Public writing autocomplete feature."""

from .routes import writer_bp


def create_writer_blueprint():
    return writer_bp
