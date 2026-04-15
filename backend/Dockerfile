# ---------------------------------------------------------------------------
# The Forge — Backend Dockerfile
# Multi-stage build: slim production image with Gunicorn
# ---------------------------------------------------------------------------

# --- Stage 1: Install dependencies -------------------------------------------
FROM python:3.11-slim AS deps

WORKDIR /app

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Production image -----------------------------------------------
FROM python:3.11-slim AS production

# Security: run as non-root user
RUN groupadd -r forge && useradd -r -g forge -s /sbin/nologin forge

WORKDIR /app

# Copy virtualenv from deps stage
COPY --from=deps /venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy application code
COPY . .

# Ensure entrypoint is executable
RUN chmod +x entrypoint.sh 2>/dev/null || true

# Own the app directory
RUN chown -R forge:forge /app

USER forge

# Environment defaults (override via docker-compose or orchestrator)
ENV FLASK_APP=wsgi.py \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GUNICORN_WORKERS=4 \
    GUNICORN_THREADS=2 \
    GUNICORN_TIMEOUT=120 \
    GUNICORN_BIND=0.0.0.0:5000

EXPOSE 5000

# Health check — hit the /api/health endpoint every 30s
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# Production: Gunicorn with configurable workers/threads
# The entrypoint runs migrations first, then exec's the CMD
ENTRYPOINT ["./entrypoint.sh"]
CMD ["sh", "-c", "gunicorn wsgi:app --workers=${GUNICORN_WORKERS} --threads=${GUNICORN_THREADS} --timeout=${GUNICORN_TIMEOUT} --bind=${GUNICORN_BIND} --access-logfile=- --error-logfile=- --preload"]
