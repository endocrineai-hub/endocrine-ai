from flask import Flask, session

from .config import Config
from .models.db import init_db
from .routes import admin_bp, api_bp, auth_bp, public_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db()
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_user_context():
        return {
            "is_user_logged_in": bool(session.get("user_id")),
            "user_name": session.get("user_name", ""),
            "is_admin_logged_in": bool(session.get("is_admin")),
        }

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
