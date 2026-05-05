# Auth utilities for Flask

from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

login_manager = LoginManager()

class UserMixin:
    """Mixin for User model with password handling"""
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
