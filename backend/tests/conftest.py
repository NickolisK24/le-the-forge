"""
pytest fixtures for The Forge backend test suite.

Run with:
    pytest                        # all tests
    pytest tests/test_craft.py    # single file
    pytest -v --tb=short          # verbose with short tracebacks
"""

import pytest
from app import create_app, db as _db
from app.models import User, Build


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Fresh DB state per test — rolls back after each."""
    with app.app_context():
        yield _db
        _db.session.rollback()
        # Clear all tables between tests
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(db):
    u = User(discord_id="test-discord-123", username="TestUser")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def auth_headers(app, user):
    """Returns Authorization header for the test user."""
    from flask_jwt_extended import create_access_token
    with app.app_context():
        token = create_access_token(identity=user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_build(db, user):
    from app.services.build_service import create_build
    return create_build(
        {
            "name": "Test Bone Curse Lich",
            "character_class": "Acolyte",
            "mastery": "Lich",
            "passive_tree": [1, 5, 12, 20],
            "is_ssf": True,
        },
        user_id=user.id,
    )
