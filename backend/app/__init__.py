from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time

from config import config
from app.utils.logging import configure_logging

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

    configure_logging(app)

    # Data pipeline + registries
    from app.game_data.pipeline import GameDataPipeline
    from app.registries.skill_registry import SkillRegistry
    from app.registries.affix_registry import AffixRegistry

    pipeline = GameDataPipeline()
    pipeline.load_all()
    app.extensions["game_data"]      = pipeline
    app.extensions["skill_registry"] = SkillRegistry(pipeline.skills)
    app.extensions["affix_registry"] = AffixRegistry(pipeline.affixes)

    # Performance profiling middleware
    @app.before_request
    def _start_timer():
        from flask import g
        g.start_time = time.perf_counter()

    @app.after_request
    def _add_response_time(response):
        from flask import g, request
        if hasattr(g, "start_time"):
            elapsed_ms = (time.perf_counter() - g.start_time) * 1000
            response.headers["X-Response-Time"] = f"{elapsed_ms:.1f}ms"
            if elapsed_ms > 500:
                app.logger.warning(
                    f"slow_request method={request.method} path={request.path} "
                    f"duration_ms={elapsed_ms:.1f}"
                )
        return response

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.builds import builds_bp
    from app.routes.craft import craft_bp
    from app.routes.ref import ref_bp
    from app.routes.passives import passives_bp
    from app.routes.profile import profile_bp
    from app.routes.simulate import simulate_bp
    from app.routes.admin import admin_bp
    from app.routes.jobs import jobs_bp
    from app.routes.version import version_bp
    from app.routes.import_route import import_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(builds_bp, url_prefix="/api/builds")
    app.register_blueprint(import_bp, url_prefix="/api/import")
    app.register_blueprint(craft_bp, url_prefix="/api/craft")
    app.register_blueprint(ref_bp, url_prefix="/api/ref")
    app.register_blueprint(passives_bp, url_prefix="/api/passives")
    app.register_blueprint(profile_bp, url_prefix="/api/profile")
    app.register_blueprint(simulate_bp, url_prefix="/api/simulate")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
    app.register_blueprint(version_bp, url_prefix="/api/version")

    # Global error handler for domain exceptions
    from app.utils.exceptions import ForgeError

    @app.errorhandler(ForgeError)
    def handle_forge_error(exc):
        from app.utils.responses import error as error_response
        return error_response(exc.message, status=exc.status_code)

    # Register CLI commands
    from app.utils.cli import register_commands
    register_commands(app)

    # Health check
    @app.get("/api/health")
    def health():
        return {"status": "ok", "env": env}

    @app.get("/api/test")
    def test():
        return {"message": "API is running"}

    return app