import os
from datetime import timedelta


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///quortol.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 7200))  # 2 hours in seconds
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=SESSION_TIMEOUT)
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:8080').split(',')
    
    # External agent timeout
    AGENT_API_TIMEOUT = int(os.environ.get('AGENT_API_TIMEOUT', 30))

    # Pokhi Wikipedia integration
    POKHI_WIKIPEDIA_LANG = os.environ.get('POKHI_WIKIPEDIA_LANG', 'en')
    POKHI_WIKIPEDIA_TIMEOUT = int(os.environ.get('POKHI_WIKIPEDIA_TIMEOUT', 8))
    POKHI_WIKIPEDIA_RETRIES = int(os.environ.get('POKHI_WIKIPEDIA_RETRIES', 2))
    POKHI_WIKIPEDIA_RETRY_DELAY = float(os.environ.get('POKHI_WIKIPEDIA_RETRY_DELAY', 0.25))
    POKHI_WIKIPEDIA_MAX_FEED_COUNT = int(os.environ.get('POKHI_WIKIPEDIA_MAX_FEED_COUNT', 20))
    POKHI_WIKIPEDIA_MAX_IMAGES = int(os.environ.get('POKHI_WIKIPEDIA_MAX_IMAGES', 8))
    POKHI_WIKIPEDIA_MAX_CONTENT_CHARS = int(os.environ.get('POKHI_WIKIPEDIA_MAX_CONTENT_CHARS', 8000))

    # Auth behavior
    REGISTRATION_ENABLED = _env_bool('REGISTRATION_ENABLED', default=False)
