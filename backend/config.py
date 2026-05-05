import os
from datetime import timedelta

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
