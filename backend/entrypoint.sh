#!/bin/sh
set -e

echo "=== The Forge Backend ==="
echo "Environment: ${FLASK_ENV:-production}"

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Seed reference data (idempotent — skips if already present)
echo "Seeding reference data..."
flask seed 2>/dev/null || echo "  seed: skipped (command not registered)"
flask seed-passives 2>/dev/null || echo "  seed-passives: skipped (command not registered)"

echo "Starting server..."
exec "$@"
