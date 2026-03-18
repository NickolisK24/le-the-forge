from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)


def create_app(env: str = "development") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[env])

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    CORS(
        app,
        origins=[app.config["FRONTEND_URL"]],
        supports_credentials=True,
    )

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.builds import builds_bp
    from app.routes.craft import craft_bp
    from app.routes.ref import ref_bp
    from app.routes.profile import profile_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(builds_bp, url_prefix="/api/builds")
    app.register_blueprint(craft_bp, url_prefix="/api/craft")
    app.register_blueprint(ref_bp, url_prefix="/api/ref")
    app.register_blueprint(profile_bp, url_prefix="/api/profile")

    # Register CLI commands
    from app.utils.cli import register_commands
    register_commands(app)

    # Health check
    @app.get("/api/health")
    def health():
        return {"status": "ok", "env": env}

    return app