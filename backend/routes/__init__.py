from .admin_routes import admin_bp
from .api_routes import api_bp
from .auth_routes import auth_bp
from .public_routes import public_bp

__all__ = ["public_bp", "admin_bp", "api_bp", "auth_bp"]
