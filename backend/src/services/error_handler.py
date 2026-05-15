"""Centralized error handling and logging infrastructure."""

import logging
import sys
from typing import Any, Dict

from flask import jsonify


def setup_error_handler(app: Any) -> None:
    """Configure centralized error handling for Flask app.

    Args:
        app: Flask application instance.
    """

    @app.errorhandler(400)
    def bad_request(error: Any) -> Any:
        """Handle 400 Bad Request errors."""
        return jsonify({
            "error": "Bad Request",
            "message": str(error) if hasattr(error, 'description') else "Invalid request",
        }), 400

    @app.errorhandler(404)
    def not_found(error: Any) -> Any:
        """Handle 404 Not Found errors."""
        return jsonify({
            "error": "Not Found",
            "message": "The requested resource was not found",
        }), 404

    @app.errorhandler(500)
    def internal_error(error: Any) -> Any:
        """Handle 500 Internal Server Error."""
        logging.getLogger(__name__).error("Internal server error: %s", str(error))
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
        }), 500


def setup_logging(level: str = "INFO") -> None:
    """Configure logging infrastructure.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def log_simulation_error(match_id: str, error: Exception) -> None:
    """Log simulation failure with context.

    Args:
        match_id: UUID of the failed simulation.
        error: Exception that caused the failure.
    """
    logger = logging.getLogger(__name__)
    logger.error(
        "Simulation failed for match_id=%s: %s",
        match_id,
        str(error),
        exc_info=True,
    )
