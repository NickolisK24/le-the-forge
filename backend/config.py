import os
from datetime import timedelta


class Config:
    """Base configuration shared across all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-dev-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://forge:forgedev@127.0.0.1:5432/the_forge"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Reference data version — bump when affixes.json / game data changes.
    DATA_VERSION = os.environ.get("DATA_VERSION", "1.0.0")
    # Last Epoch patch string tracked by this instance.
    CURRENT_PATCH = os.environ.get("CURRENT_PATCH", "1.4.3")
    # Last Epoch season number tracked by this instance.
    CURRENT_SEASON = int(os.environ.get("CURRENT_SEASON", "4"))

    DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID", "")
    DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")
    DISCORD_REDIRECT_URI = os.environ.get(
        "DISCORD_REDIRECT_URI", "http://localhost:5050/api/auth/discord/authorized"
    )

    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

    # Pagination defaults
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # Rate limiting
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    RATELIMIT_DEFAULT = "200 per day;50 per hour"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Set True to log all SQL
    LOG_LEVEL = "DEBUG"
    # Much higher limits in dev so testing never hits the ceiling
    RATELIMIT_DEFAULT = "10000 per day;2000 per hour;200 per minute"


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    LOG_LEVEL = "INFO"
    # Emit structured JSON logs so Render's log search can filter by field.
    LOG_FORMAT_JSON = True

    # Production-hardened pool settings for higher concurrency
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
    }

    # Tighter rate limits for production
    RATELIMIT_DEFAULT = "1000 per day;200 per hour;30 per minute"

    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate that all required production secrets are set via environment
        variables and are not using insecure defaults. Returns a list of
        validation errors (empty list means all checks passed).
        """
        errors: list[str] = []

        if cls.SECRET_KEY in ("dev-secret", ""):
            errors.append(
                "SECRET_KEY must be set to a strong random value in production. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        if cls.JWT_SECRET_KEY in ("jwt-dev-secret", ""):
            errors.append(
                "JWT_SECRET_KEY must be set to a strong random value in production. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        if "localhost" in (cls.SQLALCHEMY_DATABASE_URI or ""):
            errors.append(
                "DATABASE_URL points to localhost — set it to your production database."
            )
        if not cls.DISCORD_CLIENT_ID:
            errors.append("DISCORD_CLIENT_ID is required for Discord OAuth in production.")
        if not cls.DISCORD_CLIENT_SECRET:
            errors.append("DISCORD_CLIENT_SECRET is required for Discord OAuth in production.")

        frontend = cls.FRONTEND_URL or ""
        if "localhost" in frontend:
            errors.append(
                f"FRONTEND_URL is '{frontend}' — set it to your production domain "
                f"(e.g. https://epochforge.gg)."
            )

        return errors


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    # Use in-process memory storage so tests never need a running Redis
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
