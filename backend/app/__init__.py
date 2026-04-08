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


def _init_limiter(app: Flask) -> None:
    """Initialize rate limiter with Redis, falling back to in-memory if unavailable."""
    redis_url = app.config.get("RATELIMIT_STORAGE_URI", "")
    if redis_url and redis_url != "memory://":
        try:
            import redis as _redis
            r = _redis.from_url(redis_url, socket_connect_timeout=2)
            r.ping()
        except Exception:
            app.logger.warning(
                "Redis unavailable for rate limiting — falling back to in-memory storage. "
                "This is fine for development but not recommended for production."
            )
            app.config["RATELIMIT_STORAGE_URI"] = "memory://"
    limiter.init_app(app)


def create_app(env: str = "development") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[env])

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    _init_limiter(app)

    CORS(
        app,
        origins=[app.config["FRONTEND_URL"]],
        supports_credentials=True,
    )

    configure_logging(app)

    # Data pipeline + registries
    from app.game_data.pipeline import GameDataPipeline
    from app.domain.registries.skill_registry import SkillRegistry
    from app.domain.registries.affix_registry import AffixRegistry
    from app.domain.registries.enemy_registry import EnemyRegistry

    pipeline = GameDataPipeline()
    pipeline.load_all()
    app.extensions["game_data"] = pipeline

    affix_registry = AffixRegistry(pipeline.affixes)
    skill_registry = SkillRegistry(pipeline.skills)
    enemy_registry = EnemyRegistry(pipeline.enemies)

    versions = {
        affix_registry.data_version,
        skill_registry.data_version,
        enemy_registry.data_version,
    }
    if len(versions) != 1:
        raise RuntimeError(
            f"Registry version mismatch detected: {versions}"
        )

    app.extensions["affix_registry"] = affix_registry
    app.extensions["skill_registry"] = skill_registry
    app.extensions["enemy_registry"] = enemy_registry

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

    # Rate limit violation handler — log and return structured JSON
    @app.errorhandler(429)
    def _rate_limit_exceeded(e):
        from flask import jsonify, request as req
        app.logger.warning(
            f"rate_limit_exceeded ip={req.remote_addr} "
            f"path={req.path} method={req.method}"
        )
        return jsonify({
            "error": "rate_limit_exceeded",
            "message": str(e.description),
        }), 429

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.builds import builds_bp
    from app.routes.craft import craft_bp
    from app.routes.ref import ref_bp
    from app.routes.passives import passives_bp
    from app.routes.profile import profile_bp
    from app.routes.simulate import simulate_bp
    from app.routes.optimize import optimize_bp
    from app.routes.rotation import rotation_bp
    from app.routes.conditional import conditional_bp
    from app.routes.multi_target import multi_target_bp
    from app.routes.load import load_bp
    from app.routes.admin import admin_bp
    from app.routes.jobs import jobs_bp
    from app.routes.version import version_bp
    from app.routes.import_route import import_bp
    from app.routes.bis_search import bis_bp
    from app.routes.skills import skills_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(builds_bp, url_prefix="/api/builds")
    app.register_blueprint(import_bp, url_prefix="/api/import")
    app.register_blueprint(craft_bp, url_prefix="/api/craft")
    app.register_blueprint(ref_bp, url_prefix="/api/ref")
    app.register_blueprint(passives_bp, url_prefix="/api/passives")
    app.register_blueprint(profile_bp, url_prefix="/api/profile")
    app.register_blueprint(simulate_bp, url_prefix="/api/simulate")
    app.register_blueprint(optimize_bp, url_prefix="/api/optimize")
    app.register_blueprint(rotation_bp, url_prefix="/api/simulate")
    app.register_blueprint(conditional_bp, url_prefix="/api/simulate")
    app.register_blueprint(multi_target_bp, url_prefix="/api/simulate")
    app.register_blueprint(load_bp, url_prefix="/api/load")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
    app.register_blueprint(version_bp, url_prefix="/api/version")
    app.register_blueprint(bis_bp, url_prefix="/api/bis")
    app.register_blueprint(skills_bp, url_prefix="/api")

    # Global error handlers — always return JSON so frontend can parse the response
    from app.utils.exceptions import ForgeError

    @app.errorhandler(ForgeError)
    def handle_forge_error(exc):
        from app.utils.responses import error as error_response
        return error_response(exc.message, status=exc.status_code)

    @app.errorhandler(Exception)
    def handle_unexpected_error(exc):
        from flask import jsonify
        app.logger.exception("Unhandled exception: %s", exc)
        return jsonify({"data": None, "meta": None, "errors": [{"message": "Internal server error"}]}), 500

    @app.errorhandler(404)
    def handle_not_found(_exc):
        from flask import jsonify
        return jsonify({"data": None, "meta": None, "errors": [{"message": "Not found"}]}), 404

    # Register CLI commands
    from app.utils.cli import register_commands
    register_commands(app)

    # Health check
    @app.get("/api/health")
    def health():
        return {"status": "ok", "env": env}

    return app